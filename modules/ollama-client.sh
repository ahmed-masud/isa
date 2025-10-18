#!/bin/sh
# ISA-Ollama Integration Module - Shell Agnostic
# Provides HTTP API client for communicating with Ollama
# Supports bash, zsh, and basic csh/tcsh functionality

# Shell detection and compatibility loader
isa_detect_shell() {
    # Get the parent shell name
    local parent_shell
    if [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$BASH_VERSION" ]; then
        echo "bash"
    elif [ -n "$tcsh" ]; then
        echo "csh"
    else
        # Try to detect from $0 or parent process
        parent_shell=$(ps -p $$ -o comm= 2>/dev/null | sed 's/.*\///')
        case "$parent_shell" in
            zsh*) echo "zsh" ;;
            bash*) echo "bash" ;;
            csh*|tcsh*) echo "csh" ;;
            *) echo "bash" ;;  # Default to bash
        esac
    fi
}

# Load shell-specific implementation
isa_load_shell_functions() {
    local detected_shell
    detected_shell=$(isa_detect_shell)
    
    local shell_impl="${ISA_ROOT}/modules/shell-support/${detected_shell}-functions.sh"
    
    if [ -f "$shell_impl" ]; then
        [[ -n "${ISA_DEBUG}" ]] && echo "Loading ISA Ollama functions for: $detected_shell" >&2
        . "$shell_impl"
        return 0
    else
        [[ -n "${ISA_DEBUG}" ]] && echo "Warning: No shell implementation found for $detected_shell, trying bash fallback" >&2
        local bash_impl="${ISA_ROOT}/modules/shell-support/bash-functions.sh"
        if [ -f "$bash_impl" ]; then
            . "$bash_impl"
            return 0
        else
            echo "Error: No shell implementations found!" >&2
            return 1
        fi
    fi
}

# Load common configuration
if [ -f "${ISA_ROOT}/modules/common/ollama-common.sh" ]; then
    . "${ISA_ROOT}/modules/common/ollama-common.sh"
else
    [[ -n "${ISA_DEBUG}" ]] && echo "Error: Common configuration not found!" >&2
    return 1
fi

# Load the shell-specific implementation
if ! isa_load_shell_functions; then
    [[ -n "${ISA_DEBUG}" ]] && echo "Failed to load shell-specific Ollama functions" >&2
    return 1
fi

# Shell compatibility information
isa_shell_info() {
    local shell
    shell=$(isa_detect_shell)
    echo "ISA Ollama Client - Shell: $shell"
    echo "Implementation: ${ISA_ROOT}/modules/shell-support/${shell}-functions.sh"
    echo "Common config: ${ISA_ROOT}/modules/common/ollama-common.sh"
}
