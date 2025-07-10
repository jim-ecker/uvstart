#!/bin/bash
# Backend Abstraction Layer for uvstart
# Provides unified interface for uv and poetry backends

# Colors for consistent output
BLUE='\033[34m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
NC='\033[0m'

# Backend detection function
detect_backend() {
    # Check for explicit backend markers first
    if [[ -f "pdm.lock" ]]; then
        echo "pdm"
        return
    fi
    
    if [[ -f "uv.lock" || -d "__pypackages__" ]]; then
        echo "uv"
        return
    fi
    
    if [[ -f "poetry.lock" ]] || ( [[ -f "pyproject.toml" ]] && grep -q "poetry" pyproject.toml 2>/dev/null ); then
        echo "poetry"
        return
    fi
    
    # Fallback: check what's installed
    if command -v pdm >/dev/null 2>&1; then
        echo "pdm"
    elif command -v uv >/dev/null 2>&1; then
        echo "uv"
    elif command -v poetry >/dev/null 2>&1; then
        echo "poetry"
    else
        echo "unknown"
    fi
}

# Get the current backend
CURRENT_BACKEND=$(detect_backend)

# Unified logging functions
log_info() {
    echo -e "${BLUE}$1${NC}"
}

log_success() {
    echo -e "${GREEN}$1${NC}"
}

log_warning() {
    echo -e "${YELLOW}$1${NC}"
}

log_error() {
    echo -e "${RED}$1${NC}"
}

# Check if backend is available
check_backend_available() {
    local backend="$1"
    case "$backend" in
        pdm)
            if ! command -v pdm >/dev/null 2>&1; then
                log_error "pdm not found. Install it with: curl -sSL https://pdm-project.org/install-pdm.py | python3 -"
                return 1
            fi
            ;;
        uv)
            if ! command -v uv >/dev/null 2>&1; then
                log_error "uv not found. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
                return 1
            fi
            ;;
        poetry)
            if ! command -v poetry >/dev/null 2>&1; then
                log_error "poetry not found. Install it with: curl -sSL https://install.python-poetry.org | python3 -"
                return 1
            fi
            ;;
        *)
            log_error "Unknown backend: $backend"
            return 1
            ;;
    esac
    return 0
}

# Unified sync operation
backend_sync() {
    log_info "Installing dependencies with $CURRENT_BACKEND..."
    
    check_backend_available "$CURRENT_BACKEND" || return 1
    
    case "$CURRENT_BACKEND" in
        pdm)
            pdm sync "$@"
            ;;
        uv)
            uv sync "$@"
            ;;
        poetry)
            poetry install "$@"
            ;;
        *)
            log_error "Cannot sync: backend not detected"
            return 1
            ;;
    esac
}

# Unified development dependencies sync
backend_sync_dev() {
    log_info "Installing development dependencies with $CURRENT_BACKEND..."
    
    check_backend_available "$CURRENT_BACKEND" || return 1
    
    case "$CURRENT_BACKEND" in
        pdm)
            pdm sync --dev "$@"
            ;;
        uv)
            uv sync --group dev "$@"
            ;;
        poetry)
            poetry install --with dev "$@"
            ;;
        *)
            log_error "Cannot sync dev dependencies: backend not detected"
            return 1
            ;;
    esac
}

# Unified add operation
backend_add() {
    local packages="$*"
    log_info "Adding packages: $packages"
    
    check_backend_available "$CURRENT_BACKEND" || return 1
    
    case "$CURRENT_BACKEND" in
        pdm)
            pdm add $packages
            ;;
        uv)
            uv add $packages
            ;;
        poetry)
            poetry add $packages
            ;;
        *)
            log_error "Cannot add packages: backend not detected"
            return 1
            ;;
    esac
}

# Unified add development dependencies
backend_add_dev() {
    local packages="$*"
    log_info "Adding development packages: $packages"
    
    check_backend_available "$CURRENT_BACKEND" || return 1
    
    case "$CURRENT_BACKEND" in
        pdm)
            pdm add --dev $packages
            ;;
        uv)
            uv add --group dev $packages
            ;;
        poetry)
            poetry add --group dev $packages
            ;;
        *)
            log_error "Cannot add dev packages: backend not detected"
            return 1
            ;;
    esac
}

# Unified remove operation
backend_remove() {
    local packages="$*"
    log_info "Removing packages: $packages"
    
    check_backend_available "$CURRENT_BACKEND" || return 1
    
    case "$CURRENT_BACKEND" in
        pdm)
            pdm remove $packages
            ;;
        uv)
            uv remove $packages
            ;;
        poetry)
            poetry remove $packages
            ;;
        *)
            log_error "Cannot remove packages: backend not detected"
            return 1
            ;;
    esac
}

# Unified run operation
backend_run() {
    check_backend_available "$CURRENT_BACKEND" || return 1
    
    case "$CURRENT_BACKEND" in
        pdm)
            pdm run "$@"
            ;;
        uv)
            uv run "$@"
            ;;
        poetry)
            poetry run "$@"
            ;;
        *)
            log_error "Cannot run command: backend not detected"
            return 1
            ;;
    esac
}

# Unified package listing
backend_list() {
    check_backend_available "$CURRENT_BACKEND" || return 1
    
    case "$CURRENT_BACKEND" in
        pdm)
            pdm list "$@"
            ;;
        uv)
            uv pip list "$@"
            ;;
        poetry)
            poetry show "$@"
            ;;
        *)
            log_error "Cannot list packages: backend not detected"
            return 1
            ;;
    esac
}

# Get python version command
backend_python_version() {
    case "$CURRENT_BACKEND" in
        pdm)
            pdm run python --version
            ;;
        uv)
            uv run python --version
            ;;
        poetry)
            poetry run python --version
            ;;
        *)
            python --version 2>/dev/null || python3 --version
            ;;
    esac
}

# Clean up backend-specific files
backend_clean() {
    log_info "Cleaning up $CURRENT_BACKEND files..."
    
    case "$CURRENT_BACKEND" in
        pdm)
            rm -rf __pypackages__ pdm.lock .pdm-python
            ;;
        uv)
            rm -rf __pypackages__ uv.lock
            ;;
        poetry)
            rm -rf .venv poetry.lock
            ;;
        *)
            # Clean all just in case
            rm -rf .venv __pypackages__ poetry.lock uv.lock pdm.lock .pdm-python
            ;;
    esac
    
    # Common cleanup
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    rm -rf .pytest_cache .coverage htmlcov build dist
}

# Unified template dependency installation
backend_install_template_dependencies() {
    local requirements_file="$1"
    
    if [[ ! -f "$requirements_file" ]]; then
        return 0
    fi
    
    log_info "Installing template dependencies..."
    
    check_backend_available "$CURRENT_BACKEND" || return 1
    
    # Read requirements and add them one by one
    while IFS= read -r line; do
        # Skip empty lines and comments
        if [[ -n "$line" && "${line#\#}" == "$line" ]]; then
            backend_add "$line"
        fi
    done < "$requirements_file"
    
    # Clean up the requirements file since dependencies are now in pyproject.toml
    rm -f "$requirements_file"
    
    # Sync to ensure everything is installed
    backend_sync
}

# Get backend-specific doctor information
backend_doctor_info() {
    local errors=0
    
    echo -n "$CURRENT_BACKEND: "
    if check_backend_available "$CURRENT_BACKEND" >/dev/null 2>&1; then
        case "$CURRENT_BACKEND" in
            pdm)
                echo -e "${GREEN}$(pdm --version)${NC}"
                ;;
            uv)
                echo -e "${GREEN}$(uv --version)${NC}"
                ;;
            poetry)
                echo -e "${GREEN}$(poetry --version)${NC}"
                ;;
        esac
    else
        echo -e "${RED}NOT FOUND${NC}"
        errors=$((errors + 1))
    fi
    
    echo -n "Dependencies: "
    if [[ -f "pyproject.toml" ]]; then
        if backend_list >/dev/null 2>&1; then
            echo -e "${GREEN}INSTALLED${NC}"
        else
            echo -e "${YELLOW}WARNING: Run 'make sync' to install${NC}"
        fi
    else
        echo -e "${YELLOW}WARNING: No pyproject.toml found${NC}"
    fi
    
    return $errors
}

# Show backend information
backend_info() {
    echo "Backend: $CURRENT_BACKEND"
    echo
    echo -e "${BLUE}Python version:${NC}"
    backend_python_version
    echo
    echo -e "${BLUE}Installed packages:${NC}"
    backend_list 2>/dev/null || echo "No packages installed"
}

# Export functions for use in other scripts
export -f detect_backend
export -f check_backend_available
export -f backend_sync
export -f backend_sync_dev
export -f backend_add
export -f backend_add_dev
export -f backend_remove
export -f backend_run
export -f backend_list
export -f backend_python_version
export -f backend_clean
export -f backend_install_template_dependencies
export -f backend_doctor_info
export -f backend_info
export -f log_info
export -f log_success
export -f log_warning
export -f log_error

# Export the current backend for use in other scripts
export CURRENT_BACKEND 