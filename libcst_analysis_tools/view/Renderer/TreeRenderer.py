from typing import List, TypeVar, Protocol, Union
from textual.widgets     import Tree
from libcst_analysis_tools.list_classes  import ClassInfo
from libcst_analysis_tools.list_methods  import MethodInfo
from pathlib import Path

ClassWithMethods = tuple[ClassInfo, list[MethodInfo]]
ClassesWithMethods = list[ClassWithMethods]

# Generic type variable
T = TypeVar('T')

# Protocol for renderer (interface)
class TreeRenderer(Protocol[T]):
    """Protocol defining the interface for tree renderers."""
    
    def fill_tree(self, tree: Tree, data: Union[List[T], T]) -> None:
        """Fill the tree with data."""
        ...
    
    def filter_data(self, data: Union[List[T], T], filter_text: str) -> Union[List[T], T]:
        """Filter data based on filter text."""
        ...


# Concrete renderer for ClassesWithMethods
class ClassMethodsTreeRenderer(TreeRenderer[ClassWithMethods]):
    """Renderer for ClassesWithMethods data."""
    
    def fill_tree(self, tree: Tree, data: Union[ClassesWithMethods, List[ClassWithMethods]]) -> None:
        # Handle both list and direct ClassesWithMethods
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], tuple):
            classes_data = data
        else:
            classes_data = []
        
        tree.clear()
        tree.root.expand()
        
        for cls, methods in classes_data:
            class_emoji = "🧱"
            method_emoji = "⚙️"
            label = f"{class_emoji} {cls.name}"
            class_node = tree.root.add(label, expand=True)
            for method in methods:
                label = f"{method_emoji}  {method.name} ([magenta]@{method.lineno}[/magenta])"
                class_node.add_leaf(label)
    
    def filter_data(self, data: Union[ClassesWithMethods, List[ClassWithMethods]], filter_text: str) -> Union[ClassesWithMethods, List[ClassWithMethods]]:
        if not isinstance(data, list):
            return data
            
        if filter_text == "":
            return data
        
        filtered_data: ClassesWithMethods = []
        for cls, methods in data:
            filtered_methods = [m for m in methods if m.name.lower().startswith(filter_text)]
            if filtered_methods:
                filtered_data.append((cls, filtered_methods))
        return filtered_data

# Type for file system nodes
class FileNode:
    def __init__(self, path: str, name: str, is_dir: bool):
        self.path = path
        self.name = name
        self.is_dir = is_dir
    
    def __repr__(self):
        return f"FileNode(path={self.path}, name={self.name}, is_dir={self.is_dir})"



class FileSystemTreeRenderer(TreeRenderer[FileNode]):
    """Renderer for file system tree structure."""
    
    def __init__(self, root_path: str, extensions: List[str] = ['.py']):
        self.root_path = root_path
        self.extensions = extensions
    
    def fill_tree(self, tree: Tree, data: List[FileNode]) -> None:
        """Fill the tree with file system structure."""
        tree.clear()
        tree.root.expand()
        
        # Group nodes by parent directory
        path_to_node_map = {}
        
        for node in data:
            path = Path(node.path)
            
            # Determine emoji
            if node.is_dir:
                emoji = "📁"
            else:
                emoji = "📄"
            
            label = f"{emoji} {node.name}"
            
            # Find parent in tree
            parent_path = str(path.parent)
            
            if parent_path == node.path:
                # This is root
                tree_node = tree.root.add(label, expand=True, data=node.path)
                path_to_node_map[node.path] = tree_node
            elif parent_path in path_to_node_map:
                # Parent exists in tree
                parent_tree_node = path_to_node_map[parent_path]
                tree_node = parent_tree_node.add(label, expand=False, data=node.path)
                path_to_node_map[node.path] = tree_node
            else:
                # Fallback: add to root
                tree_node = tree.root.add(label, expand=False, data=node.path)
                path_to_node_map[node.path] = tree_node
    
    def filter_data(self, data: List[FileNode], filter_text: str) -> List[FileNode]:
        """Filter file nodes by name."""
        if filter_text == "":
            return data
        
        filtered = [node for node in data if filter_text in node.name.lower()]
        return filtered
