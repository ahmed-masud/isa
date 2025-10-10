# User Configuration Guide
**vibe-dev User Config System**  
**Last Updated**: 2025-10-08

---

## 🎯 Overview

The `.vdevrc` file allows you to customize vibe-dev with your personal projects, aliases, and workflows **without modifying the core tool**. This keeps vibe-dev updates clean and your customizations separate.

---

## 📂 Location

**File**: `~/vibe-dev/.vdevrc`  
**Type**: User configuration (Samba share)  
**Loaded**: Automatically after core vdev.rc

---

## 🏗️ Architecture

```
vibe-dev Core (~/projects/vibe-dev/)
    ↓ loads
User Config (~/vibe-dev/.vdevrc)
    ↓ defines
User Projects, Aliases, Functions
```

**Benefits**:
- ✅ Core tool stays clean
- ✅ User config on Samba share (syncs across machines)
- ✅ Easy to version control separately
- ✅ No conflicts when updating vdev core

---

## 📝 Template Structure

Your `.vdevrc` includes these sections:

### 1. User Information
```bash
export VDEV_USER_NAME="Ahmed Masud"
export VDEV_USER_EMAIL="ahmed.masud@saf.ai"
export VDEV_USER_CONTEXT="ahmed-masud"
```

### 2. Project Registry
```bash
declare -A VDEV_USER_PROJECTS
VDEV_USER_PROJECTS=(
    [resiliate-backend]="${VDEV_DATA}/resiliate-backend:Resiliate backend"
    [chatgpt-local]="${HOME}/projects/ahmed-masud:ChatGPT frontend"
    [saf.ai]="${HOME}/projects/saf.ai:saf.ai main project"
)
```

### 3. Custom Aliases
```bash
alias resiliate-backend='cd ${VDEV_DATA}/resiliate-backend'
alias myprojects='vdev-list-projects'
```

### 4. Custom Functions
```bash
vdev-list-projects()    # List all registered projects
vdev-work-on()          # Switch to project with status
vdev-project-status()   # Overview of all projects
```

---

## 🚀 Usage Examples

### List Your Projects
```bash
myprojects
# or
vdev-list-projects
```

Output:
```
╔════════════════════════════════════════════════════════════════════╗
║                    Registered Projects                             ║
╚════════════════════════════════════════════════════════════════════╝

  resiliate-backend    → /Users/masud/vibe-dev/resiliate-backend
                         Resiliate backend development

  chatgpt-local        → /Users/masud/projects/ahmed-masud
                         ChatGPT-like frontend with Ollama
  ...
```

### Navigate to Projects
```bash
# Using cdproject (now knows about user projects)
cdproject resiliate-backend

# Using alias
resiliate-backend

# Using work-on (shows git status)
vdev-work-on chatgpt-local
```

### Check Project Status
```bash
vdev-project-status
```

Shows git status for all registered projects.

---

## ➕ Adding Your Own Projects

Edit `~/vibe-dev/.vdevrc` and add to `VDEV_USER_PROJECTS`:

```bash
VDEV_USER_PROJECTS=(
    # Existing projects...
    
    # Your new project
    [my-new-project]="${HOME}/projects/my-new-project:Description here"
)
```

**Format**: `[shortname]="path:description"`

Then reload:
```bash
source ~/projects/vibe-dev/vdev.rc
```

---

## 🎨 Customization Examples

### Project-Specific Aliases
```bash
# In .vdevrc
alias resiliate-logs='tail -f ${VDEV_DATA}/resiliate-backend/logs/*.log'
alias resiliate-test='cd ${VDEV_DATA}/resiliate-backend && make test'
alias aifs-monitor='python3 ${VDEV_DATA}/quick-test-ai-monitor.py'
```

### Custom Functions
```bash
# Quick project note creation
vdev-project-note() {
    local project="$1"
    local note_type="${2:-general}"
    # ... creates note in project notes/ directory
}

# Usage:
vdev-project-note resiliate-backend bug
```

### Enhanced Morning Routine
```bash
vdev-morning-extended() {
    vdev-morning  # Call core morning routine
    
    # Then show your project status
    echo "Active Projects:"
    vdev-project-status
}
```

---

## 🔧 Core vs User Functions

### Core Functions (vdev.rc)
These come with vibe-dev:
- `vdev help`, `vdev me`, `vdev urgent`
- `vdev-morning`, `vdev-evening`
- `vdev-awake`, `vdev-caffeinate`
- `cdvdev`, `cdvdata`, `cdme`

### User Functions (.vdevrc)
These are yours to customize:
- `vdev-list-projects` - List your projects
- `vdev-work-on` - Enhanced project switcher
- `vdev-project-status` - Project overview
- `vdev-project-note` - Create project notes
- `vdev-morning-extended` - Enhanced morning brief

---

## 📊 Project Registry Format

```bash
declare -A VDEV_USER_PROJECTS
VDEV_USER_PROJECTS=(
    [shortname]="path:description"
)
```

**Parts**:
- `shortname`: Used in `cdproject shortname`
- `path`: Full path to project
- `description`: One-line description

**Examples**:
```bash
# Local project
[myapp]="${HOME}/projects/myapp:My awesome app"

# In vibe-dev data
[notes]="${VDEV_DATA}/personal-notes:Personal notes"

# Absolute path
[external]="/opt/external-project:External system"
```

---

## 🔄 Syncing Across Machines

Since `.vdevrc` is in `~/vibe-dev` (Samba share):
- ✅ Automatically synced to all machines
- ✅ Same projects available everywhere
- ✅ Same aliases and functions

**Just make sure**:
- Projects referenced exist on each machine
- Paths use `${HOME}` or `${VDEV_DATA}` when possible
- Machine-specific config goes in local `.zshrc`

---

## 🎯 Best Practices

### 1. Use Variables for Paths
```bash
# Good - portable
[project]="${HOME}/projects/myproject:Description"

# Bad - hardcoded
[project]="/Users/masud/projects/myproject:Description"
```

### 2. Group Related Projects
```bash
VDEV_USER_PROJECTS=(
    # Work projects
    [work-api]="${HOME}/work/api:Work API"
    [work-web]="${HOME}/work/web:Work frontend"
    
    # Personal projects
    [blog]="${HOME}/projects/blog:Personal blog"
    [hobby]="${HOME}/projects/hobby:Hobby project"
)
```

### 3. Document Your Custom Functions
```bash
# Enhanced git status for all projects
# Usage: vdev-git-status
vdev-git-status() {
    # Implementation...
}
```

### 4. Test After Changes
```bash
# After editing .vdevrc
source ~/projects/vibe-dev/vdev.rc
vdev-list-projects  # Verify it works
```

---

## 🆘 Troubleshooting

### .vdevrc Not Loading
```bash
# Check if file exists
ls -la ~/vibe-dev/.vdevrc

# Check if VDEV_DATA is set
echo $VDEV_DATA

# Manually source it
source ~/vibe-dev/.vdevrc
```

### Projects Not Showing
```bash
# Check syntax
zsh -n ~/vibe-dev/.vdevrc

# Check variable
echo ${VDEV_USER_PROJECTS[resiliate-backend]}
```

### Function Not Working
```bash
# Check if loaded
type vdev-list-projects

# Reload
source ~/projects/vibe-dev/vdev.rc
```

---

## 📚 Example Workflows

### Resiliate/AIFS Development
```bash
# Morning routine
vdev-morning-extended

# Start work on resiliate
vdev-work-on resiliate-backend

# Check AIFS
aifs-monitor

# View logs
resiliate-logs
```

### Multi-Project Day
```bash
# List projects
myprojects

# Work on chatgpt
vdev-work-on chatgpt-local

# Later, switch to resiliate
vdev-work-on resiliate-backend

# Check all project status
vdev-project-status
```

---

## 🔗 Integration with vdev Core

The `.vdevrc` extends vdev without modifying it:

```
Core vdev.rc defines:
- vdev command
- Context system
- Sleep prevention
- Basic navigation

User .vdevrc adds:
- Project registry
- Project-specific aliases
- Custom workflows
- Enhanced functions
```

Both work together seamlessly!

---

## 📝 Template File

A complete template is at: `~/vibe-dev/.vdevrc`

To start fresh:
```bash
cp ~/vibe-dev/.vdevrc ~/vibe-dev/.vdevrc.backup
$EDITOR ~/vibe-dev/.vdevrc
```

---

## ✨ Advanced Examples

### Auto-Activate Python Venv
```bash
# In .vdevrc
vdev-work-on() {
    # ... existing code ...
    
    # Auto-activate venv if present
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        echo "🐍 Python venv activated"
    fi
}
```

### Project Time Tracking
```bash
# In .vdevrc
vdev-track-time() {
    local project="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S'),${project},start" >> ${VDEV_DATA}/time-log.csv
}

# Usage:
vdev-track-time resiliate-backend
```

### Multi-Repo Git Status
```bash
# In .vdevrc
vdev-git-all() {
    for project in "${(@k)VDEV_USER_PROJECTS}"; do
        local path="${${VDEV_USER_PROJECTS[$project]}%%:*}"
        if [[ -d "$path/.git" ]]; then
            echo "📦 $project:"
            cd "$path" && git --no-pager status -sb
            echo ""
        fi
    done
}
```

---

**Created**: 2025-10-08  
**Location**: `~/vibe-dev/.vdevrc`  
**Documentation**: `~/projects/vibe-dev/docs/USER-CONFIG.md`
