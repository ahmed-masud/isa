#!/bin/sh
# ISA-Ollama Common Configuration
# Shared variables and configuration for all shell implementations

# Configuration
# Default to localhost if running on helm server, otherwise use remote IP
if [ "$(hostname)" = "helm.ahmed.saf.ai" ] || [ "$(hostname -f)" = "helm.ahmed.saf.ai" ]; then
    OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
else
    OLLAMA_HOST="${OLLAMA_HOST:-http://192.168.1.161:11434}"
fi

AI_MODEL="${AI_MODEL:-phi3:mini}"
AI_TIMEOUT="${AI_TIMEOUT:-30}"
AI_MAX_TOKENS="${AI_MAX_TOKENS:-1000}"

# Export configuration for use by implementations
export OLLAMA_HOST
export AI_MODEL
export AI_TIMEOUT
export AI_MAX_TOKENS

# Colors for output (using printf-compatible format)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Export colors
export RED GREEN YELLOW BLUE NC