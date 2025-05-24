#!/usr/bin/env python3
"""
Snippy Demo Script

This script demonstrates all the features of snippy.
"""

import subprocess
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def run_command(cmd, description=""):
    """Run a command and display the output."""
    if description:
        console.print(f"\n[bold blue]→ {description}[/bold blue]")
        console.print(f"[dim]$ {cmd}[/dim]")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        console.print(result.stdout.rstrip())
    if result.stderr:
        console.print(f"[red]{result.stderr.rstrip()}[/red]")
    
    time.sleep(1)
    return result.returncode == 0

def main():
    """Run the demo."""
    console.print(Panel.fit(
        Text("Snippy Demo", style="bold magenta", justify="center"),
        title="Welcome to",
        border_style="magenta"
    ))
    
    console.print("\n[bold green]Let's explore snippy's features![/bold green]\n")
    
    # Show help
    run_command("snippy --help", "Show help")
    
    # Show current stats
    run_command("snippy stats", "Show current statistics")
    
    # List existing snippets
    run_command("snippy list", "List all snippets")
    
    # Add some new snippets
    console.print("\n[bold yellow]Adding some useful snippets...[/bold yellow]")
    
    run_command(
        'snippy add "Find large files" "find . -type f -size +100M -exec ls -lh {} \\;" --lang bash --tags system,files',
        "Add a system administration snippet"
    )
    
    run_command(
        'snippy add "Git status short" "git status --porcelain" --lang bash --tags git,status',
        "Add a git command"
    )
    
    run_command(
        '''snippy add "JSON pretty print" "import json; print(json.dumps(data, indent=2))" --lang python --tags json,format''',
        "Add a Python utility"
    )
    
    # Search functionality
    console.print("\n[bold yellow]Testing search functionality...[/bold yellow]")
    
    run_command("snippy search git", "Search for 'git' snippets")
    run_command("snippy search --lang python", "Filter by Python language")
    run_command("snippy search --tags system", "Filter by 'system' tag")
    
    # Show specific snippet
    run_command("snippy show 1", "Show snippet #1 with syntax highlighting")
    
    # Export functionality
    console.print("\n[bold yellow]Testing export functionality...[/bold yellow]")
    
    run_command("snippy export --format json | head -10", "Export to JSON (first 10 lines)")
    run_command("snippy export --format md | head -15", "Export to Markdown (first 15 lines)")
    
    # Execute a safe snippet
    console.print("\n[bold yellow]Testing execution functionality...[/bold yellow]")
    
    # Add a safe executable snippet
    run_command(
        'snippy add "Show date" "date" --lang bash --tags time,system',
        "Add a safe executable snippet"
    )
    
    # Execute it
    run_command("echo 'y' | snippy run $(snippy list | grep 'Show date' | cut -d' ' -f1) --force", 
                "Execute the date command")
    
    # Final stats
    run_command("snippy stats", "Final statistics")
    
    console.print("\n[bold green]Demo completed! 🎉[/bold green]")
    console.print("\n[dim]Try these commands yourself:[/dim]")
    console.print("  [cyan]snippy add 'My snippet' 'echo hello' --lang bash[/cyan]")
    console.print("  [cyan]snippy search hello[/cyan]")
    console.print("  [cyan]snippy copy 1[/cyan]")
    console.print("  [cyan]snippy export --format md > my-snippets.md[/cyan]")

if __name__ == "__main__":
    main()