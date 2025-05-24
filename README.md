# snippy

**Store, search, and summon code snippets right from your terminal.**

A powerful command-line code snippet manager built for developers, sysadmins, and terminal enthusiasts. Save your frequently used commands, scripts, and code blocks with rich metadata and retrieve them instantly.

## ✨ Features

- 📝 **Rich Snippet Storage** - Store code with title, language, tags, and descriptions
- 🔍 **Powerful Search** - Full-text search with language and tag filtering
- 🎨 **Syntax Highlighting** - Beautiful code display with Pygments
- 📋 **Clipboard Integration** - Copy snippets instantly to clipboard
- ⚡ **Safe Execution** - Run snippets with built-in safety checks
- 📤 **Export/Import** - Export to Markdown or JSON for backup and sharing
- 🔒 **Encryption** - Optional AES-256 encryption for sensitive snippets
- 🎯 **Beautiful UI** - Rich terminal interface with tables and panels
- 🚀 **Cross-Platform** - Works on Linux, macOS, Windows, and Termux

## 🚀 Quick Start

### Installation

```bash
# Clone and install
git clone <repository-url>
cd snippy
pip install -e .
```

### Basic Usage

```bash
# Add your first snippet
snippy add "Restart nginx safely" "sudo systemctl reload nginx" --lang bash --tags web,server

# List all snippets
snippy list

# Search for specific snippets
snippy search "nginx"
snippy search --lang python --tags api

# Show a snippet with syntax highlighting
snippy show 1

# Copy snippet to clipboard
snippy copy 1

# Execute a snippet (with confirmation)
snippy run 1

# Export your snippets
snippy export --format md > my-snippets.md
```

## 📚 Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Add a new snippet | `snippy add "Title" "code" --lang python --tags api,json` |
| `list` | List all snippets | `snippy list` |
| `show` | Display specific snippet | `snippy show 5` |
| `search` | Search and filter | `snippy search "docker" --lang bash --tags devops` |
| `copy` | Copy to clipboard | `snippy copy 3` |
| `run` | Execute snippet | `snippy run 2 --force` |
| `delete` | Remove snippet | `snippy delete 4` |
| `export` | Export snippets | `snippy export --format json > backup.json` |
| `stats` | Show statistics | `snippy stats` |
| `secure-on` | Enable encryption | `snippy secure-on` |
| `secure-off` | Disable encryption | `snippy secure-off` |
| `info` | System information | `snippy info` |

## 🎯 Use Cases

### For Developers
```bash
# Save API request templates
snippy add "POST request" "curl -X POST -H 'Content-Type: application/json' -d '{}' URL" --lang bash --tags api,curl

# Store Python utilities
snippy add "JSON pretty print" "python3 -m json.tool" --lang python --tags json,format

# Git commands
snippy add "Git log oneline" "git log --oneline --graph --decorate" --lang bash --tags git
```

### For System Administrators
```bash
# System monitoring
snippy add "Memory usage" "free -h && ps aux --sort=-%mem | head" --lang bash --tags system,memory

# Docker management
snippy add "Docker cleanup" "docker system prune -af && docker volume prune -f" --lang bash --tags docker,cleanup

# Log analysis
snippy add "Tail logs" "tail -f /var/log/nginx/error.log" --lang bash --tags logs,nginx
```

### For DevOps Engineers
```bash
# Kubernetes commands
snippy add "Get pods" "kubectl get pods --all-namespaces" --lang bash --tags k8s,pods

# AWS CLI
snippy add "List S3 buckets" "aws s3 ls" --lang bash --tags aws,s3

# Terraform
snippy add "Plan and apply" "terraform plan && terraform apply" --lang bash --tags terraform
```

## 🔒 Security Features

Enable encryption for sensitive snippets:

```bash
# Enable encryption (will prompt for password)
snippy secure-on

# Add encrypted snippet
snippy add "API Key" "export API_KEY=secret123" --lang bash --secure

# Disable encryption
snippy secure-off
```

## 📤 Export & Backup

```bash
# Export to Markdown
snippy export --format md > my-snippets.md

# Export to JSON for backup
snippy export --format json > backup.json

# View statistics
snippy stats
```

## 🛠️ Technical Details

- **Language**: Python 3.10+
- **Database**: SQLite with optional encryption
- **UI**: Rich library for beautiful terminal output
- **Syntax Highlighting**: Pygments
- **Encryption**: AES-256 via cryptography library
- **Clipboard**: Multi-platform support (pyperclip, termux-clipboard, xclip)

## 📁 File Structure

```
~/.snippy/
├── snippets.db          # SQLite database
├── config.json          # Configuration
└── encryption.key       # Encryption key (if enabled)
```

## 🎉 Why snippy?

- **Terminal-Native**: Built for developers who live in the terminal
- **Portable**: Works everywhere - desktop, server, mobile (Termux)
- **Productive**: Stop retyping the same commands
- **Secure**: Optional encryption for sensitive data
- **Extensible**: Easy to extend and customize
- **Beautiful**: Rich UI makes terminal work enjoyable

---

*Made with ❤️ for terminal enthusiasts*