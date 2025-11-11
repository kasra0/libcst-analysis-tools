"""Analyze complete module structure in a single pass."""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import libcst as cst
from libcst.metadata import PositionProvider, MetadataWrapper
from .list_classes import ClassInfo
from .list_methods import MethodInfo

ClassWithMethods = tuple[ClassInfo, list[MethodInfo]]
ClassesWithMethods = list[ClassWithMethods]

@dataclass
class ImportInfo:
    """Information about an import statement."""
    name: str  # The module or item being imported
    lineno: int
    alias: Optional[str] = None  # The 'as' alias if any
    is_from: bool = False  # True for 'from X import Y'
    module: Optional[str] = None  # The module name in 'from X import Y'

@dataclass
class FunctionInfo:
    """Information about a module-level function."""
    name: str
    lineno: int
    parameters: List[str]
    decorators: List[str]
    is_async: bool

@dataclass
class VariableInfo:
    """Information about a class variable or module constant."""
    name: str
    lineno: int
    value: Optional[str] = None  # String representation of the value
    is_class_var: bool = False  # True if it's a class variable

@dataclass
class CallGraphInfo:
    """Call graph information for a callable (function/method)."""
    name: str  # The callable name
    incoming: List[str] = field(default_factory=list)  # Who calls this
    outgoing: List[str] = field(default_factory=list)  # What this calls

@dataclass
class ModuleInfo:
    """Complete information about a module."""
    imports: List[ImportInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    methods_by_class: Dict[str, List[MethodInfo]] = field(default_factory=dict)
    class_variables: Dict[str, List[VariableInfo]] = field(default_factory=dict)  # class_name -> variables
    module_constants: List[VariableInfo] = field(default_factory=list)
    call_graph: Dict[str, CallGraphInfo] = field(default_factory=dict)  # callable_name -> call graph

class CompleteModuleAnalyzer(cst.CSTVisitor):
    """Collect all classes, methods, functions, variables, and imports in a single traversal."""
    
    METADATA_DEPENDENCIES = (PositionProvider,)
    
    def __init__(self):
        self.classes: List[ClassInfo] = []
        self.methods_by_class: Dict[str, List[MethodInfo]] = {}
        self.class_variables: Dict[str, List[VariableInfo]] = {}
        self.functions: List[FunctionInfo] = []
        self.imports: List[ImportInfo] = []
        self.module_constants: List[VariableInfo] = []
        self.call_graph: Dict[str, CallGraphInfo] = {}
        
        self._current_class: str | None = None
        self._current_function: str | None = None  # Track current function for call graph
        self._class_depth = 0
        self._function_depth = 0
    
    def visit_Import(self, node: cst.Import) -> None:
        """Visit an import statement."""
        position = self.get_metadata(PositionProvider, node)
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                import_name = name.name.value if isinstance(name.name, cst.Name) else self._get_dotted_name(name.name)
                alias_name = None
                if name.asname and isinstance(name.asname.name, cst.Name):
                    alias_name = name.asname.name.value
                
                import_info = ImportInfo(
                    name=import_name,
                    lineno=position.start.line if position else -1,  # type: ignore
                    alias=alias_name,
                    is_from=False
                )
                self.imports.append(import_info)
    
    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Visit a from...import statement."""
        position = self.get_metadata(PositionProvider, node)
        module_name = self._get_dotted_name(node.module) if node.module else ""
        
        if isinstance(node.names, cst.ImportStar):
            import_info = ImportInfo(
                name="*",
                lineno=position.start.line if position else -1,  # type: ignore
                module=module_name,
                is_from=True
            )
            self.imports.append(import_info)
        else:
            for name in node.names:
                if isinstance(name, cst.ImportAlias):
                    import_name = name.name.value if isinstance(name.name, cst.Name) else self._get_dotted_name(name.name)
                    alias_name = None
                    if name.asname and isinstance(name.asname.name, cst.Name):
                        alias_name = name.asname.name.value
                    
                    import_info = ImportInfo(
                        name=import_name,
                        lineno=position.start.line if position else -1,  # type: ignore
                        alias=alias_name,
                        module=module_name,
                        is_from=True
                    )
                    self.imports.append(import_info)
    
    def visit_Assign(self, node: cst.Assign) -> None:
        """Visit an assignment to capture class variables and module constants."""
        position = self.get_metadata(PositionProvider, node)
        
        # Get variable names
        for target in node.targets:
            if isinstance(target.target, cst.Name):
                var_name = target.target.value
                # Try to get a string representation of the value
                value_str = None
                try:
                    value_str = cst.Module([]).code_for_node(node.value)
                    if len(value_str) > 100:  # Truncate long values
                        value_str = value_str[:100] + "..."
                except Exception:
                    pass
                
                var_info = VariableInfo(
                    name=var_name,
                    lineno=position.start.line if position else -1,  # type: ignore
                    value=value_str,
                    is_class_var=self._current_class is not None
                )
                
                if self._current_class and self._class_depth == 1 and self._function_depth == 0:
                    # Class variable
                    if self._current_class not in self.class_variables:
                        self.class_variables[self._current_class] = []
                    self.class_variables[self._current_class].append(var_info)
                elif self._class_depth == 0 and self._function_depth == 0:
                    # Module-level constant
                    self.module_constants.append(var_info)
    
    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        if self._class_depth == 0:  # Only top-level classes
            self._current_class = node.name.value
            position = self.get_metadata(PositionProvider, node)
            
            class_info = ClassInfo(
                name=node.name.value,
                lineno=position.start.line if position else -1,  # type: ignore
                bases=[self._get_base_name(base.value) for base in node.bases],
                decorators=[self._get_decorator_name(dec) for dec in node.decorators]
            )
            self.classes.append(class_info)
            self.methods_by_class[self._current_class] = []
        
        self._class_depth += 1
        return True
    
    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self._class_depth -= 1
        if self._class_depth == 0:
            self._current_class = None
    
    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        position = self.get_metadata(PositionProvider, node)
        
        if self._current_class and self._class_depth == 1:
            # This is a method
            method_name = f"{self._current_class}.{node.name.value}"
            self._current_function = method_name
            
            # Initialize call graph for this method
            if method_name not in self.call_graph:
                self.call_graph[method_name] = CallGraphInfo(name=method_name)
            
            method_info = MethodInfo(
                name=node.name.value,
                lineno=position.start.line if position else -1,  # type: ignore
                parameters=self._get_parameters(node.params),
                decorators=[self._get_decorator_name(dec) for dec in node.decorators],
                is_async=node.asynchronous is not None,
                is_staticmethod=self._has_decorator(node, "staticmethod"),
                is_classmethod=self._has_decorator(node, "classmethod"),
                is_property=self._has_decorator(node, "property")
            )
            self.methods_by_class[self._current_class].append(method_info)
        elif self._class_depth == 0:
            # This is a module-level function
            func_name = node.name.value
            self._current_function = func_name
            
            # Initialize call graph for this function
            if func_name not in self.call_graph:
                self.call_graph[func_name] = CallGraphInfo(name=func_name)
            
            function_info = FunctionInfo(
                name=node.name.value,
                lineno=position.start.line if position else -1,  # type: ignore
                parameters=self._get_parameters(node.params),
                decorators=[self._get_decorator_name(dec) for dec in node.decorators],
                is_async=node.asynchronous is not None
            )
            self.functions.append(function_info)
        
        self._function_depth += 1
        return True
    
    def leave_FunctionDef(self, node: cst.FunctionDef) -> None:
        self._function_depth -= 1
        if self._function_depth == 0:
            self._current_function = None
    
    def visit_Call(self, node: cst.Call) -> None:
        """Track function/method calls to build call graph."""
        if not self._current_function:
            return
        
        # Try to resolve the callable name
        callee_name = self._resolve_call_name(node.func)
        if not callee_name:
            return
        
        # Add outgoing call from current function
        if self._current_function in self.call_graph:
            if callee_name not in self.call_graph[self._current_function].outgoing:
                self.call_graph[self._current_function].outgoing.append(callee_name)
        
        # Add incoming call to callee (initialize if needed)
        if callee_name not in self.call_graph:
            self.call_graph[callee_name] = CallGraphInfo(name=callee_name)
        if self._current_function not in self.call_graph[callee_name].incoming:
            self.call_graph[callee_name].incoming.append(self._current_function)
    
    def _resolve_call_name(self, func: cst.BaseExpression) -> str | None:
        """Resolve the name of a called function/method."""
        if isinstance(func, cst.Name):
            # Direct call: func()
            return func.value
        elif isinstance(func, cst.Attribute):
            # Method call: obj.method() or self.method()
            if isinstance(func.value, cst.Name):
                if func.value.value == "self" and self._current_class:
                    # self.method() -> resolve to ClassName.method
                    return f"{self._current_class}.{func.attr.value}"
                # Otherwise just return method name
                return func.attr.value
            # For chained calls like obj.a.b(), just return the final method name
            return func.attr.value
        return None
    
    def _get_dotted_name(self, node: cst.BaseExpression) -> str:
        """Get a dotted name like 'a.b.c' from a node."""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            value_str = self._get_dotted_name(node.value)
            return f"{value_str}.{node.attr.value}"
        return str(node)
    
    def _get_base_name(self, base: cst.BaseExpression) -> str:
        """Extract the name of a base class."""
        if isinstance(base, cst.Name):
            return base.value
        elif isinstance(base, cst.Attribute):
            return cst.Module([]).code_for_node(base)
        return str(base)
    
    def _get_decorator_name(self, decorator: cst.Decorator) -> str:
        """Extract the name of a decorator."""
        if isinstance(decorator.decorator, cst.Name):
            return decorator.decorator.value
        elif isinstance(decorator.decorator, cst.Call):
            if isinstance(decorator.decorator.func, cst.Name):
                return decorator.decorator.func.value
        return str(decorator.decorator)
    
    def _get_parameters(self, params: cst.Parameters) -> List[str]:
        """Extract parameter names from function parameters."""
        param_names = []
        
        for param in params.params:
            param_names.append(param.name.value)
        
        if params.star_arg and isinstance(params.star_arg, cst.Param):
            param_names.append(f"*{params.star_arg.name.value}")
        
        for param in params.kwonly_params:
            param_names.append(param.name.value)
        
        if params.star_kwarg:
            param_names.append(f"**{params.star_kwarg.name.value}")
        
        return param_names
    
    def _has_decorator(self, node: cst.FunctionDef, decorator_name: str) -> bool:
        """Check if a function has a specific decorator."""
        for dec in node.decorators:
            if isinstance(dec.decorator, cst.Name):
                if dec.decorator.value == decorator_name:
                    return True
        return False


def get_complete_module_info(source_code: str) -> ModuleInfo:
    """
    Get complete module information including imports, functions, classes, methods, and variables.
    
    Args:
        source_code: Python source code as a string
        
    Returns:
        ModuleInfo object containing all module elements
        
    Example:
        >>> info = get_complete_module_info(code)
        >>> print(f"Imports: {len(info.imports)}")
        >>> print(f"Functions: {len(info.functions)}")
        >>> print(f"Classes: {len(info.classes)}")
    """
    tree = cst.parse_module(source_code)
    wrapper = MetadataWrapper(tree)
    visitor = CompleteModuleAnalyzer()
    wrapper.visit(visitor)
    
    return ModuleInfo(
        imports=visitor.imports,
        functions=visitor.functions,
        classes=visitor.classes,
        methods_by_class=visitor.methods_by_class,
        class_variables=visitor.class_variables,
        module_constants=visitor.module_constants,
        call_graph=visitor.call_graph
    )


def get_complete_module_info_from_file(file_path: str) -> ModuleInfo:
    """
    Get complete module information from a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        ModuleInfo object containing all module elements
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    return get_complete_module_info(source_code)


def analyze_module_complete(source_code: str) -> Dict[str, List[MethodInfo]]:
    """
    Analyze a module and return all classes with their methods in ONE pass.
    
    Args:
        source_code: Python source code as a string
        
    Returns:
        Dictionary mapping class names to lists of MethodInfo objects
        
    Example:
        >>> code = '''
        ... class MyClass:
        ...     def method1(self):
        ...         pass
        ...     def method2(self):
        ...         pass
        ... '''
        >>> result = analyze_module_complete(code)
        >>> result['MyClass'][0].name
        'method1'
    """
    tree    = cst.parse_module(source_code)
    wrapper = MetadataWrapper(tree)
    visitor = CompleteModuleAnalyzer()
    wrapper.visit(visitor)
    
    return visitor.methods_by_class

def get_all_classes_with_methods_from_file(file_path: str) -> ClassesWithMethods:
    """
    Get all classes with their methods from a Python file in ONE parsing pass.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of tuples (ClassInfo, List[MethodInfo])
        
    Example:
        >>> for cls, methods in get_all_classes_with_methods_from_file('example.py'):
        ...     print(f"{cls.name}: {len(methods)} methods")
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    tree = cst.parse_module(source_code)
    wrapper = MetadataWrapper(tree)
    visitor = CompleteModuleAnalyzer()
    wrapper.visit(visitor)
    
    return [(cls, visitor.methods_by_class.get(cls.name, [])) 
            for cls in visitor.classes]


def get_all_classes_with_methods(source_code: str) -> ClassesWithMethods:
    """
    Get all classes with their methods in ONE parsing pass.
    
    Args:
        source_code: Python source code as a string
        
    Returns:
        List of tuples (ClassInfo, List[MethodInfo])
        
    Example:
        >>> for cls, methods in get_all_classes_with_methods(code):
        ...     print(f"{cls.name}: {len(methods)} methods")
    """
    tree = cst.parse_module(source_code)
    wrapper = MetadataWrapper(tree)
    visitor = CompleteModuleAnalyzer()
    wrapper.visit(visitor)
    
    return [(cls, visitor.methods_by_class.get(cls.name, [])) 
            for cls in visitor.classes]
