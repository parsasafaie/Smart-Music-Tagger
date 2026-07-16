"""CLI interface for Smart Music Tagger."""

from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich import box


class CLIInterface:
    """Beautiful CLI interface for application."""

    def __init__(self):
        """Initialize CLI."""
        self.console = Console()

    def print_header(self):
        """Print application header."""
        header = """
[bold cyan]╔════════════════════════════════════════╗[/bold cyan]
[bold cyan]║     SMART MUSIC TAGGER                 ║[/bold cyan]
[bold cyan]║     AI-Powered Metadata Management     ║[/bold cyan]
[bold cyan]╚════════════════════════════════════════╝[/bold cyan]
        """
        self.console.print(header)

    def print_config_info(self, music_dir: str, file_count: int):
        """Print configuration information."""
        info = f"""
[cyan]Configuration:[/cyan]
  Music Directory: [yellow]{music_dir}[/yellow]
  Files to Process: [bold]{file_count}[/bold]
        """
        self.console.print(Panel(info, title="[bold]Settings[/bold]", expand=False))

    def print_processing_start(self, filename: str, index: int, total: int):
        """Print when processing starts."""
        self.console.print(f"\n[bold cyan][{index}/{total}] Processing:[/bold cyan]")
        self.console.print(f"  [yellow]{filename}[/yellow]")

    def print_processing_result(self, result: Dict[str, Any], new_filename: str):
        """Print processing result."""
        if result['success']:
            self.console.print(f"  [cyan]↓[/cyan]")
            self.console.print(f"  [green]{new_filename}[/green]")

            metadata = result['metadata']
            if metadata:
                self.console.print(f"\n[cyan]Metadata updated:[/cyan]")
                self.console.print(f"  [green]✓[/green] Artist: {metadata.artists[0]}")
                self.console.print(f"  [green]✓[/green] Album: {metadata.album}")
                self.console.print(f"  [green]✓[/green] Genre: {metadata.genre}")
                self.console.print(f"  [green]✓[/green] Release Year: {metadata.release_year}")
        else:
            self.console.print(f"  [red]✗ Failed[/red]")
            for error in result['errors']:
                self.console.print(f"    [red]{error}[/red]")

    def print_summary(self, total: int, successful: int, failed: int):
        """Print processing summary."""
        summary = f"""
[cyan]Processing Complete[/cyan]

Total Files:    [bold]{total}[/bold]
Successful:     [bold green]{successful}[/bold green]
Failed:         [bold red]{failed}[/bold red]
Success Rate:   [bold yellow]{(successful/total*100):.1f}%[/bold yellow]
        """
        self.console.print(Panel(summary, title="[bold]Summary[/bold]", expand=False, border_style="cyan"))

    def print_error(self, title: str, message: str):
        """Print error message."""
        self.console.print(Panel(f"[red]{message}[/red]", title=f"[bold red]{title}[/bold red]", expand=False))

    def print_warning(self, message: str):
        """Print warning message."""
        self.console.print(f"[yellow]⚠ Warning:[/yellow] {message}")

    def print_info(self, message: str):
        """Print info message."""
        self.console.print(f"[cyan]ℹ Info:[/cyan] {message}")

    def print_success(self, message: str):
        """Print success message."""
        self.console.print(f"[green]✓ Success:[/green] {message}")
