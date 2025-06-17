#!/bin/bash

INSTALL_DIR="$HOME/.local/uvstart"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

# Copy all source files into install directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR/"* "$INSTALL_DIR"

# Make the main CLI executable
chmod +x "$INSTALL_DIR/uvstart"

# Create or update symlink
ln -sf "$INSTALL_DIR/uvstart" "$BIN_DIR/uvstart"

# Add to PATH if not already present
SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
  SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
  SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
  if ! grep -q "$BIN_DIR" "$SHELL_RC"; then
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
    echo "Added $BIN_DIR to PATH in $SHELL_RC"
  fi
fi

echo "Installed uvstart to $INSTALL_DIR"
echo "You can now run: uvstart help"

