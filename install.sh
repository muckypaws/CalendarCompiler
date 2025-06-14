#!/bin/bash

echo "=== CalendarCompiler Automated Installer (Linux/macOS) ==="

# Check for Python 3.8+
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.8+ not found! Please install Python before continuing."
  exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

# Detect OS for Cairo install
OS=$(uname)
if [[ "$OS" == "Darwin" ]]; then
  # macOS
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found! Install Homebrew (https://brew.sh/) and re-run."
    exit 1
  fi
  echo "Installing cairo via Homebrew..."
  brew install cairo
else
  # Assume Linux
  if command -v apt-get >/dev/null 2>&1; then
    echo "Installing cairo via apt-get..."
    sudo apt-get update
    sudo apt-get install -y libcairo2
  elif command -v dnf >/dev/null 2>&1; then
    echo "Installing cairo via dnf..."
    sudo dnf install -y cairo
  else
    echo "Please install cairo manually via your package manager."
  fi
fi

echo "Setup complete! Edit your config/settings.json and run:"
echo "  source venv/bin/activate"
echo "  python CalendarCompiler.py"
