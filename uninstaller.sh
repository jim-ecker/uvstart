#!/bin/bash

set -e

INSTALL_DIR="$HOME/.local"
APP_DIR="$INSTALL_DIR/uvstart"
LINK_PATH="$INSTALL_DIR/bin/uvstart"

echo "Uninstalling uvstart..."

# Remove the application directory
if [ -d "$APP_DIR" ]; then
    echo "Removing $APP_DIR"
    rm -rf "$APP_DIR"
else
    echo "No uvstart install found at $APP_DIR"
fi

# Remove the symlink if it points to the app directory
if [ -L "$LINK_PATH" ]; then
    TARGET="$(readlink "$LINK_PATH")"
    if [[ "$TARGET" == "$APP_DIR/"* ]]; then
        echo "Removing symlink $LINK_PATH → $TARGET"
        rm "$LINK_PATH"
    else
        echo "Skipping $LINK_PATH — it does not point to uvstart"
    fi
elif [ -e "$LINK_PATH" ]; then
    echo "$LINK_PATH exists but is not a symlink — skipping"
fi

echo "uvstart has ben uninstalled." 
