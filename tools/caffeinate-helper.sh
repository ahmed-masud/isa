#!/bin/bash
# caffeinate-helper.sh
# Prevents macOS from sleeping during long operations
# Location: ~/dev-notes/vibe-dev/tools/caffeinate-helper.sh

# Usage:
#   ./caffeinate-helper.sh <command>
#   Example: ./caffeinate-helper.sh "sleep 3600"

if [[ -z "$1" ]]; then
    echo "Usage: $0 <command>"
    echo "Example: $0 'sleep 3600'"
    echo "Example: $0 'vdev-morning'"
    exit 1
fi

# Run command with caffeinate to prevent sleep
echo "🔋 Running with caffeinate (system won't sleep)..."
caffeinate -disu "$@"
