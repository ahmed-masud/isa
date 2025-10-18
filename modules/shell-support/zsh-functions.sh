#!/bin/bash
# ISA-Ollama Bash Functions with Semantic Context Integration
# Enhanced version with vector database semantic search

# Source common configuration
. "${ISA_ROOT}/modules/common/ollama-common.sh"

# Health check - verify Ollama is accessible
ollama_health_check() {
    if curl -s --connect-timeout 5 "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check semantic context service availability
semantic_context_available() {
    local python_client="${ISA_ROOT}/tools/ollama_client.py"
    if [ -f "$python_client" ]; then
        python3 "$python_client" --test-semantic >/dev/null 2>&1
        return $?
    fi
    return 1
}

# List available models
ollama_model_list() {
    curl -s "${OLLAMA_HOST}/api/tags" 2>/dev/null | \
    python3 -c "import json, sys; data=json.load(sys.stdin); [print(model['name']) for model in data.get('models', [])]" 2>/dev/null
}

# Basic query to Ollama (no context)
ollama_query_basic() {
    local prompt="$1"
    local model="${2:-$AI_MODEL}"
    
    if [ -z "$prompt" ]; then
        echo -e "${RED}Error: No prompt provided${NC}" >&2
        return 1
    fi
    
    local python_client="${ISA_ROOT}/tools/ollama_client.py"
    if [ -f "$python_client" ]; then
        local cmd_args=("--disable-semantic")
        if [ -n "$model" ] && [ "$model" != "$AI_MODEL" ]; then
            cmd_args+=("--model" "$model")
        fi
        
        python3 "$python_client" "${cmd_args[@]}" "$prompt" 2>/dev/null
        return $?
    fi
    
    echo -e "${RED}Error: Python client not available${NC}" >&2
    return 1
}

# Enhanced query with semantic context (NEW!)
ollama_query() {
    local prompt="$1"
    local model="${2:-$AI_MODEL}"
    local context_type="$3"  # Optional: person, project, priorities
    
    if [ -z "$prompt" ]; then
        echo -e "${RED}Error: No prompt provided${NC}" >&2
        return 1
    fi
    
    # Use Python client with semantic context
    local python_client="${ISA_ROOT}/tools/ollama_client.py"
    if [ -f "$python_client" ]; then
        local cmd_args=()
        
        if [ -n "$model" ] && [ "$model" != "$AI_MODEL" ]; then
            cmd_args+=("--model" "$model")
        fi
        
        if [ -n "$context_type" ]; then
            cmd_args+=("--context-type" "$context_type")
        fi
        
        # The Python client will automatically use semantic context if available
        python3 "$python_client" "${cmd_args[@]}" "$prompt" 2>/dev/null
        return $?
    fi
    
    echo -e "${RED}Error: Python client not available${NC}" >&2
    return 1
}

# Context-aware query - supports both file and semantic contexts
ollama_context_query() {
    local query="$1"
    local context_file="$2"
    local model="${3:-$AI_MODEL}"
    
    if [ -z "$query" ]; then
        echo -e "${RED}Error: No query provided${NC}" >&2
        return 1
    fi
    
    local python_client="${ISA_ROOT}/tools/ollama_client.py"
    if [ -f "$python_client" ]; then
        local cmd_args=()
        
        if [ -n "$model" ] && [ "$model" != "$AI_MODEL" ]; then
            cmd_args+=("--model" "$model")
        fi
        
        # If context file provided, use it; otherwise use semantic context
        if [ -n "$context_file" ] && [ -f "$context_file" ]; then
            cmd_args+=("--context-file" "$context_file")
        fi
        
        python3 "$python_client" "${cmd_args[@]}" "$query" 2>/dev/null
        return $?
    fi
    
    echo -e "${RED}Error: Python client not available${NC}" >&2
    return 1
}

# Quick AI ask function - NOW WITH SEMANTIC CONTEXT!
isa_ai_ask() {
    local question="$*"
    
    if [ -z "$question" ]; then
        echo -e "${YELLOW}💭 Ask me anything!${NC}"
        echo "Usage: computer ask \"your question here\""
        echo "Example: computer ask \"What should I prioritize today?\""
        echo ""
        
        if semantic_context_available; then
            echo -e "${GREEN}✨ Semantic context enabled - I know your priorities and projects!${NC}"
        fi
        return 0
    fi
    
    echo -e "${BLUE}🤖 Thinking...${NC}"
    
    # Show semantic context status
    if semantic_context_available; then
        echo -e "${GREEN}🔍 Searching your knowledge base...${NC}"
    fi
    echo ""
    
    local response
    # ollama_query now automatically uses semantic context
    response=$(ollama_query "$question")
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo -e "${GREEN}💡 AI Response:${NC}"
        echo "$response" | fold -w 80 -s
    else
        echo -e "${RED}❌ Sorry, I couldn't process your question right now.${NC}"
        return 1
    fi
}

# Analyze current ISA context with AI - ENHANCED WITH SEMANTIC SEARCH
isa_ai_analyze() {
    local context_type="${1:-urgent}"
    
    echo -e "${BLUE}🔍 Analyzing $context_type context...${NC}"
    
    if semantic_context_available; then
        echo -e "${GREEN}✨ Using semantic context search${NC}"
    fi
    echo ""
    
    local query
    case "$context_type" in
        urgent|priorities)
            query="Analyze my urgent priorities and tasks. What should I focus on immediately?"
            ;;
        me|self)
            query="Analyze my personal context, workflows, and preferences. What insights can you provide?"
            ;;
        current|project)
            query="Analyze my current projects and their status. What are the next steps?"
            ;;
        *)
            echo -e "${YELLOW}Available analysis types: urgent, priorities, me, current${NC}"
            return 0
            ;;
    esac
    
    local response
    # Use semantic context with appropriate type filter
    local semantic_type
    case "$context_type" in
        urgent|priorities) semantic_type="priorities" ;;
        me|self) semantic_type="person" ;;
        current|project) semantic_type="project" ;;
    esac
    
    response=$(ollama_query "$query" "$AI_MODEL" "$semantic_type")
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo -e "${GREEN}📊 AI Analysis:${NC}"
        echo "$response" | fold -w 80 -s
    else
        echo -e "${RED}❌ Analysis failed${NC}"
        return 1
    fi
}

# Suggest next actions based on context - ENHANCED WITH SEMANTIC SEARCH
isa_ai_suggest() {
    local project="current"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --project=*)
                project="${1#--project=}"
                shift
                ;;
            --project)
                if [[ -n $2 && $2 != --* ]]; then
                    project="$2"
                    shift 2
                else
                    echo -e "${RED}Error: --project requires a value${NC}" >&2
                    return 1
                fi
                ;;
            *)
                project="$1"
                shift
                ;;
        esac
    done
    
    echo -e "${BLUE}💡 Getting AI suggestions for: $project${NC}"
    
    if semantic_context_available; then
        echo -e "${GREEN}✨ Using semantic context search${NC}"
    fi
    echo ""
    
    local query="Based on my project '$project', what are the best next steps and priorities? Please be specific and actionable."
    
    local response
    # Use semantic context with project type filter
    response=$(ollama_query "$query" "$AI_MODEL" "project")
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo -e "${GREEN}🎯 AI Suggestions:${NC}"
        echo "$response" | fold -w 80 -s
    else
        echo -e "${RED}❌ Could not generate suggestions${NC}"
        return 1
    fi
}

# AI status check - ENHANCED WITH SEMANTIC CONTEXT STATUS
isa_ai_status() {
    echo -e "${BLUE}🤖 ISA-AI Integration Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check Ollama connection
    if ollama_health_check; then
        echo -e "🌐 Ollama Connection: ${GREEN}✅ Connected${NC}"
        echo -e "📍 Endpoint: $OLLAMA_HOST"
    else
        echo -e "🌐 Ollama Connection: ${RED}❌ Failed${NC}"
        echo -e "📍 Endpoint: $OLLAMA_HOST (unreachable)"
        return 1
    fi
    
    # Show current model
    echo -e "🧠 AI Model: ${GREEN}$AI_MODEL${NC}"
    
    # Check semantic context status
    echo ""
    if semantic_context_available; then
        echo -e "🔍 Semantic Context: ${GREEN}✅ Available${NC}"
        
        # Get vector database stats
        local python_client="${ISA_ROOT}/tools/ollama_client.py"
        local stats=$(python3 "$python_client" --test-semantic 2>&1 | grep "Vector database stats")
        if [ -n "$stats" ]; then
            echo -e "   $stats"
        fi
    else
        echo -e "🔍 Semantic Context: ${YELLOW}⚠️  Not Available${NC}"
        echo -e "   ${YELLOW}Using basic queries without context enhancement${NC}"
    fi
    
    # Show available models
    echo ""
    echo -e "📋 Available Models:"
    local models
    models=$(ollama_model_list)
    if [ -n "$models" ]; then
        echo "$models" | head -5 | sed 's/^/  - /'
        local total_count
        total_count=$(echo "$models" | wc -l)
        if [ "$total_count" -gt 5 ]; then
            echo "  ... and $((total_count - 5)) more"
        fi
    else
        echo "  (Could not retrieve model list)"
    fi
    
    echo ""
    echo -e "${GREEN}💡 Try these commands:${NC}"
    echo "  computer ask \"What should I work on next?\""
    echo "  isa ai-analyze urgent"
    echo "  computer suggest --project=current"
    
    if semantic_context_available; then
        echo ""
        echo -e "${GREEN}✨ Semantic context is active!${NC}"
        echo "  Your AI knows about your priorities, projects, and preferences"
    fi
}

# Note: In zsh, functions are automatically available to subshells
# No need to export functions like in bash
