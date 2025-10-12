# ISA Shell Compatibility Implementation

## Overview

This document describes the shell-agnostic implementation of the ISA Ollama client that resolves compatibility issues between bash and zsh (and provides basic csh/tcsh support).

## Problem Statement

The original `modules/ollama-client.sh` used bash-specific features, particularly:
- `export -f function_name` - Not supported in zsh
- Bash-specific function export behavior

This caused failures in zsh environments with errors like:
```
zsh: bad option: -f
```

## Solution Architecture

### Directory Structure

```
modules/
├── ollama-client.sh              # Main loader (shell detection + dispatch)
├── shell-support/
│   ├── bash-functions.sh         # Bash-specific implementations
│   ├── zsh-functions.sh          # Zsh-specific implementations  
│   └── csh-functions.sh          # CSH/TCSH implementations (basic)
└── common/
    └── ollama-common.sh          # Shared logic/variables
```

### Components

#### 1. Main Loader (`modules/ollama-client.sh`)
- Shell detection via environment variables and process inspection
- Dynamic loading of appropriate shell implementation
- Fallback mechanisms for unsupported shells

#### 2. Common Configuration (`modules/common/ollama-common.sh`)
- Shared variables (OLLAMA_HOST, AI_MODEL, etc.)
- Common color definitions
- Environment-specific configuration logic

#### 3. Shell-Specific Implementations (`modules/shell-support/`)

**bash-functions.sh:**
- Uses `export -f` for function exports
- Full implementation of all Ollama functions
- Bash-specific syntax and features

**zsh-functions.sh:**
- Avoids `export -f` (functions are globally available in zsh)
- Identical functionality to bash version
- Zsh-compatible syntax

**csh-functions.sh:**
- Basic implementation using aliases
- Limited functionality compared to bash/zsh
- CSH/TCSH syntax adaptation

## Shell Detection Logic

The `isa_detect_shell()` function detects the current shell using:

1. **Environment Variables:**
   - `$ZSH_VERSION` → zsh
   - `$BASH_VERSION` → bash
   - `$tcsh` → csh

2. **Process Inspection:**
   - `ps -p $$ -o comm=` to get parent process name
   - Pattern matching against shell names

3. **Fallback:**
   - Defaults to bash if detection fails

## Key Differences Addressed

| Feature | Bash | Zsh | CSH/TCSH |
|---------|------|-----|----------|
| Function Export | `export -f func` | Not needed | Not supported |
| Local Variables | `local var=value` | `local var=value` | `set var=value` |
| Function Definition | Standard | Standard | Aliases/limited |
| String Handling | Standard | Standard | Different quoting |

## Testing Shell Compatibility

To test the implementation:

```bash
# Test shell detection
isa_shell_info

# Test function loading in different shells
bash -c "source modules/ollama-client.sh && isa_ai_status"
zsh -c "source modules/ollama-client.sh && isa_ai_status"

# Test actual functionality
computer ask "test query"
isa ai-status
```

## Migration Benefits

1. **Cross-Shell Support:** Works in bash, zsh, and basic csh/tcsh
2. **Maintainability:** Separate implementations for each shell
3. **Fallback Safety:** Graceful degradation for unsupported shells
4. **Future Extensibility:** Easy to add new shell support

## Usage

The API remains unchanged - existing ISA commands continue to work:
- `computer ask "question"`
- `isa ai-analyze urgent`
- `computer suggest --project=current`

## Development Notes

- Common configuration is shared across all shells
- Shell-specific files contain identical logic with appropriate syntax
- Function implementations maintain API compatibility
- Error handling and fallbacks ensure robustness

## Future Enhancements

1. **Fish Shell Support:** Add `fish-functions.sh`
2. **PowerShell Support:** For Windows environments
3. **Performance Optimization:** Caching shell detection results
4. **Enhanced CSH Support:** More complete function implementations