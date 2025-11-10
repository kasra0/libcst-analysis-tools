# Package Browser Usage

## How to Browse Different Packages

The TUI app now supports browsing **any installed Python package**!

### Quick Start

1. **Default**: The app browses the `textual` package by default
2. **Change package**: Edit `App.py` line ~28:
   ```python
   package_to_browse = "textual"  # Change this!
   ```

### Examples

#### Browse Textual (UI framework)
```python
package_to_browse = "textual"
```

#### Browse LibCST (AST library)
```python
package_to_browse = "libcst"
```

#### Browse Your Own Package
```python
package_to_browse = "libcst_analysis_tools"
```

#### Browse Standard Library
```python
package_to_browse = "ast"
package_to_browse = "pathlib"
package_to_browse = "typing"
```

### What Gets Displayed

- **Left Tree**: Complete folder/file structure of the package
- **Click any `.py` file**: Middle tree updates with classes and methods from that file
- **Filter**: Each tree has independent filtering

### Features

- ✅ Lazy loading: Files are only parsed when clicked
- ✅ Shows all `.py` files in the package
- ✅ Skips `__pycache__` and hidden files
- ✅ Expandable folder structure
- ✅ File emojis: 📁 folders, 📄 Python files

### Programmatic Usage

```python
from libcst_analysis_tools.store import store

# Get path to any installed package
textual_path = store.get_package_path("textual")
print(textual_path)  # /path/to/site-packages/textual

# Scan package structure
nodes = store.filesystem_data("libcst")
for node in nodes:
    print(f"{'📁' if node.is_dir else '📄'} {node.name}")
```

### Troubleshooting

**Package not found?**
```python
# Check if package is installed
import textual  # Should not raise ImportError

# Or use pip
pip list | grep textual
```

**Want to browse a local directory?**
```python
# In store.py, directly call scan_directory
nodes = scan_directory("/path/to/your/code", extensions=['.py'])
```
