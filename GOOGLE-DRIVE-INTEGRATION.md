# ISA Google Drive Integration Guide

## 🎯 Overview

ISA now supports **context-aware Google Drive mounting** using rclone. This feature automatically mounts the appropriate Google Drive based on your current ISA context, making your cloud files directly accessible through the file system.

For the `ahmed-masud` context, this integrates with the `ahmed.masud@saf.ai` Google account, allowing seamless access to Google Drive files while working in that context.

---

## ✨ Key Features

### 📁 **Context-Aware Mounting**
- Automatically maps ISA contexts to Google Drive accounts
- Mounts appropriate drive based on current context
- Supports multiple Google accounts for different contexts

### 🔄 **Seamless File System Integration**
- Google Drive appears as regular directory: `~/GoogleDrive/ahmed-masud`
- Use normal file commands: `ls`, `cp`, `mv`, `vim`, etc.
- Full read/write access to your Google Drive

### 🎯 **ISA Command Integration**
- Natural language commands: `computer mount google drive`
- Simple ISA commands: `isa drive-mount`, `isa drive-status`
- Automatic mounting based on current context

---

## 🚀 Quick Setup

### **1. Configure rclone Remote**

First, set up the rclone remote for the ahmed-masud context:

```bash
# Get setup instructions
isa drive-setup ahmed-masud

# Follow the instructions to run:
rclone config
```

When configuring rclone:
1. Choose **'n'** for new remote
2. Name: **`ahmed-masud-drive`**
3. Storage: **`drive`** (Google Drive)
4. Follow the OAuth authentication flow
5. Use email: **`ahmed.masud@saf.ai`**
6. Accept defaults for most other options

### **2. Test the Setup**

```bash
# Check configuration
isa drive-list

# Check current status
isa drive-status

# Try mounting (will work after rclone config is complete)
isa drive-mount
```

---

## 📋 Command Reference

### **ISA Commands**

| Command | Purpose | Example |
|---------|---------|---------|
| `isa drive-mount` | Mount drive for current context | `isa drive-mount` |
| `isa drive-mount <ctx>` | Mount drive for specific context | `isa drive-mount ahmed-masud` |
| `isa drive-unmount` | Unmount drive for current context | `isa drive-unmount` |
| `isa drive-status` | Show mount status | `isa drive-status` |
| `isa drive-list` | List all configured drives | `isa drive-list` |
| `isa drive-setup <ctx>` | Show setup instructions | `isa drive-setup ahmed-masud` |

### **Natural Language Commands**

| Natural Command | ISA Equivalent | What It Does |
|-----------------|----------------|--------------|
| `computer mount google drive` | `isa drive-mount` | Mount drive for current context |
| `computer unmount google drive` | `isa drive-unmount` | Unmount current drive |
| `computer show drive status` | `isa drive-status` | Show mount status |
| `computer connect to google drive` | `isa drive-mount` | Mount Google Drive |

### **Command Aliases**

Multiple aliases are supported:
```bash
# Mount commands
isa drive-mount    # Primary
isa gdrive-mount   # Alias
isa mount-drive    # Alias

# Status commands  
isa drive-status   # Primary
isa gdrive-status  # Alias

# List commands
isa drive-list     # Primary
isa list-drives    # Alias
```

---

## 🎯 Usage Scenarios

### **Scenario 1: Working in ahmed-masud Context**

```bash
# Switch to ahmed-masud context
isa load ahmed-masud

# Mount Google Drive for this context
isa drive-mount
# ✅ Mounts ahmed.masud@saf.ai drive to ~/GoogleDrive/ahmed-masud

# Access files normally
ls ~/GoogleDrive/ahmed-masud
cd ~/GoogleDrive/ahmed-masud/Documents
vim ~/GoogleDrive/ahmed-masud/notes.txt

# When done
isa drive-unmount
```

### **Scenario 2: Context-Aware Auto-Mount**

```bash
# The system knows your current context
isa breadcrumbs
# Shows: *ahmed-masud*

# Auto-mount based on context
isa drive-mount  # No context needed - uses current context
# Automatically mounts the correct Google Drive account

# Check status
isa drive-status
# Shows ahmed-masud: MOUNTED (CURRENT)
```

### **Scenario 3: Multiple Context Support**

```bash
# Current context determines which drive
isa load ahmed-masud
isa drive-mount          # Mounts ahmed.masud@saf.ai

# Future: switch to different context
isa push some-other-person  
isa drive-mount          # Would mount different account
```

---

## 🔧 Technical Details

### **Directory Structure**

```
~/GoogleDrive/
└── ahmed-masud/          # Mount point for ahmed.masud@saf.ai
    ├── Documents/
    ├── Projects/
    ├── Photos/
    └── [all Google Drive content]
```

### **Configuration Files**

- **Drive configs**: `~/.config/isa/google_drives.json`
- **Mount status**: `~/.config/isa/.drive_mounts.json`
- **rclone config**: `~/.config/rclone/rclone.conf`

### **Default Configuration**

The system creates this configuration automatically:

```json
{
  "contexts": {
    "ahmed-masud": {
      "email": "ahmed.masud@saf.ai",
      "rclone_remote": "ahmed-masud-drive",
      "mount_point": "ahmed-masud",
      "description": "Ahmed Masud's Google Drive"
    }
  }
}
```

---

## 🛠️ Advanced Configuration

### **Adding More Contexts**

You can extend the configuration for additional contexts:

```bash
# Edit the configuration
vim ~/.config/isa/google_drives.json
```

Add more contexts:
```json
{
  "contexts": {
    "ahmed-masud": {
      "email": "ahmed.masud@saf.ai",
      "rclone_remote": "ahmed-masud-drive",
      "mount_point": "ahmed-masud",
      "description": "Ahmed Masud's Google Drive"
    },
    "work-account": {
      "email": "ahmed@company.com",
      "rclone_remote": "work-drive",
      "mount_point": "work-account",
      "description": "Work Google Drive"
    }
  }
}
```

### **Custom Mount Options**

The system uses these rclone mount options for optimal performance:

```bash
rclone mount ahmed-masud-drive: ~/GoogleDrive/ahmed-masud \
  --daemon \
  --vfs-cache-mode writes \
  --vfs-cache-max-age 1h \
  --dir-cache-time 1h \
  --poll-interval 1m \
  --log-level ERROR
```

---

## 🎨 Integration with ISA Workflows

### **With Context Stack**

```bash
# Working in cybernetic-engrams context
isa breadcrumbs  # *cybernetic-engrams*

# Push to ahmed-masud and mount drive
isa push ahmed-masud
isa drive-mount
# Now have both context and Google Drive access

# Work with files
vim ~/GoogleDrive/ahmed-masud/project-notes.md

# Pop back to previous context, drive stays mounted
isa pop
# Back to cybernetic-engrams, but can still access drive
```

### **With AI Queries**

```bash
# Mount drive first
isa drive-mount

# AI can reference both context and drive files
computer ask "Based on my priorities and the documents in my Google Drive, what should I work on?"

# Work with files AI suggests
cd ~/GoogleDrive/ahmed-masud/Projects
ls
```

### **With Semantic Search**

```bash
# Mount drive for file access
isa drive-mount

# Semantic search in contexts
isa ctx-search "project planning"

# Access related files in Google Drive
cd ~/GoogleDrive/ahmed-masud/Planning
```

---

## 🔍 Monitoring and Status

### **Check Mount Status**

```bash
# Quick status
isa drive-status
# 📊 Google Drive Mount Status
# ========================================
# Current Context: ahmed-masud
# 
#   ahmed-masud (CURRENT): MOUNTED
#     📁 /Users/masud/GoogleDrive/ahmed-masud

# Detailed list
isa drive-list
# Shows full configuration with timestamps
```

### **Verify Mount is Working**

```bash
# Check if directory is accessible
ls ~/GoogleDrive/ahmed-masud

# Test file operations
echo "test" > ~/GoogleDrive/ahmed-masud/test.txt
cat ~/GoogleDrive/ahmed-masud/test.txt
rm ~/GoogleDrive/ahmed-masud/test.txt
```

---

## 🔧 Troubleshooting

### **Common Issues**

1. **"rclone remote not found"**
   ```bash
   # Check existing remotes
   rclone listremotes
   
   # Configure the missing remote
   isa drive-setup ahmed-masud
   rclone config
   ```

2. **Mount fails silently**
   ```bash
   # Check if directory exists but is empty
   ls ~/GoogleDrive/ahmed-masud
   
   # Try manual mount with verbose output
   rclone mount ahmed-masud-drive: ~/GoogleDrive/ahmed-masud --log-level INFO
   ```

3. **Drive appears mounted but files not accessible**
   ```bash
   # Unmount and remount
   isa drive-unmount
   isa drive-mount
   
   # Or check rclone authentication
   rclone lsd ahmed-masud-drive:
   ```

4. **Permission denied errors**
   ```bash
   # Check rclone config permissions
   ls -la ~/.config/rclone/
   
   # Re-authenticate if needed
   rclone config reconnect ahmed-masud-drive:
   ```

### **Manual Operations**

If ISA commands aren't working, you can use rclone directly:

```bash
# Manual mount
rclone mount ahmed-masud-drive: ~/GoogleDrive/ahmed-masud --daemon

# Manual unmount
umount ~/GoogleDrive/ahmed-masud

# List remote contents
rclone lsd ahmed-masud-drive:

# Test remote connectivity
rclone about ahmed-masud-drive:
```

---

## 🛡️ Security and Privacy

### **Authentication**
- Uses OAuth2 with Google - no passwords stored
- Tokens stored securely in rclone configuration
- Can revoke access through Google Account settings

### **Data Handling**
- Files are cached locally for performance
- Cache location: `~/.cache/rclone/`
- Files encrypted in transit (HTTPS)

### **Access Control**
- Only authenticated Google account has access
- ISA doesn't modify rclone permissions
- File operations use your normal user permissions

---

## 🎯 Best Practices

### **1. Regular Unmounting**
```bash
# Unmount when switching contexts for long periods
isa drive-unmount

# Especially before system sleep/restart
isa drive-unmount
```

### **2. Monitor Disk Usage**
```bash
# Google Drive doesn't count against local disk
# But cache does - monitor with:
du -sh ~/.cache/rclone/
```

### **3. Network Considerations**
- Large file operations may be slow over network
- Consider working with local copies for intensive editing
- Sync changes back to Google Drive

### **4. Context Awareness**
```bash
# Always verify current context before mounting
isa breadcrumbs
isa drive-mount    # Mounts correct drive for context
```

---

## 🎉 Integration Complete

Your ISA system now has seamless Google Drive integration:

✅ **Context-aware mounting** - Right drive for right context  
✅ **Natural language support** - `computer mount google drive`  
✅ **File system integration** - Use normal file commands  
✅ **ISA command integration** - Works with all ISA features  
✅ **Multiple account support** - Ready for additional contexts  

### **Ready to Use:**

```bash
# Set up once
isa drive-setup ahmed-masud
rclone config

# Use daily
isa drive-mount      # When you need Google Drive access
isa drive-unmount    # When you're done

# Monitor
isa drive-status     # Check what's mounted
```

**Your Google Drive files are now seamlessly integrated with your ISA workflow!** 🚀

---

## 📚 Related Documentation

- **[CONTEXT-STACK-GUIDE.md](CONTEXT-STACK-GUIDE.md)** - Context push/pop operations
- **[ISA-CONTEXT-COMMANDS.md](ISA-CONTEXT-COMMANDS.md)** - Core context commands
- **[rclone documentation](https://rclone.org/docs/)** - rclone configuration reference

---

**Last Updated**: 2025-10-13  
**ISA Version**: 1.0+ with Google Drive Integration  
**Requirements**: rclone, Google account, ISA context system