from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, DataTable, Log
from textual.containers import Horizontal, Vertical


def get_sample_data(count: int = 10):
    return  [(i, f"Job #{i}", "OK" if i % 2 == 0 else "Failed") for i in range(1, count + 1)]


class DashboardApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    Header {
        dock: top;
        height: 2;
    }

    Footer {
        dock: bottom;
        height: 1;
    }

    #body {
        layout: horizontal;
        height: 1fr;
    }

    #sidebar {
        width: 30;
        border: heavy;
    }

    #main {
        layout: vertical;
        width: 1fr;

    }

    #table-container {
        height: 2fr;
        border-bottom: solid;
    }

    #log-container {
        height: 1fr;
    }

    DataTable, Log, Tree {
        height: 100%;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        # Header & Footer auto-docked via CSS
        yield Header(show_clock=True)
        yield Footer()

        # Central body
        with Horizontal(id="body"):
            # Sidebar with a tree
            sidebar_tree = Tree("Projects", id="sidebar")
            node = sidebar_tree.root.add("Project A")
            node.add_leaf("Service 1")
            node.add_leaf("Service 2")
            sidebar_tree.root.expand()
            yield sidebar_tree

            # Main area (table + log stacked)
            with Vertical(id="main"):
                with Vertical(id="table-container"):
                    table = DataTable(id="table")
                    table.add_columns("ID", "Name", "Status")
                    table.add_rows(get_sample_data())
                    yield table

                with Vertical(id="log-container"):
                    log = Log(id="log")
                    log.write("System started.")
                    log.write("Watching jobs...")
                    yield log

    # Interactivity examples

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        log = self.query_one("#log", Log)
        log.clear()
        log.write(f"Selected: {event.node.label}")

    def on_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        table = event.data_table
        row_data = table.get_row(event.row_key)
        log = self.query_one("#log", Log)
        log.clear()
        log.write(f"Row highlighted: {row_data}")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row_data = table.get_row(event.row_key)
        log = self.query_one("#log", Log)
        log.clear()
        log.write(f"Row selected: {row_data}")

if __name__ == "__main__":
    DashboardApp().run()
