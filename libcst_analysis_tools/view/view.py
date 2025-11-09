from textual.app         import App, ComposeResult
from textual.containers  import Container,VerticalScroll,VerticalGroup,Vertical,Horizontal,HorizontalGroup,HorizontalScroll
from textual.widget      import Widget 
from textual.widgets     import Header,Footer, Tree, DataTable, RichLog
from libcst_analysis_tools.analyze_complete import get_all_classes_with_methods_from_file
import inspect

def build_tree_from_classes(classes_with_methods)->Tree:
    tree: Tree[str] = Tree("Classes and Methods",id="tree-view")
    tree.root.expand()
    
    for cls, methods in classes_with_methods:
        class_node = tree.root.add(f"Class: {cls.name}", expand=True)
        for method in methods:
            class_node.add_leaf(f"Method: {method.name} (line {method.lineno})")
    
    return tree


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


ROWS = [
    ("lane", "swimmer", "country", "time"),
    (4, "Joseph Schooling", "Singapore", 50.39),
    (2, "Michael Phelps", "United States", 51.14),
    (5, "Chad le Clos", "South Africa", 51.14),
    (6, "László Cseh", "Hungary", 51.14),
    (3, "Li Zhuhao", "China", 51.26),
    (8, "Mehdy Metella", "France", 51.58),
    (7, "Tom Shields", "United States", 51.73),
    (1, "Aleksandr Sadovnikov", "Russia", 51.84),
    (10, "Darren Burns", "Scotland", 51.84),
]


class TableComponent(Widget):
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])

class TreeComponent(Widget):
    def compose(self) -> ComposeResult:
        classes_with_methods = get_all_classes_with_methods_from_file(inspect.getfile(App))
        tree = build_tree_from_classes(classes_with_methods)
        yield tree

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        """Log when a tree node is highlighted."""
        log = self.app.query_one("#event-log", RichLog)
        log.write(f"[cyan]Tree NodeHighlighted:[/cyan] {event.node.label}")


class LogComponent(Widget):
    def compose(self) -> ComposeResult:
        yield RichLog(id="event-log", highlight=True, markup=True)



if __name__ == "__main__":
    app = RootApp()
    app.run()