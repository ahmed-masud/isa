# ISA Linux Setup Guide

## Overview

ISA is fully compatible with Linux systems. This guide covers Linux-specific setup and features.

## Installation

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip git zsh curl

# Fedora/RHEL
sudo dnf install -y python3 python3-pip git zsh curl

# Arch Linux
sudo pacman -S python python-pip git zsh curl
```

### Optional Dependencies

```bash
# For better markdown viewing (recommended)
# Ubuntu/Debian
sudo apt install -y bat exa

# Fedora/RHEL
sudo dnf install -y bat exa

# Arch Linux
sudo pacman -S bat exa

# Note: On Debian/Ubuntu, 'bat' may be installed as 'batcat'
# Create alias if needed:
# mkdir -p ~/.local/bin
# ln -s /usr/bin/batcat ~/.local/bin/bat
```

### Python Dependencies

```bash
cd ~/projects/isa
pip3 install --user -r requirements-vector.txt
```

## Configuration

### Shell Setup

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# ISA Configuration
export ISA_ROOT="${HOME}/projects/isa"
source "${ISA_ROOT}/isa.rc"
```

### Ollama Server Configuration

ISA can connect to Ollama running on a remote server:

```bash
# In ~/.config/isa/.isarc
export OLLAMA_HOST="http://your-server-ip:11434"
export AI_MODEL="mistral"  # or your preferred model
```

### Vector Database Configuration

```bash
# In ~/.config/isa/.isarc
export VECTOR_DB_HOST="http://your-server-ip:8000"
```

## Linux-Specific Features

### Sleep Prevention

On Linux, ISA uses `systemd-inhibit` for preventing system sleep during long operations.

#### Check if systemd-inhibit is available:

```bash
which systemd-inhibit
```

#### If not available, install systemd (usually pre-installed):

```bash
# Ubuntu/Debian
sudo apt install systemd

# Fedora/RHEL (usually pre-installed)
# systemd is part of the base system
```

#### Usage:

```bash
# Prevent sleep for 1 hour
isa-caffeinate

# Prevent sleep for custom duration (in seconds)
isa-caffeinate 7200  # 2 hours

# Run command while preventing sleep
isa-nosleep ./long-running-script.sh

# Toggle indefinite sleep prevention
isa-awake
```

### Alternative: GNOME Session Inhibit

If you're using GNOME desktop, `gnome-session-inhibit` is also supported:

```bash
# Ubuntu/Debian
sudo apt install gnome-session

# Fedora/RHEL
sudo dnf install gnome-session
```

## File Paths

ISA uses standard Linux paths:

- **Root**: `~/projects/isa/`
- **Config**: `~/.config/isa/`
- **Contexts**: `~/.config/isa/contexts/`
- **User bin**: `~/.local/bin/`

## Shell Compatibility

### Bash

ISA works with bash 4.0+. To use bash:

```bash
# Add to ~/.bashrc instead of ~/.zshrc
source "${HOME}/projects/isa/isa.rc"
```

### Zsh

ISA is optimized for zsh and includes zsh-specific completions:

```bash
# Tab completion for isa commands
isa <TAB>
computer <TAB>
```

## Differences from macOS

### Sleep Prevention

| Feature | macOS | Linux |
|---------|-------|-------|
| Command | `caffeinate` | `systemd-inhibit` or `gnome-session-inhibit` |
| Scope | Display, disk, idle, system | Idle, sleep, lid-switch |
| Available | Built-in | Requires systemd or GNOME |

### Commands

All core ISA commands work identically on both platforms:

```bash
isa help              # Same on both
isa me                # Same on both
isa learn file.md     # Same on both
isa ctx-search "query" # Same on both
computer ask "question" # Same on both
```

## Troubleshooting

### Command Not Found

```bash
# Ensure ISA is sourced
source ~/projects/isa/isa.rc

# Or restart your shell
exec $SHELL
```

### Python Module Errors

```bash
# Install with --user flag
pip3 install --user -r ~/projects/isa/requirements-vector.txt

# Or use a virtual environment
python3 -m venv ~/.config/isa/venv
source ~/.config/isa/venv/bin/activate
pip install -r ~/projects/isa/requirements-vector.txt
```

### bat Command Not Found

```bash
# Ubuntu/Debian may install as 'batcat'
type bat || type batcat

# Create symlink if needed
mkdir -p ~/.local/bin
ln -s $(which batcat) ~/.local/bin/bat
```

### Emoji Display Issues

If emojis don't display correctly:

```bash
# Install font with emoji support
# Ubuntu/Debian
sudo apt install fonts-noto-color-emoji

# Fedora/RHEL
sudo dnf install google-noto-emoji-fonts

# Arch Linux
sudo pacman -S noto-fonts-emoji
```

## Performance

ISA performs identically on Linux and macOS. The vector database and Ollama integration work the same way on both platforms.

### Recommended for Production

For production use, consider running:
- Ollama server on a Linux server with GPU
- Vector database service on the same server
- ISA client on your local workstation (macOS or Linux)

## Security

### File Permissions

Ensure proper permissions on ISA files:

```bash
# Config directory
chmod 700 ~/.config/isa

# Context files (may contain sensitive information)
chmod 600 ~/.config/isa/contexts/**/*.md
```

### Remote Connections

When connecting to remote Ollama/vector services:

```bash
# Use SSH tunneling for security
ssh -L 11434:localhost:11434 user@remote-server
ssh -L 8000:localhost:8000 user@remote-server

# Then configure ISA to use localhost
export OLLAMA_HOST="http://localhost:11434"
export VECTOR_DB_HOST="http://localhost:8000"
```

## Systemd Integration

### Auto-start Context Watcher

```bash
# Create systemd user service
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/isa-watcher.service << 'EOF'
[Unit]
Description=ISA Context Watcher
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 %h/projects/isa/tools/context_watcher.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF

# Enable and start
systemctl --user enable isa-watcher
systemctl --user start isa-watcher
```

## Desktop Integration

### Add ISA to Application Menu (Optional)

```bash
cat > ~/.local/share/applications/isa-terminal.desktop << EOF
[Desktop Entry]
Type=Application
Name=ISA Terminal
Comment=Intelligent Support Assistant
Exec=gnome-terminal -- zsh -c "source ~/projects/isa/isa.rc && isa-morning && exec zsh"
Icon=utilities-terminal
Categories=Development;Utility;
Terminal=false
EOF
```

## Next Steps

1. Complete [GETTING-STARTED.md](../GETTING-STARTED.md) for initial setup
2. Review [QUICK-START.md](../QUICK-START.md) for basic commands
3. Check [ISA-CONTEXT-COMMANDS.md](../ISA-CONTEXT-COMMANDS.md) for advanced features

## Support

For Linux-specific issues, check:
- ISA logs: `tail -f ~/.config/isa/logs/*.log`
- System journal: `journalctl --user -u isa-watcher -f`
- Debug mode: `ISA_DEBUG=1 source ~/projects/isa/isa.rc`
