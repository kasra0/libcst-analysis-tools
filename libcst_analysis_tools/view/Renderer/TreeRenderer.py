from typing import List, TypeVar, Protocol, Union
from textual.widgets     import Tree
from libcst_analysis_tools.list_classes  import ClassInfo
from libcst_analysis_tools.list_methods  import MethodInfo
from pathlib import Path

ClassWithMethods = tuple[ClassInfo, list[MethodInfo]]
ClassesWithMethods = list[ClassWithMethods]

# Generic type variable
T = TypeVar('T')

# Protocol for renderer (interface)
class TreeRenderer(Protocol[T]):
    """Protocol defining the interface for tree renderers."""
    
    def fill_tree(self, tree: Tree, data: Union[List[T], T]) -> None:
        """Fill the tree with data."""
        ...
    
    def filter_data(self, data: Union[List[T], T], filter_text: str) -> Union[List[T], T]:
        """Filter data based on filter text."""
        ...
