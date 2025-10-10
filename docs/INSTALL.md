# vdev Installation Guide
**Last Updated**: 2025-10-08

---

## ✅ Installation Complete!

The vdev system has been successfully installed and configured on your macOS workstation.

---

## 📦 What Was Installed

### 1. **Core Files**
- **vdev.rc** - Shell configuration with all aliases and functions
  - Location: `~/dev-notes/vibe-dev/vdev.rc`
  - Loaded automatically via `~/.zshrc`

### 2. **Tools & Scripts**
- **load-context.sh** - Context loader script
  - Location: `~/dev-notes/vibe-dev/load-context.sh`
  - Symlinked to: `~/.local/bin/vdev-load`
  - In your PATH: ✅

### 3. **Shell Integration**
- **~/.zshrc** - Updated with vdev source line
  - Backup created: `~/.zshrc.backup.YYYYMMDD_HHMMSS`
  - vdev loads automatically on shell start

---

## 🚀 Quick Start

### Activate in Current Shell (one time)
```bash
# Source the RC file to enable vdev immediately
source ~/dev-notes/vibe-dev/vdev.rc
```

### Verify Installation
```bash
# Check if vdev command is available
vdev help

# Load your context
vdev me

# Check urgent items
vdev urgent
```

---

## 🎯 Available Commands

### Core Commands
```bash
vdev help              # Show help
vdev me                # View your priorities
vdev urgent            # Show urgent items
vdev week              # This week's tasks
vdev month             # Next month's plan
vdev todo              # View all TODOs
vdev edit              # Edit priorities
vdev status            # Status dashboard
vdev load <name>       # Load another context
```

### Aliases
```bash
vdev-me                # Quick priorities view
vdev-urgent            # Quick urgent view
vdev-week              # This week's tasks
vdev-matrix            # Priority matrix
vdev-todo              # All TODOs
vdev-morning           # Morning brief
vdev-evening           # Evening review
```

### Navigation
```bash
cdvdev                 # Go to vdev directory
cdnotes                # Go to dev-notes
cdme                   # Go to your context
cdproject chatgpt      # Go to ChatGPT project
cdproject vdev         # Go to vdev project
cdproject aifs         # Go to AIFS project
```

---

## 🌅 Daily Workflow

### Start Your Day
```bash
# Run morning brief
vdev-morning

# Or check specific items
vdev urgent
vdev week
```

### During the Day
```bash
# Quick priority check
vdev-me

# Edit your priorities as you complete tasks
vdev edit

# Navigate to projects
cdproject chatgpt
cdproject vdev
```

### End Your Day
```bash
# Evening review
vdev-evening

# Update your progress
vdev edit
```

---

## 🔧 Configuration

### Environment Variables (Auto-set)
```bash
VDEV_ROOT="${HOME}/dev-notes/vibe-dev"
VDEV_CONTEXTS="${VDEV_ROOT}/contexts"
VDEV_BIN="${HOME}/.local/bin"
```

### Customization
Edit `~/dev-notes/vibe-dev/vdev.rc` to customize:
- Aliases
- Functions
- Default behavior
- Startup messages

---

## 📂 Directory Structure

```
~/dev-notes/vibe-dev/
├── vdev.rc                       # Main shell configuration
├── load-context.sh              # Context loader (executable)
├── INSTALL.md                   # This file
├── QUICK-START.md               # Quick reference guide
├── TODO.md                      # All TODOs
├── ROADMAP.md                   # Development roadmap
├── CONTEXT-MANAGEMENT.md        # Context system docs
└── contexts/
    └── people/
        └── ahmed-masud/
            ├── PRIORITIES.md    # Your priorities
            ├── INDEX.md         # Quick index
            └── README.md        # Full context

~/.local/bin/
└── vdev-load -> ~/dev-notes/vibe-dev/load-context.sh
```

---

## 🔄 Updating vdev

### Auto-Update (if git repo)
```bash
vdev update
```

### Manual Update
```bash
cd ~/dev-notes/vibe-dev
git pull  # if git repo
```

### Reload Configuration
```bash
# After updating vdev.rc
source ~/dev-notes/vibe-dev/vdev.rc

# Or restart shell
exec zsh
```

---

## 🆘 Troubleshooting

### vdev command not found
```bash
# Check if vdev.rc is loaded
echo $VDEV_ROOT

# If empty, source it manually
source ~/dev-notes/vibe-dev/vdev.rc

# Or restart shell
exec zsh
```

### Commands not working
```bash
# Verify files exist
ls -la ~/dev-notes/vibe-dev/vdev.rc
ls -la ~/.local/bin/vdev-load

# Check .zshrc
tail ~/.zshrc

# Reload shell configuration
source ~/.zshrc
```

### Samba share not accessible
```bash
# Check if dev-notes is mounted
ls -la ~/dev-notes/

# If not mounted, check your Samba configuration
# The share should be mounted at ~/dev-notes
```

---

## 🔐 Security Notes

1. **Shell Configuration**
   - Backup created: `~/.zshrc.backup.YYYYMMDD_HHMMSS`
   - Can restore with: `cp ~/.zshrc.backup.* ~/.zshrc`

2. **Samba Share**
   - Ensure proper permissions on `~/dev-notes`
   - Context files contain personal information
   - Keep Samba authentication secure

3. **File Permissions**
   - `vdev.rc` - readable by you only
   - `load-context.sh` - executable
   - `~/.local/bin` - in your PATH

---

## ✨ Features

### Auto-Loading
- ✅ vdev loads automatically when you start a new shell
- ✅ Brief status message on startup
- ✅ Alert if urgent items exist

### Smart Context
- ✅ Automatically finds contexts by name
- ✅ Detects type (people/places/things)
- ✅ Tab completion for context names

### Cross-Machine
- ✅ Works on all machines with Samba share
- ✅ No manual sync needed
- ✅ Changes visible immediately everywhere

---

## 📋 Next Steps

1. **Test the installation**
   ```bash
   source ~/dev-notes/vibe-dev/vdev.rc
   vdev help
   vdev me
   ```

2. **Try the morning routine**
   ```bash
   vdev-morning
   ```

3. **Explore your priorities**
   ```bash
   vdev urgent
   vdev week
   vdev todo
   ```

4. **Edit and update**
   ```bash
   vdev edit
   ```

5. **Learn the navigation**
   ```bash
   cdvdev
   cdme
   cdproject chatgpt
   ```

---

## 🎓 Learning Resources

| Resource | Command/Location |
|----------|------------------|
| **Quick Reference** | `vdev help` or `cat ~/dev-notes/vibe-dev/QUICK-START.md` |
| **Your Priorities** | `vdev me` or `vdev-me` |
| **Context Docs** | `cat ~/dev-notes/vibe-dev/CONTEXT-MANAGEMENT.md` |
| **All TODOs** | `vdev todo` |
| **Roadmap** | `cat ~/dev-notes/vibe-dev/ROADMAP.md` |

---

## 🎉 You're All Set!

The vdev system is now ready to use. Start with:

```bash
# Source vdev in current shell
source ~/dev-notes/vibe-dev/vdev.rc

# Run your morning brief
vdev-morning

# Or check urgent items
vdev urgent
```

**Note**: vdev will load automatically in all new shells from now on!

---

**Installation Date**: 2025-10-08  
**Installed By**: Ahmed Masud  
**Shell**: zsh 5.9  
**Platform**: macOS
