#!/bin/bash

set -e

PYTHON_VERSION="$1"
shift

# Default options
BACKEND="uv"
TEMPLATE=""
NO_GIT=false

# Parse optional flags
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --backend)
            BACKEND="$2"
            shift 2
            ;;
        --template)
            TEMPLATE="$2"
            shift 2
            ;;
        --no-git)
            NO_GIT=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Determine project name from current directory, convert to snake_case
PROJECT_NAME="$(basename "$PWD")"
PROJECT_NAME=$(echo "$PROJECT_NAME" | sed -E 's/([a-z0-9])([A-Z])/\1_\2/g' | tr '[:upper:]' '[:lower:]')

# Copy backend Makefile
BACKEND_DIR="$HOME/.local/uvstart/templates/backends"
cp "$BACKEND_DIR/${BACKEND}.makefile" ./Makefile

# Copy core files
CORE_DIR="$HOME/.local/uvstart/templates/core"
cp "$CORE_DIR/.gitignore" .gitignore
cp "$CORE_DIR/main.py" main.py
cp "$CORE_DIR/.gitattributes" .gitattributes

echo "# ${PROJECT_NAME^}" > README.md

# Create pyproject.toml
cat > pyproject.toml <<EOF
[project]
name = "${PROJECT_NAME}"
version = "0.1.0"
requires-python = ">=${PYTHON_VERSION}"
EOF

# Dynamically generate apply_template.mk
TEMPLATE_ROOT="$HOME/.local/uvstart/templates"
cat > apply_template.mk <<EOF
TEMPLATE ?=
TEMPLATE_SRC := $TEMPLATE_ROOT/features/\$(TEMPLATE)
TEMPLATE_DST := .

template:
	@if [ ! -d "\$(TEMPLATE_SRC)" ]; then \\
		echo "Template '\$(TEMPLATE)' not found in \$(TEMPLATE_SRC)"; \\
		exit 1; \\
	fi
	cp -r \$(TEMPLATE_SRC)/* \$(TEMPLATE_DST)
	@if [ -f "\$(TEMPLATE_SRC)/requirements.txt" ]; then \\
		echo "Adding dependencies from \$(TEMPLATE_SRC)/requirements.txt to pyproject.toml..."; \\
		awk '/^\\[project\\]/ { print; print "dependencies = ["; while ((getline line < "\$(TEMPLATE_SRC)/requirements.txt") > 0) print "    \\"" line "\\","; print "]"; next } 1' pyproject.toml > pyproject.tmp; \\
		mv pyproject.tmp pyproject.toml; \\
		echo "Syncing dependencies..."; \\
		make sync; \\
	fi
	@echo "Applied template: \$(TEMPLATE)"
EOF

# Initialize git repo (unless disabled)
if [[ "$NO_GIT" = false ]]; then
    git init --initial-branch=main > /dev/null
    git add .
    git commit -m "Initial project scaffold for $PROJECT_NAME" > /dev/null
fi

echo "Project '$PROJECT_NAME' initialized with backend '$BACKEND'"

# Apply template if specified (so requirements & files are available immediately)
if [[ -n "$TEMPLATE" ]]; then
    make template TEMPLATE="$TEMPLATE"
fi

