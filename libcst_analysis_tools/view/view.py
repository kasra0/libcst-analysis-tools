from typing import Protocol, Any, Union,List

from textual.app         import App, ComposeResult
from textual.message     import Message
from textual.containers  import Container,VerticalScroll,VerticalGroup,Vertical,Horizontal,HorizontalGroup,HorizontalScroll
from textual.widget      import Widget 
from textual.widgets     import Header,Footer, Tree, DataTable, RichLog
from libcst_analysis_tools.list_classes  import ClassInfo
from libcst_analysis_tools.list_methods  import MethodInfo
from libcst_analysis_tools.analyze_complete import get_all_classes_with_methods_from_file,get_all_classes_with_methods
import inspect



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
            class_node.add_leaf(f"{method_emoji}  {method.name} (@{method.lineno})")
    return tree
RANDOM_CELEBRITIES = ["Ada Lovelace", "Alan Turing", "Grace Hopper", "Linus Torvalds", "Margaret Hamilton", "Tim Berners-Lee", "Katherine Johnson", "Dennis Ritchie", "Barbara Liskov", "James Gosling"] 
RANDOM_COUNTRIES = ["USA", "UK", "Canada", "Germany", "France", "Japan", "Australia", "India", "Brazil", "Italy"]
def data_sample_for_table(rows_count)->list[tuple]:
    list_ = []
    # Header
    list_.append(("ID", "Name", "Country", "Time (s)"))
    for i in range(rows_count):
        list_.append( (i, RANDOM_CELEBRITIES[i % len(RANDOM_CELEBRITIES)], RANDOM_COUNTRIES[i % len(RANDOM_COUNTRIES)], 50.0 + i*0.1) )
    return list_



class RootApp(App):
    """A Textual app to manage stopwatches."""
    
    CSS_PATH = "view.tcss"
    BINDINGS = [("D","toggle_dark","Toggle dark mode")]

    def compose(self)-> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container():
            with Horizontal():
                yield TreeComponent()
                with Vertical(id="right-panel"):
                    yield TableComponent()
                    yield LogComponent()
        yield Footer()

    
    def action_toggle_dark(self)-> None:
        """An Action to toggle dark mode."""
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")


ROWS = data_sample_for_table(100)



class TableComponent(Widget):
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])

class TreeComponent(Widget):
    def compose(self) -> ComposeResult:
        classes_with_methods = get_all_classes_with_methods_from_file(inspect.getfile(Tree))
        #sort by classes ( first level) and methods has to be sorted alphabetically
        classes_with_methods.sort(key=lambda x: x[0].name)
        for cls, methods in classes_with_methods:
            methods.sort(key=lambda m: m.name)
        tree = build_tree_from_classes(classes_with_methods,"tree-view")
        yield tree

    def _log_tree_event(self, event: TreeNodeEvent) -> None:
        log = self.app.query_one("#event-log", RichLog)
        component_type = type(self).__name__

        tree = self.query_one(Tree)
        tree_id = tree.id or "unknown"

        event_name = type(event).__name__
        value = str(event.node.label)

        message = format_log_message(component_type, tree_id, event_name, value)
        log.write(message)

    def on_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        self._log_tree_event(event)

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        self._log_tree_event(event)

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        self._log_tree_event(event)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        self._log_tree_event(event)
    
#helper function to format log messages
def format_log_message(componentType: str, tree_id: str, eventName: str, value: str) -> str:
        return f"[magenta]{componentType:20}[/magenta] | [cyan]{eventName:20}[/cyan] | {tree_id:20} | {value:20}"

class LogComponent(Widget):
    def compose(self) -> ComposeResult:
        yield RichLog(id="event-log", highlight=True, markup=True)



if __name__ == "__main__":
    app = RootApp()
    app.run()