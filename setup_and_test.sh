#!/bin/bash
# setup_and_test.sh

echo "Installing dependencies..."
# Try local pybun first, then global
if [ -f ".venv/bin/pybun" ]; then
    ./.venv/bin/pybun add pydantic
    ./.venv/bin/pybun install
    echo "Running tests..."
    ./.venv/bin/pybun run python3 -m unittest optimizer/tests/test_strategy.py
else
    pybun add pydantic
    pybun install
    echo "Running tests..."
    pybun run python3 -m unittest optimizer/tests/test_strategy.py
fi
