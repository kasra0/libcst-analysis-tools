from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import RichLog

class LogComponent(Widget):
    def compose(self) -> ComposeResult:
        yield RichLog(id="event-log", highlight=True, markup=True)