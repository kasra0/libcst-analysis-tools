import libcst_analysis_tools.store.store as store
from textual.widget import Widget
from textual.widgets import DataTable, Button
from textual.app import ComposeResult
from textual.containers import Vertical


class EnvironmentsTableComponent(Widget):
    """Component to display virtual environments in a table."""
    
    DEFAULT_CSS = """
    EnvironmentsTableComponent {
        border: solid $primary;
        border-title-align: left;
    }
    
    #scan-envs-button {
        dock: top;
        width: 100%;
        margin: 1;
    }
    """

    def __init__(self):
        """Initialize EnvironmentsTableComponent."""
        super().__init__()
        self.border_title = "🌍 Virtual Environments"
        
    def compose(self) -> ComposeResult:
        yield Button("🔍 Scan Environments", id="scan-envs-button", variant="primary")
        table = DataTable(cursor_type="row", id="environments-table")
        table.zebra_stripes = True
        yield table

    def on_mount(self) -> None:
        """Initialize table headers but don't load data yet."""
        table = self.query_one("#environments-table", DataTable)
        # Create header
        table.add_columns("Name", "Type", "Packages", "Location")
        # Don't load environments yet - wait for button click
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle scan button click."""
        if event.button.id == "scan-envs-button":
            # Load environments
            environments = store.get_virtual_environments()
            
            # Update table
            table = self.query_one("#environments-table", DataTable)
            table.clear()
            table.add_rows(environments)
            
            # Update button to show it's done
            button = event.button
            button.label = f"✅ Found {len(environments)} environments"
            button.disabled = True
