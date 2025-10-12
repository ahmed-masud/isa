#!/bin/bash
# ISA-Ollama Bash-specific Functions
# Bash implementation of Ollama client functions

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

# List available models
ollama_model_list() {
    curl -s "${OLLAMA_HOST}/api/tags" 2>/dev/null | \
    python3 -c "import json, sys; data=json.load(sys.stdin); [print(model['name']) for model in data.get('models', [])]" 2>/dev/null
}

# Basic query to Ollama
ollama_query() {
    local prompt="$1"
    local model="${2:-$AI_MODEL}"
    
    if [ -z "$prompt" ]; then
        echo -e "${RED}Error: No prompt provided${NC}" >&2
        return 1
    fi
    
    # Use Python client (more reliable)
    local python_client="${ISA_ROOT}/tools/ollama_client.py"
    if [ -f "$python_client" ]; then
        local cmd_args=()
        if [ -n "$model" ] && [ "$model" != "$AI_MODEL" ]; then
            cmd_args+=("--model" "$model")
        fi
        
        python3 "$python_client" "${cmd_args[@]}" "$prompt" 2>/dev/null
        return $?
    fi
    
    # Fallback to original curl method if Python client not available
    echo -e "${YELLOW}Warning: Using fallback curl method${NC}" >&2
    
    # Check if Ollama is available
    if ! ollama_health_check; then
        echo -e "${RED}Error: Cannot connect to Ollama at ${OLLAMA_HOST}${NC}" >&2
        return 1
    fi
    
    # Make API request
    local response
    response=$(curl -s --max-time "$AI_TIMEOUT" \
        -H "Content-Type: application/json" \
        -d "{\"model\": \"$model\", \"prompt\": \"$prompt\", \"stream\": false}" \
        "${OLLAMA_HOST}/api/generate" 2>/dev/null)
    local curl_exit_code=$?
    
    if [ $curl_exit_code -eq 0 ] && [ -n "$response" ]; then
        # Extract response text using python
        local parsed_response
        parsed_response=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('response', ''))
except Exception as e:
    print('JSON_PARSE_ERROR: ' + str(e), file=sys.stderr)
    sys.exit(1)" 2>/dev/null)
        local parse_exit_code=$?
        if [ $parse_exit_code -eq 0 ] && [ -n "$parsed_response" ]; then
            echo "$parsed_response"
        else
            echo -e "${RED}Error: Failed to parse JSON response${NC}" >&2
            return 1
        fi
    else
        echo -e "${RED}Error: Failed to get response from Ollama${NC}" >&2
        return 1
    fi
}

# Context-aware query - includes ISA context information
ollama_context_query() {
    local query="$1"
    local context_file="$2"
    local model="${3:-$AI_MODEL}"
    
    if [ -z "$query" ]; then
        echo -e "${RED}Error: No query provided${NC}" >&2
        return 1
    fi
    
    # Use Python client if available (supports context files natively)
    local python_client="${ISA_ROOT}/tools/ollama_client.py"
    if [ -f "$python_client" ]; then
        local cmd_args=()
        
        if [ -n "$model" ] && [ "$model" != "$AI_MODEL" ]; then
            cmd_args+=("--model" "$model")
        fi
        
        if [ -n "$context_file" ] && [ -f "$context_file" ]; then
            cmd_args+=("--context-file" "$context_file")
        fi
        
        python3 "$python_client" "${cmd_args[@]}" "$query" 2>/dev/null
        return $?
    fi
    
    # Fallback to building prompt manually
    local full_prompt
    if [ -n "$context_file" ] && [ -f "$context_file" ]; then
        local context_data
        context_data=$(head -50 "$context_file" 2>/dev/null)
        full_prompt="Context: $context_data

Query: $query

Please provide a helpful response based on the context provided."
    else
        full_prompt="$query"
    fi
    
    ollama_query "$full_prompt" "$model"
}

# Quick AI ask function - for "computer ask" command
isa_ai_ask() {
    local question="$*"
    
    if [ -z "$question" ]; then
        echo -e "${YELLOW}💭 Ask me anything!${NC}"
        echo "Usage: computer ask \"your question here\""
        echo "Example: computer ask \"What should I prioritize today?\""
        return 0
    fi
    
    echo -e "${BLUE}🤖 Thinking...${NC}"
    echo ""
    
    local response
    response=$(ollama_query "$question")
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo -e "${GREEN}💡 AI Response:${NC}"
        echo "$response" | fold -w 80 -s
    else
        echo -e "${RED}❌ Sorry, I couldn't process your question right now.${NC}"
        return 1
    fi
}

# Analyze current ISA context with AI
isa_ai_analyze() {
    local context_type="${1:-urgent}"
    local context_path
    
    case "$context_type" in
        urgent|priorities)
            context_path="${ISA_CONTEXTS}/people/ahmed-masud/PRIORITIES.md"
            ;;
        me|self)
            context_path="${ISA_CONTEXTS}/people/ahmed-masud/README.md"
            ;;
        current|project)
            # Use current loaded context if available
            context_path="${ISA_CONTEXTS}/things/isa-ollama-integration/README.md"
            ;;
        *)
            echo -e "${YELLOW}Available analysis types: urgent, priorities, me, current${NC}"
            return 0
            ;;
    esac
    
    if [ ! -f "$context_path" ]; then
        echo -e "${RED}Context file not found: $context_path${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🔍 Analyzing $context_type context...${NC}"
    echo ""
    
    local query="Please analyze this context and provide actionable insights, suggestions, and next steps:"
    local response
    response=$(ollama_context_query "$query" "$context_path")
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo -e "${GREEN}📊 AI Analysis:${NC}"
        echo "$response" | fold -w 80 -s
    else
        echo -e "${RED}❌ Analysis failed${NC}"
        return 1
    fi
}

# Suggest next actions based on context
isa_ai_suggest() {
    local project="current"
    
    # Parse arguments to support both --project=value and positional args
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
            -*)
                echo -e "${RED}Error: Unknown flag $1${NC}" >&2
                return 1
                ;;
            *)
                # Positional argument (backward compatibility)
                project="$1"
                shift
                ;;
        esac
    done
    
    echo -e "${BLUE}💡 Getting AI suggestions for: $project${NC}"
    echo ""
    
    local context_path
    case "$project" in
        current|isa|ollama)
            context_path="${ISA_CONTEXTS}/things/isa-ollama-integration/PRIORITIES.md"
            ;;
        email|integration)
            # Use main priorities for email integration project
            context_path="${ISA_CONTEXTS}/people/ahmed-masud/PRIORITIES.md"
            ;;
        chatgpt|frontend)
            context_path="${ISA_CONTEXTS}/people/ahmed-masud/README.md"
            ;;
        *)
            context_path="${ISA_CONTEXTS}/people/ahmed-masud/PRIORITIES.md"
            ;;
    esac
    
    local query="Based on this project context, what are the best next steps and priorities? Please be specific and actionable."
    local response
    response=$(ollama_context_query "$query" "$context_path")
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo -e "${GREEN}🎯 AI Suggestions:${NC}"
        echo "$response" | fold -w 80 -s
    else
        echo -e "${RED}❌ Could not generate suggestions${NC}"
        return 1
    fi
}

# AI status check
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
    
    # Show available models
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
}

# Export functions for bash
export -f ollama_health_check
export -f ollama_model_list
export -f ollama_query
export -f ollama_context_query
export -f isa_ai_ask
export -f isa_ai_analyze
export -f isa_ai_suggest
export -f isa_ai_status