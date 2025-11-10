from typing import Union,List
from textual.app         import App, ComposeResult
from textual.widget      import Widget 
from textual.widgets     import Header,Footer, Tree, DataTable, RichLog,Label
from textual.widgets     import Input
from libcst_analysis_tools.list_classes  import ClassInfo
from libcst_analysis_tools.list_methods  import MethodInfo
from libcst_analysis_tools.analyze_complete import get_all_classes_with_methods_from_file
import inspect
from datetime import datetime, timezone
from libcst_analysis_tools.view.logger import Logger

TreeNodeEvent = Union[Tree.NodeCollapsed, Tree.NodeExpanded, Tree.NodeHighlighted, Tree.NodeSelected]

def build_tree_from_classes(classes_with_methods:List[tuple[ClassInfo, List[MethodInfo]]],id)->Tree:
    tree: Tree[str] = Tree("Classes and Methods",id=id)
    tree.root.expand()
    
    for cls, methods in classes_with_methods:
        class_emoji   = "🧱"
        method_emoji  = "⚙️"
        package_emoji = "📦"
        class_node = tree.root.add(f"{class_emoji} {cls.name}", expand=True)
        for method in methods:
            class_node.add_leaf(f"{method_emoji}  {method.name} ([lightgreen]@{method.lineno}[/lightgreen])")
    return tree

class TreeComponent(Widget):
    def __init__(self):
        super().__init__()
        # Store original data
        self.all_classes_with_methods = get_all_classes_with_methods_from_file(inspect.getfile(App))
        # Sort by classes and methods alphabetically
        self.all_classes_with_methods.sort(key=lambda x: x[0].name)
        for cls, methods in self.all_classes_with_methods:
            methods.sort(key=lambda m: m.name)
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter methods...", id="filter-input")
        yield build_tree_from_classes(self.all_classes_with_methods, "tree-view")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter tree when input changes."""
        Logger._log_Input_event(self, event)
        self.filter_tree(event.value)
        
    def filter_tree(self, filter_text: str) -> None:
        # Filter methods by name (startswith)
        filtered_data: List[tuple[ClassInfo, List[MethodInfo]]] = []
        for cls, methods in self.all_classes_with_methods:
            if filter_text == "":
                # No filter, include all methods
                filtered_data.append((cls, methods))
            else:
                # Filter methods that start with the filter text
                filtered_methods = [m for m in methods if m.name.lower().startswith(filter_text)]
                # Only include class if it has matching methods
                if filtered_methods:
                    filtered_data.append((cls, filtered_methods))
        
        # Rebuild tree with filtered data
        tree = self.query_one("#tree-view", Tree)
        tree.clear()
        tree.root.expand()
        
        for cls, methods in filtered_data:
            class_emoji = "🧱"
            method_emoji = "⚙️"
            class_node = tree.root.add(f"{class_emoji} {cls.name}", expand=True)
            for method in methods:
                class_node.add_leaf(f"{method_emoji}  {method.name} ([lightgreen]@{method.lineno}[/lightgreen])")

    def on_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        Logger._log_tree_event(self,event)

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        Logger._log_tree_event(self,event)

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        Logger._log_tree_event(self,event)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        Logger._log_tree_event(self,event)
    
#helper function to format log messages
def format_log_message(componentType: str, tree_id: str, eventName: str, value: str) -> str:
        return f"[magenta]{componentType:20}[/magenta] | [cyan]{eventName:20}[/cyan] | {tree_id:20} | {value:20}"