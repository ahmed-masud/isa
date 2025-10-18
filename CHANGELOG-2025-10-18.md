# ISA Changelog - October 18, 2025

## Summary

Major updates to add dynamic context management (`learn`/`unlearn` commands) and full Linux compatibility.

---

## New Features

### 1. Dynamic Context Management

#### `isa learn` Command
Add files or text to your current context dynamically.

**Usage:**
```bash
# Add a file to current context
isa learn /path/to/document.md

# Add text as a note
isa learn "Remember to call Bob tomorrow"
```

**Features:**
- Copies files into the current context directory
- Creates timestamped markdown notes from text input
- Automatically adds content to the vector database
- Works with all context types (people, places, things, sub-contexts)

#### `isa unlearn` Command
Remove files from your current context.

**Usage:**
```bash
# Remove a specific file
isa unlearn note-20251018-012345.md

# List files if you forget the name
isa unlearn
```

**Features:**
- Removes files from the current context
- Shows available files if no filename provided
- Protects core files (README.md, PRIORITIES.md, INDEX.md) with confirmation
- Automatically rebuilds vector database after removal

### 2. Linux Compatibility

#### OS Detection
ISA now automatically detects the operating system on startup:
- macOS: 🍎
- Linux: 🐧

#### Cross-Platform Sleep Prevention

**macOS:**
- Uses built-in `caffeinate` command
- All existing functionality preserved

**Linux:**
- Uses `systemd-inhibit` (primary)
- Falls back to `gnome-session-inhibit` (GNOME desktop)
- Prevents idle, sleep, and lid-switch events

**Commands work identically on both platforms:**
```bash
isa-caffeinate          # Keep awake for 1 hour
isa-caffeinate 7200     # Keep awake for 2 hours
isa-nosleep ./script.sh # Run command with sleep prevention
isa-awake               # Toggle indefinite sleep prevention
```

#### Shell Compatibility
- Fully compatible with **zsh** and **bash** on both platforms
- Shell-specific optimizations maintained
- Tab completion works on both

---

## Performance Improvements

### Clean Loading Status
- Single-line status message on shell initialization
- Shows load time in milliseconds
- Displays OS with emoji (🍎 or 🐧)
- Shows count of urgent items if any exist
- Suppressed module loading messages

**Before:**
```
Loading ISA Ollama functions for: zsh
✨ ISA (Issa) loaded | Type 'isa help' for commands | 'isa-morning' for daily brief
⚠️  URGENT: You have items with approaching deadlines! Run 'isa urgent'
```

**After:**
```
✨ ISA loaded (45ms) 🍎 | isa help for commands
```

Or with urgent items:
```
✨ ISA loaded (45ms) 🍎 | 🔥 2 urgent items | isa help
```

### Debug Mode
- All module loading messages now silent by default
- Enable with `ISA_DEBUG=1` for troubleshooting
- Example: `ISA_DEBUG=1 source ~/projects/isa/isa.rc`

---

## Documentation Updates

### New Documentation
- **[docs/LINUX-SETUP.md](docs/LINUX-SETUP.md)** - Complete Linux setup guide
  - Installation instructions for Ubuntu/Debian, Fedora/RHEL, Arch Linux
  - Sleep prevention configuration
  - Troubleshooting common Linux issues
  - Systemd integration examples
  - Desktop integration options

### Updated Documentation
- **README.md** - Added Linux compatibility badges and references
- **isa.rc** - Updated header with compatibility info
- **Help text** - Updated to include `learn` and `unlearn` commands

---

## Technical Changes

### Files Modified

#### `/Users/masud/projects/isa/isa.rc`
- Added OS detection at startup (lines 15-32)
- Added `learn` command implementation (lines 310-396)
- Added `unlearn` command implementation (lines 397-487)
- Updated `isa-caffeinate` for cross-platform support (lines 1314-1335)
- Updated `isa-nosleep` for cross-platform support (lines 1337-1361)
- Updated `isa-awake` for cross-platform support (lines 1363-1395)
- Added OS indicator to loading message (lines 1263-1269)
- Added clean loading status with timing (lines 1219-1249)
- Updated help text to include new commands (lines 829-830, 910-912)
- Updated `computer` function to recognize new commands (line 983)

#### `/Users/masud/projects/isa/modules/ollama-client.sh`
- Added `ISA_DEBUG` checks to suppress loading messages (lines 36, 40, 56, 62)
- Messages now only shown when `ISA_DEBUG=1` is set

#### New Files Created
- `docs/LINUX-SETUP.md` - Linux-specific setup and troubleshooting guide

---

## Breaking Changes

None. All existing commands and workflows remain unchanged.

---

## Upgrade Instructions

### For Existing Users

1. **Update ISA:**
   ```bash
   cd ~/projects/isa
   git pull
   ```

2. **Reload configuration:**
   ```bash
   source ~/projects/isa/isa.rc
   ```

3. **Verify OS detection:**
   ```bash
   echo $ISA_OS  # Should show 'macos' or 'linux'
   ```

4. **Test new commands:**
   ```bash
   # Ensure you're in a context first
   isa load ahmed-masud  # or your context name
   
   # Try learning
   isa learn "Testing the new learn command"
   
   # Try unlearning
   isa unlearn  # Lists files
   ```

### For Linux Users

1. **Install prerequisites:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install -y python3 python3-pip git zsh curl systemd
   
   # Fedora/RHEL
   sudo dnf install -y python3 python3-pip git zsh curl systemd
   ```

2. **Follow Linux setup guide:**
   See [docs/LINUX-SETUP.md](docs/LINUX-SETUP.md) for complete instructions

3. **Test sleep prevention:**
   ```bash
   which systemd-inhibit  # Should exist on most Linux systems
   isa-awake              # Toggle sleep prevention
   ```

---

## Known Issues

### Linux
- Sleep prevention requires `systemd-inhibit` or `gnome-session-inhibit`
  - Most modern Linux distributions have systemd installed
  - Alternative: Install `gnome-session` package for GNOME desktop environments

### macOS
- No known issues

---

## Future Enhancements

### Planned Features
- [ ] Integration with `isa context-sync` to auto-learn on file changes
- [ ] Batch learn: `isa learn-dir /path/to/directory`
- [ ] Learn from URLs: `isa learn https://example.com/doc.pdf`
- [ ] Smart context detection (auto-switch based on directory)
- [ ] Cross-platform clipboard integration (pbcopy/xclip)

### Under Consideration
- [ ] Windows WSL support
- [ ] Remote context synchronization (git-based)
- [ ] Encrypted context storage
- [ ] Integration with external note-taking apps (Obsidian, Notion)

---

## Testing Performed

### macOS (Sonoma 14.x)
- ✅ Clean loading with OS indicator
- ✅ `isa learn` with files
- ✅ `isa learn` with text
- ✅ `isa unlearn` with confirmation
- ✅ Vector database integration
- ✅ Sleep prevention (caffeinate)

### Linux (Tested on Ubuntu 22.04)
- ✅ OS detection
- ✅ Module loading
- ✅ Sleep prevention (systemd-inhibit)
- ✅ All core ISA commands
- ✅ Shell completion

---

## Contributors

- Ahmed Masud (@masud) - All features and documentation

---

## Version

- **Version**: 1.1.0
- **Date**: 2025-10-18
- **Compatibility**: ISA 1.0.0+

---

## Rollback Instructions

If you encounter issues, rollback with:

```bash
cd ~/projects/isa
git log --oneline  # Find commit before changes
git checkout <commit-hash>
source ~/projects/isa/isa.rc
```

To return to latest:
```bash
git checkout main  # or master
source ~/projects/isa/isa.rc
```
