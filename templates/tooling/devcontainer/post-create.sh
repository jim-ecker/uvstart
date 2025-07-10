#!/bin/bash

# Post-create script for {{ project_name_title }} development environment
# This script runs once after the container is created

set -e

echo "=== Setting up {{ project_name_title }} development environment ==="

# Update package lists
sudo apt-get update

# Install additional system dependencies
{% if has_notebook %}
echo "Installing Jupyter dependencies..."
sudo apt-get install -y pandoc texlive-xetex texlive-fonts-recommended texlive-plain-generic
{% endif %}

{% if has_docker %}
echo "Configuring Docker permissions..."
sudo usermod -aG docker vscode
{% endif %}

# Install Python package manager and dependencies
echo "Installing Python dependencies with {{ backend }}..."
{% if backend == "uv" %}
# uv is already installed via features, just sync
uv sync
{% elif backend == "poetry" %}
# Install Poetry if not already installed
if ! command -v poetry &> /dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
fi
poetry install
{% elif backend == "pdm" %}
# Install PDM if not already installed
if ! command -v pdm &> /dev/null; then
    pip install --user pdm
fi
pdm sync
{% else %}
# Fallback to pip
pip install -e .
{% endif %}

# Set up pre-commit hooks
{% if enable_pre_commit %}
echo "Setting up pre-commit hooks..."
{% if backend == "uv" %}
uv run pre-commit install
{% elif backend == "poetry" %}
poetry run pre-commit install
{% else %}
pre-commit install
{% endif %}
{% endif %}

# Configure Git (if not already configured)
if [ -z "$(git config --global user.name)" ]; then
    echo "Configuring Git with placeholder values (please update)..."
    git config --global user.name "{{ author }}"
    git config --global user.email "{{ email }}"
    git config --global init.defaultBranch main
    git config --global pull.rebase false
fi

# Set up shell completion
{% if backend == "uv" and enable_shell_completion %}
echo "Setting up shell completion for uv..."
uv generate-shell-completion zsh > ~/.zsh/completions/_uv
uv generate-shell-completion bash > ~/.bash_completion.d/uv
{% endif %}

# Create necessary directories
mkdir -p .vscode
mkdir -p docs
mkdir -p scripts

{% if has_notebook %}
# Set up Jupyter kernel
echo "Setting up Jupyter kernel..."
{% if backend == "uv" %}
uv run python -m ipykernel install --user --name {{ project_name }} --display-name "{{ project_name_title }}"
{% elif backend == "poetry" %}
poetry run python -m ipykernel install --user --name {{ project_name }} --display-name "{{ project_name_title }}"
{% else %}
python -m ipykernel install --user --name {{ project_name }} --display-name "{{ project_name_title }}"
{% endif %}
{% endif %}

{% if enable_monitoring %}
# Set up monitoring directories
mkdir -p monitoring/grafana
mkdir -p monitoring/prometheus
{% endif %}

# Install additional development tools
echo "Installing additional development tools..."

# GitHub CLI extensions
gh extension install github/gh-copilot || true

# Install useful CLI tools via apt
sudo apt-get install -y \
    htop \
    tree \
    jq \
    curl \
    wget \
    unzip \
    vim \
    nano \
    fd-find \
    ripgrep \
    bat \
    exa

# Set up aliases for modern CLI tools
echo "Setting up shell aliases..."
cat >> ~/.zshrc << 'EOF'

# Modern CLI aliases
alias ls='exa --icons'
alias ll='exa -l --icons'
alias la='exa -la --icons'
alias tree='exa --tree --icons'
alias cat='bat'
alias find='fd'
alias grep='rg'

# Project-specific aliases
alias {{ backend }}-shell='{{ backend }} shell'
alias test='{{ backend }} run pytest'
alias format='{{ backend }} run black . && {{ backend }} run isort .'
alias lint='{{ backend }} run ruff check .'
alias typecheck='{{ backend }} run mypy .'
alias dev='{{ backend }} run uvicorn main:app --reload --host 0.0.0.0'

EOF

# Set up .vscode/settings.json with project-specific settings
cat > .vscode/settings.json << 'EOF'
{
    "python.pythonPath": "{{ python_path }}",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
EOF

{% if has_docker %}
# Set up Docker Compose override for development
if [ ! -f docker-compose.override.yml ]; then
    cat > docker-compose.override.yml << 'EOF'
version: '3.8'
services:
  app:
    volumes:
      - .:/workspace:cached
    environment:
      - DEBUG=true
      - DEVELOPMENT=true
    ports:
      - "8000:8000"
EOF
fi
{% endif %}

# Create useful development scripts
cat > scripts/dev-setup.sh << 'EOF'
#!/bin/bash
# Quick development environment setup
{{ backend }} sync
{% if enable_pre_commit %}
{{ backend }} run pre-commit install
{% endif %}
echo "Development environment ready!"
EOF

chmod +x scripts/dev-setup.sh

# Initialize project if it's a new repository
if [ ! -f .git/config ]; then
    echo "Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: {{ project_name_title }} project setup"
fi

echo "=== Development environment setup complete! ==="
echo ""
echo "Next steps:"
echo "1. Update Git configuration: git config --global user.name 'Your Name'"
echo "2. Update Git configuration: git config --global user.email 'your@email.com'"
{% if has_web or has_fastapi %}
echo "3. Start the development server: {{ backend }} run dev"
{% endif %}
{% if has_notebook %}
echo "3. Start Jupyter Lab: {{ backend }} run jupyter lab"
{% endif %}
echo ""
echo "Happy coding! 🚀" 