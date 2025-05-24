"""
Basic tests for snippy functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path

from snippy.database import SnippetDatabase
from snippy.display import SnippyDisplay
from snippy.clipboard import copy_to_clipboard
from snippy.executor import SnippetExecutor


class TestSnippetDatabase:
    """Test the SnippetDatabase class."""
    
    def setup_method(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = SnippetDatabase(self.db_path)
    
    def teardown_method(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_add_snippet(self):
        """Test adding a snippet."""
        snippet_id = self.db.add_snippet(
            title="Test Snippet",
            content="echo 'hello world'",
            language="bash",
            tags=["test", "example"],
            description="A test snippet"
        )
        
        assert snippet_id == 1
        
        # Retrieve the snippet
        snippet = self.db.get_snippet(snippet_id)
        assert snippet is not None
        assert snippet['title'] == "Test Snippet"
        assert snippet['content'] == "echo 'hello world'"
        assert snippet['language'] == "bash"
        assert snippet['tags'] == ["test", "example"]
        assert snippet['description'] == "A test snippet"
    
    def test_list_snippets(self):
        """Test listing snippets."""
        # Add multiple snippets
        self.db.add_snippet("Snippet 1", "content 1", "bash", ["tag1"])
        self.db.add_snippet("Snippet 2", "content 2", "python", ["tag2"])
        self.db.add_snippet("Snippet 3", "content 3", "bash", ["tag1", "tag3"])
        
        # List all snippets
        snippets = self.db.list_snippets()
        assert len(snippets) == 3
        
        # Filter by language
        bash_snippets = self.db.list_snippets(language="bash")
        assert len(bash_snippets) == 2
        
        # Filter by tags
        tag1_snippets = self.db.list_snippets(tags=["tag1"])
        assert len(tag1_snippets) == 2
        
        # Search by content
        search_snippets = self.db.list_snippets(search_term="content 2")
        assert len(search_snippets) == 1
        assert search_snippets[0]['title'] == "Snippet 2"
    
    def test_update_snippet(self):
        """Test updating a snippet."""
        snippet_id = self.db.add_snippet("Original", "original content", "bash")
        
        # Update the snippet
        success = self.db.update_snippet(
            snippet_id,
            title="Updated",
            content="updated content",
            language="python"
        )
        assert success
        
        # Verify the update
        snippet = self.db.get_snippet(snippet_id)
        assert snippet['title'] == "Updated"
        assert snippet['content'] == "updated content"
        assert snippet['language'] == "python"
    
    def test_delete_snippet(self):
        """Test deleting a snippet."""
        snippet_id = self.db.add_snippet("To Delete", "content", "bash")
        
        # Verify it exists
        assert self.db.get_snippet(snippet_id) is not None
        
        # Delete it
        success = self.db.delete_snippet(snippet_id)
        assert success
        
        # Verify it's gone
        assert self.db.get_snippet(snippet_id) is None
    
    def test_export_json(self):
        """Test JSON export."""
        self.db.add_snippet("Test", "echo test", "bash", ["export"])
        
        export_data = self.db.export_snippets("json")
        assert "Test" in export_data
        assert "echo test" in export_data
        assert "bash" in export_data
    
    def test_export_markdown(self):
        """Test Markdown export."""
        self.db.add_snippet("Test", "echo test", "bash", ["export"])
        
        export_data = self.db.export_snippets("md")
        assert "# Code Snippets" in export_data
        assert "## Test" in export_data
        assert "```bash" in export_data
        assert "echo test" in export_data


class TestSnippetExecutor:
    """Test the SnippetExecutor class."""
    
    def setup_method(self):
        """Set up test executor."""
        self.executor = SnippetExecutor()
    
    def test_can_execute(self):
        """Test language execution support."""
        assert self.executor.can_execute("bash")
        assert self.executor.can_execute("python")
        assert not self.executor.can_execute("unknown")
    
    def test_get_interpreter(self):
        """Test interpreter detection."""
        assert self.executor.get_interpreter("bash") == "bash"
        assert self.executor.get_interpreter("python") == "python3"
        assert self.executor.get_interpreter("unknown") is None
    
    def test_validate_snippet_safety(self):
        """Test snippet safety validation."""
        # Safe snippet
        safe, msg = self.executor.validate_snippet_safety("echo hello", "bash")
        assert safe
        
        # Dangerous snippet
        unsafe, msg = self.executor.validate_snippet_safety("rm -rf /", "bash")
        assert not unsafe
        assert "rm -rf" in msg
    
    def test_execute_simple_bash(self):
        """Test executing a simple bash command."""
        snippet = {
            "content": "echo 'test output'",
            "language": "bash"
        }
        
        success, stdout, stderr = self.executor.execute_snippet(snippet)
        assert success
        assert "test output" in stdout
        assert stderr == ""
    
    def test_execute_python(self):
        """Test executing a Python snippet."""
        snippet = {
            "content": "print('hello from python')",
            "language": "python"
        }
        
        success, stdout, stderr = self.executor.execute_snippet(snippet)
        assert success
        assert "hello from python" in stdout


class TestDisplay:
    """Test the SnippyDisplay class."""
    
    def setup_method(self):
        """Set up test display."""
        self.display = SnippyDisplay()
    
    def test_display_creation(self):
        """Test that display can be created."""
        assert self.display.console is not None


if __name__ == "__main__":
    pytest.main([__file__])