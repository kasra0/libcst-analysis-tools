from libcst_analysis_tools.analyze_complete import get_all_classes_with_methods_from_file
from libcst_analysis_tools.view.Renderer.TreeRenderer import  FileNode
from typing import List
import inspect 
from textual.app import App
import os
from pathlib import Path


def get_package_path(package_name: str) -> str:
    """
    Get the installation path of a Python package.
    
    Args:
        package_name: Name of the package (e.g., 'textual', 'libcst')
    
    Returns:
        Absolute path to the package directory
        
    Example:
        >>> get_package_path('textual')
        '/path/to/site-packages/textual'
    """
    try:
        module = __import__(package_name)
        if hasattr(module, '__file__') and module.__file__:
            # Get the directory containing the package
            return os.path.dirname(module.__file__)
        elif hasattr(module, '__path__'):
            # For namespace packages
            return str(module.__path__[0])
        else:
            raise ValueError(f"Cannot determine path for package: {package_name}")
    except ImportError as e:
        raise ValueError(f"Package '{package_name}' not found: {e}")


def scan_directory(root_path: str, extensions: List[str] = ['.py']) -> List[FileNode]:
    """
    Scan a directory and return a list of FileNode objects.
    
    Args:
        root_path: Path to scan
        extensions: File extensions to include (default: ['.py'])
    
    Returns:
        List of FileNode objects representing the directory structure
    """
    nodes = []
    root = Path(root_path)
    
    if not root.exists():
        return nodes
    
    # Add the root directory itself
    nodes.append(FileNode(str(root), root.name, True))
    
    # Walk the directory tree
    for item in sorted(root.rglob('*')):
        # Skip hidden files and __pycache__
        if any(part.startswith('.') or part == '__pycache__' for part in item.parts):
            continue
        
        if item.is_dir():
            nodes.append(FileNode(str(item), item.name, True))
        elif item.is_file() and item.suffix in extensions:
            nodes.append(FileNode(str(item), item.name, False))
    
    return nodes

RANDOM_CELEBRITIES = ["Ada Lovelace", "Alan Turing", "Grace Hopper", "Linus Torvalds", "Margaret Hamilton", "Tim Berners-Lee", "Katherine Johnson", "Dennis Ritchie", "Barbara Liskov", "James Gosling"] 
RANDOM_COUNTRIES   = ["USA", "UK", "Canada", "Germany", "France", "Japan", "Australia", "India", "Brazil", "Italy"]

# Default package to browse - change this to browse different packages
DEFAULT_PACKAGE_NAME = "textual"  # Can be: "textual", "libcst", "libcst_analysis_tools", etc.
DEFAULT_PACKAGE_PATH = get_package_path(DEFAULT_PACKAGE_NAME)

def tabular_data(rows_count)->list[tuple]:
    list_ = []
    # Header
    list_.append(("ID", "Name", "Country", "Time (s)"))
    for i in range(rows_count):
        celebrity=RANDOM_CELEBRITIES[i % len(RANDOM_CELEBRITIES)]
        country  =RANDOM_COUNTRIES[i % len(RANDOM_COUNTRIES)]
        time=50.0 + i*0.1
        list_.append( (i, celebrity, country, time) )
    return list_

def tree_data():
    return get_all_classes_with_methods_from_file(inspect.getfile(App))

def tree_title():
    # just get the 2 last parts of the path
    return f"Classes and Methods in {'/'.join(inspect.getfile(App).split('/')[-2:])}"

def filesystem_data(package_name: str = DEFAULT_PACKAGE_NAME) -> List[FileNode]:
    """
    Get file system tree data for a package.
    
    Args:
        package_name: Name of the package to browse (e.g., 'textual', 'libcst')
    
    Returns:
        List of FileNode objects
    """
    package_path = get_package_path(package_name)
    return scan_directory(package_path, extensions=['.py'])

def filesystem_title(package_name: str = DEFAULT_PACKAGE_NAME):
    """Get title for filesystem tree."""
    return f"Package Explorer: {package_name}"