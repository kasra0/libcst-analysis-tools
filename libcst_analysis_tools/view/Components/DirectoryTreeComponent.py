"""DirectoryTreeComponent using Textual's built-in DirectoryTree widget."""

from textual.app     import ComposeResult
from textual.widget  import Widget
from textual.widgets import DirectoryTree, Input
from textual.message import Message
from rich.text import Text
from pathlib import Path
from typing import Tuple, Dict
from libcst_analysis_tools.view.logger import Logger

class FilteredDirectoryTree(DirectoryTree):
    """DirectoryTree with filtering capability and enhanced labels."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_text = ""
    
    def filter_paths(self, paths):
        """Filter paths based on filter text."""
        if not self.filter_text:
            return paths
        return [p for p in paths if self.filter_text in str(p.name).lower()]
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file quickly."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def _count_directory_stats(self, directory: Path) -> Tuple[int, int]:
        """Count files and total lines in a directory (non-recursive for speed).
        
        Returns:
            Tuple of (file_count, total_lines)
        """
        file_count = 0
        total_lines = 0
        
        try:
            # Only count direct children, not recursive
            for item in directory.glob('*.py'):
                if item.is_file():
                    file_count += 1
                    total_lines += self._count_lines(item)
        except Exception:
            pass
        
        return file_count, total_lines
    
    def render_label(self, node, base_style, style):
        """Render the label with additional info: folder item count or file line count."""
        # Get the original label
        label = super().render_label(node, base_style, style)  # type: ignore
        
        # Get the path from node data
        if node.data is None:
            return label
        
        dir_entry = node.data
        path = Path(dir_entry.path)
        
        try:
            if path.is_dir():
                # Count files and lines in direct children only (fast)
                file_count, total_lines = self._count_directory_stats(path)
                if file_count > 0:
                    label.append(" ")
                    label.append(f"({file_count}F, {total_lines}L)", style="magenta bold")
            elif path.is_file() and path.suffix == '.py':
                # Count lines in file
                lines = self._count_lines(path)
                label.append(" ")
                label.append(f"({lines}L)", style="cyan")
        except Exception:
            # If we can't access the path, just return the original label
            pass
        
        return label

class DirectoryTreeComponent(Widget):
    """Component that wraps DirectoryTree for browsing file systems with filtering."""
    
    class PythonFileSelected(Message):
        """Message emitted when a Python file is selected."""
        def __init__(self, file_path: str):
            super().__init__()
            self.file_path = file_path
    
    def __init__(self, path: str, component_id: str = "directory-tree", border_title: str = "Directory Tree"):
        super().__init__(id=component_id)
        self.path = path
        self.filter_input_id = f"{component_id}-filter-input"
        self.tree_id = f"{component_id}-tree"
        self.border_title = border_title
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Input(placeholder="Filter files/folders...", id=self.filter_input_id)
        yield FilteredDirectoryTree(self.path, id=self.tree_id)
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection and emit custom message for Python files."""
        file_path = str(event.path)
        
        # Only emit message for Python files
        if file_path.endswith('.py'):
            self.post_message(self.PythonFileSelected(file_path))
    
    def reload_path(self, new_path: str) -> None:
        """Reload the directory tree with a new path."""
        self.path = new_path
        tree = self.query_one(f"#{self.tree_id}", FilteredDirectoryTree)
        tree.path = new_path
        tree.reload()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter directory tree when input changes."""
        # Check if the input belongs to this component
        if event.input.id != self.filter_input_id:
            return
            
        filter_text = event.value.strip().lower()
        tree = self.query_one(f"#{self.tree_id}", FilteredDirectoryTree)
        
        # Update filter and reload tree
        tree.filter_text = filter_text
        tree.reload()
        
        Logger._log(self, event)