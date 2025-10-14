# ISA Context Stack Guide - Push/Pop Context Management

## 🎯 Overview

ISA now supports **context stacking** with push/pop operations, allowing you to temporarily switch contexts while preserving the ability to return to your previous working context. This is perfect for temporarily exploring related contexts without losing your place.

---

## ✨ Key Features

### 📚 **Stack-Based Context Management**
- **Push**: Save current context to stack and load new one
- **Pop**: Return to previous context from stack  
- **Stack Visualization**: See your current context history
- **Breadcrumbs**: Track your context navigation trail

### 🔄 **Persistent Stack State**
- Context stack survives shell sessions
- Automatic state persistence to `~/.config/isa/.context_stack.json`
- Current context tracking across commands

### 🗣️ **Natural Language Interface**
- Intuitive commands like `computer push context X` and `computer go back`
- Multiple ways to express the same operation
- Integrated with existing ISA command system

---

## 🚀 Quick Start

### **Basic Operations**

```bash
# Currently in 'cybernetic-engrams' context
isa push ahmed-masud           # Push cybernetic-engrams to stack, load ahmed-masud
isa pop                        # Return to cybernetic-engrams

# Natural language alternatives
computer push context resiliate    # Push and load resiliate
computer go back                   # Pop and return to previous
computer pop context              # Explicit pop command
```

### **Stack Management**

```bash
# Check current stack status
isa stack
computer show stack

# See context breadcrumb trail
isa breadcrumbs
computer show breadcrumbs

# Clear entire stack (if needed)
python3 tools/context_stack.py clear
```

---

## 📋 Command Reference

### **Direct Commands**

| Command | Purpose | Example |
|---------|---------|---------|
| `isa push <context>` | Push current context to stack, load new one | `isa push ahmed-masud` |
| `isa pop` | Pop context from stack and load it | `isa pop` |
| `isa stack` | Show current context stack | `isa stack` |
| `isa breadcrumbs` | Show context breadcrumb trail | `isa breadcrumbs` |

### **Natural Language Commands**

| Natural Command | Traditional Equivalent | What It Does |
|-----------------|----------------------|--------------|
| `computer push context X` | `isa push X` | Push current, load X |
| `computer go back` | `isa pop` | Return to previous context |
| `computer pop context` | `isa pop` | Return to previous context |
| `computer show stack` | `isa stack` | Display context stack |
| `computer show breadcrumbs` | `isa breadcrumbs` | Show context trail |
| `computer return to previous` | `isa pop` | Return to previous context |

### **Advanced Operations**

```bash
# Python script direct usage
python3 tools/context_stack.py push <context>     # Push operation
python3 tools/context_stack.py pop                # Pop operation
python3 tools/context_stack.py stack              # Show stack
python3 tools/context_stack.py peek               # Peek at top without popping
python3 tools/context_stack.py clear              # Clear entire stack
python3 tools/context_stack.py history            # Show context history
python3 tools/context_stack.py breadcrumbs        # Show breadcrumb trail
```

---

## 🎯 Usage Scenarios

### **Scenario 1: Exploring Related Contexts**

```bash
# Working on cybernetic-engrams
isa load cybernetic-engrams

# Need to quickly check a person's context
isa push ahmed-masud
# Now in ahmed-masud context, cybernetic-engrams is saved

# Check their priorities, do some work...
# Ready to return to cybernetic-engrams
isa pop
# Back to cybernetic-engrams, ahmed-masud forgotten
```

### **Scenario 2: Deep Context Navigation**

```bash
# Start with cybernetic-engrams
Current: cybernetic-engrams

# Push to person context
isa push ahmed-masud
Stack: cybernetic-engrams → *ahmed-masud*

# Push to another project context
isa push resiliate  
Stack: cybernetic-engrams → ahmed-masud → *resiliate*

# Pop back through the stack
isa pop  # Returns to ahmed-masud
Stack: cybernetic-engrams → *ahmed-masud*

isa pop  # Returns to cybernetic-engrams
Stack: *cybernetic-engrams*
```

### **Scenario 3: Context Research Sessions**

```bash
# Research workflow with natural language
computer push context isa-ollama-integration
# Explore AI integration docs...

computer push context isa-helm-deployment  
# Check deployment procedures...

computer show breadcrumbs
# See: cybernetic-engrams → isa-ollama-integration → *isa-helm-deployment*

computer go back  # Return to isa-ollama-integration
computer go back  # Return to cybernetic-engrams
```

---

## 🔍 Stack Visualization

### **Stack Status Display**

```bash
$ isa stack

🏗️  ISA Context Stack
==================================================
📍 Current: resiliate

📋 Stack (2 contexts):
  → [1] ahmed-masud (pushed at 18:15:32)
    [0] cybernetic-engrams (pushed at 18:10:45)

💡 Use 'isa pop' to return to 'ahmed-masud'
```

### **Breadcrumb Trail**

```bash
$ isa breadcrumbs
cybernetic-engrams → ahmed-masud → *resiliate*
```

The breadcrumb trail shows:
- **Stack contexts**: Plain names (cybernetic-engrams → ahmed-masud)
- **Current context**: Surrounded by asterisks (*resiliate*)

---

## ⚙️ Technical Implementation

### **Files Created**

- **`tools/context_stack.py`** - Core context stack manager
- **`context-stack.sh`** - Shell wrapper script  
- **Enhanced command intent system** - Natural language support
- **Enhanced command handler** - Integration with ISA workflow

### **State Management**

- **Stack State**: `~/.config/isa/.context_stack.json`
- **Current Context**: `~/.config/isa/.current_context`
- **Automatic Persistence**: State saved after every operation

### **Integration Points**

- Uses existing `load-context.sh` for context loading
- Integrates with ISA's natural language command system
- Works with semantic search and AI query features
- Compatible with all existing ISA workflows

---

## 🎛️ Advanced Features

### **Stack History**

```bash
# Show recent context history
python3 tools/context_stack.py history

📜 Recent Context History
========================================
  resiliate (2025-10-13 18:16:42)
  ahmed-masud (2025-10-13 18:15:32)
  cybernetic-engrams (2025-10-13 18:10:45)
```

### **Stack Inspection**

```bash
# Peek at top of stack without popping
python3 tools/context_stack.py peek
# Output: Top of stack: ahmed-masud

# Show detailed stack with timestamps
isa stack
# Shows full stack with push times
```

### **Stack Maintenance**

```bash
# Clear entire stack (nuclear option)
python3 tools/context_stack.py clear
# Output: 🗑️  Cleared 3 context(s) from stack

# Manual stack inspection
cat ~/.config/isa/.context_stack.json
```

---

## 🔧 Troubleshooting

### **Common Issues**

1. **"Context not found" Error**
   ```bash
   # Check available contexts
   isa contexts
   
   # Use exact context name
   isa push cybernetic-engrams  # Not cybernetic-engram
   ```

2. **"Stack is empty" when popping**
   ```bash
   # Check stack status first
   isa stack
   
   # If empty, just use regular load
   isa load previous-context
   ```

3. **Natural language not working**
   ```bash
   # Use enhanced command handler directly
   python3 tools/enhanced_command_handler.py push context-name
   
   # Or use traditional commands
   isa push context-name
   ```

### **State Recovery**

```bash
# If state gets corrupted, reset manually:
rm ~/.config/isa/.context_stack.json
rm ~/.config/isa/.current_context

# Then reload your current context
isa load your-context
```

---

## 🎯 Integration with Existing ISA Features

### **AI Queries with Context Stack**

```bash
# Push to a project context for AI analysis
isa push isa-ollama-integration
computer ask "What are the next steps for this project?"

# Return to previous context
isa pop
computer ask "How does this relate to cybernetic engrams?"
```

### **Semantic Search Across Stack**

```bash
# Search works in current context regardless of stack
computer search for "deployment"
# Searches current context (top of navigation)

# Stack doesn't affect semantic search behavior
isa push different-context
computer search for "same query"  # Searches different-context
```

### **Context-Aware AI with Stack**

All AI features work normally with the stack system:
- Context-aware queries use the currently loaded context
- Semantic search operates on the active context
- AI analysis focuses on current context priorities
- Stack provides navigation, AI provides intelligence

---

## 🏗️ Best Practices

### **1. Use Push/Pop for Temporary Context Switches**
```bash
# Good: Temporary exploration
isa push related-context    # Quick look
# Do some research...
isa pop                     # Return to work

# Avoid: Permanent context changes
# Use regular 'isa load' for that
```

### **2. Keep Stack Shallow**
- Recommended depth: 2-3 contexts maximum
- Deeper stacks become hard to track mentally
- Use breadcrumbs to see your navigation trail

### **3. Clear Stack Periodically**
```bash
# At end of research session
python3 tools/context_stack.py clear
```

### **4. Use Natural Language for Clarity**
```bash
# Clear intent
computer push context project-name
computer go back

# Less clear but works
isa push project-name
isa pop
```

---

## 🎉 Examples in Action

### **Real Workflow Example**

```bash
# Start your day in personal context
isa load ahmed-masud
computer ask "What should I prioritize today?"

# Temporarily explore a technical concept
computer push context cybernetic-engrams  
computer ask "What are the key implementation approaches?"

# Dive into a specific project
computer push context resiliate
computer ask "How does resiliate use cybernetic engrams?"

# Check the trail
computer show breadcrumbs
# ahmed-masud → cybernetic-engrams → *resiliate*

# Return to work
computer go back  # Back to cybernetic-engrams
computer go back  # Back to ahmed-masud

# Continue with priorities
computer ask "Based on my research, what should I work on?"
```

---

## 📚 Related Documentation

- **[ISA-CONTEXT-COMMANDS.md](ISA-CONTEXT-COMMANDS.md)** - Core context commands
- **[GETTING-STARTED.md](GETTING-STARTED.md)** - ISA basics
- **[ISA-SEMANTIC-SETUP.md](ISA-SEMANTIC-SETUP.md)** - Semantic search setup

---

## 🎯 Summary

The context stack feature transforms ISA from a simple context switcher into a powerful navigation system that remembers where you've been and makes it easy to return. Perfect for research sessions, project exploration, and maintaining workflow continuity.

**Key Benefits:**
- 🧠 **Mental Model**: Stack mirrors how you naturally think about context
- 🔄 **Workflow Preservation**: Never lose your place during exploration  
- 🎯 **Focused Research**: Dive deep while keeping return path clear
- 🗣️ **Natural Interface**: Intuitive commands that match your intent

**Start using it today:**
```bash
isa push interesting-context
# Explore, learn, research...  
isa pop
# Back to where you started! 
```

---

**Last Updated**: 2025-10-13  
**ISA Version**: 1.0+ with Context Stack  
**Feature Status**: ✅ Production Ready