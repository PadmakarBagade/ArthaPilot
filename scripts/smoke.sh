#!/usr/bin/env bash
# ArthaPilot Smoke Test Script (Bash)
set -euo pipefail

echo "--- Running ArthaPilot Smoke Checks ---"

# 1. Run Python unit tests
echo "1. Verifying backend test suite..."
python -m pytest backend/tests -q

# 2. Check categoriser accuracy
echo "2. Verifying ML categoriser..."
python scripts/evaluate_categoriser.py

# 3. Check forecast backtest
echo "3. Verifying Monte Carlo forecast backtest..."
python scripts/backtest.py

echo "=== All Smoke Checks Succeeded! ==="
exit 0

