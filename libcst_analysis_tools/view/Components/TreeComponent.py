from typing import List, Generic, TypeVar, Protocol
from textual.app         import ComposeResult
from textual.widget      import Widget 
from textual.widgets     import Tree
from textual.widgets     import Input
from libcst_analysis_tools.list_classes  import ClassInfo
from libcst_analysis_tools.list_methods  import MethodInfo
from libcst_analysis_tools.view.logger   import Logger

ClassWithMethods = tuple[ClassInfo, list[MethodInfo]]
ClassesWithMethods = list[ClassWithMethods]

# Generic type variable
T = TypeVar('T')

# Protocol for renderer (interface)
class TreeRenderer(Protocol[T]):
    """Protocol defining the interface for tree renderers."""
    
    def fill_tree(self, tree: Tree, data: List[T]) -> None:
        """Fill the tree with data."""
        ...
    
    def filter_data(self, data: List[T], filter_text: str) -> List[T]:
        """Filter data based on filter text."""
        ...


# Concrete renderer for ClassesWithMethods
class ClassMethodsTreeRenderer(TreeRenderer[ClassWithMethods]):
    """Renderer for ClassesWithMethods data."""
    
    def fill_tree(self, tree: Tree, data: ClassesWithMethods) -> None:
        tree.clear()
        tree.root.expand()
        
        for cls, methods in data:
            class_emoji = "🧱"
            method_emoji = "⚙️"
            label = f"{class_emoji} {cls.name}"
            class_node = tree.root.add(label, expand=True)
            for method in methods:
                label = f"{method_emoji}  {method.name} ([magenta]@{method.lineno}[/magenta])"
                class_node.add_leaf(label)
    
    def filter_data(self, data: ClassesWithMethods, filter_text: str) -> ClassesWithMethods:
        if filter_text == "":
            return data
        
        filtered_data: ClassesWithMethods = []
        for cls, methods in data:
            filtered_methods = [m for m in methods if m.name.lower().startswith(filter_text)]
            if filtered_methods:
                filtered_data.append((cls, filtered_methods))
        return filtered_data



class TreeComponent(Widget, Generic[T]):
    def __init__(self, data: List[T], renderer: TreeRenderer[T], title: str = "Tree View"):
        super().__init__()
        self.data = data
        self.renderer = renderer
        self.title = title
        self.tree_view_id = "tree-view"
        self.tree_filter_input_id = "filter-input"
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter methods...", id=self.tree_filter_input_id)
        tree = Tree(self.title, id=self.tree_view_id)
        self.renderer.fill_tree(tree, self.data)
        yield tree
    
    def get_filtered_data(self, filter_text: str) -> List[T]:
        return self.renderer.filter_data(self.data, filter_text.strip().lower())
    
    def filter_tree(self, filter_text: str) -> None:
        filtered_data = self.get_filtered_data(filter_text)
        tree = self.query_one(f"#{self.tree_view_id}", Tree)
        self.renderer.fill_tree(tree, filtered_data)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter tree when input changes."""
        Logger._log_Input_event(self, event)
        self.filter_tree(event.value)

    def on_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        Logger._log_tree_event(self,event)

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        Logger._log_tree_event(self,event)

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        Logger._log_tree_event(self,event)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        Logger._log_tree_event(self,event)
