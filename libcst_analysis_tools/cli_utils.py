"""Common CLI utilities for the LibCST analysis tools."""

import argparse
import sys
from pathlib import Path
from typing import Callable, Any, List


def create_common_parser(description: str, tool_name: str) -> argparse.ArgumentParser:
    """Create a common argument parser for LibCST analysis tools.
    
    Args:
        description: Description of the tool
        tool_name: Name of the tool (e.g., 'list_classes')
        
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python src/{tool_name}.py file1.py file2.py
  python src/{tool_name}.py src/*.py
  python src/{tool_name}.py --example
        """
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        help='Python files to analyze'
    )
    
    parser.add_argument(
        '--example',
        action='store_true',
        help='Run with example code instead of files'
    )
    
    return parser


def process_files(args: argparse.Namespace, 
                 example_function: Callable[[], None],
                 analysis_function: Callable[[str], List[Any]],
                 result_formatter: Callable[[str, List[Any]], None]) -> None:
    """Process command line arguments and run the appropriate analysis.
    
    Args:
        args: Parsed command line arguments
        example_function: Function to run when --example is specified
        analysis_function: Function that analyzes a file and returns results
        result_formatter: Function that formats and prints results for a file
    """
    if args.example:
        example_function()
    elif args.files:
        # Process specified files
        for file_path in args.files:
            path = Path(file_path)
            
            if not path.exists():
                print(f"Error: File '{file_path}' not found", file=sys.stderr)
                continue
                
            if not path.suffix == '.py':
                print(f"Warning: '{file_path}' is not a Python file", file=sys.stderr)
                continue
            
            try:
                results = analysis_function(file_path)
                result_formatter(file_path, results)
            except Exception as e:
                print(f"Error processing '{file_path}': {e}", file=sys.stderr)
    else:
        # No files specified, show help
        parser = create_common_parser("", "")
        parser.print_help()
        sys.exit(1)


def format_classes_results(file_path: str, classes: List[Any]) -> None:
    """Format and print class analysis results."""
    print(f"\nClasses in {file_path}:")
    if classes:
        for cls in classes:
            print(f"  - {cls['name']} (line {cls['lineno']}, bases: {cls['bases']}, decorators: {cls['decorators']})")
    else:
        print("  No classes found")


def format_functions_results(file_path: str, functions: List[Any]) -> None:
    """Format and print function analysis results."""
    print(f"\nFunctions in {file_path}:")
    if functions:
        for func in functions:
            async_prefix = "async " if func.get('is_async', False) else ""
            params = ", ".join(func.get('parameters', []))
            decorators = func.get('decorators', [])
            decorators_str = f" (decorators: {decorators})" if decorators else ""
            print(f"  - {async_prefix}{func['name']}({params}) (line {func['lineno']}){decorators_str}")
    else:
        print("  No functions found")


def format_methods_results(file_path: str, methods: List[Any], class_name: str | None = None) -> None:
    """Format and print method analysis results."""
    if class_name:
        print(f"\nMethods in class '{class_name}' from {file_path}:")
    else:
        print(f"\nMethods in {file_path}:")
    
    if methods:
        for method in methods:
            # Build method type indicators
            indicators = []
            if method.get('is_async', False):
                indicators.append("async")
            if method.get('is_staticmethod', False):
                indicators.append("@staticmethod")
            elif method.get('is_classmethod', False):
                indicators.append("@classmethod")
            elif method.get('is_property', False):
                indicators.append("@property")
            
            prefix = " ".join(indicators) + " " if indicators else ""
            params = ", ".join(method.get('parameters', []))
            decorators = method.get('decorators', [])
            decorators_str = f" (decorators: {decorators})" if decorators else ""
            
            print(f"  - {prefix}{method['name']}({params}) (line {method['lineno']}){decorators_str}")
    else:
        print("  No methods found")