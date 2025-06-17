#!/bin/bash

INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/uvstart" "$INSTALL_DIR/uvstart"
chmod +x "$INSTALL_DIR/uvstart"

# Add to PATH if not already in shell rc
SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
  SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
  SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
  if ! grep -q "$INSTALL_DIR" "$SHELL_RC"; then
    echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
    echo "Added $INSTALL_DIR to PATH in $SHELL_RC"
  fi
fi

echo "Installed uvstart to $INSTALL_DIR"
echo "You can now run: uvstart help"
