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

# Determine project name from current directory
PROJECT_NAME="$(basename "$PWD")"
PROJECT_NAME=$(echo "$PROJECT_NAME" | sed -E 's/([a-z0-9])([A-Z])/\1_\2/g' | tr '[:upper:]' '[:lower:]')

# Create base files in current directory
cp "$(
    cd "$(dirname "$0")/../templates/backends"
    pwd
)/${BACKEND}.makefile" ./Makefile

CORE_TEMPLATES="$(cd "$(dirname "$0")/../templates/core" && pwd)"
cp "$CORE_TEMPLATES/.gitignore" .gitignore
cp "$CORE_TEMPLATES/main.py" main.py
cp "$CORE_TEMPLATES/.gitattributes" .gitattributes
cp "$CORE_TEMPLATES/apply_template.mk" apply_template.mk

echo "# ${PROJECT_NAME^}" > README.md

# Create pyproject.toml
cat > pyproject.toml <<EOF
[project]
name = "${PROJECT_NAME}"
version = "0.1.0"
requires-python = ">=${PYTHON_VERSION}"
EOF

# Initialize git repo (unless disabled)
if [[ "$NO_GIT" = false ]]; then
    git init --initial-branch=main > /dev/null
    git add .
    git commit -m "Initial project scaffold for $PROJECT_NAME" > /dev/null
fi

echo "Project '$PROJECT_NAME' initialized with backend '$BACKEND'"

# Apply template if specified
if [[ -n "$TEMPLATE" ]]; then
    bash "$(dirname "$0")/template.sh" apply "$TEMPLATE"
fi

