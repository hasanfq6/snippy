"""
Display module for snippy - handles pretty printing and syntax highlighting.
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.columns import Columns
from rich.padding import Padding
from datetime import datetime
import textwrap


class SnippyDisplay:
    """Handles all display operations for snippy."""
    
    def __init__(self):
        self.console = Console()
    
    def print_snippet_list(self, snippets: List[Dict[str, Any]], show_content: bool = False) -> None:
        """Display a list of snippets in a table format."""
        if not snippets:
            self.console.print("[yellow]No snippets found.[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Title", style="green", min_width=20)
        table.add_column("Language", style="blue", width=10)
        table.add_column("Tags", style="yellow", width=15)
        table.add_column("Created", style="dim", width=12)
        
        if show_content:
            table.add_column("Content Preview", style="white", width=30)
        
        for snippet in snippets:
            # Format created date
            created = snippet.get('created_at', '')
            if created:
                try:
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    created = dt.strftime('%Y-%m-%d')
                except:
                    created = created[:10]  # Fallback to first 10 chars
            
            # Format tags
            tags = ', '.join(snippet.get('tags', []))[:15]
            if len(', '.join(snippet.get('tags', []))) > 15:
                tags += "..."
            
            # Prepare row data
            row_data = [
                str(snippet['id']),
                snippet['title'][:30] + ("..." if len(snippet['title']) > 30 else ""),
                snippet.get('language', 'text')[:10],
                tags,
                created
            ]
            
            if show_content:
                content_preview = snippet['content'][:50].replace('\n', ' ')
                if len(snippet['content']) > 50:
                    content_preview += "..."
                row_data.append(content_preview)
            
            table.add_row(*row_data)
        
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(snippets)} snippet(s)[/dim]")
    
    def print_snippet_detail(self, snippet: Dict[str, Any]) -> None:
        """Display a single snippet with full details and syntax highlighting."""
        if not snippet:
            self.console.print("[red]Snippet not found.[/red]")
            return
        
        # Create header with metadata
        header_text = f"[bold green]{snippet['title']}[/bold green]"
        if snippet.get('description'):
            header_text += f"\n[dim]{snippet['description']}[/dim]"
        
        # Metadata panel
        metadata_items = []
        metadata_items.append(f"[cyan]ID:[/cyan] {snippet['id']}")
        metadata_items.append(f"[cyan]Language:[/cyan] {snippet.get('language', 'text')}")
        
        if snippet.get('tags'):
            tags_str = ', '.join(snippet['tags'])
            metadata_items.append(f"[cyan]Tags:[/cyan] {tags_str}")
        
        if snippet.get('created_at'):
            metadata_items.append(f"[cyan]Created:[/cyan] {snippet['created_at']}")
        
        if snippet.get('updated_at') and snippet['updated_at'] != snippet.get('created_at'):
            metadata_items.append(f"[cyan]Updated:[/cyan] {snippet['updated_at']}")
        
        if snippet.get('is_encrypted'):
            metadata_items.append("[red]🔒 Encrypted[/red]")
        
        metadata_text = " | ".join(metadata_items)
        
        # Create syntax highlighted code
        language = snippet.get('language', 'text')
        content = snippet['content']
        
        try:
            syntax = Syntax(content, language, theme="monokai", line_numbers=True)
        except:
            # Fallback if language is not recognized
            syntax = Syntax(content, "text", theme="monokai", line_numbers=True)
        
        # Display everything
        self.console.print()
        self.console.print(Panel(header_text, style="bold"))
        self.console.print(f"[dim]{metadata_text}[/dim]")
        self.console.print()
        self.console.print(syntax)
        self.console.print()
    
    def print_search_results(self, snippets: List[Dict[str, Any]], search_term: str) -> None:
        """Display search results with highlighted search terms."""
        if not snippets:
            self.console.print(f"[yellow]No snippets found matching '[bold]{search_term}[/bold]'[/yellow]")
            return
        
        self.console.print(f"[green]Found {len(snippets)} snippet(s) matching '[bold]{search_term}[/bold]':[/green]\n")
        self.print_snippet_list(snippets, show_content=True)
    
    def print_stats(self, stats: Dict[str, Any]) -> None:
        """Display database statistics."""
        self.console.print("[bold magenta]📊 Snippy Statistics[/bold magenta]\n")
        
        # Main stats
        main_stats = Table(show_header=False, box=None)
        main_stats.add_column("Metric", style="cyan")
        main_stats.add_column("Value", style="green")
        
        main_stats.add_row("Total Snippets", str(stats['total_snippets']))
        main_stats.add_row("Encrypted Snippets", str(stats['encrypted_snippets']))
        main_stats.add_row("Encryption Enabled", "Yes" if stats['encryption_enabled'] else "No")
        
        self.console.print(main_stats)
        
        # Language breakdown
        if stats['languages']:
            self.console.print("\n[bold cyan]Languages:[/bold cyan]")
            lang_table = Table(show_header=True, header_style="bold")
            lang_table.add_column("Language", style="blue")
            lang_table.add_column("Count", style="green", justify="right")
            
            for lang, count in stats['languages'].items():
                lang_table.add_row(lang, str(count))
            
            self.console.print(lang_table)
    
    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"[green]✓ {message}[/green]")
    
    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[red]✗ {message}[/red]")
    
    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[yellow]⚠ {message}[/yellow]")
    
    def print_info(self, message: str) -> None:
        """Print an info message."""
        self.console.print(f"[blue]ℹ {message}[/blue]")
    
    def prompt_password(self, prompt: str = "Enter password: ") -> str:
        """Prompt for password input (hidden)."""
        import getpass
        return getpass.getpass(prompt)
    
    def confirm(self, message: str) -> bool:
        """Ask for user confirmation."""
        response = self.console.input(f"[yellow]{message} (y/N): [/yellow]")
        return response.lower() in ['y', 'yes']
    
    def print_export_info(self, format_type: str, output_file: Optional[str] = None) -> None:
        """Print information about export operation."""
        if output_file:
            self.print_success(f"Snippets exported to {output_file} in {format_type.upper()} format")
        else:
            self.print_info(f"Snippets exported in {format_type.upper()} format")
    
    def print_clipboard_info(self, available_methods: str) -> None:
        """Print clipboard method information."""
        self.console.print("[bold cyan]Clipboard Methods:[/bold cyan]")
        self.console.print(available_methods)
    
    def print_help_text(self, command: str) -> None:
        """Print help text for specific commands."""
        help_texts = {
            "add": """
[bold cyan]Add a new snippet:[/bold cyan]

  snippy add "Title" --lang python --tags api,json --desc "Description"

[dim]Options:[/dim]
  --lang, -l     Programming language (for syntax highlighting)
  --tags, -t     Comma-separated tags
  --desc, -d     Description
  --secure, -s   Store with encryption (requires password)

[dim]Examples:[/dim]
  snippy add "Docker cleanup" --lang bash --tags docker,cleanup
  snippy add "Python API call" --lang python --tags api,requests --secure
            """,
            
            "search": """
[bold cyan]Search snippets:[/bold cyan]

  snippy search "nginx"
  snippy search --lang python --tags api

[dim]Options:[/dim]
  --lang, -l     Filter by programming language
  --tags, -t     Filter by tags (comma-separated)
  --limit        Limit number of results

[dim]Examples:[/dim]
  snippy search "docker" --lang bash
  snippy search --tags api,json --limit 10
            """,
            
            "export": """
[bold cyan]Export snippets:[/bold cyan]

  snippy export --format md > snippets.md
  snippy export --format json > backup.json

[dim]Formats:[/dim]
  md, markdown   Export as Markdown file
  json          Export as JSON file

[dim]Examples:[/dim]
  snippy export --format md > my-snippets.md
  snippy export --format json | jq '.'
            """
        }
        
        if command in help_texts:
            self.console.print(help_texts[command])
        else:
            self.print_error(f"No help available for command: {command}")