"""
Executor module for snippy - handles running code snippets safely.
"""

import subprocess
import tempfile
import os
import sys
from typing import Dict, Any, Optional, Tuple
from pathlib import Path


class SnippetExecutor:
    """Handles execution of code snippets."""
    
    def __init__(self):
        self.safe_languages = {
            'bash', 'sh', 'zsh', 'fish',
            'python', 'python3', 'py',
            'node', 'javascript', 'js',
            'ruby', 'rb',
            'perl', 'pl'
        }
    
    def can_execute(self, language: str) -> bool:
        """Check if a language can be executed safely."""
        return language.lower() in self.safe_languages
    
    def get_interpreter(self, language: str) -> Optional[str]:
        """Get the appropriate interpreter for a language."""
        lang = language.lower()
        
        interpreters = {
            'bash': 'bash',
            'sh': 'sh',
            'zsh': 'zsh',
            'fish': 'fish',
            'python': 'python3',
            'python3': 'python3',
            'py': 'python3',
            'node': 'node',
            'javascript': 'node',
            'js': 'node',
            'ruby': 'ruby',
            'rb': 'ruby',
            'perl': 'perl',
            'pl': 'perl'
        }
        
        return interpreters.get(lang)
    
    def check_interpreter_available(self, interpreter: str) -> bool:
        """Check if an interpreter is available on the system."""
        try:
            result = subprocess.run(
                [interpreter, '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def execute_snippet(
        self, 
        snippet: Dict[str, Any], 
        working_dir: Optional[str] = None,
        timeout: int = 30
    ) -> Tuple[bool, str, str]:
        """
        Execute a code snippet safely.
        
        Returns:
            Tuple of (success, stdout, stderr)
        """
        language = snippet.get('language', '').lower()
        content = snippet['content']
        
        if not self.can_execute(language):
            return False, "", f"Cannot execute {language} snippets"
        
        interpreter = self.get_interpreter(language)
        if not interpreter:
            return False, "", f"No interpreter found for {language}"
        
        if not self.check_interpreter_available(interpreter):
            return False, "", f"Interpreter '{interpreter}' not available on system"
        
        # Create temporary file for the snippet
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=self._get_file_extension(language),
                delete=False
            ) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Set working directory
            if working_dir is None:
                working_dir = os.getcwd()
            
            # Execute the snippet
            if language in ['bash', 'sh', 'zsh', 'fish']:
                # For shell scripts, execute directly
                cmd = [interpreter, temp_file_path]
            else:
                # For other languages, pass the file to the interpreter
                cmd = [interpreter, temp_file_path]
            
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return (
                result.returncode == 0,
                result.stdout,
                result.stderr
            )
            
        except subprocess.TimeoutExpired:
            return False, "", f"Execution timed out after {timeout} seconds"
        except Exception as e:
            return False, "", f"Execution error: {str(e)}"
        finally:
            # Clean up temporary file
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
            except:
                pass
    
    def _get_file_extension(self, language: str) -> str:
        """Get appropriate file extension for a language."""
        extensions = {
            'bash': '.sh',
            'sh': '.sh',
            'zsh': '.zsh',
            'fish': '.fish',
            'python': '.py',
            'python3': '.py',
            'py': '.py',
            'javascript': '.js',
            'js': '.js',
            'node': '.js',
            'ruby': '.rb',
            'rb': '.rb',
            'perl': '.pl',
            'pl': '.pl'
        }
        
        return extensions.get(language.lower(), '.txt')
    
    def get_execution_info(self) -> Dict[str, bool]:
        """Get information about available interpreters."""
        info = {}
        
        interpreters_to_check = {
            'bash': 'bash',
            'python': 'python3',
            'node': 'node',
            'ruby': 'ruby',
            'perl': 'perl'
        }
        
        for name, interpreter in interpreters_to_check.items():
            info[name] = self.check_interpreter_available(interpreter)
        
        return info
    
    def validate_snippet_safety(self, content: str, language: str) -> Tuple[bool, str]:
        """
        Validate if a snippet is safe to execute.
        
        Returns:
            Tuple of (is_safe, warning_message)
        """
        dangerous_patterns = {
            'bash': [
                'rm -rf', 'rm -r /', '> /dev/', 'dd if=', 'mkfs',
                'fdisk', 'parted', 'format', 'del /s', 'rmdir /s',
                'shutdown', 'reboot', 'halt', 'init 0', 'init 6',
                'curl | sh', 'wget | sh', 'curl | bash', 'wget | bash'
            ],
            'python': [
                'os.system', 'subprocess.call', 'exec(', 'eval(',
                '__import__', 'open(', 'file(', 'input(', 'raw_input('
            ],
            'javascript': [
                'require(', 'process.exit', 'child_process', 'fs.unlink',
                'fs.rmdir', 'fs.writeFile'
            ]
        }
        
        lang_patterns = dangerous_patterns.get(language.lower(), [])
        
        for pattern in lang_patterns:
            if pattern in content.lower():
                return False, f"Potentially dangerous pattern detected: {pattern}"
        
        # Check for very long lines (potential obfuscation)
        lines = content.split('\n')
        for line in lines:
            if len(line) > 1000:
                return False, "Very long line detected (potential obfuscation)"
        
        return True, ""