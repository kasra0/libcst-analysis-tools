"""Analyze complete module structure in a single pass."""

from typing import Dict, List
import libcst as cst
from libcst.metadata import PositionProvider, MetadataWrapper
from .list_classes import ClassInfo
from .list_methods import MethodInfo


class CompleteModuleAnalyzer(cst.CSTVisitor):
    """Collect all classes and their methods in a single traversal."""
    
    METADATA_DEPENDENCIES = (PositionProvider,)
    
    def __init__(self):
        self.classes: List[ClassInfo] = []
        self.methods_by_class: Dict[str, List[MethodInfo]] = {}
        self._current_class: str | None = None
        self._class_depth = 0
    
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
    
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        if self._current_class and self._class_depth == 1:
            position = self.get_metadata(PositionProvider, node)
            
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
    tree = cst.parse_module(source_code)
    wrapper = MetadataWrapper(tree)
    visitor = CompleteModuleAnalyzer()
    wrapper.visit(visitor)
    
    return visitor.methods_by_class

def get_all_classes_with_methods_from_file(file_path: str) -> List[tuple[ClassInfo, List[MethodInfo]]]:
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


def get_all_classes_with_methods(source_code: str) -> List[tuple[ClassInfo, List[MethodInfo]]]:
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
