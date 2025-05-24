# Snippy Examples

Here are some example snippets to get you started with snippy:

## Basic Usage

```bash
# Add a simple bash command
snippy add "Check disk usage" "df -h" --lang bash --tags system,disk

# Add a Python function
snippy add "Read JSON file" --lang python --tags python,json << 'EOF'
import json

def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)
EOF

# List all snippets
snippy list

# Search for specific snippets
snippy search "json"
snippy search --lang python
snippy search --tags system

# Show a specific snippet with syntax highlighting
snippy show 1

# Copy snippet to clipboard
snippy copy 1

# Execute a bash snippet
snippy run 1
```

## Advanced Examples

### Docker Commands
```bash
snippy add "Docker logs" "docker logs -f --tail 100" --lang bash --tags docker,logs
snippy add "Docker cleanup" "docker system prune -af" --lang bash --tags docker,cleanup
snippy add "Docker build" "docker build -t myapp:latest ." --lang bash --tags docker,build
```

### Python Utilities
```bash
snippy add "HTTP Server" "python3 -m http.server 8000" --lang python --tags server,http
snippy add "JSON Pretty Print" "python3 -m json.tool" --lang python --tags json,format
```

### Git Commands
```bash
snippy add "Git status" "git status --porcelain" --lang bash --tags git,status
snippy add "Git log oneline" "git log --oneline --graph --decorate" --lang bash --tags git,log
```

### System Administration
```bash
snippy add "Find large files" "find . -type f -size +100M -exec ls -lh {} \;" --lang bash --tags system,files
snippy add "Memory usage" "free -h && ps aux --sort=-%mem | head" --lang bash --tags system,memory
```

## Export and Backup

```bash
# Export all snippets to Markdown
snippy export --format md > my-snippets.md

# Export to JSON for backup
snippy export --format json > backup.json

# View statistics
snippy stats
```

## Security Features

```bash
# Enable encryption
snippy secure-on

# Add encrypted snippet
snippy add "API Key" "export API_KEY=secret123" --lang bash --secure

# Disable encryption
snippy secure-off
```