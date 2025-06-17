#!/bin/bash

# Set install paths
INSTALL_DIR="$HOME/.local/uvstart"
BIN_DIR="$HOME/.local/bin"
EXECUTABLE="uvstart"

# Create target directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Copy all files into the install directory
SCRIPT_SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_SOURCE_DIR/"* "$INSTALL_DIR"

# Create or update the symlink
ln -sf "$INSTALL_DIR/$EXECUTABLE" "$BIN_DIR/$EXECUTABLE"
chmod +x "$INSTALL_DIR/$EXECUTABLE"

# Ensure bin directory is in PATH
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

echo "uvstart installed to $INSTALL_DIR"
echo "You can now run: uvstart init ..."
