from libcst_analysis_tools.view.Renderer.TreeRenderer import TreeRenderer
from typing import List, Union
from textual.widgets import Tree
from pathlib import Path

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
