"""Utility to list all class definitions in a Python module using LibCST."""

from typing import List, Dict, Any, Union
import libcst as cst
from libcst.metadata import PositionProvider, MetadataWrapper
import inspect
import types


class ClassDefinitionVisitor(cst.CSTVisitor):
    """Visitor that collects all class definitions in a module."""
    
    METADATA_DEPENDENCIES = (PositionProvider,)
    
    def __init__(self):
        self.classes: List[Dict[str, Any]] = []
    
    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        """Visit a class definition and collect its information."""
        class_info = {
            "name": node.name.value,
            "lineno": self._get_line_number(node),
            "bases": [self._get_base_name(base.value) for base in node.bases],
            "decorators": [self._get_decorator_name(dec) for dec in node.decorators],
        }
        self.classes.append(class_info)
    
    def _get_line_number(self, node: cst.ClassDef) -> int:
        """Get the line number of a node."""
        try:
            position = self.get_metadata(PositionProvider, node)
            return position.start.line # type: ignore
        except Exception:
            return -1
    
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


def list_classes_from_source_code(source_code: str) -> List[Dict[str, Any]]:
    """
    List all class definitions in the given Python source code.
    
    Args:
        source_code: Python source code as a string
        
    Returns:
        A list of dictionaries containing class information:
        - name: class name
        - lineno: line number where class is defined
        - bases: list of base class names
        - decorators: list of decorator names
        
    Example:
        >>> code = '''
        ... class MyClass:
        ...     pass
        ... 
        ... class AnotherClass(MyClass):
        ...     pass
        ... '''
        >>> classes = list_classes_from_source_code(code)
        >>> len(classes)
        2
        >>> classes[0]['name']
        'MyClass'
    """
    try:
        tree = cst.parse_module(source_code)
        
        # Use MetadataWrapper to collect position metadata
        wrapper = MetadataWrapper(tree)
        visitor = ClassDefinitionVisitor()
        
        # Visit the tree with metadata enabled
        wrapper.visit(visitor)
        
        return visitor.classes
    except Exception as e:
        raise ValueError(f"Failed to parse source code: {e}")


def list_classes_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    List all class definitions in a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        A list of dictionaries containing class information
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    return list_classes_from_source_code(source_code)


def list_classes_from_module(module: Union[types.ModuleType, str]) -> List[Dict[str, Any]]:
    """
    List all class definitions in an imported Python module.
    
    Args:
        module: Either an imported module object or module name as string
        
    Returns:
        A list of dictionaries containing class information
        
    Example:
        >>> import transformers
        >>> classes = list_classes_from_module(transformers)
        >>> # Or by name
        >>> classes = list_classes_from_module('transformers')
    """
    if isinstance(module, str):
        # If string, try to import the module
        import importlib
        try:
            module = importlib.import_module(module)
        except ImportError as e:
            raise ValueError(f"Could not import module '{module}': {e}")
    
    if not isinstance(module, types.ModuleType):
        raise ValueError(f"Expected module object or string, got {type(module)}")
    
    # Get the source file path
    try:
        module_file = inspect.getfile(module)
        if module_file.endswith('.pyc'):
            module_file = module_file[:-1]  # Convert .pyc to .py
    except (OSError, TypeError):
        # For built-in modules or modules without source files
        raise ValueError(f"Cannot get source file for module {module.__name__}. "
                        "This might be a built-in module or compiled extension.")
    
    # Read and parse the source file
    return list_classes_from_file(module_file)


# Backward compatibility alias
def list_classes(source_code: str) -> List[Dict[str, Any]]:
    """Backward compatibility alias for list_classes_from_source_code."""
    return list_classes_from_source_code(source_code)

example_code = """
class MyClass:
    '''A simple class.'''
    pass

class AnotherClass(MyClass):
    '''Inherits from MyClass.'''
    def method1(self):
        pass

@dataclass
class DataClass:
    '''A dataclass.'''
    name: str
    value: int
"""

def main():
    """Entry point for the CLI script."""
    from cli_utils import create_common_parser, process_files, format_classes_results
    
    def run_example():
        """Run the example with hardcoded code."""
        classes = list_classes_from_source_code(example_code)
        print("Source code example:") 
        print(example_code)
        print("Extracted classes:")
        for cls in classes:
            print(f"  - {cls['name']} (bases: {cls['bases']}, decorators: {cls['decorators']})")
    
    parser = create_common_parser(
        "List all class definitions in Python files using LibCST",
        "list_classes"
    )
    args = parser.parse_args()
    process_files(args, run_example, list_classes_from_file, format_classes_results)


if __name__ == "__main__":
    main()
