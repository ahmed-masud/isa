#!/bin/bash
# ISA Deployment Script for Helm Server
# Deploys ISA bundle to remote server via SSH

set -e

# Configuration
HELM_HOST="${1:-192.168.1.0}"
HELM_USER="${2:-helm}"
BUNDLE_PATH="/tmp/isa-deployment-*.tar.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ISA Deployment to Helm Server${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Target: $HELM_USER@$HELM_HOST"
echo ""

# Find the latest bundle
LATEST_BUNDLE=$(ls -t $BUNDLE_PATH 2>/dev/null | head -1)
if [ -z "$LATEST_BUNDLE" ]; then
    echo -e "${RED}❌ No ISA deployment bundle found!${NC}"
    echo "Create one first with: ./deploy/create-bundle.sh"
    exit 1
fi

BUNDLE_NAME=$(basename "$LATEST_BUNDLE" .tar.gz)
echo -e "${GREEN}📦 Found bundle: $BUNDLE_NAME${NC}"
echo -e "   Size: $(du -h "$LATEST_BUNDLE" | cut -f1)"
echo ""

# Test connectivity
echo -e "${YELLOW}🔍 Testing connection to $HELM_HOST...${NC}"
if ping -c 1 -W 3 "$HELM_HOST" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Host is reachable${NC}"
else
    echo -e "${RED}❌ Host is not reachable${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check if $HELM_HOST is the correct IP address"
    echo "2. Verify the host is online and network accessible"
    echo "3. Check firewall settings"
    echo ""
    echo "Alternative deployment methods:"
    echo "  # Manual copy via USB/network share"
    echo "  # Use different IP address"
    echo "  # Use hostname instead of IP"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Test SSH connection
echo -e "${YELLOW}🔐 Testing SSH connection...${NC}"
if ssh -o ConnectTimeout=5 -o BatchMode=yes "$HELM_USER@$HELM_HOST" 'echo "SSH OK"' >/dev/null 2>&1; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ SSH connection failed${NC}"
    echo ""
    echo "SSH Troubleshooting:"
    echo "1. Verify SSH keys are set up: ssh-copy-id $HELM_USER@$HELM_HOST"
    echo "2. Try different username (masud, admin, etc.)"
    echo "3. Check SSH service is running on remote host"
    echo "4. Verify SSH port (default 22)"
    echo ""
    echo "Manual deployment alternative:"
    echo "  scp $LATEST_BUNDLE $HELM_USER@$HELM_HOST:~/"
    echo "  ssh $HELM_USER@$HELM_HOST"
    echo "  tar -xzf $BUNDLE_NAME.tar.gz"
    echo "  cd $BUNDLE_NAME"
    echo "  ./install.sh"
    echo ""
    read -p "Try manual deployment commands? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}📋 Manual Deployment Commands:${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "# Copy bundle"
        echo "scp $LATEST_BUNDLE $HELM_USER@$HELM_HOST:~/"
        echo ""
        echo "# SSH and install"
        echo "ssh $HELM_USER@$HELM_HOST"
        echo "tar -xzf $BUNDLE_NAME.tar.gz"
        echo "cd $BUNDLE_NAME"
        echo "./install.sh"
        echo ""
        echo "# Activate ISA"
        echo "source ~/projects/isa/isa.rc"
        echo "isa help"
        echo ""
    fi
    exit 1
fi

# Deploy the bundle
echo -e "${BLUE}📤 Uploading ISA bundle...${NC}"
if scp "$LATEST_BUNDLE" "$HELM_USER@$HELM_HOST:~/"; then
    echo -e "${GREEN}✅ Bundle uploaded successfully${NC}"
else
    echo -e "${RED}❌ Failed to upload bundle${NC}"
    exit 1
fi

# Extract and install
echo -e "${BLUE}📋 Installing ISA on remote server...${NC}"
ssh "$HELM_USER@$HELM_HOST" << EOF
set -e
echo "🔧 Extracting bundle..."
tar -xzf $BUNDLE_NAME.tar.gz

echo "📦 Installing ISA..."
cd $BUNDLE_NAME
./install.sh

echo ""
echo "✨ Testing ISA installation..."
source ~/projects/isa/isa.rc
isa help | head -5

echo ""
echo "🎉 ISA deployment completed successfully!"
echo ""
echo "To use ISA on helm server:"
echo "  ssh $HELM_USER@$HELM_HOST"
echo "  source ~/projects/isa/isa.rc"
echo "  isa help"
echo "  computer help"
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "1. SSH to helm: ssh $HELM_USER@$HELM_HOST"
    echo "2. Source ISA: source ~/projects/isa/isa.rc"  
    echo "3. Test ISA: isa help"
    echo "4. Test computer: computer help"
    echo ""
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi