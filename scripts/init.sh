#!/bin/bash
PYTHON_VERSION="$1"
shift

BACKEND="uv"
TEMPLATE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --backend)
      BACKEND="$2"
      shift 2
      ;;
    --template)
      TEMPLATE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

PROJECT_NAME=$(basename "$PWD")
PROJECT_NAME=$(echo "$PROJECT_NAME" | sed -E 's/([a-z0-9])([A-Z])/\1_\2/g' | tr '[:upper:]' '[:lower:]')

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load and apply backend Makefile
TEMPLATE_FILE="$SCRIPT_DIR/templates/backends/${BACKEND}.makefile"
if [[ ! -f "$TEMPLATE_FILE" ]]; then
  echo "Backend template not found: $TEMPLATE_FILE"
  exit 1
fi
sed "s/{{PYTHON_VERSION}}/$PYTHON_VERSION/g; s/{{PROJECT_NAME}}/$PROJECT_NAME/g" "$TEMPLATE_FILE" > Makefile

cp "$SCRIPT_DIR/apply_template.mk" .

echo 'print("Hello from uvstart!")' > main.py
mkdir -p notebooks

echo "*.ipynb filter=nbstripout" > .gitattributes
cat <<EOF > .gitignore
.venv/
__pypackages__/
.ipynb_checkpoints/
__pycache__/
EOF

cat <<EOF > README.md
# $PROJECT_NAME

Bootstrapped with uvstart.
EOF

# If template specified, apply it
if [[ -n "$TEMPLATE" ]]; then
  "$SCRIPT_DIR/scripts/template.sh" apply "$TEMPLATE"
fi

if [ ! -d .git ]; then
  git init
fi
if [ -z "$(git rev-parse --quiet HEAD)" ]; then
  git add .
  git commit -m "Initial scaffold with uvstart"
fi

echo "Project '$PROJECT_NAME' initialized with backend '$BACKEND'"
