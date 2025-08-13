#!/bin/bash

echo "🔧 Fixing Shell Configuration Issues"
echo "===================================="

# The issue appears to be in the shell configuration files
# Let's create a backup and fix the problematic configurations

echo "1. Backing up current shell configs..."
cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d) 2>/dev/null || echo "No .zshrc found"
cp ~/.bashrc ~/.bashrc.backup.$(date +%Y%m%d) 2>/dev/null || echo "No .bashrc found"

echo "2. Checking for problematic configurations..."

# Look for anything that might be wrapping head or cat commands
if grep -q "head\|cat" ~/.zshrc 2>/dev/null; then
    echo "⚠️  Found head/cat references in .zshrc"
    grep -n "head\|cat" ~/.zshrc 2>/dev/null || true
fi

# Add safe AWS CLI configuration
echo "3. Adding AWS CLI environment fixes..."

cat >> ~/.zshrc << 'EOF'

# AWS CLI fixes for shell issues
export AWS_PAGER=""
export AWS_CLI_AUTO_PROMPT=off
unalias head 2>/dev/null || true
unalias cat 2>/dev/null || true

EOF

echo "4. Creating clean environment function..."

cat >> ~/.zshrc << 'EOF'
# Function for clean AWS CLI usage
aws_clean() {
    local old_path="$PATH"
    export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    unset PAGER
    aws "$@"
    export PATH="$old_path"
}

EOF

echo "✅ Shell fixes applied!"
echo ""
echo "To apply the changes:"
echo "1. Run: source ~/.zshrc"
echo "2. Or restart your terminal"
echo ""
echo "Alternative: Use 'aws_clean' instead of 'aws' for problematic commands"
