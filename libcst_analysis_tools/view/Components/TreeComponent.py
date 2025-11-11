from typing import List, Generic, TypeVar, Union, Optional
from textual.app         import ComposeResult
from textual.widget      import Widget 
from textual.widgets     import Tree
from textual.widgets     import Input
from textual.containers import HorizontalScroll
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
        with HorizontalScroll(id="tree-scroll"):
            tree = Tree(self.title, id=self.tree_view_id)
            tree.auto_expand = False  # Don't auto-expand but allow full width labels
            self.renderer.fill_tree(tree, self.data)
            yield tree
    
    def get_filtered_data(self, filter_text: str) -> Union[List[T], T]:
        return self.renderer.filter_data(self.data, filter_text.strip().lower())
    
    def filter_tree(self, filter_text: str) -> None:
        filtered_data = self.get_filtered_data(filter_text)
        tree = self.query_one(f"#{self.tree_view_id}", Tree)
        self.renderer.fill_tree(tree, filtered_data)
    
    def reload_data(self, new_data: Union[List[T], T], title: Optional[str] = None) -> None:
        """Reload tree with new data and optionally update title."""
        self.data = new_data
        tree = self.query_one(f"#{self.tree_view_id}", Tree)
        if title:
            tree.root.label = title
        self.renderer.fill_tree(tree, new_data)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter tree when input changes."""
        # Only handle input changes from this component's filter input
        if event.input.id != self.tree_filter_input_id:
            return
        
        Logger._log(self, event)
        self.filter_tree(event.value)

    def on_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        Logger._log(self,event)

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        Logger._log(self,event)

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        Logger._log(self,event)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        Logger._log(self,event)