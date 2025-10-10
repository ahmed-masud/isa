# vdev Quick Start Guide
**Samba Share Location**: `/Users/masud/dev-notes` (accessible from all machines)

---

## 🚀 Quick Access to Your Context

### Load Ahmed Masud Context (Personal Priorities)

```bash
# From anywhere on any machine:
~/dev-notes/vibe-dev/load-context.sh ahmed-masud

# Or manually:
cat ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md

# View urgent items only:
grep -A 25 "URGENT" ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md
```

---

## 📂 Context Directory Structure

```
~/dev-notes/vibe-dev/
├── contexts/
│   ├── people/
│   │   ├── ahmed-masud/          # Your personal context
│   │   │   ├── README.md         # Full profile & background
│   │   │   ├── PRIORITIES.md     # Current priorities (NEW!)
│   │   │   ├── Ahmed_Masud_Project_Context.json
│   │   │   ├── Ahmed_Masud_Resume_2025_Updated.md
│   │   │   └── Ahmed_Masud_Resume_2024_Latest.pdf
│   │   ├── david-malcarney/
│   │   ├── denis-krusos/
│   │   ├── ling-young/
│   │   └── maximillian-schweizer/
│   ├── places/                    # (future contexts)
│   └── things/                    # (future contexts)
├── load-context.sh               # Context loader script
├── TODO.md                       # All vdev tasks
├── ROADMAP.md                    # vdev roadmap
├── CONTEXT-MANAGEMENT.md         # How contexts work
└── CONTEXT-FEATURE-SPEC.md       # Context feature specs
```

---

## 🎯 Your Current Priorities at a Glance

```bash
# See priority matrix
grep -A 10 "PRIORITY MATRIX" ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md

# See this week's tasks
grep -A 10 "This Week" ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md

# Check all TODOs across vdev
cat ~/dev-notes/vibe-dev/TODO.md
```

---

## 🔄 Accessing From Different Machines

Since `~/dev-notes` is a Samba share, you can access your contexts from any machine:

### From macOS (your workstation):
```bash
# Direct access
cd ~/dev-notes/vibe-dev
./load-context.sh ahmed-masud
```

### From Linux servers:
```bash
# Mount Samba share (if not already mounted)
# Then same commands:
cd ~/dev-notes/vibe-dev
./load-context.sh ahmed-masud
```

### From any terminal:
```bash
# Quick priority check
cat ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md | less

# Search for specific items
grep -i "email" ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md
```

---

## 📝 Common Commands

### View Full Context
```bash
# Complete profile and background
cat ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/README.md

# Current priorities and projects
cat ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md
```

### Edit Context
```bash
# Edit priorities
vim ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md

# Or with your preferred editor
$EDITOR ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md
```

### Quick Status Checks
```bash
# Check urgent items
grep -A 30 "🔥 URGENT" ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md

# Check this week's tasks
grep -A 15 "This Week" ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md

# Check project locations
grep -A 20 "PROJECT LOCATIONS" ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md

# Check all related files
grep -A 10 "Related Files" ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md
```

### Work on Specific Projects
```bash
# Go to vdev development
cd ~/dev-notes/vibe-dev

# Go to ChatGPT local project
cd ~/projects/ahmed-masud

# Test AIFS monitoring
python3 ~/dev-notes/quick-test-ai-monitor.py
```

---

## 🔍 Search Across All Contexts

```bash
# Find contexts mentioning a keyword
grep -r "saf.ai" ~/dev-notes/vibe-dev/contexts/

# List all people contexts
ls -1 ~/dev-notes/vibe-dev/contexts/people/

# Find all priority files
find ~/dev-notes/vibe-dev/contexts -name "PRIORITIES.md"
```

---

## 💾 Backup & Sync

Since this is on a Samba share, your contexts are automatically:
- ✅ Accessible from all your machines
- ✅ Backed up (if your Samba share is backed up)
- ✅ Synchronized across devices

No additional sync needed!

---

## 🎨 Add to Your Shell Profile (Optional)

Add these aliases to your `~/.zshrc` or `~/.bashrc`:

```bash
# vdev aliases
alias vdev-load='~/dev-notes/vibe-dev/load-context.sh'
alias vdev-me='cat ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md'
alias vdev-urgent='grep -A 30 "URGENT" ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md'
alias vdev-todo='cat ~/dev-notes/vibe-dev/TODO.md'
alias vdev-week='grep -A 15 "This Week" ~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md'

# Quick navigation
alias cdvdev='cd ~/dev-notes/vibe-dev'
alias cdnotes='cd ~/dev-notes'
```

Then use:
```bash
vdev-me              # View your priorities
vdev-urgent          # See urgent items
vdev-week            # This week's tasks
vdev-load denis-krusos  # Load another context
```

---

## 🔐 Security Note

Remember that `~/dev-notes` is a Samba share. Ensure:
1. The share has appropriate permissions
2. Only trusted machines have access
3. Sensitive information (like passwords) is not stored in plain text
4. Use secure authentication for Samba access

---

## 🆘 Quick Help

```bash
# List available contexts
~/dev-notes/vibe-dev/load-context.sh nonexistent-context

# This will show all available contexts in people/places/things
```

---

## 🚀 Next Steps

1. **Set up aliases** (see above) for faster access
2. **Bookmark important files** in your editor
3. **Review priorities weekly** and update PRIORITIES.md
4. **Create contexts** for new people/places/things as needed
5. **Keep contexts updated** as projects evolve

---

## 📞 Context Locations Summary

| Context | Path |
|---------|------|
| **Your Priorities** | `~/dev-notes/vibe-dev/contexts/people/ahmed-masud/PRIORITIES.md` |
| **Your Profile** | `~/dev-notes/vibe-dev/contexts/people/ahmed-masud/README.md` |
| **All vdev TODOs** | `~/dev-notes/vibe-dev/TODO.md` |
| **vdev Roadmap** | `~/dev-notes/vibe-dev/ROADMAP.md` |
| **Context Docs** | `~/dev-notes/vibe-dev/CONTEXT-MANAGEMENT.md` |
| **ChatGPT Local** | `~/projects/ahmed-masud/README.md` |
| **AIFS Monitoring** | `~/dev-notes/README.md` |

---

**Last Updated**: 2025-10-08  
**Maintained By**: Ahmed Masud via vdev context management
