"""Utility to list all function definitions in a Python module using LibCST."""

from typing import List, Dict, Any
import libcst as cst
from libcst.metadata import PositionProvider, MetadataWrapper


class FunctionDefinitionVisitor(cst.CSTVisitor):
    """Visitor that collects all function definitions in a module."""
    
    METADATA_DEPENDENCIES = (PositionProvider,)
    
    def __init__(self):
        self.functions: List[Dict[str, Any]] = []
        self._in_class = False
    
    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        """Track when we're inside a class to distinguish methods from functions."""
        self._in_class = True
        return True
    
    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        """Track when we leave a class."""
        self._in_class = False
    
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        """Visit a function definition and collect its information if it's not a method."""
        # Only collect top-level functions, not methods inside classes
        if not self._in_class:
            function_info = {
                "name": node.name.value,
                "lineno": self._get_line_number(node),
                "parameters": self._get_parameters(node.params),
                "decorators": [self._get_decorator_name(dec) for dec in node.decorators],
                "is_async": isinstance(node, cst.FunctionDef) and node.asynchronous is not None,
            }
            self.functions.append(function_info)
    
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


def list_functions(source_code: str) -> List[Dict[str, Any]]:
    """
    List all function definitions (not methods) in the given Python source code.
    
    Args:
        source_code: Python source code as a string
        
    Returns:
        A list of dictionaries containing function information:
        - name: function name
        - lineno: line number where function is defined
        - parameters: list of parameter names
        - decorators: list of decorator names
        - is_async: whether the function is async
        
    Example:
        >>> code = '''
        ... def my_function(a, b):
        ...     return a + b
        ... 
        ... async def async_function():
        ...     pass
        ... '''
        >>> functions = list_functions(code)
        >>> len(functions)
        2
        >>> functions[0]['name']
        'my_function'
        >>> functions[1]['is_async']
        True
    """
    try:
        tree = cst.parse_module(source_code)
        
        # Use MetadataWrapper to collect position metadata
        wrapper = MetadataWrapper(tree)
        visitor = FunctionDefinitionVisitor()
        
        # Visit the tree with metadata enabled
        wrapper.visit(visitor)
        
        return visitor.functions
    except Exception as e:
        raise ValueError(f"Failed to parse source code: {e}")


def list_functions_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    List all function definitions in a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        A list of dictionaries containing function information
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    return list_functions(source_code)


def main():
    """Entry point for the CLI script."""
    from cli_utils import create_common_parser, process_files, format_functions_results
    
    def run_example():
        """Run the example with hardcoded code."""
        example_code = """
def simple_function():
    '''A simple function.'''
    pass

def function_with_params(a, b, c=10):
    '''Function with parameters.'''
    return a + b + c

@decorator
async def async_function(*args, **kwargs):
    '''An async function with decorators.'''
    pass

class MyClass:
    def method(self):
        '''This should not be listed as a function.'''
        pass
"""
        
        functions = list_functions(example_code)
        print("Found functions in example code:")
        for func in functions:
            async_marker = "async " if func['is_async'] else ""
            params = ", ".join(func['parameters'])
            decorators = f"@{', @'.join(func['decorators'])}" if func['decorators'] else ""
            if decorators:
                print(f"  {decorators}")
            print(f"  - {async_marker}{func['name']}({params})")
    
    parser = create_common_parser(
        "List all function definitions in Python files using LibCST",
        "list_functions"
    )
    args = parser.parse_args()
    
    process_files(args, run_example, list_functions_from_file, format_functions_results)


if __name__ == "__main__":
    main()
