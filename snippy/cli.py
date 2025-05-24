"""
Command-line interface for snippy.
"""

import argparse
import sys
import os
from typing import List, Optional
from pathlib import Path

from .database import SnippetDatabase
from .display import SnippyDisplay
from .clipboard import copy_to_clipboard, get_clipboard_info
from .executor import SnippetExecutor


class SnippyCLI:
    """Main CLI application class."""
    
    def __init__(self):
        self.db = SnippetDatabase()
        self.display = SnippyDisplay()
        self.executor = SnippetExecutor()
    
    def _ensure_authenticated(self) -> bool:
        """Ensure user is authenticated if encryption is enabled."""
        if not self.db.is_encryption_enabled():
            return True
        
        if self.db.encryption_key is not None:
            return True
        
        password = self.display.prompt_password("Enter encryption password: ")
        if self.db.authenticate(password):
            return True
        else:
            self.display.print_error("Invalid password")
            return False
    
    def cmd_add(self, args) -> None:
        """Add a new snippet."""
        if not self._ensure_authenticated():
            return
        
        # Get content from stdin or prompt
        if args.content:
            content = args.content
        else:
            self.display.print_info("Enter snippet content (Ctrl+D to finish):")
            try:
                content = sys.stdin.read().strip()
            except KeyboardInterrupt:
                self.display.print_warning("Cancelled")
                return
        
        if not content:
            self.display.print_error("No content provided")
            return
        
        # Parse tags
        tags = []
        if args.tags:
            tags = [tag.strip() for tag in args.tags.split(',')]
        
        # Add snippet
        try:
            snippet_id = self.db.add_snippet(
                title=args.title,
                content=content,
                language=args.lang,
                tags=tags,
                description=args.desc,
                secure=args.secure
            )
            
            self.display.print_success(f"Added snippet #{snippet_id}: {args.title}")
            
            if args.secure and not self.db.encryption_key:
                self.display.print_warning("Secure flag ignored - encryption not enabled")
        
        except Exception as e:
            self.display.print_error(f"Failed to add snippet: {e}")
    
    def cmd_list(self, args) -> None:
        """List snippets."""
        if not self._ensure_authenticated():
            return
        
        try:
            snippets = self.db.list_snippets(
                search_term=args.search,
                language=args.lang,
                tags=args.tags.split(',') if args.tags else None,
                limit=args.limit,
                offset=args.offset
            )
            
            self.display.print_snippet_list(snippets, show_content=args.verbose)
        
        except Exception as e:
            self.display.print_error(f"Failed to list snippets: {e}")
    
    def cmd_show(self, args) -> None:
        """Show a specific snippet."""
        if not self._ensure_authenticated():
            return
        
        try:
            snippet = self.db.get_snippet(args.id)
            if snippet:
                self.display.print_snippet_detail(snippet)
            else:
                self.display.print_error(f"Snippet #{args.id} not found")
        
        except Exception as e:
            self.display.print_error(f"Failed to show snippet: {e}")
    
    def cmd_search(self, args) -> None:
        """Search snippets."""
        if not self._ensure_authenticated():
            return
        
        try:
            snippets = self.db.list_snippets(
                search_term=args.query,
                language=args.lang,
                tags=args.tags.split(',') if args.tags else None,
                limit=args.limit
            )
            
            if args.query:
                self.display.print_search_results(snippets, args.query)
            else:
                self.display.print_snippet_list(snippets, show_content=True)
        
        except Exception as e:
            self.display.print_error(f"Failed to search snippets: {e}")
    
    def cmd_copy(self, args) -> None:
        """Copy snippet to clipboard."""
        if not self._ensure_authenticated():
            return
        
        try:
            snippet = self.db.get_snippet(args.id)
            if not snippet:
                self.display.print_error(f"Snippet #{args.id} not found")
                return
            
            if copy_to_clipboard(snippet['content']):
                self.display.print_success(f"Copied snippet #{args.id} to clipboard")
            else:
                self.display.print_error("Failed to copy to clipboard")
                self.display.print_info("Try installing pyperclip: pip install pyperclip")
        
        except Exception as e:
            self.display.print_error(f"Failed to copy snippet: {e}")
    
    def cmd_run(self, args) -> None:
        """Execute a snippet."""
        if not self._ensure_authenticated():
            return
        
        try:
            snippet = self.db.get_snippet(args.id)
            if not snippet:
                self.display.print_error(f"Snippet #{args.id} not found")
                return
            
            language = snippet.get('language', '')
            
            if not self.executor.can_execute(language):
                self.display.print_error(f"Cannot execute {language} snippets")
                return
            
            # Safety check
            is_safe, warning = self.executor.validate_snippet_safety(
                snippet['content'], language
            )
            
            if not is_safe:
                self.display.print_warning(f"Safety warning: {warning}")
                if not self.display.confirm("Continue execution?"):
                    return
            
            # Show snippet before execution
            if not args.quiet:
                self.display.print_info(f"Executing snippet #{args.id}: {snippet['title']}")
                self.display.print_snippet_detail(snippet)
                
                if not args.force and not self.display.confirm("Execute this snippet?"):
                    return
            
            # Execute
            success, stdout, stderr = self.executor.execute_snippet(
                snippet, 
                working_dir=args.workdir,
                timeout=args.timeout
            )
            
            if stdout:
                self.display.console.print("[green]Output:[/green]")
                self.display.console.print(stdout)
            
            if stderr:
                self.display.console.print("[red]Errors:[/red]")
                self.display.console.print(stderr)
            
            if success:
                self.display.print_success("Execution completed successfully")
            else:
                self.display.print_error("Execution failed")
        
        except Exception as e:
            self.display.print_error(f"Failed to execute snippet: {e}")
    
    def cmd_delete(self, args) -> None:
        """Delete a snippet."""
        if not self._ensure_authenticated():
            return
        
        try:
            snippet = self.db.get_snippet(args.id)
            if not snippet:
                self.display.print_error(f"Snippet #{args.id} not found")
                return
            
            if not args.force:
                self.display.print_info(f"Snippet to delete: {snippet['title']}")
                if not self.display.confirm("Are you sure you want to delete this snippet?"):
                    return
            
            if self.db.delete_snippet(args.id):
                self.display.print_success(f"Deleted snippet #{args.id}")
            else:
                self.display.print_error("Failed to delete snippet")
        
        except Exception as e:
            self.display.print_error(f"Failed to delete snippet: {e}")
    
    def cmd_export(self, args) -> None:
        """Export snippets."""
        if not self._ensure_authenticated():
            return
        
        try:
            export_data = self.db.export_snippets(args.format)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(export_data)
                self.display.print_export_info(args.format, args.output)
            else:
                print(export_data)
                self.display.print_export_info(args.format)
        
        except Exception as e:
            self.display.print_error(f"Failed to export snippets: {e}")
    
    def cmd_stats(self, args) -> None:
        """Show database statistics."""
        if not self._ensure_authenticated():
            return
        
        try:
            stats = self.db.get_stats()
            self.display.print_stats(stats)
        
        except Exception as e:
            self.display.print_error(f"Failed to get statistics: {e}")
    
    def cmd_secure_on(self, args) -> None:
        """Enable encryption."""
        if self.db.is_encryption_enabled():
            self.display.print_warning("Encryption is already enabled")
            return
        
        password = self.display.prompt_password("Enter new encryption password: ")
        confirm_password = self.display.prompt_password("Confirm password: ")
        
        if password != confirm_password:
            self.display.print_error("Passwords do not match")
            return
        
        if len(password) < 8:
            self.display.print_error("Password must be at least 8 characters long")
            return
        
        try:
            self.db.enable_encryption(password)
            self.display.print_success("Encryption enabled")
            self.display.print_warning("Existing snippets are NOT encrypted. Use --secure flag for new snippets.")
        
        except Exception as e:
            self.display.print_error(f"Failed to enable encryption: {e}")
    
    def cmd_secure_off(self, args) -> None:
        """Disable encryption."""
        if not self.db.is_encryption_enabled():
            self.display.print_warning("Encryption is not enabled")
            return
        
        if not self._ensure_authenticated():
            return
        
        if not self.display.confirm("Disable encryption? Encrypted snippets will become inaccessible."):
            return
        
        try:
            self.db.disable_encryption()
            self.display.print_success("Encryption disabled")
            self.display.print_warning("Encrypted snippets are now inaccessible")
        
        except Exception as e:
            self.display.print_error(f"Failed to disable encryption: {e}")
    
    def cmd_info(self, args) -> None:
        """Show system information."""
        self.display.console.print("[bold cyan]📋 Snippy System Information[/bold cyan]\n")
        
        # Database info
        self.display.console.print(f"[cyan]Database:[/cyan] {self.db.db_path}")
        self.display.console.print(f"[cyan]Encryption:[/cyan] {'Enabled' if self.db.is_encryption_enabled() else 'Disabled'}")
        
        # Clipboard info
        self.display.console.print("\n[cyan]Clipboard Support:[/cyan]")
        clipboard_info = get_clipboard_info()
        self.display.console.print(clipboard_info)
        
        # Execution support
        self.display.console.print("\n[cyan]Execution Support:[/cyan]")
        exec_info = self.executor.get_execution_info()
        for interpreter, available in exec_info.items():
            status = "✓" if available else "✗"
            self.display.console.print(f"{status} {interpreter}")
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            prog='snippy',
            description='Store, search, and summon code snippets right from your terminal.',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  snippy add "Restart nginx" --lang bash --tags web,server
  snippy list --lang python
  snippy search "docker" --tags devops
  snippy show 5
  snippy copy 3
  snippy export --format md > snippets.md
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Add command
        add_parser = subparsers.add_parser('add', help='Add a new snippet')
        add_parser.add_argument('title', help='Snippet title')
        add_parser.add_argument('content', nargs='?', help='Snippet content (or read from stdin)')
        add_parser.add_argument('--lang', '-l', help='Programming language')
        add_parser.add_argument('--tags', '-t', help='Comma-separated tags')
        add_parser.add_argument('--desc', '-d', help='Description')
        add_parser.add_argument('--secure', '-s', action='store_true', help='Store with encryption')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List snippets')
        list_parser.add_argument('--search', help='Search term')
        list_parser.add_argument('--lang', '-l', help='Filter by language')
        list_parser.add_argument('--tags', '-t', help='Filter by tags (comma-separated)')
        list_parser.add_argument('--limit', type=int, default=50, help='Limit results')
        list_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
        list_parser.add_argument('--verbose', '-v', action='store_true', help='Show content preview')
        
        # Show command
        show_parser = subparsers.add_parser('show', help='Show a specific snippet')
        show_parser.add_argument('id', type=int, help='Snippet ID')
        
        # Search command
        search_parser = subparsers.add_parser('search', help='Search snippets')
        search_parser.add_argument('query', nargs='?', help='Search query (optional)')
        search_parser.add_argument('--lang', '-l', help='Filter by language')
        search_parser.add_argument('--tags', '-t', help='Filter by tags (comma-separated)')
        search_parser.add_argument('--limit', type=int, default=20, help='Limit results')
        
        # Copy command
        copy_parser = subparsers.add_parser('copy', help='Copy snippet to clipboard')
        copy_parser.add_argument('id', type=int, help='Snippet ID')
        
        # Run command
        run_parser = subparsers.add_parser('run', help='Execute a snippet')
        run_parser.add_argument('id', type=int, help='Snippet ID')
        run_parser.add_argument('--workdir', help='Working directory for execution')
        run_parser.add_argument('--timeout', type=int, default=30, help='Execution timeout in seconds')
        run_parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation')
        run_parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
        
        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete a snippet')
        delete_parser.add_argument('id', type=int, help='Snippet ID')
        delete_parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation')
        
        # Export command
        export_parser = subparsers.add_parser('export', help='Export snippets')
        export_parser.add_argument('--format', choices=['json', 'md', 'markdown'], default='json', help='Export format')
        export_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
        
        # Stats command
        subparsers.add_parser('stats', help='Show database statistics')
        
        # Security commands
        subparsers.add_parser('secure-on', help='Enable encryption')
        subparsers.add_parser('secure-off', help='Disable encryption')
        
        # Info command
        subparsers.add_parser('info', help='Show system information')
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> None:
        """Run the CLI application."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return
        
        # Map commands to methods
        command_map = {
            'add': self.cmd_add,
            'list': self.cmd_list,
            'show': self.cmd_show,
            'search': self.cmd_search,
            'copy': self.cmd_copy,
            'run': self.cmd_run,
            'delete': self.cmd_delete,
            'export': self.cmd_export,
            'stats': self.cmd_stats,
            'secure-on': self.cmd_secure_on,
            'secure-off': self.cmd_secure_off,
            'info': self.cmd_info,
        }
        
        command_func = command_map.get(parsed_args.command)
        if command_func:
            try:
                command_func(parsed_args)
            except KeyboardInterrupt:
                self.display.print_warning("Operation cancelled")
            except Exception as e:
                self.display.print_error(f"Unexpected error: {e}")
                if os.getenv('SNIPPY_DEBUG'):
                    raise
        else:
            self.display.print_error(f"Unknown command: {parsed_args.command}")


def main() -> None:
    """Main entry point."""
    cli = SnippyCLI()
    cli.run()


if __name__ == '__main__':
    main()