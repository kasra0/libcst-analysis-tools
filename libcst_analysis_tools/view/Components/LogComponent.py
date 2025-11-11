from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import RichLog

class LogComponent(Widget):
    
    DEFAULT_CSS = """
    LogComponent {
        border: solid $primary;
        border-title-align: left;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield RichLog(id="event-log", highlight=True, markup=True)
    
    def on_mount(self) -> None:
        """Set the border title when mounted."""
        self.border_title = "Application Log"