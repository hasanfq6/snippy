"""
Clipboard module for snippy - handles copying snippets to clipboard.
"""

import subprocess
import sys
from typing import Optional


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard using the best available method.
    
    Returns True if successful, False otherwise.
    """
    # Try pyperclip first (cross-platform)
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        pass
    except Exception:
        # pyperclip might fail in some environments
        pass
    
    # Try termux-clipboard-set (for Termux on Android)
    try:
        result = subprocess.run(
            ["termux-clipboard-set"],
            input=text,
            text=True,
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    # Try xclip (Linux with X11)
    try:
        result = subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text,
            text=True,
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    # Try xsel (Linux with X11, alternative)
    try:
        result = subprocess.run(
            ["xsel", "--clipboard", "--input"],
            input=text,
            text=True,
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    # Try pbcopy (macOS)
    try:
        result = subprocess.run(
            ["pbcopy"],
            input=text,
            text=True,
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    # Try Windows clip command
    try:
        result = subprocess.run(
            ["clip"],
            input=text,
            text=True,
            capture_output=True,
            timeout=5,
            shell=True
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    return False


def get_clipboard_info() -> str:
    """Get information about available clipboard methods."""
    methods = []
    
    # Check pyperclip
    try:
        import pyperclip
        methods.append("✓ pyperclip (cross-platform)")
    except ImportError:
        methods.append("✗ pyperclip (not installed)")
    
    # Check termux-clipboard-set
    try:
        subprocess.run(["termux-clipboard-set", "--help"], 
                      capture_output=True, timeout=2)
        methods.append("✓ termux-clipboard-set (Termux)")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        methods.append("✗ termux-clipboard-set (not available)")
    
    # Check xclip
    try:
        subprocess.run(["xclip", "-version"], 
                      capture_output=True, timeout=2)
        methods.append("✓ xclip (Linux X11)")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        methods.append("✗ xclip (not available)")
    
    # Check xsel
    try:
        subprocess.run(["xsel", "--version"], 
                      capture_output=True, timeout=2)
        methods.append("✓ xsel (Linux X11)")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        methods.append("✗ xsel (not available)")
    
    # Check pbcopy (macOS)
    if sys.platform == "darwin":
        try:
            subprocess.run(["pbcopy"], 
                          input="", text=True, capture_output=True, timeout=2)
            methods.append("✓ pbcopy (macOS)")
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            methods.append("✗ pbcopy (not available)")
    
    # Check Windows clip
    if sys.platform == "win32":
        try:
            subprocess.run(["clip"], 
                          input="", text=True, capture_output=True, timeout=2, shell=True)
            methods.append("✓ clip (Windows)")
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            methods.append("✗ clip (not available)")
    
    return "\n".join(methods)