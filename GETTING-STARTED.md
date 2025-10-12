# Getting Started with ISA

**Welcome to ISA - Your Intelligent Support Assistant!** 🚀

ISA is your personal AI-powered command-line assistant that helps you manage priorities, search through your knowledge base, and interact with your work using natural language.

---

## 📖 Table of Contents

1. [What is ISA?](#what-is-isa)
2. [Quick Start](#quick-start)
3. [First Steps](#first-steps)
4. [Basic Commands](#basic-commands)
5. [Natural Language](#natural-language)
6. [Your Context](#your-context)
7. [AI Features](#ai-features)
8. [Pro Tips](#pro-tips)
9. [Getting Help](#getting-help)

---

## 🤔 What is ISA?

ISA is a context-aware shell assistant that:

- **Manages your priorities and projects** in markdown files
- **Provides AI-powered insights** using Ollama for intelligent suggestions
- **Semantic search** through your knowledge base using vector embeddings
- **Natural language commands** - talk to your computer like a colleague
- **Tracks command history** for contextual operations

Think of ISA as your digital chief of staff - always ready to help you focus on what matters most.

---

## ⚡ Quick Start

### 1. Load ISA in Your Shell

Add this to your `~/.zshrc` or `~/.bashrc`:

```bash
source ~/projects/isa/isa.rc
```

Then reload your shell:

```bash
source ~/.zshrc   # for zsh
# or
source ~/.bashrc  # for bash
```

### 2. Verify Installation

```bash
isa help
```

You should see the ISA help menu. Congratulations! 🎉

---

## 👣 First Steps

### Create Your Priority File

ISA needs a place to store your priorities. Create one:

```bash
mkdir -p ~/.config/isa/contexts/people/$(whoami)
```

Create your priorities file:

```bash
cat > ~/.config/isa/contexts/people/$(whoami)/PRIORITIES.md << 'EOF'
# My Priorities

## Current Focus

**This Week:**
- [ ] Get familiar with ISA
- [ ] Set up my first project context

## Projects

### Learning ISA
- **Status**: In Progress
- **Priority**: High
- **Next Actions**:
  - [ ] Complete getting started guide
  - [ ] Try natural language commands
  - [ ] Create my first context

EOF
```

### View Your Priorities

```bash
isa me
# or
computer me
```

---

## 🎯 Basic Commands

ISA has three command styles - use whichever feels natural!

### Traditional Style (Precise)

```bash
isa me                  # View your priorities
isa urgent              # See urgent items
isa week                # This week's tasks
isa todo                # View all TODOs
isa edit                # Edit your priorities
```

### Status & Information

```bash
isa status              # Dashboard view
isa contexts            # List all contexts
isa search "query"      # Search all contexts (grep)
```

### Semantic Context Commands

```bash
isa ctx-stats           # Vector database statistics
isa ctx-health          # Check all services
isa ctx-search "query"  # Semantic search
isa ctx-sync            # Sync contexts to database
```

---

## 🗣️ Natural Language

This is where ISA gets fun! Talk to your computer naturally:

### Imperative Commands (Fast & Direct)

```bash
computer show stats
computer check health
computer sync
computer rebuild
computer find helm
```

### Natural Questions (Conversational)

```bash
computer show me the context stats
computer are the services healthy
computer how many chunks are there
computer find information about deployment
```

### Contextual Commands (History-Aware)

```bash
# Run a command
computer show stats

# Later, repeat it
computer repeat last
computer do it again

# Or reference it
computer stop the previous command
```

**Pro tip:** Shorter is faster! `computer show stats` beats typing the full question.

---

## 📁 Your Context

ISA organizes your knowledge into **contexts** - structured markdown files that the AI can understand.

### Context Types

```
~/.config/isa/contexts/
├── people/              # Personal contexts, priorities
├── places/              # Locations, servers, environments
└── things/              # Projects, systems, processes
```

### Creating a Project Context

```bash
mkdir -p ~/.config/isa/contexts/things/my-project
cat > ~/.config/isa/contexts/things/my-project/README.md << 'EOF'
# My Project

**Type**: Web Application
**Status**: Planning
**Stack**: Python, React

## Overview

Brief description of what this project does.

## Current Status

- Planning phase
- Setting up repository

## Next Steps

1. Create repository
2. Set up development environment
3. Write initial documentation

EOF
```

### Sync Your Contexts

After creating contexts, add them to the semantic search database:

```bash
isa ctx-sync
# or naturally:
computer sync all my contexts
```

Now ISA's AI can understand and search through your project!

---

## 🤖 AI Features

ISA integrates with Ollama AI (if available) for intelligent assistance.

### Ask Questions

```bash
computer ask "What should I work on today?"
computer ask "What's the best approach for this task?"
```

### Get AI Analysis

```bash
isa ai-analyze urgent        # Analyze urgent items
isa ai-analyze me            # Analyze your context
isa ai-analyze current       # Analyze current project
```

### Get Suggestions

```bash
computer suggest             # Suggestions for current work
computer suggest --project=my-project
```

### Check AI Status

```bash
isa ai-status               # See AI integration status
computer are the ai services running
```

---

## 💡 Pro Tips

### 1. Morning Routine

Start your day with:

```bash
isa-morning
# or create an alias in your shell:
alias morning='isa-morning'
```

This shows:
- Today's date and time
- Urgent items
- This week's focus

### 2. Quick Priority Check

```bash
isa-check
```

Get a snapshot of your priorities without opening files.

### 3. Fast Navigation

```bash
cdisa          # Jump to ISA directory
cdconfig       # Jump to ISA config
cdme           # Jump to your context directory
```

### 4. Semantic Search > Grep

Instead of:
```bash
grep -r "deployment" ~/.config/isa/contexts/
```

Use:
```bash
computer find deployment
```

Semantic search understands meaning, not just keywords!

### 5. Use Command History

ISA tracks your commands, so you can:

```bash
computer repeat last        # Repeat the last command
computer redo              # Same thing
computer stop that         # Stop a running command
```

### 6. Mix and Match Styles

```bash
# Traditional for scripts
isa ctx-sync && isa ctx-stats

# Natural for interactive use
computer sync && computer show me the stats
```

---

## 🎓 Learning Path

Here's a suggested path for getting comfortable with ISA:

### Week 1: Basics
- [ ] Set up your priority file
- [ ] Try all traditional commands (`isa me`, `isa urgent`, etc.)
- [ ] Create one project context
- [ ] Use `isa edit` to update priorities daily

### Week 2: Natural Language
- [ ] Try imperative commands (`computer show stats`)
- [ ] Try natural questions (`computer are services healthy`)
- [ ] Use `computer find` for semantic search
- [ ] Try contextual commands (`computer repeat last`)

### Week 3: Advanced
- [ ] Set up AI integration (if available)
- [ ] Create multiple project contexts
- [ ] Use semantic search regularly
- [ ] Integrate ISA into your daily workflow

---

## 🆘 Getting Help

### Built-in Help

```bash
isa help                    # Show all commands
isa ctx-health              # Check service health
computer show me the commands
```

### Documentation

- `README.md` - Project overview
- `ISA-CONTEXT-COMMANDS.md` - Comprehensive command reference
- `QUICK-START.md` - Quick reference guide (if exists)

### Check Status

```bash
isa status                  # ISA dashboard
isa ai-status              # AI integration status
computer are things working
```

### Common Issues

**Q: Commands not found?**
```bash
# Make sure ISA is loaded:
source ~/projects/isa/isa.rc
```

**Q: Semantic search fails?**
```bash
# Check service health:
computer check health

# On remote server, ensure vector service is running:
ssh helm 'cd ~/projects/isa && python3 vector_service_simple.py &'
```

**Q: AI not responding?**
```bash
# Check AI status:
isa ai-status

# Verify Ollama is running (if using remote):
curl http://192.168.1.161:11434/api/tags
```

---

## 🎨 Customization

### Add Your Own Aliases

Edit your `~/.zshrc` or `~/.bashrc`:

```bash
# Quick priority checks
alias p='isa me'
alias urgent='isa urgent'
alias todo='isa todo'

# Morning routine
alias morning='isa-morning'
alias evening='isa-evening'

# Natural shortcuts
alias ask='computer ask'
alias find='computer find'
```

### Customize Priority File Location

The default user context is in:
```
~/.config/isa/contexts/people/$(whoami)/PRIORITIES.md
```

You can create additional contexts for different roles:
```bash
~/.config/isa/contexts/people/$(whoami)/
├── PRIORITIES.md           # Main priorities
├── WORK.md                 # Work-specific
├── PERSONAL.md             # Personal projects
└── LEARNING.md             # Learning goals
```

---

## 🚀 Next Steps

Once you're comfortable with the basics:

1. **Explore Semantic Context**
   - Read `ISA-CONTEXT-COMMANDS.md`
   - Set up semantic search
   - Try `computer find` with different queries

2. **Set Up AI Integration**
   - Install Ollama (if not already)
   - Try `computer ask` commands
   - Use AI analysis features

3. **Create Rich Contexts**
   - Document your projects in markdown
   - Use consistent structure
   - Sync regularly with `isa ctx-sync`

4. **Build Your Workflow**
   - Morning routine with `isa-morning`
   - Regular priority reviews
   - End-of-day review with `isa-evening`

---

## 🌟 Welcome Aboard!

You're now ready to use ISA! Remember:

- **Start simple** - Basic commands first, then natural language
- **Be consistent** - Update your priorities regularly
- **Experiment** - Try different command styles
- **Ask for help** - Use `isa help` anytime

ISA learns as you use it. The more you add to your contexts, the smarter the semantic search becomes.

**Happy prioritizing!** 🎯

---

**Questions? Issues?**
- Check `isa help` for quick reference
- Review `ISA-CONTEXT-COMMANDS.md` for detailed command info
- Check `isa status` to verify everything is running

**Version**: 1.0.0-semantic-context  
**Last Updated**: 2025-10-12
