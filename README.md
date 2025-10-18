# ISA - Intelligent Support Assistant
**AI-Powered Context-Aware Shell Assistant**

A powerful shell-based assistant that combines priority management, semantic search, and natural language AI to help you stay focused and productive.

🍎 **macOS** | 🐧 **Linux** | 💙 **zsh/bash**

---

## 🎯 What is ISA?

ISA (Intelligent Support Assistant) is your AI-powered command-line assistant that helps you:
- **Manage priorities** across multiple projects with markdown-based contexts
- **Talk naturally** to your computer with imperative and conversational commands
- **Search semantically** through your knowledge base using vector embeddings
- **Get AI insights** with Ollama integration for intelligent suggestions
- **Learn and unlearn** by adding files or notes to your contexts
- **Track command history** for contextual operations (repeat, stop, etc.)

**Latest:** `learn` and `unlearn` commands for dynamic context management!

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
- **Cross-platform**: Works on macOS (`caffeinate`) and Linux (`systemd-inhibit`)
- **Toggle Mode**: Simple on/off with `isa-awake`
- **Timed Mode**: Prevent sleep for specific duration
- **Command Wrapper**: Run commands without interruption

### Cross-Machine Sync
- **Samba Share**: User data on network share
- **No Manual Sync**: Changes visible everywhere instantly
- **Tool Updates**: Pull from git repository

---

## 🚀 Quick Start

**New to ISA?** Start here: **[GETTING-STARTED.md](GETTING-STARTED.md)** 🎓

### Installation
```bash
# Add to your shell configuration
echo 'source ~/projects/isa/isa.rc' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Verify installation
isa help
```

### Basic Usage
```bash
# Traditional style
isa me                          # View your priorities
isa urgent                      # Check urgent items
isa week                        # This week's tasks

# Natural language (NEW!)
computer show stats             # Show vector database stats
computer are the services healthy   # Health check
computer find deployment        # Semantic search
computer sync                   # Sync contexts

# AI features
computer ask "What should I work on?"   # Get AI suggestions
isa ai-analyze urgent           # AI analysis of urgent items
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[GETTING-STARTED.md](GETTING-STARTED.md)** | **Complete beginner's guide** 🎓 |
| **[docs/LINUX-SETUP.md](docs/LINUX-SETUP.md)** | **Linux-specific setup guide** 🐧 |
| [ISA-CONTEXT-COMMANDS.md](ISA-CONTEXT-COMMANDS.md) | Comprehensive command reference |
| [GIT-FLOW-SETUP.md](GIT-FLOW-SETUP.md) | Git workflow documentation |
| [ISA-SEMANTIC-SETUP.md](ISA-SEMANTIC-SETUP.md) | Semantic context setup guide |
| [VECTOR-DATABASE-DESIGN.md](VECTOR-DATABASE-DESIGN.md) | Architecture documentation |

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
