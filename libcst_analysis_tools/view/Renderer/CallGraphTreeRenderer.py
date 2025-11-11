"""Tree renderer for call graph visualization."""

from typing import List, Union
from textual.widgets import Tree
from libcst_analysis_tools.analyze_complete import CallGraphInfo


class CallGraphTreeRenderer:
    """Renderer for call graph with incoming and outgoing calls."""
    
    # Emojis
    INCOMING_EMOJI = "📥"
    OUTGOING_EMOJI = "📤"
    INCOMING_CALL_EMOJI     = "➡️ "
    OUTGOING_CALL_EMOJI     = "➡️ "
    
    def fill_tree(self, tree: Tree, data: Union[CallGraphInfo, List[CallGraphInfo]]) -> None:
        """Fill tree with call graph information."""
        # Handle Union type - extract CallGraphInfo
        if isinstance(data, list):
            if len(data) == 0:
                tree.clear()
                tree.root.label = "No callable selected"
                return
            call_info = data[0]
        else:
            call_info = data
        
        tree.clear()
        tree.root.expand()
        
        # Add incoming calls section
        if call_info.incoming:
            incoming_node = tree.root.add(f"{self.INCOMING_EMOJI} Incoming Calls ({len(call_info.incoming)})", expand=True)
            for caller in call_info.incoming:
                incoming_node.add_leaf(f"{self.INCOMING_CALL_EMOJI} {caller}")
        else:
            tree.root.add(f"{self.INCOMING_EMOJI} Incoming Calls (0)", expand=False)
        
        # Add outgoing calls section
        if call_info.outgoing:
            outgoing_node = tree.root.add(f"{self.OUTGOING_EMOJI} Outgoing Calls ({len(call_info.outgoing)})", expand=True)
            for callee in call_info.outgoing:
                outgoing_node.add_leaf(f"{self.OUTGOING_CALL_EMOJI} {callee}")
        else:
            tree.root.add(f"{self.OUTGOING_EMOJI} Outgoing Calls (0)", expand=False)
    
    def filter_data(self, data: Union[CallGraphInfo, List[CallGraphInfo]], filter_text: str) -> Union[CallGraphInfo, List[CallGraphInfo]]:
        """Filter call graph data based on text."""
        # Handle list wrapping
        if isinstance(data, list):
            if not data:
                return data
            call_info = data[0]
        else:
            call_info = data
        
        # If no filter, return original
        if not filter_text:
            return data
        
        filter_lower = filter_text.lower()
        
        # Filter incoming and outgoing calls
        filtered_incoming = [c for c in call_info.incoming if filter_lower in c.lower()]
        filtered_outgoing = [c for c in call_info.outgoing if filter_lower in c.lower()]
        
        # Create filtered CallGraphInfo
        filtered = CallGraphInfo(
            name=call_info.name,
            incoming=filtered_incoming,
            outgoing=filtered_outgoing
        )
        
        return filtered
