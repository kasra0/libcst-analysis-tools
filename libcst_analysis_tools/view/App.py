
from textual.app         import App, ComposeResult
from textual.containers  import Container,Vertical,Horizontal
from textual.widgets     import Header,Footer

from libcst_analysis_tools.view.Components.TreeComponent  import TreeComponent
from libcst_analysis_tools.view.Components.TreeComponent  import ClassMethodsTreeRenderer
from libcst_analysis_tools.view.Components.TableComponent import TableComponent
from libcst_analysis_tools.view.Components.LogComponent   import LogComponent

import  libcst_analysis_tools.store.store as store 


class RootApp(App):
    """A Textual app to manage stopwatches."""
    
    CSS_PATH = "view.tcss"
    BINDINGS = [("D","toggle_dark","Toggle dark mode")]

    def compose(self)-> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container():
            with Horizontal():
                yield TreeComponent(data=store.tree_data(), renderer=ClassMethodsTreeRenderer())
                with Vertical(id="right-panel"):
                    yield TableComponent(store.tabular_data(100))
                    yield LogComponent()
        yield Footer()

    
    def action_toggle_dark(self)-> None:
        """An Action to toggle dark mode."""
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")



if __name__ == "__main__":
    app = RootApp()
    app.run()