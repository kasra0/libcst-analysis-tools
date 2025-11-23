
from textual.app         import App, ComposeResult
from textual.reactive    import reactive
from textual.containers  import Container,Vertical,Horizontal,HorizontalScroll
from textual.widgets     import Header,Footer,Tree,Input,Collapsible,DataTable
import re
from textual.widgets     import RichLog
from libcst_analysis_tools.view.Components.TreeComponent            import TreeComponent
from libcst_analysis_tools.view.Components.DirectoryTreeComponent   import DirectoryTreeComponent
from libcst_analysis_tools.view.Renderer.CompleteModuleTreeRenderer import CompleteModuleTreeRenderer
from libcst_analysis_tools.view.Renderer.CallGraphTreeRenderer      import CallGraphTreeRenderer
from libcst_analysis_tools.view.Components.TableComponent           import TableComponent
from libcst_analysis_tools.view.Components.EnvironmentsTableComponent import EnvironmentsTableComponent
from libcst_analysis_tools.view.Components.LogComponent             import LogComponent
from libcst_analysis_tools.analyze_complete                         import get_complete_module_info_from_file, ModuleInfo, CallGraphInfo
from libcst_analysis_tools.view.logger import Logger
import  libcst_analysis_tools.store.store as store 


class PackageAnalysisApp(App):
    """A Textual app for analyzing Python packages with call graph visualization.
    
    Args:
        package_name: Optional initial package to browse. If None, starts empty.
    """
    
    CSS_PATH = "style.tcss"
    BINDINGS = [("D","toggle_dark","Toggle dark mode")]
    
    # Reactive property for package browsing
    package_to_browse = reactive("")
    # Track current environment context
    current_env_name = ""
    current_env_type = ""
    current_env_location = ""
    
    def __init__(self, package_name: str | None = None, **kwargs):
        """Initialize the app with an optional package to browse."""
        super().__init__(**kwargs)
        # Store initial package to set after mount
        self._initial_package = package_name

    def compose(self)-> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container():
            # Main horizontal layout: Left (envs + packages) | Right (trees + log)
            with Horizontal(id="main-layout"):
                # LEFT PANEL: Environments (top 1/3) + Packages (bottom 2/3)
                with Vertical(id="left-panel"):
                    # Environments section (1/3)
                    with Vertical(id="environments-section"):
                        yield EnvironmentsTableComponent()
                    
                    # Packages section (2/3)
                    with Vertical(id="packages-section"):
                        # Filter input for the table
                        yield Input(
                            placeholder="Filter packages...", 
                            id="package-filter-input"
                        )
                        
                        with HorizontalScroll(id="table-scroll"):
                            yield TableComponent()  # Auto-loads installed packages
                        
                        # Show selected package (read-only display)
                        initial_value = ""
                        if self.package_to_browse:
                            initial_value = self.package_to_browse
                        elif hasattr(self, '_initial_package') and self._initial_package:
                            initial_value = self._initial_package
                            
                        yield Input(
                            placeholder="Selected package: (none)", 
                            id="package-name-input", 
                            value=initial_value
                        )
                
                # RIGHT PANEL: Trees (top 70%) + Log (bottom 30%)
                with Vertical(id="right-panel"):
                    # Trees section (horizontal: 3 trees side by side)
                    with Horizontal(id="trees-panel"):
                        # Check both reactive property and initial package
                        initial_path = "."
                        if self.package_to_browse:
                            initial_path = store.get_package_path(self.package_to_browse)
                        elif hasattr(self, '_initial_package') and self._initial_package:
                            initial_path = store.get_package_path(self._initial_package)
                        
                        yield DirectoryTreeComponent(
                            path=initial_path,
                            component_id="filesystem-tree"
                        )
                        
                        yield TreeComponent[ModuleInfo](
                            data=ModuleInfo(), 
                            renderer=CompleteModuleTreeRenderer(),
                            title="Module Content",
                            component_id="content-tree",
                            border_title="Module Content"
                        )
                        
                        yield TreeComponent[CallGraphInfo](
                            data=CallGraphInfo(name="No selection"),
                            renderer=CallGraphTreeRenderer(),
                            title="Call Graph",
                            component_id="callgraph-tree",
                            border_title="Call Graph"
                        )
                    
                    # Log section
                    yield LogComponent()
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app is mounted. Set initial package if provided."""
        if hasattr(self, '_initial_package') and self._initial_package:
            self.package_to_browse = self._initial_package
    
    def watch_package_to_browse(self, new_package: str) -> None:
        """React to package_to_browse changes - update DirectoryTree and clear content trees."""
        # Skip if empty or during initialization
        if not new_package or not self.is_mounted:
            return
            
        try:
            # Get new package path with environment context
            log = self.query_one("#event-log", RichLog)
            
            # Log which environment we're searching in
            env_info = "current environment"
            if self.current_env_name:
                env_info = f"environment '{self.current_env_name}' ({self.current_env_type})"
            log.write(f"🔍 Searching for package '{new_package}' in {env_info}")
            
            new_path = store.get_package_path(
                new_package, 
                self.current_env_name, 
                self.current_env_type, 
                self.current_env_location
            )
            log.write(f"✅ Loading package '{new_package}' from path: {new_path}")
            
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
            
            # Update input field
            input_field = self.query_one("#package-name-input", Input)
            if input_field.value != new_package:
                input_field.value = new_package
            
        except Exception as e:
            # Log error
            if self.is_mounted:
                log = self.query_one("#event-log", RichLog)
                log.write(f"Error loading package '{new_package}': {str(e)}")
    
    def on_directory_tree_component_python_file_selected(self, event: DirectoryTreeComponent.PythonFileSelected) -> None:
        """Handle Python file selection from DirectoryTreeComponent."""
        try:
            # Use complete module analysis
            self.current_module_info = get_complete_module_info_from_file(event.file_path)
            
            # Get file name and calculate stats
            import os
            file_name = os.path.basename(event.file_path)
            
            # Count total lines in file
            with open(event.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines = sum(1 for _ in f)
            
            # Count stats from module info
            num_imports = len(self.current_module_info.imports)
            num_classes = len(self.current_module_info.classes)
            num_functions = len(self.current_module_info.functions)
            
            # Create title with stats: filename(L(lines),I(imports),C(classes),F(functions))
            stats_title = f"📄 {file_name} (L({total_lines}), I({num_imports}), C({num_classes}), F({num_functions}))"
            
            # Update the content tree with new data and title
            content_tree = self.query_one("#content-tree", TreeComponent)
            content_tree.reload_data(self.current_module_info, title=stats_title)
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
        """Handle input changes for filtering the packages table."""
        # Only handle the filter input
        if event.input.id == "package-filter-input":
            filter_text = event.value.strip()
            # Filter the packages table in real-time
            table_component = self.query_one(TableComponent)
            table_component.filter_packages(filter_text)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission - Enter key to load package manually."""
        # Handle manual package entry from the package-name-input
        if event.input.id == "package-name-input":
            new_package = event.value.strip()
            if new_package:
                # Update reactive property - this will trigger watch_package_to_browse
                self.package_to_browse = new_package
                
                # Log
                log = self.query_one("#event-log", RichLog)
                log.write(f"Switching to package: {new_package}")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in tables (environments or packages)."""
        table = event.control
        row_key = event.row_key
        
        # Get the row data
        row_data = table.get_row(row_key)
        if not row_data:
            return
        
        # Check which table was clicked by ID
        if table.id == "environments-table":
            # Environment selected - load its packages
            env_name = str(row_data[0])
            env_type = str(row_data[1])
            env_location = str(row_data[3])
            
            # Store current environment context
            self.current_env_name = env_name
            self.current_env_type = env_type
            self.current_env_location = env_location
            
            # Log
            log = self.query_one("#event-log", RichLog)
            log.write(f"🌍 Selected environment: {env_name} ({env_type}) at {env_location}")
            
            # Get packages from this environment
            packages = store.get_packages_from_environment(env_name, env_type, env_location)
            
            # Update TableComponent with new packages (updates internal state)
            table_component = self.query_one(TableComponent)
            table_component.update_packages(packages)
            
            # Also clear the filter input
            filter_input = self.query_one("#package-filter-input", Input)
            filter_input.value = ""
            
            log.write(f"Loaded {len(packages)} packages from {env_name}")
            
        elif table.id == "packages-table":
            # Package selected - load package details
            package_name = str(row_data[0])  # First column is package name
            
            # Update reactive property - this will trigger watch_package_to_browse
            self.package_to_browse = package_name
            
            # Update input field to show selected package
            input_field = self.query_one("#package-name-input", Input)
            input_field.value = package_name
            
            # Log
            log = self.query_one("#event-log", RichLog)
            log.write(f"📦 Selected package from table: {package_name}")

    def action_toggle_dark(self)-> None:
        """An Action to toggle dark mode."""
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")


def main():
    """CLI entry point for the package analysis TUI."""
    import sys
    
    # Check if package name provided as argument
    package_name = None
    if len(sys.argv) > 1:
        package_name = sys.argv[1]
    
    app = PackageAnalysisApp(package_name=package_name)
    app.run()
    

if __name__ == "__main__":
    main()