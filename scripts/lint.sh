#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

FIX=false

case "${1:-}" in
    "")
        ;;
    --fix)
        FIX=true
        ;;
    *)
        echo "Unknown argument: $1"
        echo "Usage: $0 [--fix]"
        exit 1
        ;;
esac

if [[ "${FIX}" == true ]]; then
    echo "Running Ruff with automatic fixes..."
    uv run ruff check . --fix
    uv run ruff format .
else
    echo "Running Ruff checks..."
    uv run ruff check .
    uv run ruff format --check .
fi

echo "Linting successful."
