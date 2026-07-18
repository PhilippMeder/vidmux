#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

echo "Running lint..."
"${SCRIPT_DIR}/lint.sh"

echo
echo "Running tests..."
"${SCRIPT_DIR}/test-all-python.sh"

echo
echo "All checks passed."
