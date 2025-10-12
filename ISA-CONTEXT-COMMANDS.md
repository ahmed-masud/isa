# ISA Semantic Context Commands - Quick Reference

## 🎯 Overview

ISA now provides high-level commands for managing the semantic context system without needing to use low-level Python scripts.

## 📋 Available Commands

### Context Statistics
```bash
isa context-stats
# or short form:
isa ctx-stats
```
Shows vector database statistics including:
- Total chunks indexed
- Training status
- Storage location

**Example output:**
```
📊 Vector Database Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Chunks: 237
  Trained: True
  Storage: simple_vector_storage
```

---

### Health Check
```bash
isa context-health
# or short form:
isa ctx-health
```
Checks status of all semantic context services:
- Vector Database (192.168.1.161:8000)
- Ollama AI (192.168.1.161:11434)
- Context Watcher (local)

**Example output:**
```
🏥 Checking semantic context services...

Vector Database (192.168.1.161:8000):
  ✅ Healthy

Ollama AI (192.168.1.161:11434):
  ✅ Healthy

Context Watcher (local):
  ✅ Running
```

---

### Semantic Search
```bash
isa context-search "your search query"
# or short form:
isa ctx-search "deployment procedures"
```
Performs semantic search across all your contexts, returning the most relevant results with relevance scores.

**Example:**
```bash
isa ctx-search "how to deploy to helm"
```

**Example output:**
```
🔍 Semantic Search: how to deploy to helm

Found 3 relevant contexts:
==================================================

1. things/isa-helm-deployment/README.md (Deployment) - Relevance: 0.89
----------------------------------------
[Relevant content displayed]

2. things/isa-ollama-integration/PRIORITIES.md (Remote Integration) - Relevance: 0.46
----------------------------------------
[Relevant content displayed]
```

---

### Sync All Contexts
```bash
isa context-sync
# or short form:
isa ctx-sync
```
Processes all markdown files in your contexts directory and syncs them to the vector database.

**Use when:**
- You've added new context files
- You've made significant updates to existing contexts
- You want to ensure all contexts are indexed

**Example output:**
```
🔄 Processing contexts into vector database...
  Processing: README.md
  Processing: PRIORITIES.md
  Processing: DEPLOYMENT.md
✅ Processed 5 context files
```

---

### Add Single Context
```bash
isa context-add <path-to-markdown-file>
# or short form:
isa ctx-add ~/.config/isa/contexts/things/my-project/README.md
```
Adds or updates a single context file in the vector database.

**Use when:**
- You've created a new context file
- You've updated a specific context and want immediate indexing

---

### Rebuild Index
```bash
isa context-rebuild
# or short form:
isa ctx-rebuild
```
Rebuilds the entire vector database index. Use this if the index seems corrupted or after bulk changes.

**Example output:**
```
🔨 Rebuilding vector database index...
✅ Rebuilt: 237 chunks
```

---

## 🔗 Integration with AI Commands

The semantic context system works automatically with existing AI commands:

```bash
# AI automatically uses semantic context
computer ask "What should I work on next?"

# AI analysis with semantic context
isa ai-analyze urgent

# AI suggestions with project context
computer suggest --project=isa-ollama

# Check if semantic context is active
isa ai-status
```

When semantic context is available, you'll see:
```
🔍 Semantic Context: ✅ Available
   📊 Vector database stats: {'total_chunks': 237, 'is_trained': True}
```

---

## 💡 Common Workflows

### Daily Use
```bash
# Morning check
isa ctx-health                          # Ensure services are running
isa ctx-stats                           # See current context state
computer ask "What are my priorities?"  # AI uses semantic context
```

### After Adding New Context
```bash
# Add new context immediately
isa ctx-add ~/.config/isa/contexts/things/new-project/README.md

# Or sync all contexts
isa ctx-sync
```

### Troubleshooting
```bash
# Check service health
isa ctx-health

# Rebuild if something seems wrong
isa ctx-rebuild

# Check stats to verify
isa ctx-stats
```

### Finding Information
```bash
# Semantic search is more powerful than grep
isa ctx-search "deployment procedures"
isa ctx-search "AI integration steps"
isa ctx-search "priority tasks"

# Then ask AI about the results
computer ask "Based on my deployment procedures, what should I do first?"
```

---

## 📊 Command Comparison

### Before (Low-level Python)
```bash
# Check stats
curl -s http://192.168.1.161:8000/stats | python3 -m json.tool

# Add context
python3 ~/projects/isa/tools/chunk_and_embed.py ~/path/to/file.md

# Search
python3 ~/projects/isa/tools/semantic_context.py "query" --format text

# Health check
curl -s http://192.168.1.161:8000/health
python3 ~/projects/isa/tools/ollama_client.py --health-check
```

### After (High-level ISA)
```bash
# Check stats
isa ctx-stats

# Add context
isa ctx-add ~/path/to/file.md

# Search
isa ctx-search "query"

# Health check
isa ctx-health
```

---

## 🎯 Best Practices

1. **Regular Health Checks**: Run `isa ctx-health` periodically to ensure services are running

2. **Keep Contexts Synced**: After editing context files, run `isa ctx-sync` or let the context watcher handle it automatically

3. **Use Semantic Search**: Instead of grepping through files, use `isa ctx-search` for better results

4. **Leverage AI Integration**: Use `computer ask` instead of manually searching - the AI will use semantic context automatically

5. **Monitor Growth**: Check `isa ctx-stats` occasionally to see how your knowledge base is growing

---

## 📚 Related Documentation

- `ISA-SEMANTIC-SETUP.md` - Complete semantic context setup guide
- `VECTOR-DATABASE-DESIGN.md` - Architecture and design documentation
- `RELEASE-NOTES.md` - Version history and features
- `GIT-FLOW-SETUP.md` - Development workflow

---

## 🆘 Troubleshooting

### "Vector service not available"
```bash
# On Helm server
ssh 192.168.1.161
cd /home/masud/projects/isa
python3 vector_service_simple.py > simple_vector_service.log 2>&1 &
```

### "Context watcher not running"
```bash
# On local machine
cd ~/projects/isa
python3 tools/context_watcher.py --verbose > context_watcher.log 2>&1 &
```

### "Semantic context not active in AI"
```bash
# Test the connection
python3 ~/projects/isa/tools/ollama_client.py --test-semantic

# Check health
isa ctx-health
```

---

**With these commands, managing your ISA semantic context system is as easy as any other ISA operation!** 🚀