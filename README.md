# vibe-dev (vdev)
**Development Context Management System**

A powerful shell-based tool for managing personal and project contexts, priorities, and development workflows across multiple machines.

---

## 🎯 What is vibe-dev?

vibe-dev (vdev) is a context management system that helps you:
- **Track priorities** across multiple projects
- **Manage contexts** for people, places, and things
- **Navigate quickly** between projects and work areas
- **Prevent interruptions** from system sleep
- **Sync seamlessly** across machines via Samba/network shares

---

## 📂 Architecture

```
~/projects/vibe-dev/          # This repository (tool code)
├── vdev.rc                   # Main shell configuration
├── load-context.sh           # Context loader script
├── tools/                    # Helper scripts
│   └── caffeinate-helper.sh
└── docs/                     # Documentation
    ├── QUICK-START.md
    ├── INSTALL.md
    ├── PREVENT-SLEEP-GUIDE.md
    └── [more docs]

~/vibe-dev/                   # User data (Samba share)
├── contexts/                 # User contexts
│   ├── people/
│   ├── places/
│   └── things/
├── resiliate-backend/        # User projects
├── resiliate-fe/
└── [other user files]
```

---

## ✨ Features

### Context Management
- **People, Places, Things**: Organize information by context type
- **Priorities Tracking**: Maintain current priorities and deadlines
- **Cross-References**: Link related contexts together
- **Search**: Find information across all contexts

### Shell Integration
- **Auto-Loading**: Loads automatically in new shells
- **Smart Aliases**: Quick access to common operations
- **Tab Completion**: Context names and commands
- **Status Notifications**: Urgent deadline alerts

### Sleep Prevention
- **macOS caffeinate**: Prevent system sleep during work
- **Toggle Mode**: Simple on/off with `vdev-awake`
- **Timed Mode**: Prevent sleep for specific duration
- **Command Wrapper**: Run commands without interruption

### Cross-Machine Sync
- **Samba Share**: User data on network share
- **No Manual Sync**: Changes visible everywhere instantly
- **Tool Updates**: Pull from git repository

---

## 🚀 Quick Start

### Installation
```bash
# Clone/setup vibe-dev tool
cd ~/projects
git clone <repo-url> vibe-dev  # Or setup as needed

# Ensure user data directory exists
mkdir -p ~/vibe-dev/contexts

# Add to shell
echo 'source ~/projects/vibe-dev/vdev.rc' >> ~/.zshrc

# Reload shell
exec zsh
```

### Basic Usage
```bash
# View your priorities
vdev me

# Check urgent items
vdev urgent

# This week's tasks
vdev week

# Morning brief
vdev-morning

# Load another context
vdev load denis-krusos
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICK-START.md](docs/QUICK-START.md) | Get started quickly |
| [INSTALL.md](docs/INSTALL.md) | Detailed installation guide |
| [PREVENT-SLEEP-GUIDE.md](docs/PREVENT-SLEEP-GUIDE.md) | Sleep prevention guide |
| [CONTEXT-MANAGEMENT.md](docs/CONTEXT-MANAGEMENT.md) | Context system docs |
| [TODO.md](docs/TODO.md) | Development tasks |
| [ROADMAP.md](docs/ROADMAP.md) | Future plans |

---

## 🎯 Key Commands

### Core Commands
| Command | Purpose |
|---------|---------|
| `vdev help` | Show help |
| `vdev me` | View your priorities |
| `vdev urgent` | Show urgent items |
| `vdev week` | This week's tasks |
| `vdev edit` | Edit priorities |
| `vdev load <name>` | Load a context |

### Aliases
| Alias | Purpose |
|-------|---------|
| `vdev-me` | Quick priorities view |
| `vdev-urgent` | Quick urgent view |
| `vdev-week` | This week's tasks |
| `vdev-morning` | Morning brief |
| `vdev-evening` | Evening review |

### Navigation
| Command | Purpose |
|---------|---------|
| `cdvdev` | Go to tool directory |
| `cdvdata` | Go to user data directory |
| `cdme` | Go to your context |
| `cdproject <name>` | Jump to project |

### Sleep Prevention
| Command | Purpose |
|---------|---------|
| `vdev-awake` | Toggle system awake on/off |
| `vdev-caffeinate <sec>` | Keep awake for duration |
| `vdev-nosleep <cmd>` | Run command without sleep |

---

## 🔧 Configuration

### Environment Variables
```bash
VDEV_ROOT        # Tool location: ~/projects/vibe-dev
VDEV_DATA        # User data: ~/vibe-dev
VDEV_CONTEXTS    # Contexts: ~/vibe-dev/contexts
VDEV_BIN         # Binary tools: ~/.local/bin
```

### Customization
Edit `vdev.rc` to customize:
- Aliases
- Functions
- Default behavior
- Startup messages

---

## 🤝 Contributing

This is a personal tool, but improvements are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 License

MIT License (or your preference)

---

## 🔗 Related Projects

- **contexts**: Context data storage
- **resiliate**: AIFS/filesystem projects
- **chatgpt-local**: ChatGPT-like frontend

---

## 👤 Author

**Ahmed Masud**
- Email: ahmed.masud@saf.ai
- LinkedIn: [ahmedmasud](https://linkedin.com/in/ahmedmasud)

---

## 📊 Project Status

- **Version**: 0.1.0 (Initial Release)
- **Status**: Active Development
- **Platform**: macOS (primary), Linux (compatible)
- **Shell**: zsh (primary), bash (compatible)

---

## 🙏 Acknowledgments

Built for personal productivity and context management across multiple projects and machines.

---

**Last Updated**: 2025-10-08  
**Location**: `~/projects/vibe-dev`  
**User Data**: `~/vibe-dev` (Samba share)
