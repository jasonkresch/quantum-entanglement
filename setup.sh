#!/usr/bin/env bash
set -euo pipefail

# setup.sh
# Create a local Python virtual environment and install the packages needed
# for logging and analyzing Geiger-counter coincidence runs.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo "Quantum Entanglement / Geiger Coincidence setup"
echo "Project directory: $PROJECT_DIR"
echo

# Check Python
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "Error: python3 was not found."
  echo "Please install Python 3.10+ and rerun this script."
  exit 1
fi

PY_VERSION="$($PYTHON_BIN - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
PY
)"

echo "Found Python: $PY_VERSION"

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment at .venv ..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  echo "Virtual environment already exists at .venv"
fi

# Activate venv
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Upgrading pip ..."
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
  echo "Installing dependencies from requirements.txt ..."
  python -m pip install -r "$PROJECT_DIR/requirements.txt"
else
  echo "requirements.txt not found; installing default analysis/logging dependencies ..."
  python -m pip install numpy pandas matplotlib pyserial
fi

# Create common output folders if they do not exist
mkdir -p "$PROJECT_DIR/experiments"
mkdir -p "$PROJECT_DIR/media"
mkdir -p "$PROJECT_DIR/analysis-output"

echo
echo "Setup complete."
echo
echo "To activate the environment later, run:"
echo "  source .venv/bin/activate"
echo
echo "Example analysis command:"
echo "  python analyze_geiger_run_enhanced.py experiments/example-run.csv --half-window-us 3 --center-us 0"
echo
echo "Example serial-port discovery:"
echo "  python -m serial.tools.list_ports"
echo
