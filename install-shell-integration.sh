#!/usr/bin/env bash
# ISA Shell Integration Installer
# Adds ISA to your shell configuration files

set -e

ISA_ROOT="${HOME}/projects/isa"
BACKUP_SUFFIX=".backup-$(date +%Y%m%d-%H%M%S)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ISA Shell Integration Installer            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo ""

# Check if ISA exists
if [[ ! -f "${ISA_ROOT}/isa.rc" ]]; then
    echo -e "${RED}❌ Error: ISA not found at ${ISA_ROOT}${NC}"
    echo -e "${YELLOW}   Please clone ISA to ${ISA_ROOT} first${NC}"
    exit 1
fi

echo -e "${GREEN}✅ ISA found at ${ISA_ROOT}${NC}"
echo ""

# Function to add ISA to a config file
add_isa_to_config() {
    local config_file="$1"
    local config_name="$2"
    
    # Check if already configured
    if grep -q "isa.rc" "${config_file}" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  ISA already configured in ${config_name}${NC}"
        return 0
    fi
    
    # Backup existing file
    if [[ -f "${config_file}" ]]; then
        cp "${config_file}" "${config_file}${BACKUP_SUFFIX}"
        echo -e "${BLUE}📦 Backed up ${config_name} to ${config_file}${BACKUP_SUFFIX}${NC}"
    fi
    
    # Add ISA configuration
    cat >> "${config_file}" << 'EOFCONFIG'

# ============================================================================
# ISA (Intelligent Support Assistant) Configuration
# ============================================================================
export ISA_ROOT="${HOME}/projects/isa"
if [[ -f "${ISA_ROOT}/isa.rc" ]]; then
    source "${ISA_ROOT}/isa.rc"
fi
EOFCONFIG
    
    echo -e "${GREEN}✅ Added ISA to ${config_name}${NC}"
}

# Detect shell and configure
echo -e "${BLUE}🔍 Detecting shell configuration...${NC}"
echo ""

# Configure for zsh
if [[ -n "${ZSH_VERSION}" ]] || [[ -f "${HOME}/.zshrc" ]]; then
    echo -e "${BLUE}📝 Configuring for Zsh...${NC}"
    add_isa_to_config "${HOME}/.zshrc" ".zshrc"
fi

# Configure for bash
if [[ -n "${BASH_VERSION}" ]] || [[ -f "${HOME}/.bashrc" ]] || [[ -f "${HOME}/.bash_profile" ]]; then
    echo -e "${BLUE}📝 Configuring for Bash...${NC}"
    
    # Create/update .bashrc
    if [[ ! -f "${HOME}/.bashrc" ]]; then
        touch "${HOME}/.bashrc"
    fi
    add_isa_to_config "${HOME}/.bashrc" ".bashrc"
    
    # Ensure .bash_profile sources .bashrc
    if [[ ! -f "${HOME}/.bash_profile" ]]; then
        cat > "${HOME}/.bash_profile" << 'EOFPROFILE'
# Bash Profile - Login Shell Configuration

# Source .bashrc for interactive shells
if [[ -f ~/.bashrc ]]; then
    source ~/.bashrc
fi
EOFPROFILE
        echo -e "${GREEN}✅ Created .bash_profile${NC}"
    else
        if ! grep -q ".bashrc" "${HOME}/.bash_profile" 2>/dev/null; then
            cp "${HOME}/.bash_profile" "${HOME}/.bash_profile${BACKUP_SUFFIX}"
            cat >> "${HOME}/.bash_profile" << 'EOFPROFILE'

# Source .bashrc for interactive shells
if [[ -f ~/.bashrc ]]; then
    source ~/.bashrc
fi
EOFPROFILE
            echo -e "${GREEN}✅ Updated .bash_profile to source .bashrc${NC}"
        fi
    fi
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Installation Complete! 🎉                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo -e "  1. Restart your shell or run: ${BLUE}source ~/.zshrc${NC} (or ${BLUE}~/.bashrc${NC})"
echo -e "  2. Test ISA: ${BLUE}isa help${NC}"
echo -e "  3. Check status: ${BLUE}isa show config${NC}"
echo ""
echo -e "${BLUE}💡 Tip: Your old config files are backed up with suffix ${BACKUP_SUFFIX}${NC}"
echo ""
