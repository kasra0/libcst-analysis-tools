# LibCST Analysis Tools

Python code analysis tools built with LibCST - extract classes, functions, and methods from Python source code.

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
from src.list_classes import list_classes, list_classes_from_file

# From source code string
code = """
class MyClass:
    pass

class AnotherClass(MyClass):
    pass
"""
classes = list_classes(code)
for cls in classes:
    print(f"Class: {cls['name']}, Bases: {cls['bases']}")

# From file
classes = list_classes_from_file('mymodule.py')
```

### List Functions

```python
from src.list_functions import list_functions, list_functions_from_file

# From source code string
code = """
def my_function(a, b):
    return a + b

async def async_function():
    pass
"""
functions = list_functions(code)
for func in functions:
    print(f"Function: {func['name']}, Params: {func['parameters']}, Async: {func['is_async']}")

# From file
functions = list_functions_from_file('mymodule.py')
```

### List Methods

```python
from src.list_methods import list_methods, list_methods_from_file

# From source code string
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
methods = list_methods(code, 'MyClass')
for method in methods:
    print(f"Method: {method['name']}, Static: {method['is_staticmethod']}")

# From file
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