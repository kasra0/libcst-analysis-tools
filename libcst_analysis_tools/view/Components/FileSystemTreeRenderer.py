# """FileSystemTreeRenderer for browsing package/file structure."""

# import os
# from pathlib import Path
# from typing import List, Protocol, TypeVar
# from textual.widgets import Tree

# # Generic type variable
# T = TypeVar('T')

# # Protocol for renderer (interface) - duplicated to avoid circular import
# class TreeRenderer(Protocol[T]):
#     """Protocol defining the interface for tree renderers."""
    
#     def fill_tree(self, tree: Tree, data: List[T]) -> None:
#         """Fill the tree with data."""
#         ...
    
#     def filter_data(self, data: List[T], filter_text: str) -> List[T]:
#         """Filter data based on filter text."""
#         ...

# # Type for file system nodes
# class FileNode:
#     def __init__(self, path: str, name: str, is_dir: bool):
#         self.path = path
#         self.name = name
#         self.is_dir = is_dir
    
#     def __repr__(self):
#         return f"FileNode(path={self.path}, name={self.name}, is_dir={self.is_dir})"


# def scan_directory(root_path: str, extensions: List[str] = ['.py']) -> List[FileNode]:
#     """
#     Scan a directory and return a list of FileNode objects.
    
#     Args:
#         root_path: Path to scan
#         extensions: File extensions to include (default: ['.py'])
    
#     Returns:
#         List of FileNode objects representing the directory structure
#     """
#     nodes = []
#     root = Path(root_path)
    
#     if not root.exists():
#         return nodes
    
#     # Add the root directory itself
#     nodes.append(FileNode(str(root), root.name, True))
    
#     # Walk the directory tree
#     for item in sorted(root.rglob('*')):
#         # Skip hidden files and __pycache__
#         if any(part.startswith('.') or part == '__pycache__' for part in item.parts):
#             continue
        
#         if item.is_dir():
#             nodes.append(FileNode(str(item), item.name, True))
#         elif item.is_file() and item.suffix in extensions:
#             nodes.append(FileNode(str(item), item.name, False))
    
#     return nodes


# class FileSystemTreeRenderer(TreeRenderer[FileNode]):
#     """Renderer for file system tree structure."""
    
#     def __init__(self, root_path: str, extensions: List[str] = ['.py']):
#         self.root_path = root_path
#         self.extensions = extensions
    
#     def fill_tree(self, tree: Tree, data: List[FileNode]) -> None:
#         """Fill the tree with file system structure."""
#         tree.clear()
#         tree.root.expand()
        
#         # Group nodes by parent directory
#         path_to_node_map = {}
        
#         for node in data:
#             path = Path(node.path)
            
#             # Determine emoji
#             if node.is_dir:
#                 emoji = "📁"
#             else:
#                 emoji = "📄"
            
#             label = f"{emoji} {node.name}"
            
#             # Find parent in tree
#             parent_path = str(path.parent)
            
#             if parent_path == node.path:
#                 # This is root
#                 tree_node = tree.root.add(label, expand=True, data=node.path)
#                 path_to_node_map[node.path] = tree_node
#             elif parent_path in path_to_node_map:
#                 # Parent exists in tree
#                 parent_tree_node = path_to_node_map[parent_path]
#                 tree_node = parent_tree_node.add(label, expand=False, data=node.path)
#                 path_to_node_map[node.path] = tree_node
#             else:
#                 # Fallback: add to root
#                 tree_node = tree.root.add(label, expand=False, data=node.path)
#                 path_to_node_map[node.path] = tree_node
    
#     def filter_data(self, data: List[FileNode], filter_text: str) -> List[FileNode]:
#         """Filter file nodes by name."""
#         if filter_text == "":
#             return data
        
#         filtered = [node for node in data if filter_text in node.name.lower()]
#         return filtered
