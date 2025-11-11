
from textual.app         import App, ComposeResult
from textual.reactive    import reactive
from textual.containers  import Container,Vertical,Horizontal
from textual.widgets     import Header,Footer,Tree,Input
import re
from textual.widgets     import RichLog
from libcst_analysis_tools.view.Components.TreeComponent            import TreeComponent
from libcst_analysis_tools.view.Components.DirectoryTreeComponent   import DirectoryTreeComponent
from libcst_analysis_tools.view.Renderer.CompleteModuleTreeRenderer import CompleteModuleTreeRenderer
from libcst_analysis_tools.view.Renderer.CallGraphTreeRenderer      import CallGraphTreeRenderer
from libcst_analysis_tools.view.Components.TableComponent           import TableComponent
from libcst_analysis_tools.view.Components.LogComponent             import LogComponent
from libcst_analysis_tools.analyze_complete                         import get_complete_module_info_from_file, ModuleInfo, CallGraphInfo
from libcst_analysis_tools.view.logger import Logger
import  libcst_analysis_tools.store.store as store 


class PackageAnalysisApp(App):
    """A Textual app to manage stopwatches."""
    
    CSS_PATH = "style.tcss"
    BINDINGS = [("D","toggle_dark","Toggle dark mode")]
    
    # Reactive property for package browsing
    package_to_browse = reactive("textual")

    def compose(self)-> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container():
            with Vertical(id="main-panel"):
                with Horizontal(id="main-content"):
                    # Left: Directory tree - browsing package (will be reactive)
                    yield DirectoryTreeComponent(
                        path=store.get_package_path(self.package_to_browse),
                        component_id="filesystem-tree"
                    )
                    # Right content trees
                    yield TreeComponent[ModuleInfo](
                        data=ModuleInfo(), 
                        renderer=CompleteModuleTreeRenderer(),
                        title="Module Content",
                        component_id="content-tree"
                    )
                    # Call graph tree
                    yield TreeComponent[CallGraphInfo](
                        data=CallGraphInfo(name="No selection"),
                        renderer=CallGraphTreeRenderer(),
                        title="Call Graph",
                        component_id="callgraph-tree"
                    )
                    with Vertical(id="right-panel"):
                        yield Input(placeholder="package...", id="package-name-input", value=self.package_to_browse)
                        yield TableComponent(store.tabular_data(100))
                
                yield LogComponent()
        yield Footer()
    
    def watch_package_to_browse(self, new_package: str) -> None:
        """React to package_to_browse changes - update DirectoryTree and clear content trees."""
        try:
            # Get new package path
            new_path = store.get_package_path(new_package)
            
            # Update DirectoryTreeComponent with new path
            filesystem_tree = self.query_one("#filesystem-tree", DirectoryTreeComponent)
            filesystem_tree.reload_path(new_path)
            
            # Clear content tree
            content_tree = self.query_one("#content-tree", TreeComponent)
            content_tree.reload_data(ModuleInfo(), title="Module Content")
            
            # Clear call graph tree
            callgraph_tree = self.query_one("#callgraph-tree", TreeComponent)
            callgraph_tree.reload_data(CallGraphInfo(name="No selection"), title="Call Graph")
            
            # Clear current module info
            self.current_module_info = None
            
        except Exception as e:
            # Log error
            x=10
            #log = self.query_one("#event-log", RichLog)
            #log.write(f"Error loading package '{new_package}': {str(e)}")
    
    def on_directory_tree_component_python_file_selected(self, event: DirectoryTreeComponent.PythonFileSelected) -> None:
        """Handle Python file selection from DirectoryTreeComponent."""
        try:
            # Use complete module analysis
            self.current_module_info = get_complete_module_info_from_file(event.file_path)
            
            # Get file name for title
            import os
            file_name = os.path.basename(event.file_path)
            
            # Update the content tree with new data and title
            content_tree = self.query_one("#content-tree", TreeComponent)
            content_tree.reload_data(self.current_module_info, title=f"📄 {file_name}")
        except Exception as e:
            # Log error if needed
            self.current_module_info = None
            pass
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection in any tree - update call graph when callable is selected."""
        # Only handle selections from the content tree
        tree = event.control  # type: ignore
        if tree.id != "content-tree-tree-view":
            return
        
        if not hasattr(self, 'current_module_info') or not self.current_module_info:
            return
        
        # Extract callable name from the selected node label
        label = str(event.node.label)
        callable_name = self._extract_callable_name(label)
        

        if not callable_name:
            return
        
        # Look up call graph info
        call_info = self.current_module_info.call_graph.get(callable_name)
        
        if call_info:
            # Update call graph tree
            callgraph_tree = self.query_one("#callgraph-tree", TreeComponent)
            callgraph_tree.reload_data(call_info, title=f"➡️ {callable_name}")
        
    def _extract_callable_name(self, label: str) -> str | None:
        """Extract callable name from tree node label."""
        # The label format from CompleteModuleTreeRenderer is like:
        # "🔧 method_name(params) @123"
        # We need to extract just "method_name" for methods
        # But the call_graph stores it as "ClassName.method_name"
        
        # First, remove everything after @ (line numbers)
        if '@' in label:
            label = label.split('@')[0].strip()
        
        # Remove emojis and decorators
        label = re.sub(r'[🔧⚙️📦📊🔢🧱]', '', label)
        label = re.sub(r'@\w+\s+', '', label)  # Remove decorators like @staticmethod
        label = re.sub(r'async\s+', '', label)  # Remove async keyword
        label = label.strip()
        
        # Pattern: function_name(...) or method_name(...)
        match = re.search(r'([\w]+)\s*\(', label)
        if match:
            method_name = match.group(1).strip()
            
            # Now we need to figure out if this is a method (needs ClassName prefix)
            # Check if we have current class context from the tree structure
            # For now, try both: just the name and also check all call_graph keys
            if hasattr(self, 'current_module_info') and self.current_module_info:
                # First try exact match
                if method_name in self.current_module_info.call_graph:
                    return method_name
                
                # Then try to find it with class prefix
                for key in self.current_module_info.call_graph.keys():
                    if key.endswith(f".{method_name}"):
                        return key
            
            return method_name
        
        return None

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes in the package name input."""
        # Only handle input changes from the package name input
        if event.input.id != "package-name-input":
            return
        
        package_name = event.value.strip()
        if not package_name:
            return
        #self.query_one("#event-log", RichLog).write(f"Package name input changed to: {package_name}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission in the package name input."""
        # Only handle input submissions from the package name input
        if event.input.id != "package-name-input":
            return
        
        new_package = event.value.strip()
        if new_package:
            # Update reactive property - this will trigger watch_package_to_browse
            self.package_to_browse = new_package
            
            # Log
            log = self.query_one("#event-log", RichLog)
            log.write(f"Switching to package: {new_package}")


    def action_toggle_dark(self)-> None:
        """An Action to toggle dark mode."""
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")
    

if __name__ == "__main__":
    app = PackageAnalysisApp()
    app.run()