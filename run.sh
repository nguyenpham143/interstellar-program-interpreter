#!/bin/bash
set -e

# Detect python3 or python
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "Python is not installed or not in PATH."
    exit 1
fi

echo "=== Running IFP Interpreter Test Suite (CO2039 - Assignment 2) ==="
$PYTHON_CMD -m unittest discover tests

echo ""
echo "=== Quick Evaluation Demonstration ==="
echo "Evaluating: B+ I\" I# (1 + 2)"
echo "B+ I\" I#" | $PYTHON_CMD src/main.py
