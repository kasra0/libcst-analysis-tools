
from textual.app         import App, ComposeResult
from textual.containers  import Container,Vertical,Horizontal
from textual.widgets     import Header,Footer,Tree

from libcst_analysis_tools.view.Components.TreeComponent  import TreeComponent
from libcst_analysis_tools.view.Components.DirectoryTreeComponent import DirectoryTreeComponent
from libcst_analysis_tools.view.Renderer.CompleteModuleTreeRenderer import CompleteModuleTreeRenderer
from libcst_analysis_tools.view.Components.TableComponent import TableComponent
from libcst_analysis_tools.view.Components.LogComponent   import LogComponent
from libcst_analysis_tools.analyze_complete import get_complete_module_info_from_file, ModuleInfo

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
                # Left: Directory tree - browsing Textual package
                package_to_browse = "textual"  # Change this to browse other packages
                yield DirectoryTreeComponent(
                    path=store.get_package_path(package_to_browse),
                    component_id="filesystem-tree"
                )
                # Right content trees
                yield TreeComponent[ModuleInfo](
                    data=ModuleInfo(), 
                    renderer=CompleteModuleTreeRenderer(),
                    title="Module Content",
                    component_id="content-tree"
                )
                with Vertical(id="right-panel"):
                    yield TableComponent(store.tabular_data(100))
                    yield LogComponent()
        yield Footer()
    
    def on_directory_tree_component_python_file_selected(self, event: DirectoryTreeComponent.PythonFileSelected) -> None:
        """Handle Python file selection from DirectoryTreeComponent."""
        try:
            # Use complete module analysis
            module_info = get_complete_module_info_from_file(event.file_path)
            
            # Get file name for title
            import os
            file_name = os.path.basename(event.file_path)
            
            # Update the content tree with new data and title
            content_tree = self.query_one("#content-tree", TreeComponent)
            content_tree.reload_data(module_info, title=f"📄 {file_name}")
        except Exception as e:
            # Log error if needed
            pass

    
    def action_toggle_dark(self)-> None:
        """An Action to toggle dark mode."""
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")

if __name__ == "__main__":
    app = RootApp()
    app.run()