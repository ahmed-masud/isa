#!/bin/bash
# ISA Deployment Bundle Creation Script
# Creates a deployable package of ISA system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISA_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUNDLE_NAME="isa-deployment-$(date +%Y%m%d-%H%M%S)"
BUNDLE_DIR="/tmp/$BUNDLE_NAME"

echo "🚀 Creating ISA deployment bundle..."
echo "📦 Bundle: $BUNDLE_NAME"
echo "📁 Source: $ISA_ROOT"
echo ""

# Create bundle directory
mkdir -p "$BUNDLE_DIR"

echo "📋 Copying core ISA files..."

# Copy essential files
cp "$ISA_ROOT/isa.rc" "$BUNDLE_DIR/"
cp "$ISA_ROOT/load-context.sh" "$BUNDLE_DIR/"
cp "$ISA_ROOT/README.md" "$BUNDLE_DIR/"

# Copy tools
if [ -d "$ISA_ROOT/tools" ]; then
    cp -r "$ISA_ROOT/tools" "$BUNDLE_DIR/"
fi

# Copy docs (essential ones only)
mkdir -p "$BUNDLE_DIR/docs"
cp "$ISA_ROOT/docs/QUICK-START.md" "$BUNDLE_DIR/docs/" 2>/dev/null || true
cp "$ISA_ROOT/docs/INSTALL.md" "$BUNDLE_DIR/docs/" 2>/dev/null || true
cp "$ISA_ROOT/docs/TODO.md" "$BUNDLE_DIR/docs/" 2>/dev/null || true

# Create deployment structure
mkdir -p "$BUNDLE_DIR/contexts/people"
mkdir -p "$BUNDLE_DIR/contexts/places" 
mkdir -p "$BUNDLE_DIR/contexts/things"

# Create installation script
cat > "$BUNDLE_DIR/install.sh" << 'EOF'
#!/bin/bash
# ISA Installation Script for Remote Deployment

set -e

USER_HOME="$HOME"
ISA_ROOT="$USER_HOME/projects/isa"
ISA_CONFIG="$USER_HOME/.config/isa"

echo "🌟 Installing ISA (Intelligent Support Assistant)..."
echo ""

# Create directories
echo "📁 Creating directory structure..."
mkdir -p "$ISA_ROOT"
mkdir -p "$ISA_CONFIG/contexts/people"
mkdir -p "$ISA_CONFIG/contexts/places"
mkdir -p "$ISA_CONFIG/contexts/things"
mkdir -p "$USER_HOME/.local/bin"

# Copy files to proper locations
echo "📋 Installing ISA files..."
cp isa.rc "$ISA_ROOT/"
cp load-context.sh "$ISA_ROOT/"
cp README.md "$ISA_ROOT/"

if [ -d "tools" ]; then
    cp -r tools "$ISA_ROOT/"
fi

if [ -d "docs" ]; then
    cp -r docs "$ISA_ROOT/"
fi

# Set executable permissions
chmod +x "$ISA_ROOT/load-context.sh"
if [ -f "$ISA_ROOT/tools/caffeinate-helper.sh" ]; then
    chmod +x "$ISA_ROOT/tools/caffeinate-helper.sh"
fi

# Create symlink for isa-load command
ln -sf "$ISA_ROOT/load-context.sh" "$USER_HOME/.local/bin/isa-load"

echo ""
echo "✅ ISA installed successfully!"
echo ""
echo "📍 Locations:"
echo "  Tool:   $ISA_ROOT"
echo "  Config: $ISA_CONFIG"
echo ""
echo "🔧 To activate ISA, add this to your shell profile:"
echo "  source $ISA_ROOT/isa.rc"
echo ""
echo "💡 Quick test:"
echo "  source $ISA_ROOT/isa.rc"
echo "  isa help"
echo "  computer help"
echo ""
EOF

chmod +x "$BUNDLE_DIR/install.sh"

# Create deployment info
cat > "$BUNDLE_DIR/DEPLOYMENT-INFO.md" << EOF
# ISA Deployment Bundle

**Created**: $(date)
**Bundle**: $BUNDLE_NAME
**Source**: $(hostname):$ISA_ROOT

## Contents
- isa.rc - Main configuration and functions
- load-context.sh - Context loader script
- install.sh - Automated installation script
- tools/ - Helper scripts (caffeinate, etc.)
- docs/ - Essential documentation
- contexts/ - Directory structure for contexts

## Installation
\`\`\`bash
# Extract and install
tar -xzf $BUNDLE_NAME.tar.gz
cd $BUNDLE_NAME
./install.sh
\`\`\`

## Activation
Add to ~/.zshrc or ~/.bashrc:
\`\`\`bash
source ~/projects/isa/isa.rc
\`\`\`

## Verification
\`\`\`bash
isa help
computer help
isa contexts
\`\`\`
EOF

# Create tarball
echo "📦 Creating deployment archive..."
cd /tmp
tar -czf "${BUNDLE_NAME}.tar.gz" "$BUNDLE_NAME"

echo ""
echo "✅ ISA deployment bundle created!"
echo ""
echo "📦 Bundle: /tmp/${BUNDLE_NAME}.tar.gz"
echo "📁 Size: $(du -h /tmp/${BUNDLE_NAME}.tar.gz | cut -f1)"
echo ""
echo "🚀 Ready for deployment to helm (192.168.1.0)"
echo ""
echo "Next steps:"
echo "  scp /tmp/${BUNDLE_NAME}.tar.gz helm@192.168.1.0:~/"
echo "  ssh helm@192.168.1.0 'tar -xzf ${BUNDLE_NAME}.tar.gz && cd ${BUNDLE_NAME} && ./install.sh'"
echo ""