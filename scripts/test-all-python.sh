#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

PYTHON_VERSIONS=(
    "3.10"
    "3.11"
    "3.12"
    "3.13"
    "3.14"
)

# Persistent environments outside the repository.
# Override this if you prefer another location.
UV_TEST_ENV_ROOT="${UV_TEST_ENV_ROOT:-${HOME}/.cache/uv-test-envs/$(basename "${PROJECT_ROOT}")}"

for version in "${PYTHON_VERSIONS[@]}"; do
    env_dir="${UV_TEST_ENV_ROOT}/py${version//./}"

    echo
    echo "======================================"
    echo "Testing Python ${version}"
    echo "Environment: ${env_dir}"
    echo "======================================"

    # Create the environment if missing.
    if [[ ! -d "${env_dir}" ]]; then
        uv venv \
            --python "${version}" \
            "${env_dir}"
    fi

    python="${env_dir}/bin/python"

    # Install/update the project and test dependencies.
    #
    # Replace --group dev with your actual dependency group if needed.
    uv pip install \
    --python "${python}" \
    -e . \
    --group dev

    # Disable pytest addopts from pyproject.toml so coverage is not
    # generated once per Python version.
    "${python}" -m pytest -o addopts=""
done

echo
echo "All Python versions passed."
