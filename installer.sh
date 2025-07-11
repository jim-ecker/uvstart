#!/bin/bash
set -e

# uvstart installer with isolated environment
# Creates a dedicated venv for uvstart to avoid polluting host system

# Color codes for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Installation paths
UVSTART_HOME="$HOME/.local/uvstart"
UVSTART_VENV="$UVSTART_HOME/venv"
UVSTART_BIN="$HOME/.local/bin"
UVSTART_CONFIG="$UVSTART_HOME/config.yaml"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}uvstart Installer${NC}"
echo -e "${BLUE}=================${NC}"
echo ""
echo "This installer will:"
echo "• Create an isolated Python environment for uvstart"
echo "• Install dependencies (Jinja2, PyYAML, rich) in isolation"
echo "• Detect available Python package managers"
echo "• Set up your preferred configuration"
echo ""

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found${NC}"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "Found Python ${GREEN}${PYTHON_VERSION}${NC}"

# Create installation directory
echo -e "\n${CYAN}Setting up installation directory...${NC}"
mkdir -p "$UVSTART_HOME"
mkdir -p "$UVSTART_BIN"

# Create isolated virtual environment
echo -e "${CYAN}Creating isolated Python environment...${NC}"
if [ -d "$UVSTART_VENV" ]; then
    echo -e "${YELLOW}Removing existing uvstart environment...${NC}"
    rm -rf "$UVSTART_VENV"
fi

python3 -m venv "$UVSTART_VENV"
source "$UVSTART_VENV/bin/activate"

# Upgrade pip in the venv
echo -e "${CYAN}Upgrading pip in isolated environment...${NC}"
pip install --upgrade pip > /dev/null 2>&1

# Install uvstart dependencies
echo -e "${CYAN}Installing uvstart dependencies...${NC}"
pip install -r "$SCRIPT_DIR/requirements.txt" > /dev/null 2>&1

# Copy uvstart files to venv
echo -e "${CYAN}Installing uvstart files...${NC}"
cp -r "$SCRIPT_DIR/frontend" "$UVSTART_VENV/"
cp -r "$SCRIPT_DIR/templates" "$UVSTART_VENV/"
cp -r "$SCRIPT_DIR/engine" "$UVSTART_VENV/"

# Create the main uvstart executable in the venv
cat > "$UVSTART_VENV/bin/uvstart" << EOF
#!$UVSTART_VENV/bin/python
"""
uvstart - Isolated executable with dependencies
"""
import sys
import os
from pathlib import Path

# Resolve symlinks to get actual file location
actual_file = Path(__file__).resolve()
venv_root = actual_file.parent.parent
frontend_path = str(venv_root / "frontend")
sys.path.insert(0, frontend_path)

# Import and run main
from uvstart import main

if __name__ == "__main__":
    main()
EOF

chmod +x "$UVSTART_VENV/bin/uvstart"

# Create symlink in user's bin directory
echo -e "${CYAN}Creating command symlink...${NC}"
ln -sf "$UVSTART_VENV/bin/uvstart" "$UVSTART_BIN/uvstart"

# Detect available backends
echo -e "\n${CYAN}Detecting Python package managers...${NC}"
DETECTED_BACKENDS=()

if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>/dev/null | cut -d' ' -f2 || echo "unknown")
    echo -e "✓ ${GREEN}uv${NC} (${UV_VERSION}) - Ultra-fast Python package manager"
    DETECTED_BACKENDS+=("uv")
fi

if command -v poetry &> /dev/null; then
    POETRY_VERSION=$(poetry --version 2>/dev/null | cut -d' ' -f3 || echo "unknown")
    echo -e "✓ ${GREEN}poetry${NC} (${POETRY_VERSION}) - Mature dependency management"
    DETECTED_BACKENDS+=("poetry")
fi

if command -v pdm &> /dev/null; then
    PDM_VERSION=$(pdm --version 2>/dev/null | cut -d' ' -f3 || echo "unknown")
    echo -e "✓ ${GREEN}pdm${NC} (${PDM_VERSION}) - Fast Python package manager"
    DETECTED_BACKENDS+=("pdm")
fi

if [ ${#DETECTED_BACKENDS[@]} -eq 0 ]; then
    echo -e "${YELLOW}No package managers detected${NC}"
    echo "You can install one later. Recommended: uv (fastest)"
    DEFAULT_BACKEND="uv"
else
    echo ""
fi

# Interactive backend selection
echo -e "${CYAN}Backend Selection${NC}"
echo "Choose your preferred default backend for new projects:"
echo ""

# Show detected backends with numbers
for i in "${!DETECTED_BACKENDS[@]}"; do
    backend="${DETECTED_BACKENDS[$i]}"
    echo "  $((i+1)). $backend"
done

# Add option for uninstalled backend
echo "  $((${#DETECTED_BACKENDS[@]}+1)). Other (specify a backend not yet installed)"

echo ""
read -p "Enter your choice [1]: " CHOICE

# Process choice
if [ -z "$CHOICE" ]; then
    CHOICE=1
fi

if [ "$CHOICE" -le "${#DETECTED_BACKENDS[@]}" ] && [ "$CHOICE" -ge 1 ]; then
    SELECTED_BACKEND="${DETECTED_BACKENDS[$((CHOICE-1))]}"
elif [ "$CHOICE" -eq "$((${#DETECTED_BACKENDS[@]}+1))" ]; then
    echo ""
    echo "Available backends: uv, poetry, pdm"
    read -p "Enter backend name: " SELECTED_BACKEND
    if [ -z "$SELECTED_BACKEND" ]; then
        SELECTED_BACKEND="uv"
    fi
else
    echo -e "${YELLOW}Invalid choice, defaulting to first detected backend${NC}"
    SELECTED_BACKEND="${DETECTED_BACKENDS[0]:-uv}"
fi

# Detect Python version
DETECTED_PYTHON=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)

# Get user info
echo ""
echo -e "${CYAN}User Configuration${NC}"
read -p "Your name [Developer]: " USER_NAME
read -p "Your email [dev@example.com]: " USER_EMAIL

USER_NAME="${USER_NAME:-Developer}"
USER_EMAIL="${USER_EMAIL:-dev@example.com}"

# Create configuration file
echo -e "\n${CYAN}Creating configuration...${NC}"
cat > "$UVSTART_CONFIG" << EOF
# uvstart configuration
# This file stores your preferences for new projects

# Default backend for new projects
default_backend: "$SELECTED_BACKEND"

# Default Python version
default_python_version: "$DETECTED_PYTHON"

# User information for project templates
author: "$USER_NAME"
email: "$USER_EMAIL"

# Installation info
installed_version: "2.0.0"
install_date: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
venv_path: "$UVSTART_VENV"
EOF

echo -e "${GREEN}✓ Configuration saved to $UVSTART_CONFIG${NC}"

# Final setup
echo -e "\n${CYAN}Final setup...${NC}"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}Note: $HOME/.local/bin is not in your PATH${NC}"
    echo "Add this to your shell profile (.bashrc, .zshrc, etc.):"
    echo -e "${BLUE}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo ""
fi

echo -e "${GREEN}✓ uvstart installation complete!${NC}"
echo ""
echo -e "${CYAN}Installation Summary:${NC}"
echo "• Installation path: $UVSTART_HOME"
echo "• Virtual environment: $UVSTART_VENV"
echo "• Executable: $UVSTART_BIN/uvstart"
echo "• Default backend: $SELECTED_BACKEND"
echo "• Configuration: $UVSTART_CONFIG"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "1. Ensure ~/.local/bin is in your PATH"
echo "2. Test installation: uvstart doctor"
echo "3. Create your first project: uvstart generate my-project"
echo ""
echo -e "${GREEN}Happy coding!${NC}"

