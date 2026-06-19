#!/usr/bin/env bash
# RotorEdge — KEYLESS one-command reproduction (Linux/macOS/Git-Bash).
# Reproduces every headline number from the committed snapshot with NO API key.
set -euo pipefail
PY="${PY:-python}"

echo ">> installing pinned deps"
$PY -m pip install -q -r requirements.txt

echo ">> running walk-forward backtest (keyless)"
$PY scripts/run_backtest.py

echo ">> verifying results match the committed reference"
$PY scripts/verify.py

echo ">> done. Open dashboard/index.html to explore. See results/metrics.json + results/strategy_spec.json."
