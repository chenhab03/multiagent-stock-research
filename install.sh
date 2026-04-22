#!/usr/bin/env bash
# Install multiagent-stock-research commands into Claude Code.
set -euo pipefail

COMMANDS_DIR="${HOME}/.claude/commands"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$COMMANDS_DIR" ]; then
    echo "⚠️  ${COMMANDS_DIR} does not exist. Is Claude Code installed?"
    echo "   Create the directory with: mkdir -p \"${COMMANDS_DIR}\""
    exit 1
fi

echo "Installing commands to ${COMMANDS_DIR}..."

for cmd in analyze report; do
    src="${SCRIPT_DIR}/commands/${cmd}.md"
    dst="${COMMANDS_DIR}/${cmd}.md"

    if [ ! -f "$src" ]; then
        echo "✗ Source file missing: $src"
        exit 1
    fi

    if [ -f "$dst" ]; then
        backup="${dst}.backup-$(date +%Y%m%d-%H%M%S)"
        mv "$dst" "$backup"
        echo "  📦 Backed up existing ${cmd}.md → $(basename "$backup")"
    fi

    cp "$src" "$dst"
    echo "  ✓ Installed /${cmd}"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Installation complete."
echo ""
echo "  Next steps:"
echo ""
echo "  1. Set API keys (add to ~/.zshrc or ~/.bashrc):"
echo "       export TUSHARE_TOKEN='your_token'    # A-shares (https://tushare.pro)"
echo "       export FINNHUB_TOKEN='your_token'    # US market (https://finnhub.io)"
echo "       export RESEARCH_OUTPUT_DIR='\${HOME}/equity-research'  # optional, default: ~/equity-research/"
echo ""
echo "  2. Restart Claude Code."
echo ""
echo "  3. Test:"
echo "       /analyze NVDA"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
