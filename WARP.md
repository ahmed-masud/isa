# Warp AI Agent Guidelines - ISA-First Approach

## Core Principle
**Use ISA system first** - Prioritize local semantic search and AI capabilities over external queries to save tokens and leverage your knowledge base.

## Primary Tools (Use These First)

### Natural Language Interface
```bash
computer ask "question"                    # AI analysis using semantic context
computer search for "topic"               # Find information in contexts
computer show stats                        # System status
computer check health                      # Service verification
computer sync                              # Update contexts
computer rebuild                           # Rebuild index
```

### Direct ISA Commands
```bash
isa ctx-search "query"                     # Semantic search across contexts
isa ctx-add /path/to/file.md              # Add new context
isa ctx-sync                               # Sync all contexts
isa ctx-stats                              # Database statistics
isa ctx-health                             # Health check
isa ctx-rebuild                            # Rebuild vector database
```

## Decision Flow
1. **First**: Check if ISA semantic search can answer the question
2. **Second**: Use `computer ask` for AI analysis with your context
3. **Last Resort**: External queries only if ISA lacks the information

## Context Management
- Always add new documents to appropriate context directories
- Use singular form for context names (e.g., `cybernetic-engram`)
- Create relationships between contexts in README files
- Sync contexts after adding new files: `isa ctx-add` or `isa ctx-sync`

## File Operations
- Avoid shell exclamation marks to prevent syntax errors
- Use absolute paths when possible
- Create proper directory structures under `~/.config/isa/contexts/`

## Context Structure
```
~/.config/isa/contexts/
├── people/[person-name]/
├── places/[location-name]/
└── things/[concept-name]/
```

## Shell Efficiency
- Prefer ISA commands over manual file operations
- Use semantic search instead of grep when possible
- Let ISA handle context relationships and indexing

## Token Conservation
- ISA system uses local AI and semantic search
- Reduces external API calls and token usage
- Maintains privacy by keeping queries local
- Faster responses from local semantic database

---

**Load this file on shell startup to remind Warp AI agent of ISA-first approach**  
**Last Updated**: 2025-10-13