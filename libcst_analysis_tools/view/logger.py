from textual.widgets import Tree, Input,RichLog
from typing import Union
from textual.widget import Widget   
from datetime import datetime

TreeNodeEvent = Union[Tree.NodeCollapsed, Tree.NodeExpanded, Tree.NodeHighlighted, Tree.NodeSelected]

class Logger:
    """A simple logger for Textual widgets."""
    
    @staticmethod
    def _log_Input_event(widget: Widget, event: Input.Changed) -> None:
        log = widget.app.query_one("#event-log", RichLog)
        component_type = event.input.__class__.__name__
        tree = widget.query_one(Input)
        tree_id = tree.id or "unknown"
        event_name = type(event).__name__
        value = str(event.value)
        message = format_log_message(component_type, tree_id, event_name, value)
        timestamp_utc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamped_message = f"[{timestamp_utc}] {message}"
        log.write(timestamped_message)
        
    @staticmethod
    def _log_tree_event(widget: Widget, event: TreeNodeEvent) -> None:
        log = widget.app.query_one("#event-log", RichLog)
        component_type = event.node.__class__.__name__
        tree = widget.query_one(Tree)
        tree_id = tree.id or "unknown"
        event_name = type(event).__name__
        value = str(event.node.label)
        message = format_log_message(component_type, tree_id, event_name, value)
        timestamp_utc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamped_message = f"[{timestamp_utc}] {message}"
        log.write(timestamped_message)

#helper function to format log messages
def format_log_message(componentType: str, tree_id: str, eventName: str, value: str) -> str:
        return f"[magenta]{componentType:20}[/magenta] | [cyan]{eventName:20}[/cyan] | {tree_id:20} | {value:20}"