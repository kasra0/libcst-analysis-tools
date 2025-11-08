"""
Mini API ts-morph-like pour Python, basé sur libcst.

Objectif : fournir des fonctions getXXXFromYYY(...) pour explorer un projet Python
(dossiers, packages, modules, classes, fonctions, méthodes, args) en statique,
avec libcst comme backend.

Ce fichier est pensé comme point de départ pédagogique / outil interne.
Tu peux l'adapter librement.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

import libcst as cst

# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Folder:
    path: Path

    def __post_init__(self):
        if not self.path.is_dir():
            raise ValueError(f"Folder does not exist or is not a directory: {self.path}")


@dataclass(frozen=True)
class File:
    path: Path

    def __post_init__(self):
        if not self.path.is_file():
            raise ValueError(f"File does not exist: {self.path}")
        if self.path.suffix != ".py":
            raise ValueError(f"Not a Python file: {self.path}")


@dataclass(frozen=True)
class Package:
    name: str           # ex: "mypkg.subpkg"
    path: Path          # chemin du dossier du package


@dataclass(frozen=True)
class Module:
    name: str           # ex: "mypkg.mod" ou "mypkg.__init__"
    path: Path          # chemin du .py
    package: Optional[Package]


@dataclass(frozen=True)
class Class:
    name: str
    module: Module
    node: cst.ClassDef


@dataclass(frozen=True)
class Function:
    name: str
    module: Module
    node: cst.FunctionDef


@dataclass(frozen=True)
class Method:
    name: str
    cls: Class
    module: Module
    node: cst.FunctionDef


class ArgKind(Enum):
    POSITIONAL_ONLY = auto()
    POSITIONAL_OR_KEYWORD = auto()
    VAR_POSITIONAL = auto()   # *args
    KEYWORD_ONLY = auto()
    VAR_KEYWORD = auto()      # **kwargs


@dataclass(frozen=True)
class Arg:
    name: Optional[str]          # None pour *args sans nom (rare) etc.
    annotation: Optional[str]
    default: Optional[str]
    kind: ArgKind
    function: Union[Function, Method]


# ---------------------------------------------------------------------------
# Index interne par module
# ---------------------------------------------------------------------------


@dataclass
class ModuleIndex:
    module: Module
    classes: List[Class]
    functions: List[Function]
    methods: List[Method]


class _CSTCollector(cst.CSTVisitor):
    """Visiteur pour collecter classes, fonctions et méthodes dans un module."""

    def __init__(self, module: Module):
        self.module = module
        self.classes: List[Class] = []
        self.functions: List[Function] = []
        self.methods: List[Method] = []
        self._class_stack: List[Class] = []

    # Top-level function
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        if not self._class_stack:
            fn = Function(name=node.name.value, module=self.module, node=node)
            self.functions.append(fn)
        else:
            # Méthode de la classe courante
            cls = self._class_stack[-1]
            m = Method(name=node.name.value, cls=cls, module=self.module, node=node)
            self.methods.append(m)

    # Classes
    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        cls = Class(name=node.name.value, module=self.module, node=node)
        self.classes.append(cls)
        self._class_stack.append(cls)

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self._class_stack.pop()


# ---------------------------------------------------------------------------
# Project : façade principale
# ---------------------------------------------------------------------------


class Project:
    """Représente un projet Python rooté sur un dossier.

    Construit un index basé sur libcst, utilisable via les fonctions getXXXFromYYY.
    """

    def __init__(self, root: Union[str, Path]):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise ValueError(f"Project root must be a folder: {self.root}")

        self._folders: Dict[Path, Folder] = {}
        self._files: Dict[Path, File] = {}
        self._packages: Dict[Path, Package] = {}
        self._modules_by_path: Dict[Path, Module] = {}
        self._module_indexes: Dict[Path, ModuleIndex] = {}

        self._build_index()

    # ------------------------- scan & index -------------------------

    def _build_index(self) -> None:
        # 1. créer Folder/File de base
        for path in self.root.rglob("*.py"):
            self._files[path] = File(path)
            parent = path.parent
            while parent is not None and parent.is_dir() and parent >= self.root:
                self._folders.setdefault(parent, Folder(parent))
                if parent == self.root:
                    break
                parent = parent.parent

        # 2. détecter les packages (__init__.py)
        for folder in list(self._folders.values()):
            init_file = folder.path / "__init__.py"
            if init_file.exists():
                rel = folder.path.relative_to(self.root)
                pkg_name = ".".join(rel.parts) if rel.parts else ""
                if pkg_name:
                    self._packages[folder.path] = Package(name=pkg_name, path=folder.path)

        # 3. créer les modules
        for path, file in self._files.items():
            rel = path.relative_to(self.root)
            parts = list(rel.parts)
            if parts[-1] == "__init__.py":
                # module de package
                pkg_path = path.parent
                pkg = self._packages.get(pkg_path)
                if pkg is not None:
                    mod_name = pkg.name + ".__init__"
                else:
                    # __init__ sans package détecté (edge) : traiter comme module normal
                    mod_name = ".".join(parts)[:-3]
                    pkg = None
            else:
                mod_name = ".".join(parts)[:-3]  # retire ".py"
                # trouver package parent si il existe
                pkg = None
                parent = path.parent
                while parent != self.root.parent:
                    if parent in self._packages:
                        pkg = self._packages[parent]
                        break
                    parent = parent.parent

            module = Module(name=mod_name, path=path, package=pkg)
            self._modules_by_path[path] = module

        # 4. parser chaque module avec libcst + construire ModuleIndex
        for path, module in self._modules_by_path.items():
            code = path.read_text(encoding="utf-8")
            try:
                tree = cst.parse_module(code)
            except Exception as e:  # pragma: no cover - robustesse
                # on ignore les fichiers non parsables
                continue

            collector = _CSTCollector(module)
            tree.visit(collector)

            index = ModuleIndex(
                module=module,
                classes=collector.classes,
                functions=collector.functions,
                methods=collector.methods,
            )
            self._module_indexes[path] = index

    # ------------------------- Helpers internes -------------------------

    def _get_module_index(self, module: Module) -> ModuleIndex:
        idx = self._module_indexes.get(module.path)
        if idx is None:
            raise KeyError(f"No index for module {module}")
        return idx

    # -------------------------------------------------------------------
    # API getXXXFromYYY
    # -------------------------------------------------------------------

    # --- Folder ---

    def getFoldersFromFolder(self, folder: Folder) -> List[Folder]:
        return [
            Folder(p)
            for p in folder.path.iterdir()
            if p.is_dir()
        ]

    def getFilesFromFolder(self, folder: Folder) -> List[File]:
        return [
            File(p)
            for p in folder.path.iterdir()
            if p.is_file() and p.suffix == ".py"
        ]

    def getPackagesFromFolder(self, folder: Folder) -> List[Package]:
        # packages directement contenus
        result = []
        for p in folder.path.iterdir():
            if p.is_dir() and (p / "__init__.py").exists():
                pkg = self._packages.get(p)
                if pkg:
                    result.append(pkg)
        return result

    def getModulesFromFolder(self, folder: Folder) -> List[Module]:
        result = []
        for p in folder.path.iterdir():
            if p.is_file() and p.suffix == ".py":
                mod = self._modules_by_path.get(p)
                if mod:
                    result.append(mod)
        return result

    # --- File / Package / Module relations ---

    def getModuleFromFile(self, file: File) -> Optional[Module]:
        return self._modules_by_path.get(file.path)

    def getPackageFromFolder(self, folder: Folder) -> Optional[Package]:
        return self._packages.get(folder.path)

    def getSubPackagesFromPackage(self, package: Package) -> List[Package]:
        result = []
        for path, pkg in self._packages.items():
            if path.parent == package.path:
                result.append(pkg)
        return result

    def getModulesFromPackage(self, package: Package) -> List[Module]:
        result = []
        for mod in self._modules_by_path.values():
            if mod.package == package:
                result.append(mod)
        return result

    def getPackageFromModule(self, module: Module) -> Optional[Package]:
        return module.package

    # --- Module → Classes / Functions / Methods ---

    def getClassesFromModule(self, module: Module) -> List[Class]:
        return list(self._get_module_index(module).classes)

    def getFunctionsFromModule(self, module: Module) -> List[Function]:
        return list(self._get_module_index(module).functions)

    def getMethodsFromModule(self, module: Module) -> List[Method]:
        return list(self._get_module_index(module).methods)

    # --- Package agrégé ---

    def getClassesFromPackage(self, package: Package) -> List[Class]:
        classes: List[Class] = []
        for mod in self.getModulesFromPackage(package):
            classes.extend(self.getClassesFromModule(mod))
        return classes

    def getFunctionsFromPackage(self, package: Package) -> List[Function]:
        fns: List[Function] = []
        for mod in self.getModulesFromPackage(package):
            fns.extend(self.getFunctionsFromModule(mod))
        return fns

    def getMethodsFromPackage(self, package: Package) -> List[Method]:
        methods: List[Method] = []
        for mod in self.getModulesFromPackage(package):
            methods.extend(self.getMethodsFromModule(mod))
        return methods

    # --- Class ---

    def getMethodsFromClass(self, cls: Class) -> List[Method]:
        # filtrer les méthodes dont cls correspond
        idx = self._get_module_index(cls.module)
        return [m for m in idx.methods if m.cls == cls]

    def getModuleFromClass(self, cls: Class) -> Module:
        return cls.module

    def getPackageFromClass(self, cls: Class) -> Optional[Package]:
        return cls.module.package

    # --- Function ---

    def getArgsFromFunction(self, fn: Function) -> List[Arg]:
        return _extract_args(fn.node, fn)

    def getModuleFromFunction(self, fn: Function) -> Module:
        return fn.module

    def getPackageFromFunction(self, fn: Function) -> Optional[Package]:
        return fn.module.package

    # --- Method ---

    def getArgsFromMethod(self, m: Method) -> List[Arg]:
        return _extract_args(m.node, m)

    def getClassFromMethod(self, m: Method) -> Class:
        return m.cls

    def getModuleFromMethod(self, m: Method) -> Module:
        return m.module

    def getPackageFromMethod(self, m: Method) -> Optional[Package]:
        return m.module.package

    # --- Args ---

    def getDefaultFromArg(self, arg: Arg) -> Optional[str]:
        return arg.default

    def getAnnotationFromArg(self, arg: Arg) -> Optional[str]:
        return arg.annotation

    def getKindFromArg(self, arg: Arg) -> ArgKind:
        return arg.kind

    def getFunctionFromArg(self, arg: Arg) -> Union[Function, Method]:
        return arg.function


# ---------------------------------------------------------------------------
# Utilitaires : extraction des arguments & signature texte
# ---------------------------------------------------------------------------


def _expr_to_str(node: Optional[cst.CSTNode]) -> Optional[str]:
    if node is None:
        return None
    try:
        # On reconstruit le code source de l'expression telle qu'écrite
        return node.code
    except Exception:  # pragma: no cover - safe fallback
        return None


def _extract_args(fn_node: cst.FunctionDef, owner: Union[Function, Method]) -> List[Arg]:
    params = fn_node.params
    result: List[Arg] = []

    # positional-only (Python 3.8+ "x, /")
    for p in params.posonly_params:
        result.append(
            Arg(
                name=p.name.value,
                annotation=_expr_to_str(p.annotation.annotation) if p.annotation else None,
                default=_expr_to_str(p.default),
                kind=ArgKind.POSITIONAL_ONLY,
                function=owner,
            )
        )

    # regular positional-or-keyword
    for p in params.params:
        result.append(
            Arg(
                name=p.name.value,
                annotation=_expr_to_str(p.annotation.annotation) if p.annotation else None,
                default=_expr_to_str(p.default),
                kind=ArgKind.POSITIONAL_OR_KEYWORD,
                function=owner,
            )
        )

    # *args
    if params.star_arg is not None:
        p = params.star_arg
        result.append(
            Arg(
                name=p.name.value if p.name else None,
                annotation=_expr_to_str(p.annotation.annotation) if p.annotation else None,
                default=None,
                kind=ArgKind.VAR_POSITIONAL,
                function=owner,
            )
        )

    # keyword-only
    for p in params.kwonly_params:
        result.append(
            Arg(
                name=p.name.value,
                annotation=_expr_to_str(p.annotation.annotation) if p.annotation else None,
                default=_expr_to_str(p.default),
                kind=ArgKind.KEYWORD_ONLY,
                function=owner,
            )
        )

    # **kwargs
    if params.star_kwarg is not None:
        p = params.star_kwarg
        result.append(
            Arg(
                name=p.name.value if p.name else None,
                annotation=_expr_to_str(p.annotation.annotation) if p.annotation else None,
                default=None,
                kind=ArgKind.VAR_KEYWORD,
                function=owner,
            )
        )

    return result


# ---------------------------------------------------------------------------
# Exemple d'utilisation (à virer / adapter pour intégration)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Exemple simple : scanner le projet courant
    project = Project(".")

    print("Modules:")
    for mod in sorted({m for m in project._modules_by_path.values()}, key=lambda m: m.name):
        print(" -", mod.name)
        for cls in project.getClassesFromModule(mod):
            print(f"    class {cls.name}")
            for m in project.getMethodsFromClass(cls):
                args = project.getArgsFromMethod(m)
                sig = ", ".join(
                    f"{a.name}: {a.annotation}" if a.annotation else (a.name or "?")
                    for a in args
                )
                print(f"        def {m.name}({sig})")
        for fn in project.getFunctionsFromModule(mod):
            args = project.getArgsFromFunction(fn)
            sig = ", ".join(
                f"{a.name}: {a.annotation}" if a.annotation else (a.name or "?")
                for a in args
            )
            print(f"    def {fn.name}({sig})")
