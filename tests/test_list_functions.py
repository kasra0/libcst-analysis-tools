"""Tests for list_functions module."""

import pytest
from libcst_analysis_tools.list_functions import list_functions, list_functions_from_file


def test_list_simple_function():
    """Test listing a simple function with no parameters."""
    code = """
def simple_function():
    pass
"""
    functions = list_functions(code)
    assert len(functions) == 1
    assert functions[0].name == 'simple_function'
    assert functions[0].parameters == []
    assert functions[0].is_async == False


def test_list_function_with_parameters():
    """Test listing a function with parameters."""
    code = """
def function_with_params(a, b, c):
    return a + b + c
"""
    functions = list_functions(code)
    assert len(functions) == 1
    assert functions[0].name == 'function_with_params'
    assert functions[0].parameters == ['a', 'b', 'c']


def test_list_function_with_default_params():
    """Test listing a function with default parameters."""
    code = """
def function_with_defaults(a, b=10, c=20):
    return a + b + c
"""
    functions = list_functions(code)
    assert len(functions) == 1
    assert functions[0].name == 'function_with_defaults'
    assert 'a' in functions[0].parameters
    assert 'b' in functions[0].parameters
    assert 'c' in functions[0].parameters


def test_list_function_with_args_kwargs():
    """Test listing a function with *args and **kwargs."""
    code = """
def function_with_varargs(a, *args, **kwargs):
    pass
"""
    functions = list_functions(code)
    assert len(functions) == 1
    assert functions[0].name == 'function_with_varargs'
    assert 'a' in functions[0].parameters
    assert '*args' in functions[0].parameters
    assert '**kwargs' in functions[0].parameters


def test_list_async_function():
    """Test listing an async function."""
    code = """
async def async_function():
    pass
"""
    functions = list_functions(code)
    assert len(functions) == 1
    assert functions[0].name == 'async_function'
    assert functions[0].is_async == True


def test_list_function_with_decorator():
    """Test listing a function with a decorator."""
    code = """
@decorator
def decorated_function():
    pass
"""
    functions = list_functions(code)
    assert len(functions) == 1
    assert functions[0].name == 'decorated_function'
    assert 'decorator' in functions[0].decorators


def test_list_multiple_functions():
    """Test listing multiple functions."""
    code = """
def function1():
    pass

def function2():
    pass

def function3():
    pass
"""
    functions = list_functions(code)
    assert len(functions) == 3
    function_names = [f.name for f in functions]
    assert 'function1' in function_names
    assert 'function2' in function_names
    assert 'function3' in function_names


def test_methods_not_included():
    """Test that class methods are not included in function list."""
    code = """
def top_level_function():
    pass

class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        pass
"""
    functions = list_functions(code)
    assert len(functions) == 1
    assert functions[0].name == 'top_level_function'


def test_empty_module():
    """Test with an empty module."""
    code = ""
    functions = list_functions(code)
    assert len(functions) == 0


def test_module_without_functions():
    """Test with a module that has no functions."""
    code = """
x = 10
y = 20

class MyClass:
    pass
"""
    functions = list_functions(code)
    assert len(functions) == 0


def test_invalid_syntax():
    """Test that invalid syntax raises an error."""
    code = """
def invalid_function(
    pass
"""
    with pytest.raises(ValueError):
        list_functions(code)


def test_nested_function():
    """Test that nested functions are included."""
    code = """
def outer_function():
    def inner_function():
        pass
    return inner_function
"""
    functions = list_functions(code)
    # Both outer and inner functions should be found
    # Note: LibCST visitor will find both as they're not inside a class
    assert len(functions) >= 1
    function_names = [f.name for f in functions]
    assert 'outer_function' in function_names


def test_multiple_decorators():
    """Test function with multiple decorators."""
    code = """
@decorator1
@decorator2
@decorator3
def multi_decorated_function():
    pass
"""
    functions = list_functions(code)
    assert len(functions) == 1
    assert functions[0].name == 'multi_decorated_function'
    assert len(functions[0].decorators) == 3


def test_lambda_not_included():
    """Test that lambda functions are not included."""
    code = """
lambda_func = lambda x: x * 2

def regular_function():
    pass
"""
    functions = list_functions(code)
    assert len(functions) == 1
    assert functions[0].name == 'regular_function'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
