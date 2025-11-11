"""LibCST Analysis Tools

A collection of Python code analysis tools built with LibCST.
"""
__version__ = "0.3.0"

# Type definitions
from .list_classes   import ClassInfo
from .list_functions import FunctionInfo
from .list_methods   import MethodInfo
from .analyze_complete import (
    ImportInfo,
    VariableInfo,
    ModuleInfo,
    CallGraphInfo,
    get_complete_module_info,
    get_complete_module_info_from_file
)

# TUI Application
from .view.App import PackageAnalysisApp

# Modern API (recommended)
from .list_classes   import list_classes_from_source_code,   list_classes_from_file,   list_classes_from_module
from .list_functions import list_functions_from_source_code, list_functions_from_file, list_functions_from_module
from .list_methods   import list_methods_from_source_code,   list_methods_from_file,   list_methods_from_module

# Backward compatibility aliases
from .list_classes   import list_classes
from .list_functions import list_functions
from .list_methods   import list_methods

__all__ = [
    # Type definitions
    "ClassInfo",
    "FunctionInfo",
    "MethodInfo",
    "ImportInfo",
    "VariableInfo",
    "ModuleInfo",
    "CallGraphInfo",
    
    # Complete module analysis
    "get_complete_module_info",
    "get_complete_module_info_from_file",
    
    # Modern API
    "list_classes_from_source_code",
    "list_classes_from_file",
    "list_classes_from_module",
    "list_functions_from_source_code",
    "list_functions_from_file",
    "list_functions_from_module",
    "list_methods_from_source_code",
    "list_methods_from_file",
    "list_methods_from_module",
    
    # Backward compatibility
    "list_classes",
    "list_functions",
    
    # TUI Application
    "PackageAnalysisApp",
    "list_methods",
]