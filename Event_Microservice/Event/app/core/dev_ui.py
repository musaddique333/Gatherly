from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from rich.style import Style

def print_ui(module_name="app.main", app_import_string="app.main:app", dev_mode_url="http://localhost:8001"):
    """
    Prints the formatted terminal UI for the module.

    Args:
        module_name (str): The module name to display.
        app_import_string (str): The import string for the FastAPI app.
        dev_mode_url (str): The URL for the development server.
    """
    console = Console()

    # Define styles
    title_style = Style(color="bright_blue", bold=True)
    subtitle_style = Style(color="green")
    text_style = Style(color="white", bgcolor="blue", bold=True)
    panel_style = Style(bgcolor="black", color="white")
    tree_style = Style(color="cyan")

    # Draw the Python package file structure
    tree = Tree("📁 app", style=tree_style)
    tree.add("🐍 __init__.py")
    tree.add("🐍 main.py")
    print("\n\n")
    panel_file_structure = Panel(tree, title="Python package file structure", expand=False, style=panel_style)

    # Print file structure
    console.print(panel_file_structure)

    # Another INFO log
    console.log(f"\n\n[{text_style}]Using import string [bold]{app_import_string}[/bold][/]", style=subtitle_style)

    # Draw the FastAPI CLI panel
    fastapi_panel = Panel(
        Text.from_markup(
            f"""Serving at: {dev_mode_url}
API docs: {dev_mode_url}/docs

Running in development mode, for production use:
fastapi run""",
            justify="center"
        ),
        title="FastAPI CLI - Development mode",
        expand=False,
        style=panel_style
    )
    console.print(fastapi_panel)

    print("\n\n")
