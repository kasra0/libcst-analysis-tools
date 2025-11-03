"""Tests for list_methods module."""

import pytest
from src.list_methods import list_methods, list_methods_from_file


def test_list_simple_method():
    """Test listing a simple method."""
    code = """
class MyClass:
    def simple_method(self):
        pass
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 1
    assert methods[0]['name'] == 'simple_method'
    assert 'self' in methods[0]['parameters']


def test_list_init_method():
    """Test listing __init__ method."""
    code = """
class MyClass:
    def __init__(self, value):
        self.value = value
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 1
    assert methods[0]['name'] == '__init__'
    assert 'self' in methods[0]['parameters']
    assert 'value' in methods[0]['parameters']


def test_list_multiple_methods():
    """Test listing multiple methods in a class."""
    code = """
class MyClass:
    def __init__(self):
        pass
    
    def method1(self):
        pass
    
    def method2(self, x, y):
        pass
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 3
    method_names = [m['name'] for m in methods]
    assert '__init__' in method_names
    assert 'method1' in method_names
    assert 'method2' in method_names


def test_staticmethod():
    """Test listing a static method."""
    code = """
class MyClass:
    @staticmethod
    def static_method(x, y):
        return x + y
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 1
    assert methods[0]['name'] == 'static_method'
    assert methods[0]['is_staticmethod'] == True
    assert methods[0]['is_classmethod'] == False
    assert 'x' in methods[0]['parameters']
    assert 'y' in methods[0]['parameters']


def test_classmethod():
    """Test listing a class method."""
    code = """
class MyClass:
    @classmethod
    def class_method(cls, value):
        return cls(value)
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 1
    assert methods[0]['name'] == 'class_method'
    assert methods[0]['is_classmethod'] == True
    assert methods[0]['is_staticmethod'] == False
    assert 'cls' in methods[0]['parameters']


def test_property():
    """Test listing a property."""
    code = """
class MyClass:
    @property
    def my_property(self):
        return self._value
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 1
    assert methods[0]['name'] == 'my_property'
    assert methods[0]['is_property'] == True


def test_async_method():
    """Test listing an async method."""
    code = """
class MyClass:
    async def async_method(self):
        pass
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 1
    assert methods[0]['name'] == 'async_method'
    assert methods[0]['is_async'] == True


def test_method_with_decorators():
    """Test listing a method with custom decorators."""
    code = """
class MyClass:
    @decorator1
    @decorator2
    def decorated_method(self):
        pass
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 1
    assert methods[0]['name'] == 'decorated_method'
    assert 'decorator1' in methods[0]['decorators']
    assert 'decorator2' in methods[0]['decorators']


def test_wrong_class_name():
    """Test with a non-existent class name."""
    code = """
class MyClass:
    def method(self):
        pass
"""
    methods = list_methods(code, 'NonExistentClass')
    assert len(methods) == 0


def test_multiple_classes():
    """Test that only methods from the target class are returned."""
    code = """
class Class1:
    def method1(self):
        pass

class Class2:
    def method2(self):
        pass
    
    def method3(self):
        pass
"""
    methods = list_methods(code, 'Class2')
    assert len(methods) == 2
    method_names = [m['name'] for m in methods]
    assert 'method2' in method_names
    assert 'method3' in method_names
    assert 'method1' not in method_names


def test_method_with_args_kwargs():
    """Test method with *args and **kwargs."""
    code = """
class MyClass:
    def method_with_varargs(self, *args, **kwargs):
        pass
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 1
    assert '*args' in methods[0]['parameters']
    assert '**kwargs' in methods[0]['parameters']


def test_dunder_methods():
    """Test listing special dunder methods."""
    code = """
class MyClass:
    def __init__(self):
        pass
    
    def __str__(self):
        pass
    
    def __repr__(self):
        pass
    
    def __len__(self):
        pass
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 4
    method_names = [m['name'] for m in methods]
    assert '__init__' in method_names
    assert '__str__' in method_names
    assert '__repr__' in method_names
    assert '__len__' in method_names


def test_empty_class():
    """Test with an empty class."""
    code = """
class EmptyClass:
    pass
"""
    methods = list_methods(code, 'EmptyClass')
    assert len(methods) == 0


def test_invalid_syntax():
    """Test that invalid syntax raises an error."""
    code = """
class MyClass:
    def invalid_method(
        pass
"""
    with pytest.raises(ValueError):
        list_methods(code, 'MyClass')


def test_nested_class_methods():
    """Test that nested class methods are not included."""
    code = """
class OuterClass:
    def outer_method(self):
        pass
    
    class InnerClass:
        def inner_method(self):
            pass
"""
    methods = list_methods(code, 'OuterClass')
    # Should only include outer_method, not inner_method
    assert len(methods) == 1
    assert methods[0]['name'] == 'outer_method'


def test_method_with_complex_parameters():
    """Test method with complex parameter types."""
    code = """
class MyClass:
    def complex_method(self, a: int, b: str = "default", *args, c: float, **kwargs):
        pass
"""
    methods = list_methods(code, 'MyClass')
    assert len(methods) == 1
    params = methods[0]['parameters']
    assert 'self' in params
    assert 'a' in params
    assert 'b' in params
    assert '*args' in params
    assert 'c' in params
    assert '**kwargs' in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
