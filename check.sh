#!/usr/bin/env bash
# Pre-commit verification: scan for API tokens and hardcoded user paths
# that must never ship in the public repo.
set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

fail=0

echo "→ Checking for API token leaks..."
if grep -rE "tushare_token\s*=\s*['\"][a-f0-9]{20,}" commands/ docs/ 2>/dev/null; then
    echo "  ✗ LEAK: literal TuShare token found"
    fail=1
fi
if grep -rE "finnhub_token\s*=\s*['\"][a-z0-9]{20,}" commands/ docs/ 2>/dev/null; then
    echo "  ✗ LEAK: literal Finnhub token found"
    fail=1
fi

echo "→ Checking for hardcoded user paths..."
# exclude docs/superpowers/** from this check — specs and plans may reference
# the user's local environment as context
if grep -rE "/Users/[a-z_][a-z0-9_-]+/" commands/ 2>/dev/null; then
    echo "  ✗ LEAK: hardcoded absolute /Users/ path in commands/"
    fail=1
fi

echo "→ Checking for email leaks..."
if grep -rE "[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}" commands/ docs/methodology.md docs/debate-mechanism.md README.md 2>/dev/null; then
    echo "  ✗ LEAK: email address in public-facing file"
    fail=1
fi

if [ $fail -eq 0 ]; then
    echo "✓ All leak checks passed"
else
    echo ""
    echo "FAIL: fix the leaks above before committing"
    exit 1
fi
