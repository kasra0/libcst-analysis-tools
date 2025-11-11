from textual.widgets import Tree, Input,RichLog
from typing import Union
from textual.widget import Widget   
from datetime import datetime

TreeNodeEvent = Union[Tree.NodeCollapsed, Tree.NodeExpanded, Tree.NodeHighlighted, Tree.NodeSelected]

class Logger:
    """A simple logger for Textual widgets."""

    @staticmethod
    def _log(widget:Widget,event:Union[Input.Changed,TreeNodeEvent]) -> None:
        if isinstance(event,Input.Changed):
            Logger._log_Input_event(widget,event)
        else:
            Logger._log_tree_event(widget,event)
    
    @staticmethod
    def _log_event(widget:Widget,component_type:str,event_name:str,id:str,value:str) -> None:
        log                 = widget.app.query_one("#event-log", RichLog)
        message             = format_log_message(component_type, id, event_name, value)
        timestamp_utc       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamped_message = f"[{timestamp_utc}] {message}"
        log.write(timestamped_message)
    
    @staticmethod
    def _log_Input_event(widget: Widget, event: Input.Changed) -> None:
        Logger._log_event(widget,
                          event.input.__class__.__name__,
                          type(event).__name__,
                          widget.query_one(Input).id or "unknown",
                          str(event.value))
        
    @staticmethod
    def _log_tree_event(widget: Widget, event: TreeNodeEvent) -> None:
        Logger._log_event( widget,
                           event.node.__class__.__name__,
                           type(event).__name__,
                           widget.query_one(Tree).id or "unknown",
                           str(event.node.label))

#helper function to format log messages
def format_log_message(componentType: str, tree_id: str, eventName: str, value: str) -> str:
        return f"[magenta]{componentType:20}[/magenta] | {tree_id:30} | [cyan]{eventName:20}[/cyan] | {value:20}"