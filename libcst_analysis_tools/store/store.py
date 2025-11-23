from libcst_analysis_tools.analyze_complete import get_all_classes_with_methods_from_file
from libcst_analysis_tools.view.Renderer.FileSystemTreeRenderer import  FileNode
from typing import List, Tuple, Optional
import inspect 
from textual.app import App
import os
import sys
from pathlib import Path
import importlib.metadata
import subprocess
import json
from datetime import datetime


def get_virtual_environments() -> List[Tuple[str, str, int, str]]:
    """
    Detect virtual environments (conda and venv).
    
    Returns:
        List of tuples (name, type, package_count, location)
        
    Example:
        >>> get_virtual_environments()
        [('base', 'conda', 245, '/opt/anaconda3'),
         ('myenv', 'venv', 12, '/path/to/myenv'), ...]
    """
    environments = []
    
    # 1. Detect Conda environments
    try:
        result = subprocess.run(
            ['conda', 'env', 'list', '--json'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            conda_data = json.loads(result.stdout)
            for env_path in conda_data.get('envs', []):
                env_path_obj = Path(env_path)
                env_name = env_path_obj.name
                
                # Count packages in this conda env
                try:
                    pkg_result = subprocess.run(
                        ['conda', 'list', '-n', env_name, '--json'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if pkg_result.returncode == 0:
                        packages = json.loads(pkg_result.stdout)
                        pkg_count = len(packages)
                    else:
                        pkg_count = 0
                except:
                    pkg_count = 0
                
                environments.append((env_name, 'conda', pkg_count, str(env_path)))
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        # Conda not installed or error
        pass
    
    # 2. Detect venv environments in current directory and common locations
    search_paths = [
        Path.cwd(),  # Current directory
        Path.home() / 'venvs',  # Common venv location
        Path.cwd().parent,  # Parent directory
    ]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
            
        try:
            # Look for directories with bin/python or Scripts/python.exe
            for item in search_path.iterdir():
                if not item.is_dir():
                    continue
                
                # Check for venv markers
                python_paths = [
                    item / 'bin' / 'python',
                    item / 'Scripts' / 'python.exe'
                ]
                
                for python_path in python_paths:
                    if python_path.exists():
                        # This looks like a venv
                        env_name = item.name
                        
                        # Count packages
                        try:
                            pkg_result = subprocess.run(
                                [str(python_path), '-m', 'pip', 'list', '--format=json'],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if pkg_result.returncode == 0:
                                packages = json.loads(pkg_result.stdout)
                                pkg_count = len(packages)
                            else:
                                pkg_count = 0
                        except:
                            pkg_count = 0
                        
                        environments.append((env_name, 'venv', pkg_count, str(item)))
                        break  # Found one python, move to next directory
        except PermissionError:
            continue
    
    # 3. Add current environment (always)
    current_env_name = os.environ.get('CONDA_DEFAULT_ENV') or os.environ.get('VIRTUAL_ENV', 'current')
    if isinstance(current_env_name, str) and current_env_name != 'current':
        # Already in list from conda detection
        pass
    else:
        # Count current packages
        current_packages = get_installed_packages()
        environments.insert(0, ('⭐ Current', 'active', len(current_packages), sys.prefix))
    
    return environments


def get_installed_packages() -> List[Tuple[str, str, str]]:
    """
    Get list of all installed packages in the current Python environment.
    
    Returns:
        List of tuples (package_name, version, location)
        
    Example:
        >>> get_installed_packages()
        [('textual', '0.47.1', '/path/to/site-packages'),
         ('libcst', '1.8.5', '/path/to/site-packages'), ...]
    """
    packages = []
    
    try:
        # Use importlib.metadata (Python 3.8+)
        for dist in importlib.metadata.distributions():
            name = dist.metadata['Name']
            version = dist.version
            
            # Try to get location
            location = "Unknown"
            if dist.files:
                # Get the first file to determine location
                first_file = list(dist.files)[0]
                file_path = first_file.locate()
                location = str(Path(file_path).parent.parent)
            
            packages.append((name, version, location))
    except Exception as e:
        # Fallback: at least return some basic info
        packages.append(("Error", str(e), "N/A"))
    
    # Sort by package name
    packages.sort(key=lambda x: x[0].lower())
    
    return packages


def get_packages_from_environment(env_name: str, env_type: str, env_location: str) -> List[Tuple[str, str, str]]:
    """
    Get packages from a specific virtual environment.
    
    Args:
        env_name: Name of the environment
        env_type: Type ('conda', 'venv', 'active')
        env_location: Path to the environment
    
    Returns:
        List of tuples (package_name, version, location)
    """
    packages = []
    
    try:
        if env_type == 'active' or env_name == '⭐ Current':
            # Current environment - use the current function
            return get_installed_packages()
        
        elif env_type == 'conda':
            # Use conda list for conda environments
            result = subprocess.run(
                ['conda', 'list', '-n', env_name, '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                conda_packages = json.loads(result.stdout)
                for pkg in conda_packages:
                    name = pkg.get('name', 'unknown')
                    version = pkg.get('version', 'unknown')
                    channel = pkg.get('channel', 'unknown')
                    packages.append((name, version, channel))
        
        elif env_type == 'venv':
            # Use pip list for venv
            python_path = Path(env_location) / 'bin' / 'python'
            if not python_path.exists():
                python_path = Path(env_location) / 'Scripts' / 'python.exe'
            
            if python_path.exists():
                result = subprocess.run(
                    [str(python_path), '-m', 'pip', 'list', '--format=json'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    pip_packages = json.loads(result.stdout)
                    for pkg in pip_packages:
                        name = pkg.get('name', 'unknown')
                        version = pkg.get('version', 'unknown')
                        packages.append((name, version, env_location))
    except Exception as e:
        packages.append(("Error", str(e), "N/A"))
    
    # Sort by package name
    packages.sort(key=lambda x: x[0].lower())
    
    return packages


def get_python_environment_info() -> dict:
    """
    Get information about the current Python environment.
    
    Returns:
        Dictionary with environment details:
        - python_executable: Path to Python interpreter
        - python_version: Python version string
        - virtual_env: Virtual environment path (if any)
        - site_packages: List of site-packages directories
    """
    info = {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "virtual_env": os.environ.get('VIRTUAL_ENV') or os.environ.get('CONDA_DEFAULT_ENV'),
        "site_packages": [p for p in sys.path if 'site-packages' in p]
    }
    return info


def _get_import_name(package_name: str) -> str:
    """
    Convert package name to Python import name.
    
    Many packages have different names for pip/conda vs Python import.
    
    Args:
        package_name: Package name as shown in pip/conda (e.g., 'py-opencv')
    
    Returns:
        Module name to use for import (e.g., 'cv2')
    """
    # Common package name to module name mappings
    PACKAGE_TO_MODULE = {
        'py-opencv': 'cv2',
        'opencv-python': 'cv2',
        'opencv-contrib-python': 'cv2',
        'pillow': 'PIL',
        'scikit-learn': 'sklearn',
        'scikit-image': 'skimage',
        'beautifulsoup4': 'bs4',
        'pyyaml': 'yaml',
        'python-dateutil': 'dateutil',
        'attrs': 'attr',
        'protobuf': 'google.protobuf',
        'pycryptodome': 'Crypto',
        'pyyaml-env-tag': 'yaml',
        'msgpack-python': 'msgpack',
        'ruamel.yaml': 'ruamel.yaml',
    }
    
    # Check if we have a mapping
    package_lower = package_name.lower()
    if package_lower in PACKAGE_TO_MODULE:
        return PACKAGE_TO_MODULE[package_lower]
    
    # Default: use package name as-is (but replace hyphens with underscores)
    # This works for most packages
    return package_name.replace('-', '_')


def get_package_path(package_name: str, env_name: str = "", env_type: str = "", env_location: str = "") -> str:
    """
    Get the installation path of a Python package.
    
    Args:
        package_name: Name of the package (e.g., 'textual', 'libcst', 'py-opencv')
        env_name: Name of the environment (empty for current)
        env_type: Type of environment ('conda', 'venv', 'active', or empty)
        env_location: Path to the environment
    
    Returns:
        Absolute path to the package directory
        
    Example:
        >>> get_package_path('textual')
        '/path/to/site-packages/textual'
    """
    # Convert package name to import name (e.g., 'py-opencv' -> 'cv2')
    import_name = _get_import_name(package_name)
    
    # If no environment specified or current environment, use direct import
    if not env_name or env_type == 'active' or '⭐' in env_name:
        try:
            module = __import__(import_name)
            if hasattr(module, '__file__') and module.__file__:
                return os.path.dirname(module.__file__)
            elif hasattr(module, '__path__'):
                return str(module.__path__[0])
            else:
                raise ValueError(f"Cannot determine path for package: {package_name} (import: {import_name})")
        except ImportError as e:
            raise ValueError(f"Package '{package_name}' (import: {import_name}) not found: {e}")
    
    # For other environments, we need to query the environment's Python
    try:
        if env_type == 'conda':
            # Use conda run to execute Python in that environment
            result = subprocess.run(
                ['conda', 'run', '-n', env_name, 'python', '-c',
                 f"import {import_name}; import os; print(os.path.dirname({import_name}.__file__) if hasattr({import_name}, '__file__') else {import_name}.__path__[0])"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                # Try to find it in site-packages directly
                error_msg = result.stderr.strip()
                raise ValueError(f"Package '{package_name}' (import: {import_name}) not found in conda env '{env_name}': {error_msg}")
        
        elif env_type == 'venv':
            # Use the venv's Python directly
            python_path = Path(env_location) / 'bin' / 'python'
            if not python_path.exists():
                python_path = Path(env_location) / 'Scripts' / 'python.exe'
            
            if python_path.exists():
                result = subprocess.run(
                    [str(python_path), '-c',
                     f"import {import_name}; import os; print(os.path.dirname({import_name}.__file__) if hasattr({import_name}, '__file__') else {import_name}.__path__[0])"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    error_msg = result.stderr.strip()
                    raise ValueError(f"Package '{package_name}' (import: {import_name}) not found in venv '{env_name}': {error_msg}")
            else:
                raise ValueError(f"Python executable not found in venv: {env_location}")
        
        # If we get here, unknown env_type
        raise ValueError(f"Unknown environment type: {env_type}")
    
    except subprocess.TimeoutExpired:
        raise ValueError(f"Timeout while searching for package '{package_name}' in {env_type} environment '{env_name}'")
    except Exception as e:
        raise ValueError(f"Error finding package '{package_name}' in environment '{env_name}': {str(e)}")


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