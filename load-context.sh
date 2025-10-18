#!/bin/bash
# ISA Context Loader
# Usage: ./load-context.sh <context-name>
# Example: ./load-context.sh ahmed-masud

CONTEXT_NAME="${1:-ahmed-masud}"
ISA_ROOT="${ISA_ROOT:-$HOME/projects/isa}"
CONTEXT_DIR="${ISA_CONTEXTS:-$HOME/.config/isa/contexts}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Loading context: ${CONTEXT_NAME}${NC}"
echo ""

# Search for context in people, places, things, and sub-contexts
FOUND=false
CONTEXT_PATH=""
SUB_CONTEXT_DIR="$HOME/.config/isa/sub-contexts"

for TYPE in people places things; do
    if [ -d "$CONTEXT_DIR/$TYPE/$CONTEXT_NAME" ]; then
        FOUND=true
        CONTEXT_PATH="$CONTEXT_DIR/$TYPE/$CONTEXT_NAME"
        echo -e "${GREEN}✓ Found context in: $TYPE${NC}"
        echo -e "${BLUE}  Location: $CONTEXT_PATH${NC}"
        echo ""
        break
    fi
done

# If not found in standard locations, check sub-contexts
if [ "$FOUND" = false ] && [ -d "$SUB_CONTEXT_DIR/$CONTEXT_NAME" ]; then
    FOUND=true
    CONTEXT_PATH="$SUB_CONTEXT_DIR/$CONTEXT_NAME"
    echo -e "${GREEN}✓ Found context in: sub-contexts${NC}"
    echo -e "${BLUE}  Location: $CONTEXT_PATH${NC}"
    echo ""
fi

if [ "$FOUND" = false ]; then
    echo -e "${RED}✗ Context not found: $CONTEXT_NAME${NC}"
    echo ""
    echo "Available contexts:"
    for TYPE in people places things; do
        if [ -d "$CONTEXT_DIR/$TYPE" ]; then
            echo -e "${YELLOW}  $TYPE:${NC}"
            ls -1 "$CONTEXT_DIR/$TYPE" 2>/dev/null | sed 's/^/    /'
        fi
    done
    if [ -d "$SUB_CONTEXT_DIR" ]; then
        echo -e "${YELLOW}  sub-contexts:${NC}"
        ls -1 "$SUB_CONTEXT_DIR" 2>/dev/null | sed 's/^/    /'
    fi
    exit 1
fi

# Display context information
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "$CONTEXT_PATH/README.md" ]; then
    echo -e "${GREEN}📄 README.md${NC}"
    echo ""
    head -n 30 "$CONTEXT_PATH/README.md"
    echo ""
    echo -e "${BLUE}... (showing first 30 lines, see full file at: $CONTEXT_PATH/README.md)${NC}"
    echo ""
fi

if [ -f "$CONTEXT_PATH/PRIORITIES.md" ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}🎯 PRIORITIES.md${NC}"
    echo ""
    
    # Show urgent section
    if grep -q "URGENT" "$CONTEXT_PATH/PRIORITIES.md"; then
        echo -e "${RED}🔥 URGENT ITEMS:${NC}"
        grep -A 20 "## 🔥" "$CONTEXT_PATH/PRIORITIES.md" | head -n 25
        echo ""
    fi
    
    echo -e "${BLUE}... (see full priorities at: $CONTEXT_PATH/PRIORITIES.md)${NC}"
    echo ""
fi

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}📂 Files in context:${NC}"
ls -lh "$CONTEXT_PATH" | tail -n +2
echo ""

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}💡 Quick Commands:${NC}"
echo ""
echo "  # View full context"
echo "  cat $CONTEXT_PATH/README.md"
echo ""
echo "  # View priorities"
echo "  cat $CONTEXT_PATH/PRIORITIES.md"
echo ""
echo "  # Edit context"
echo "  \$EDITOR $CONTEXT_PATH/README.md"
echo ""
echo "  # View all TODOs"
echo "  cat $ISA_ROOT/TODO.md"
echo ""

# Check for project links in priorities
if [ -f "$CONTEXT_PATH/PRIORITIES.md" ]; then
    if grep -q "PROJECT LOCATIONS" "$CONTEXT_PATH/PRIORITIES.md"; then
        echo -e "${BLUE}📍 Related Project Locations:${NC}"
        grep -A 20 "PROJECT LOCATIONS" "$CONTEXT_PATH/PRIORITIES.md" | grep "^/Users" | sed 's/^/  /'
        echo ""
    fi
fi

# Update current context tracking for stack management
echo "$CONTEXT_NAME" > "$HOME/.config/isa/.current_context"

echo -e "${GREEN}✓ Context loaded successfully${NC}"
