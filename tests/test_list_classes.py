"""Tests for list_classes module."""

import pytest
import tempfile
import os
from libcst_analysis_tools.list_classes import (
    list_classes, list_classes_from_source_code, 
    list_classes_from_file, list_classes_from_module
)


def test_list_simple_class():
    """Test listing a simple class with no bases or decorators."""
    code = """
class SimpleClass:
    pass
"""
    classes = list_classes_from_source_code(code)
    assert len(classes) == 1
    assert classes[0].name == 'SimpleClass'
    assert classes[0].bases == []
    assert classes[0].decorators == []


def test_list_simple_class_backward_compatibility():
    """Test backward compatibility alias."""
    code = """
class SimpleClass:
    pass
"""
    classes = list_classes(code)
    assert len(classes) == 1
    assert classes[0].name == 'SimpleClass'


def test_list_class_with_inheritance():
    """Test listing a class with inheritance."""
    code = """
class BaseClass:
    pass

class DerivedClass(BaseClass):
    pass
"""
    classes = list_classes(code)
    assert len(classes) == 2
    assert classes[0].name == 'BaseClass'
    assert classes[1].name == 'DerivedClass'
    assert 'BaseClass' in classes[1].bases


def test_list_class_with_multiple_bases():
    """Test listing a class with multiple base classes."""
    code = """
class Base1:
    pass

class Base2:
    pass

class MultiDerived(Base1, Base2):
    pass
"""
    classes = list_classes(code)
    assert len(classes) == 3
    assert classes[2].name == 'MultiDerived'
    assert 'Base1' in classes[2].bases
    assert 'Base2' in classes[2].bases


def test_list_class_with_decorator():
    """Test listing a class with decorators."""
    code = """
@dataclass
class DecoratedClass:
    name: str
    value: int
"""
    classes = list_classes(code)
    assert len(classes) == 1
    assert classes[0].name == 'DecoratedClass'
    assert 'dataclass' in classes[0].decorators


def test_list_multiple_classes():
    """Test listing multiple classes in one module."""
    code = """
class Class1:
    pass

class Class2:
    pass

class Class3:
    pass
"""
    classes = list_classes(code)
    assert len(classes) == 3
    assert classes[0].name == 'Class1'
    assert classes[1].name == 'Class2'
    assert classes[2].name == 'Class3'


def test_list_nested_class():
    """Test that nested classes are also found."""
    code = """
class OuterClass:
    class InnerClass:
        pass
"""
    classes = list_classes(code)
    assert len(classes) == 2
    class_names = [cls.name for cls in classes]
    assert 'OuterClass' in class_names
    assert 'InnerClass' in class_names


def test_empty_module():
    """Test with an empty module."""
    code = ""
    classes = list_classes(code)
    assert len(classes) == 0


def test_module_without_classes():
    """Test with a module that has no classes."""
    code = """
def function():
    pass

x = 10
"""
    classes = list_classes(code)
    assert len(classes) == 0


def test_invalid_syntax():
    """Test that invalid syntax raises an error."""
    code = """
class InvalidClass
    pass
"""
    with pytest.raises(ValueError):
        list_classes(code)


def test_complex_inheritance():
    """Test class with complex inheritance patterns."""
    code = """
from typing import Generic, TypeVar

T = TypeVar('T')

class GenericClass(Generic[T]):
    pass
"""
    classes = list_classes(code)
    assert len(classes) == 1
    assert classes[0].name == 'GenericClass'
    # The base will include the Generic[T] expression


def test_multiple_decorators():
    """Test class with multiple decorators."""
    code = """
@decorator1
@decorator2
@decorator3
class MultiDecoratedClass:
    pass
"""
    classes = list_classes(code)
    assert len(classes) == 1
    assert classes[0].name == 'MultiDecoratedClass'
    assert len(classes[0].decorators) == 3
    assert 'decorator1' in classes[0].decorators
    assert 'decorator2' in classes[0].decorators
    assert 'decorator3' in classes[0].decorators


def test_list_classes_from_module():
    """Test listing classes from a module object."""
    # Create a temporary Python file
    test_code = """
class ModuleTestClass:
    '''A test class in a module.'''
    pass

class AnotherModuleClass:
    '''Another test class.'''
    def method(self):
        pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_file = f.name
    
    try:
        # Import the temporary module
        import importlib.util
        import sys
        
        spec = importlib.util.spec_from_file_location("temp_module", temp_file)
        if spec is None or spec.loader is None:
            pytest.skip("Could not create module spec")
            
        temp_module = importlib.util.module_from_spec(spec)
        sys.modules["temp_module"] = temp_module
        spec.loader.exec_module(temp_module)
        
        # Test list_classes_from_module
        classes = list_classes_from_module(temp_module)
        assert len(classes) == 2
        class_names = [c.name for c in classes]
        assert 'ModuleTestClass' in class_names
        assert 'AnotherModuleClass' in class_names
        
        # Test by module name
        classes2 = list_classes_from_module('temp_module')
        assert len(classes2) == 2
        
    finally:
        # Clean up
        if 'temp_module' in sys.modules:
            del sys.modules['temp_module']
        os.unlink(temp_file)


def test_list_classes_from_module_errors():
    """Test error handling for list_classes_from_module."""
    # Test with non-existent module name
    with pytest.raises(ValueError, match="Could not import module"):
        list_classes_from_module('non_existent_module_xyz')
    
    # Test with wrong type
    with pytest.raises(ValueError, match="Expected module object or string"):
        list_classes_from_module(42)  # type: ignore


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
