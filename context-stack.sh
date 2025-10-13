#!/bin/bash
# ISA Context Stack Operations
# Integrates with ISA command system for push/pop context management

ISA_ROOT="${ISA_ROOT:-$HOME/projects/isa}"
PYTHON_SCRIPT="$ISA_ROOT/tools/context_stack.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Error: Context stack manager not found at $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "ISA Context Stack Operations"
    echo ""
    echo "USAGE:"
    echo "  isa push <context>     Push current context and load new one"
    echo "  isa pop               Pop context from stack"
    echo "  isa stack             Show current context stack"
    echo "  isa peek              Peek at top of stack"
    echo "  isa breadcrumbs       Show context breadcrumb trail"
    echo ""
    echo "NATURAL LANGUAGE:"
    echo "  computer push context <name>    # Same as 'isa push <name>'"
    echo "  computer pop context           # Same as 'isa pop'"
    echo "  computer show stack            # Same as 'isa stack'"
    echo "  computer go back               # Same as 'isa pop'"
    echo ""
    echo "EXAMPLES:"
    echo "  isa push ahmed-masud           # Push cybernetic-engrams, load ahmed-masud"
    echo "  isa pop                        # Return to cybernetic-engrams"
    echo "  isa stack                      # Show current stack status"
}

# Check for command
COMMAND="$1"
shift

case "$COMMAND" in
    "push")
        if [ -z "$1" ]; then
            echo -e "${RED}Error: Context name required${NC}"
            echo "Usage: isa push <context-name>"
            exit 1
        fi
        
        # Set current context before push operation
        if [ -n "$ISA_CURRENT_CONTEXT" ]; then
            echo "$ISA_CURRENT_CONTEXT" > ~/.config/isa/.current_context
        fi
        
        # Execute push operation
        python3 "$PYTHON_SCRIPT" push "$1"
        EXIT_CODE=$?
        
        # Update shell environment variable if successful
        if [ $EXIT_CODE -eq 0 ]; then
            export ISA_CURRENT_CONTEXT="$1"
        fi
        
        exit $EXIT_CODE
        ;;
    
    "pop")
        # Execute pop operation
        python3 "$PYTHON_SCRIPT" pop
        EXIT_CODE=$?
        
        # Update shell environment variable if successful
        if [ $EXIT_CODE -eq 0 ]; then
            # Get the new current context
            if [ -f ~/.config/isa/.current_context ]; then
                export ISA_CURRENT_CONTEXT=$(cat ~/.config/isa/.current_context)
            fi
        fi
        
        exit $EXIT_CODE
        ;;
    
    "stack")
        python3 "$PYTHON_SCRIPT" stack
        ;;
    
    "peek")
        python3 "$PYTHON_SCRIPT" peek
        ;;
    
    "clear")
        python3 "$PYTHON_SCRIPT" clear
        ;;
    
    "history")
        python3 "$PYTHON_SCRIPT" history "$@"
        ;;
    
    "breadcrumbs")
        python3 "$PYTHON_SCRIPT" breadcrumbs
        ;;
    
    "help"|"-h"|"--help"|"")
        show_usage
        ;;
    
    *)
        echo -e "${RED}Unknown context stack command: $COMMAND${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac