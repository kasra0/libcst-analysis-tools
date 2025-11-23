import libcst_analysis_tools.store.store as store
from textual.widget import Widget
from textual.widgets import DataTable
from textual.app import ComposeResult
from typing import List, Tuple



class TableComponent(Widget):

    def __init__(self, rows=None):
        """Initialize TableComponent with optional data rows.
        
        Args:
            rows: Optional list of tuples. If None, will load installed packages.
        """
        super().__init__()
        self.rows = rows
        self.all_packages: List[Tuple[str, str, str]] = []  # Store all packages for filtering
        self.current_filter = ""  # Current filter text
        self.last_sorted_column: int | None = None  # Track last sorted column
        
    def compose(self) -> ComposeResult:
        table = DataTable(cursor_type="row", id="packages-table")  # Enable row selection with ID
        table.zebra_stripes = True
        yield table

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        
        # If no rows provided, load installed packages
        if self.rows is None:
            self.all_packages = store.get_installed_packages()
            # Create header with sorting enabled
            table.add_columns("Package Name", "Version", "Location")
            # Add package rows
            table.add_rows(self.all_packages)
        else:
            # Use provided rows (legacy behavior)
            table.add_columns(*self.rows[0])
            table.add_rows(self.rows[1:])
    
    def filter_packages(self, filter_text: str) -> None:
        """Filter packages based on package name.
        
        Args:
            filter_text: Text to filter package names (case-insensitive)
        """
        self.current_filter = filter_text.lower().strip()
        table = self.query_one(DataTable)
        
        # Clear current rows
        table.clear()
        
        if not self.current_filter:
            # No filter, show all packages
            table.add_rows(self.all_packages)
        else:
            # Filter packages by name
            filtered = [
                pkg for pkg in self.all_packages
                if self.current_filter in pkg[0].lower()
            ]
            table.add_rows(filtered)
    
    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Handle column header click for sorting."""
        table = event.control
        
        # Get current data
        current_packages = self.all_packages if not self.current_filter else [
            pkg for pkg in self.all_packages
            if self.current_filter in pkg[0].lower()
        ]
        
        # Sort based on clicked column
        if event.column_index == 0:  # Package Name
            sorted_packages = sorted(current_packages, key=lambda x: x[0].lower())
        elif event.column_index == 1:  # Version
            # Sort versions intelligently (try to parse as version numbers)
            def version_key(pkg):
                try:
                    # Split version into parts and convert to integers when possible
                    parts = pkg[1].split('.')
                    return tuple(int(p) if p.isdigit() else p for p in parts)
                except:
                    return (pkg[1],)
            sorted_packages = sorted(current_packages, key=version_key)
        else:  # Location
            sorted_packages = sorted(current_packages, key=lambda x: x[2])
        
        # Toggle sort order if clicking same column
        if self.last_sorted_column == event.column_index:
            sorted_packages.reverse()
            self.last_sorted_column = None  # Reset to allow toggling
        else:
            self.last_sorted_column = event.column_index
        
        # Update table
        table.clear()
        table.add_rows(sorted_packages)
    
    def update_packages(self, packages: List[Tuple[str, str, str]]) -> None:
        """Update the packages list and refresh the table.
        
        Args:
            packages: New list of packages to display
        """
        self.all_packages = packages
        self.current_filter = ""  # Reset filter
        self.last_sorted_column = None  # Reset sort
        
        # Update table
        table = self.query_one(DataTable)
        table.clear()
        table.add_rows(self.all_packages)
