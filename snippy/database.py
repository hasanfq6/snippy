"""
Database module for snippy - handles SQLite operations for storing snippets.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from cryptography.fernet import Fernet
import base64
import hashlib


class SnippetDatabase:
    """Handles all database operations for snippets."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection."""
        if db_path is None:
            # Default to ~/.snippy/snippets.db
            home = Path.home()
            self.db_dir = home / ".snippy"
            self.db_dir.mkdir(exist_ok=True)
            self.db_path = self.db_dir / "snippets.db"
        else:
            self.db_path = Path(db_path)
            self.db_dir = self.db_path.parent
            self.db_dir.mkdir(exist_ok=True, parents=True)
        
        self.encryption_key: Optional[bytes] = None
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    language TEXT,
                    tags TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_encrypted BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            # Create indexes for better search performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_title ON snippets(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_language ON snippets(language)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tags ON snippets(tags)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON snippets(created_at)")
    
    def _get_encryption_key(self, password: str) -> bytes:
        """Generate encryption key from password."""
        # Use PBKDF2 to derive key from password
        salt = b'snippy_salt_2024'  # In production, use random salt per user
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return base64.urlsafe_b64encode(key)
    
    def enable_encryption(self, password: str) -> None:
        """Enable encryption mode with password."""
        self.encryption_key = self._get_encryption_key(password)
        
        # Store encrypted flag in config
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                ("encryption_enabled", "true")
            )
    
    def disable_encryption(self) -> None:
        """Disable encryption mode."""
        self.encryption_key = None
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                ("encryption_enabled", "false")
            )
    
    def is_encryption_enabled(self) -> bool:
        """Check if encryption is enabled."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM config WHERE key = ?",
                ("encryption_enabled",)
            )
            result = cursor.fetchone()
            return result and result[0] == "true"
    
    def authenticate(self, password: str) -> bool:
        """Authenticate with password for encrypted mode."""
        if not self.is_encryption_enabled():
            return True
        
        try:
            self.encryption_key = self._get_encryption_key(password)
            # Try to decrypt a test snippet to verify password
            snippets = self.list_snippets(limit=1)
            if snippets and snippets[0].get('is_encrypted'):
                # Try to decrypt the content
                encrypted_content = snippets[0]['content']
                fernet = Fernet(self.encryption_key)
                fernet.decrypt(encrypted_content.encode())
            return True
        except Exception:
            self.encryption_key = None
            return False
    
    def _encrypt_content(self, content: str) -> str:
        """Encrypt content if encryption is enabled."""
        if self.encryption_key is None:
            return content
        
        fernet = Fernet(self.encryption_key)
        encrypted = fernet.encrypt(content.encode())
        return encrypted.decode()
    
    def _decrypt_content(self, content: str, is_encrypted: bool) -> str:
        """Decrypt content if it's encrypted."""
        if not is_encrypted or self.encryption_key is None:
            return content
        
        try:
            fernet = Fernet(self.encryption_key)
            decrypted = fernet.decrypt(content.encode())
            return decrypted.decode()
        except Exception:
            return "[ENCRYPTED - Invalid password]"
    
    def add_snippet(
        self,
        title: str,
        content: str,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        secure: bool = False
    ) -> int:
        """Add a new snippet to the database."""
        tags_str = ",".join(tags) if tags else ""
        is_encrypted = secure and self.encryption_key is not None
        
        # Encrypt content if needed
        stored_content = self._encrypt_content(content) if is_encrypted else content
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO snippets (title, content, language, tags, description, is_encrypted)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, stored_content, language, tags_str, description, is_encrypted))
            
            return cursor.lastrowid
    
    def get_snippet(self, snippet_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific snippet by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM snippets WHERE id = ?
            """, (snippet_id,))
            
            row = cursor.fetchone()
            if row:
                snippet = dict(row)
                # Decrypt content if needed
                snippet['content'] = self._decrypt_content(
                    snippet['content'], 
                    snippet['is_encrypted']
                )
                # Parse tags
                snippet['tags'] = snippet['tags'].split(',') if snippet['tags'] else []
                return snippet
            
            return None
    
    def list_snippets(
        self,
        search_term: Optional[str] = None,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List snippets with optional filtering."""
        query = "SELECT * FROM snippets WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (title LIKE ? OR content LIKE ?)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern])
        
        if language:
            query += " AND language = ?"
            params.append(language)
        
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            snippets = []
            for row in cursor.fetchall():
                snippet = dict(row)
                # Decrypt content if needed
                snippet['content'] = self._decrypt_content(
                    snippet['content'], 
                    snippet['is_encrypted']
                )
                # Parse tags
                snippet['tags'] = snippet['tags'].split(',') if snippet['tags'] else []
                snippets.append(snippet)
            
            return snippets
    
    def update_snippet(
        self,
        snippet_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> bool:
        """Update an existing snippet."""
        # Get current snippet to preserve encryption status
        current = self.get_snippet(snippet_id)
        if not current:
            return False
        
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if content is not None:
            # Encrypt if the snippet was originally encrypted
            if current['is_encrypted']:
                content = self._encrypt_content(content)
            updates.append("content = ?")
            params.append(content)
        
        if language is not None:
            updates.append("language = ?")
            params.append(language)
        
        if tags is not None:
            updates.append("tags = ?")
            params.append(",".join(tags))
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if not updates:
            return True
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(snippet_id)
        
        query = f"UPDATE snippets SET {', '.join(updates)} WHERE id = ?"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0
    
    def delete_snippet(self, snippet_id: int) -> bool:
        """Delete a snippet."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
            return cursor.rowcount > 0
    
    def export_snippets(self, format_type: str = "json") -> str:
        """Export all snippets to JSON or Markdown format."""
        snippets = self.list_snippets()
        
        if format_type.lower() == "json":
            return json.dumps(snippets, indent=2, default=str)
        
        elif format_type.lower() == "md":
            md_content = "# Code Snippets\n\n"
            md_content += f"Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for snippet in snippets:
                md_content += f"## {snippet['title']}\n\n"
                
                if snippet['description']:
                    md_content += f"{snippet['description']}\n\n"
                
                # Metadata
                md_content += f"**Language:** {snippet['language'] or 'text'}  \n"
                md_content += f"**Tags:** {', '.join(snippet['tags']) if snippet['tags'] else 'None'}  \n"
                md_content += f"**Created:** {snippet['created_at']}  \n\n"
                
                # Code block
                lang = snippet['language'] or ''
                md_content += f"```{lang}\n{snippet['content']}\n```\n\n"
                md_content += "---\n\n"
            
            return md_content
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM snippets")
            total_snippets = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT language, COUNT(*) as count 
                FROM snippets 
                WHERE language IS NOT NULL 
                GROUP BY language 
                ORDER BY count DESC
            """)
            languages = dict(cursor.fetchall())
            
            cursor = conn.execute("""
                SELECT COUNT(*) FROM snippets WHERE is_encrypted = TRUE
            """)
            encrypted_count = cursor.fetchone()[0]
            
            return {
                "total_snippets": total_snippets,
                "languages": languages,
                "encrypted_snippets": encrypted_count,
                "encryption_enabled": self.is_encryption_enabled()
            }