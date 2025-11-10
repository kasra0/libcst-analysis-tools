from typing import List, Generic, TypeVar, Union
from textual.app         import ComposeResult
from textual.widget      import Widget 
from textual.widgets     import Tree
from textual.widgets     import Input
from libcst_analysis_tools.view.logger   import Logger
from libcst_analysis_tools.view.Renderer.TreeRenderer import TreeRenderer

T = TypeVar('T')


class TreeComponent(Widget, Generic[T]):
    def __init__(self, data: Union[List[T], T], renderer: TreeRenderer[T], title: str = "Root", component_id: str = "tree-component"):
        super().__init__(id=component_id)
        self.data = data
        self.renderer = renderer
        self.title = title
        self.tree_view_id = f"{component_id}-tree-view"
        self.tree_filter_input_id = f"{component_id}-filter-input"
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter methods...", id=self.tree_filter_input_id)
        tree = Tree(self.title, id=self.tree_view_id)
        self.renderer.fill_tree(tree, self.data)
        yield tree
    
    def get_filtered_data(self, filter_text: str) -> Union[List[T], T]:
        return self.renderer.filter_data(self.data, filter_text.strip().lower())
    
    def filter_tree(self, filter_text: str) -> None:
        filtered_data = self.get_filtered_data(filter_text)
        tree = self.query_one(f"#{self.tree_view_id}", Tree)
        self.renderer.fill_tree(tree, filtered_data)
    
    def reload_data(self, new_data: Union[List[T], T]) -> None:
        """Reload tree with new data."""
        self.data = new_data
        tree = self.query_one(f"#{self.tree_view_id}", Tree)
        self.renderer.fill_tree(tree, new_data)

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
