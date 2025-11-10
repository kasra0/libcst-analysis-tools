from typing import Protocol, Any, Union,List

from textual.app         import App, ComposeResult
from textual.message     import Message
from textual.containers  import Container,VerticalScroll,VerticalGroup,Vertical,Horizontal,HorizontalGroup,HorizontalScroll
from textual.widget      import Widget 
from textual.widgets     import Header,Footer, Tree, DataTable, RichLog
from libcst_analysis_tools.view.Components.TreeComponent import TreeComponent


TreeNodeEvent = Union[Tree.NodeCollapsed, Tree.NodeExpanded, Tree.NodeHighlighted, Tree.NodeSelected]


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

class LogComponent(Widget):
    def compose(self) -> ComposeResult:
        yield RichLog(id="event-log", highlight=True, markup=True)

if __name__ == "__main__":
    app = RootApp()
    app.run()