# LibCST Analysis Tools

Python code analysis tools built with LibCST - extract classes, functions, and methods from Python source code with full type safety and IntelliSense support.

## Features

- 🔍 **Extract class definitions** with bases and decorators
- 🔧 **Extract function definitions** with parameters and async support
- 📦 **Extract class methods** with staticmethod/classmethod/property detection
- 🎯 **Full type safety** with dataclass return types for perfect IntelliSense
- 📁 **Analyze source code strings, files, or imported modules**
- 🖥️ **Command-line tools** for quick analysis
- ✨ **Accurate line numbers** using LibCST metadata

## Installation

### From GitHub

```bash
pip install git+https://github.com/kasra0/libcst-analysis-tools.git
```

### Local Development

```bash
git clone https://github.com/kasra0/libcst-analysis-tools.git
cd libcst-analysis-tools
pip install -e .
```

## Command Line Usage

Once installed, you can use the command-line tools:

```bash
# List classes in Python files
list-classes file1.py file2.py
list-classes src/*.py

# List functions in Python files  
list-functions file1.py file2.py
list-functions src/*.py

# List methods of a specific class
list-methods --class MyClass file1.py
list-methods --class SomeClass src/*.py

# Run examples
list-classes --example
list-functions --example  
list-methods --example
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install libcst pytest
```

## Project Structure

```
python-libcst-sandbox/
├── env-libcst/              # Virtual environment
├── src/                     # Source code
│   ├── __init__.py
│   ├── list_classes.py      # List class definitions
│   ├── list_functions.py    # List function definitions
│   └── list_methods.py      # List methods of a class
├── tests/                   # Test files
│   ├── __init__.py
│   ├── test_list_classes.py
│   ├── test_list_functions.py
│   └── test_list_methods.py
├── requirements.txt         # Dependencies
└── README.md
```

## Usage

### List Classes

```python
from libcst_analysis_tools import list_classes_from_source_code, ClassInfo

# From source code string
code = """
class MyClass:
    pass

class AnotherClass(MyClass):
    pass
"""

# Returns List[ClassInfo] - full IntelliSense support!
classes = list_classes_from_source_code(code)
for cls in classes:
    # Type 'cls.' and get autocomplete: name, lineno, bases, decorators
    print(f"Class: {cls.name}, Bases: {cls.bases}, Line: {cls.lineno}")

# From file
from libcst_analysis_tools import list_classes_from_file
classes = list_classes_from_file('mymodule.py')

# From imported module
from libcst_analysis_tools import list_classes_from_module
import transformers
classes = list_classes_from_module(transformers)
```

### List Functions

```python
from libcst_analysis_tools import list_functions_from_source_code, FunctionInfo

code = """
def my_function(a, b):
    return a + b

async def async_function():
    pass
"""

# Returns List[FunctionInfo] - full type safety!
functions = list_functions_from_source_code(code)
for func in functions:
    # IntelliSense shows: name, lineno, parameters, decorators, is_async
    print(f"Function: {func.name}, Params: {func.parameters}, Async: {func.is_async}")
```

### List Methods

```python
from libcst_analysis_tools import list_methods_from_source_code, MethodInfo

code = """
class MyClass:
    def __init__(self):
        pass
    
    def instance_method(self, x):
        return x * 2
    
    @staticmethod
    def static_method():
        pass
"""

# Returns List[MethodInfo] with rich type information!
methods = list_methods_from_source_code(code, 'MyClass')
for method in methods:
    # IntelliSense: name, lineno, parameters, decorators, is_async, 
    #               is_staticmethod, is_classmethod, is_property
    print(f"Method: {method.name}, Static: {method.is_staticmethod}")
```

## Type Definitions

The package exports three dataclasses for type-safe results:

### `ClassInfo`
```python
@dataclass
class ClassInfo:
    name: str              # Class name
    lineno: int            # Line number where defined
    bases: List[str]       # Base class names
    decorators: List[str]  # Decorator names
```

### `FunctionInfo`
```python
@dataclass
class FunctionInfo:
    name: str                  # Function name
    lineno: int                # Line number where defined
    parameters: List[str]      # Parameter names (including *args, **kwargs)
    decorators: List[str]      # Decorator names
    is_async: bool             # Whether function is async
```

### `MethodInfo`
```python
@dataclass
class MethodInfo:
    name: str                  # Method name
    lineno: int                # Line number where defined
    parameters: List[str]      # Parameter names
    decorators: List[str]      # Decorator names
    is_async: bool             # Whether method is async
    is_staticmethod: bool      # Whether decorated with @staticmethod
    is_classmethod: bool       # Whether decorated with @classmethod
    is_property: bool          # Whether decorated with @property
```

## API Reference

### Modern API (Recommended)

All functions come in three variants for flexibility:

- `list_classes_from_source_code(source_code: str) -> List[ClassInfo]`
- `list_classes_from_file(file_path: str) -> List[ClassInfo]`
- `list_classes_from_module(module: Union[types.ModuleType, str]) -> List[ClassInfo]`

- `list_functions_from_source_code(source_code: str) -> List[FunctionInfo]`
- `list_functions_from_file(file_path: str) -> List[FunctionInfo]`
- `list_functions_from_module(module: Union[types.ModuleType, str]) -> List[FunctionInfo]`

- `list_methods_from_source_code(source_code: str, class_name: str) -> List[MethodInfo]`
- `list_methods_from_file(file_path: str, class_name: str) -> List[MethodInfo]`
- `list_methods_from_module(module: Union[types.ModuleType, str], class_name: str) -> List[MethodInfo]`

### Backward Compatibility

Legacy dict-based API still supported:
- `list_classes(source_code: str) -> List[ClassInfo]`
- `list_functions(source_code: str) -> List[FunctionInfo]`
- `list_methods(source_code: str, class_name: str) -> List[MethodInfo]`
methods = list_methods_from_file('mymodule.py', 'MyClass')
```

## Running Examples

Each module has example usage in its `__main__` block:

```bash
# Activate virtual environment first
source env-libcst/bin/activate

# Run examples
python src/list_classes.py
python src/list_functions.py
python src/list_methods.py
```

## Running Tests

```bash
# Activate virtual environment
source env-libcst/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_list_classes.py -v
pytest tests/test_list_functions.py -v
pytest tests/test_list_methods.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## API Reference

### list_classes(source_code: str) -> List[Dict]

Returns a list of dictionaries with class information:
- `name`: Class name
- `lineno`: Line number (if available)
- `bases`: List of base class names
- `decorators`: List of decorator names

### list_functions(source_code: str) -> List[Dict]

Returns a list of dictionaries with function information:
- `name`: Function name
- `lineno`: Line number (if available)
- `parameters`: List of parameter names (including *args, **kwargs)
- `decorators`: List of decorator names
- `is_async`: Boolean indicating if function is async

### list_methods(source_code: str, class_name: str) -> List[Dict]

Returns a list of dictionaries with method information:
- `name`: Method name
- `lineno`: Line number (if available)
- `parameters`: List of parameter names (including *args, **kwargs)
- `decorators`: List of decorator names
- `is_async`: Boolean indicating if method is async
- `is_staticmethod`: Boolean indicating if it's a static method
- `is_classmethod`: Boolean indicating if it's a class method
- `is_property`: Boolean indicating if it's a property

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=libcst_analysis_tools tests/

# Generate HTML coverage report
pytest --cov=libcst_analysis_tools --cov-report=html tests/

# Or use the helper script
./run_tests.sh
```

### Coverage Report

After running tests with coverage, open the HTML report:

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

Current coverage: **~45%** (tests for all major functions)

### Installing Dev Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- pytest
- pytest-cov
- coverage
- black (code formatter)
- flake8 (linter)
- mypy (type checker)

## Dependencies

- **libcst** (1.8.5): Concrete Syntax Tree parser for Python
- **pytest** (8.4.2): Testing framework

## License

MIT    