# Preventing System Sleep During Long Operations
**macOS Sleep Prevention Guide for vdev**  
**Last Updated**: 2025-10-08

---

## 🎯 The Problem

macOS screensavers and system sleep can interrupt:
- Long-running AI/terminal sessions
- Build processes
- File operations
- Interactive sessions (like this one!)

---

## ✅ Solutions Included in vdev

### Method 1: vdev-awake (Toggle System Awake)
**Best for**: General work sessions

```bash
# Keep system awake indefinitely
vdev-awake

# Work for hours without interruption...

# Allow system to sleep again (run same command)
vdev-awake
```

**What it does**:
- Starts `caffeinate` in background
- Prevents system sleep, display sleep, and disk sleep
- Toggle on/off with same command
- Survives terminal closure

---

### Method 2: vdev-caffeinate (Timed Awake)
**Best for**: Known duration work

```bash
# Keep awake for 1 hour (default)
vdev-caffeinate

# Keep awake for 4 hours
vdev-caffeinate 14400

# Keep awake for 30 minutes
vdev-caffeinate 1800
```

**Time conversions**:
- 30 min = 1800 seconds
- 1 hour = 3600 seconds
- 2 hours = 7200 seconds
- 4 hours = 14400 seconds
- 8 hours = 28800 seconds

---

### Method 3: vdev-nosleep (Wrap Command)
**Best for**: Specific long-running commands

```bash
# Run a command while preventing sleep
vdev-nosleep "python3 train_model.py"

# Run multiple commands
vdev-nosleep "cd ~/projects && make build && make test"

# Chain with other commands
vdev-nosleep "vdev-morning && vdev todo"
```

---

## 🚀 Recommended Workflow

### For AI/Terminal Sessions (Like This One)
```bash
# At start of session
vdev-awake

# Work for hours...

# At end of session (or when done)
vdev-awake
```

### For Specific Tasks
```bash
# Before long operation
vdev-caffeinate 7200  # 2 hours

# In another terminal, do your work
# System won't sleep for 2 hours
```

### For Scripts/Commands
```bash
# Wrap your command
vdev-nosleep "./long-script.sh"
```

---

## ⚙️ Permanent Settings (System Preferences)

For more permanent changes, you can also adjust macOS settings:

### Via GUI
1. System Preferences → Battery/Energy Saver
2. Adjust "Turn display off after" slider
3. Uncheck "Put hard disks to sleep when possible"

### Via Command Line
```bash
# Prevent sleep while plugged in (until next reboot)
sudo pmset -c sleep 0
sudo pmset -c displaysleep 0

# Check current settings
pmset -g

# Reset to defaults
sudo pmset -c sleep 10
sudo pmset -c displaysleep 10
```

---

## 🔋 What Each caffeinate Flag Does

The vdev functions use `caffeinate -disu`:

| Flag | Prevents |
|------|----------|
| `-d` | Display sleep |
| `-i` | System idle sleep |
| `-s` | System sleep (when lid is closed) |
| `-u` | Declare user activity (prevents screensaver) |

**All together**: System won't sleep, display won't turn off, screensaver won't start.

---

## 📊 Check If System is Being Kept Awake

```bash
# Check for running caffeinate processes
ps aux | grep caffeinate

# Or use vdev helper
pgrep -af caffeinate
```

---

## 🛑 Stop All Caffeinate Processes

```bash
# Kill all caffeinate processes
pkill caffeinate

# Or use vdev toggle
vdev-awake  # If it's currently on, this turns it off
```

---

## 💡 Usage Examples

### Example 1: Long AI Session
```bash
# Start session
vdev-awake
echo "☕ System will stay awake"

# Do your work with AI...
# Hours pass...

# End session
vdev-awake
echo "😴 System can sleep again"
```

### Example 2: Overnight Build
```bash
# Keep awake for 8 hours
vdev-caffeinate 28800 &

# Run your build
cd ~/projects/large-project
make all
```

### Example 3: Wrap Specific Command
```bash
# Training ML model (won't be interrupted)
vdev-nosleep "python3 train.py --epochs 1000"
```

---

## 🔍 Troubleshooting

### System Still Sleeping
```bash
# Check if caffeinate is running
ps aux | grep caffeinate

# If not running, start it
vdev-awake

# Verify it's running
pgrep -af caffeinate
```

### Can't Stop Caffeinate
```bash
# Force kill all caffeinate processes
killall -9 caffeinate

# Or specific PID
ps aux | grep caffeinate
kill -9 <PID>
```

### Want to Prevent Only Screensaver
```bash
# Just prevent screensaver (allow sleep)
caffeinate -u -t 3600 &
```

---

## 🎨 Add to Your Workflow

### Morning Routine
```bash
# Start your day keeping system awake
vdev-morning
vdev-awake  # Toggle on
```

### Evening Routine
```bash
# End your day allowing system to sleep
vdev-evening
vdev-awake  # Toggle off
```

### Update vdev.rc Aliases
You can add these to your `vdev.rc` if you want:

```bash
# Add to vdev.rc
alias work-start='vdev-morning && vdev-awake'
alias work-end='vdev-evening && vdev-awake'
```

---

## 📋 Quick Reference

| Command | Purpose |
|---------|---------|
| `vdev-awake` | Toggle system awake on/off |
| `vdev-caffeinate` | Keep awake for duration (default 1 hour) |
| `vdev-caffeinate 14400` | Keep awake for 4 hours |
| `vdev-nosleep <cmd>` | Run command while preventing sleep |
| `pkill caffeinate` | Stop all caffeinate processes |
| `ps aux \| grep caffeinate` | Check if caffeinate is running |

---

## 🚨 Important Notes

1. **Battery Impact**: Keeping system awake uses more battery
2. **Lid Closed**: `-s` flag keeps system awake even with lid closed
3. **Background Process**: `vdev-awake` runs in background, survives terminal closure
4. **Multiple Instances**: You can have multiple caffeinate processes running
5. **Manual Override**: You can still force sleep with Apple menu → Sleep

---

## 🔗 Integration with .zshrc

The vdev.rc file now includes these functions automatically:
- ✅ `vdev-awake` - Toggle indefinite awake
- ✅ `vdev-caffeinate` - Timed awake
- ✅ `vdev-nosleep` - Wrap command

**Reload to activate:**
```bash
source ~/dev-notes/vibe-dev/vdev.rc
```

Or start a new shell (it auto-loads).

---

## 🎯 For Your Current Session

To prevent interruption RIGHT NOW:

```bash
# Simple - keep awake indefinitely
vdev-awake

# That's it! Now you can work for hours without interruption
```

To stop it later:
```bash
vdev-awake  # Same command toggles it off
```

---

## 🔥 Best Practice for AI Sessions

**Recommended approach:**
1. At session start: `vdev-awake`
2. Do your work (hours if needed)
3. At session end: `vdev-awake`

**Alternative for timed sessions:**
```bash
# Keep awake for 4 hours
vdev-caffeinate 14400 &

# Continue working in same terminal
```

---

**Updated**: 2025-10-08  
**Part of**: vdev system  
**Location**: `~/dev-notes/vibe-dev/PREVENT-SLEEP-GUIDE.md`
