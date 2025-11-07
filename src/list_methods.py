"""Utility to list all methods of a class using LibCST."""

from typing import List, Dict, Any, Optional
import libcst as cst
from libcst.metadata import PositionProvider, MetadataWrapper



class MethodCollector(cst.CSTVisitor):
    """Visitor that collects methods from a specific class."""
    
    METADATA_DEPENDENCIES = (PositionProvider,)
    
    def __init__(self, target_class_name: str):
        self.target_class_name = target_class_name
        self.methods: List[Dict[str, Any]] = []
        self._current_class: Optional[str] = None
        self._class_depth = 0
    
    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        """Track the current class we're visiting."""
        if self._class_depth == 0:  # Top-level class
            self._current_class = node.name.value
        self._class_depth += 1
        return True
    
    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        """Track when we leave a class."""
        self._class_depth -= 1
        if self._class_depth == 0:
            self._current_class = None
    
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        """Visit a function definition and collect it if it's a method of the target class."""
        if self._current_class == self.target_class_name and self._class_depth == 1:
            method_info = {
                "name": node.name.value,
                "lineno": self._get_line_number(node),
                "parameters": self._get_parameters(node.params),
                "decorators": [self._get_decorator_name(dec) for dec in node.decorators],
                "is_async": isinstance(node, cst.FunctionDef) and node.asynchronous is not None,
                "is_staticmethod": self._has_decorator(node, "staticmethod"),
                "is_classmethod": self._has_decorator(node, "classmethod"),
                "is_property": self._has_decorator(node, "property"),
            }
            self.methods.append(method_info)
    
    def _get_line_number(self, node: cst.FunctionDef) -> int:
        """Get the line number of a node."""
        try:
            position = self.get_metadata(PositionProvider, node)
            return position.start.line # type: ignore
        except Exception:
            return -1
    
    def _get_parameters(self, params: cst.Parameters) -> List[str]:
        """Extract parameter names from function parameters."""
        param_names = []
        
        # Regular parameters
        for param in params.params:
            param_names.append(param.name.value)
        
        # *args
        if params.star_arg and isinstance(params.star_arg, cst.Param):
            param_names.append(f"*{params.star_arg.name.value}")
        
        # Keyword-only parameters (after *args)
        for param in params.kwonly_params:
            param_names.append(param.name.value)
        
        # **kwargs
        if params.star_kwarg:
            param_names.append(f"**{params.star_kwarg.name.value}")
        
        return param_names
    
    def _get_decorator_name(self, decorator: cst.Decorator) -> str:
        """Extract the name of a decorator."""
        if isinstance(decorator.decorator, cst.Name):
            return decorator.decorator.value
        elif isinstance(decorator.decorator, cst.Call):
            if isinstance(decorator.decorator.func, cst.Name):
                return decorator.decorator.func.value
        return str(decorator.decorator)
    
    def _has_decorator(self, node: cst.FunctionDef, decorator_name: str) -> bool:
        """Check if a function has a specific decorator."""
        for decorator in node.decorators:
            if isinstance(decorator.decorator, cst.Name):
                if decorator.decorator.value == decorator_name:
                    return True
            elif isinstance(decorator.decorator, cst.Call):
                if isinstance(decorator.decorator.func, cst.Name):
                    if decorator.decorator.func.value == decorator_name:
                        return True
        return False


def list_methods(source_code: str, class_name: str) -> List[Dict[str, Any]]:
    """
    List all methods of a specific class in the given Python source code.
    
    Args:
        source_code: Python source code as a string
        class_name: Name of the class to extract methods from
        
    Returns:
        A list of dictionaries containing method information:
        - name: method name
        - lineno: line number where method is defined
        - parameters: list of parameter names
        - decorators: list of decorator names
        - is_async: whether the method is async
        - is_staticmethod: whether it's a static method
        - is_classmethod: whether it's a class method
        - is_property: whether it's a property
        
    Example:
        >>> code = '''
        ... class MyClass:
        ...     def __init__(self):
        ...         pass
        ...     
        ...     def method1(self, x):
        ...         return x * 2
        ...     
        ...     @staticmethod
        ...     def static_method():
        ...         pass
        ... '''
        >>> methods = list_methods(code, 'MyClass')
        >>> len(methods)
        3
        >>> methods[0]['name']
        '__init__'
    """
    try:
        tree = cst.parse_module(source_code)
        
        # Use MetadataWrapper to collect position metadata
        wrapper = MetadataWrapper(tree)
        visitor = MethodCollector(class_name)
        
        # Visit the tree with metadata enabled
        wrapper.visit(visitor)
        
        return visitor.methods
    except Exception as e:
        raise ValueError(f"Failed to parse source code: {e}")


def list_methods_from_file(file_path: str, class_name: str) -> List[Dict[str, Any]]:
    """
    List all methods of a specific class in a Python file.
    
    Args:
        file_path: Path to the Python file
        class_name: Name of the class to extract methods from
        
    Returns:
        A list of dictionaries containing method information
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    return list_methods(source_code, class_name)


def main():
    """Entry point for the CLI script."""
    from cli_utils import create_common_parser, process_files
    import argparse
    import sys
    from pathlib import Path
    
    def run_example():
        """Run the example with hardcoded code."""
        example_code = """
class MyClass:
    '''A class with various methods.'''
    
    def __init__(self, value):
        self.value = value
    
    def instance_method(self, x):
        '''An instance method.'''
        return self.value + x
    
    @classmethod
    def class_method(cls, x):
        '''A class method.'''
        return cls(x)
    
    @staticmethod
    def static_method(x, y):
        '''A static method.'''
        return x + y
    
    @property
    def my_property(self):
        '''A property.'''
        return self.value
    
    async def async_method(self):
        '''An async method.'''
        pass

class AnotherClass:
    def other_method(self):
        '''This should not be listed.'''
        pass
"""
        
        methods = list_methods(example_code, 'MyClass')
        print("Found methods in MyClass:")
        for method in methods:
            type_markers = []
            if method['is_staticmethod']:
                type_markers.append('@staticmethod')
            if method['is_classmethod']:
                type_markers.append('@classmethod')
            if method['is_property']:
                type_markers.append('@property')
            if method['is_async']:
                type_markers.append('async')
            
            marker_str = ' '.join(type_markers) + ' ' if type_markers else ''
            params = ', '.join(method['parameters'])
            print(f"  - {marker_str}{method['name']}({params})")
    
    # Custom parser for list_methods because it needs a class name
    parser = argparse.ArgumentParser(
        description="List all methods of a specific class in Python files using LibCST",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  list-methods --class MyClass file1.py file2.py
  list-methods --class SomeClass src/*.py
  list-methods --example
        """
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        help='Python files to analyze'
    )
    
    parser.add_argument(
        '--class', '--class-name',
        dest='class_name',
        help='Name of the class to extract methods from'
    )
    
    parser.add_argument(
        '--example',
        action='store_true',
        help='Run with example code instead of files'
    )
    
    args = parser.parse_args()
    
    if args.example:
        run_example()
    elif args.files and args.class_name:
        # Process specified files
        for file_path in args.files:
            path = Path(file_path)
            
            if not path.exists():
                print(f"Error: File '{file_path}' not found", file=sys.stderr)
                continue
                
            if not path.suffix == '.py':
                print(f"Warning: '{file_path}' is not a Python file", file=sys.stderr)
                continue
            
            try:
                methods = list_methods_from_file(file_path, args.class_name)
                print(f"\nMethods in class '{args.class_name}' from {file_path}:")
                if methods:
                    for method in methods:
                        # Build method type indicators
                        indicators = []
                        if method.get('is_async', False):
                            indicators.append("async")
                        if method.get('is_staticmethod', False):
                            indicators.append("@staticmethod")
                        elif method.get('is_classmethod', False):
                            indicators.append("@classmethod")
                        elif method.get('is_property', False):
                            indicators.append("@property")
                        
                        prefix = " ".join(indicators) + " " if indicators else ""
                        params = ", ".join(method.get('parameters', []))
                        decorators = method.get('decorators', [])
                        decorators_str = f" (decorators: {decorators})" if decorators else ""
                        
                        print(f"  - {prefix}{method['name']}({params}) (line {method['lineno']}){decorators_str}")
                else:
                    print(f"  No methods found in class '{args.class_name}'")
            except Exception as e:
                print(f"Error processing '{file_path}': {e}", file=sys.stderr)
    else:
        # Missing required arguments
        if not args.class_name and not args.example:
            print("Error: --class argument is required when analyzing files", file=sys.stderr)
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
