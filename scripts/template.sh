#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/templates/features"

COMMAND="$1"
shift

case "$COMMAND" in
  apply)
    NAME="$1"
    [ -z "$NAME" ] && echo "Please provide a template name" && exit 1
    SRC="$TEMPLATE_DIR/$NAME"
    if [ ! -d "$SRC" ]; then
      echo "Template '$NAME' not found"
      exit 1
    fi
    cp -r "$SRC/"* .
    echo "Applied template: $NAME"
    ;;
  list)
    echo "Available templates:"
    ls "$TEMPLATE_DIR"
    ;;
  *)
    echo "Usage:"
    echo "  uvstart template list"
    echo "  uvstart template apply <name>"
    exit 1
    ;;
esac
