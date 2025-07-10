# Shared Makefile for uvstart projects
# Backend-agnostic implementation using the abstraction layer

# Include the backend abstraction layer
SHELL := /bin/bash
ABSTRACTION_LAYER := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))/backend_abstraction.sh

# Colors for output (works on most terminals)
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

# Default target - show help
.DEFAULT_GOAL := help

.PHONY: help sync sync-dev add add-dev run dev repl test test-cov fmt lint typecheck audit notebook kernel template templates clean info update-uvstart doctor

# Help target with descriptions
help: ## Show this help message
	@echo "$(BLUE)Available commands:$(NC)"
	@echo
	@echo "$(GREEN)Development Workflow:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z_-]+:.*?## .*Development/ {printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "$(GREEN)Environment Management:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z_-]+:.*?## .*Environment/ {printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "$(GREEN)Project Management:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z_-]+:.*?## .*Project/ {printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make sync              # Install dependencies"
	@echo "  make run               # Run the application"
	@echo "  make test              # Run tests"
	@echo "  make template TEMPLATE=notebook  # Apply a template"

# Install/sync dependencies
sync: ## Development - Install dependencies
	@source $(ABSTRACTION_LAYER) && backend_sync
	@echo "$(GREEN)SUCCESS: Dependencies installed!$(NC)"

# Install development dependencies
sync-dev: ## Development - Install development dependencies
	@source $(ABSTRACTION_LAYER) && backend_sync_dev
	@echo "$(GREEN)SUCCESS: Development dependencies installed!$(NC)"

# Add new dependencies interactively
add: ## Environment - Add new dependencies interactively
	@echo "$(BLUE)Add new dependencies:$(NC)"
	@echo "  Examples: requests, numpy>=1.20, 'fastapi[all]'"
	@read -p "Enter packages to add: " pkgs; \
	if [ -n "$$pkgs" ]; then \
		source $(ABSTRACTION_LAYER) && backend_add $$pkgs && echo "$(GREEN)SUCCESS: Added: $$pkgs$(NC)"; \
	else \
		echo "$(RED)ERROR: No packages specified$(NC)"; \
	fi

# Add development dependencies
add-dev: ## Environment - Add development dependencies
	@echo "$(BLUE)Add development dependencies:$(NC)"
	@read -p "Enter dev packages to add: " pkgs; \
	if [ -n "$$pkgs" ]; then \
		source $(ABSTRACTION_LAYER) && backend_add_dev $$pkgs && echo "$(GREEN)SUCCESS: Added to dev group: $$pkgs$(NC)"; \
	else \
		echo "$(RED)ERROR: No packages specified$(NC)"; \
	fi

# Run the main application
run: ## Development - Run the main application
	@echo "$(BLUE)Running $(PROJECT_NAME)...$(NC)"
	@source $(ABSTRACTION_LAYER) && backend_run python main.py $(ARGS)

# Run with hot reload (if main.py supports it)
dev: ## Development - Run in development mode
	@echo "$(BLUE)Running in development mode...$(NC)"
	@source $(ABSTRACTION_LAYER) && backend_run python main.py --dev $(ARGS)

# Start Python REPL with project dependencies
repl: ## Environment - Start Python REPL with project dependencies
	@echo "$(BLUE)Starting Python REPL...$(NC)"
	@source $(ABSTRACTION_LAYER) && backend_run python

# Run tests
test: ## Development - Run test suite
	@echo "$(BLUE)Running tests...$(NC)"
	@if [ -d "tests" ]; then \
		source $(ABSTRACTION_LAYER) && backend_run pytest $(ARGS); \
	else \
		echo "$(YELLOW)WARNING: No tests directory found. Create tests/ and add test files.$(NC)"; \
	fi

# Run tests with coverage
test-cov: ## Development - Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@if [ -d "tests" ]; then \
		source $(ABSTRACTION_LAYER) && backend_run pytest --cov=$(PROJECT_NAME) --cov-report=term-missing --cov-report=html $(ARGS); \
	else \
		echo "$(YELLOW)WARNING: No tests directory found.$(NC)"; \
	fi

# Format code with black and ruff
fmt: ## Development - Format code with black and ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	@source $(ABSTRACTION_LAYER); \
	if backend_run black --version >/dev/null 2>&1; then \
		backend_run black .; \
	else \
		echo "$(YELLOW)WARNING: black not available. Install with: make add-dev$(NC)"; \
	fi; \
	if backend_run ruff --version >/dev/null 2>&1; then \
		backend_run ruff check --fix .; \
	else \
		echo "$(YELLOW)WARNING: ruff not available. Install with: make add-dev$(NC)"; \
	fi
	@echo "$(GREEN)SUCCESS: Code formatted!$(NC)"

# Lint code
lint: ## Development - Lint and check code
	@echo "$(BLUE)Linting code...$(NC)"
	@source $(ABSTRACTION_LAYER); \
	ERRORS=0; \
	if backend_run ruff --version >/dev/null 2>&1; then \
		if ! backend_run ruff check .; then ERRORS=$$((ERRORS + 1)); fi; \
	else \
		echo "$(YELLOW)WARNING: ruff not available$(NC)"; \
	fi; \
	if backend_run black --version >/dev/null 2>&1; then \
		if ! backend_run black --check .; then ERRORS=$$((ERRORS + 1)); fi; \
	else \
		echo "$(YELLOW)WARNING: black not available$(NC)"; \
	fi; \
	if [ $$ERRORS -eq 0 ]; then \
		echo "$(GREEN)SUCCESS: All checks passed!$(NC)"; \
	else \
		echo "$(RED)ERROR: Found $$ERRORS issue(s). Run 'make fmt' to fix formatting.$(NC)"; \
		exit 1; \
	fi

# Type check
typecheck: ## Development - Run type checking
	@echo "$(BLUE)Type checking...$(NC)"
	@source $(ABSTRACTION_LAYER); \
	if backend_run mypy --version >/dev/null 2>&1; then \
		backend_run mypy .; \
	else \
		echo "$(YELLOW)WARNING: mypy not available. Install with: make add-dev$(NC)"; \
	fi

# Security audit
audit: ## Development - Run security audit
	@echo "$(BLUE)Running security audit...$(NC)"
	@source $(ABSTRACTION_LAYER); \
	if backend_run safety --version >/dev/null 2>&1; then \
		case "$$CURRENT_BACKEND" in \
			uv) \
				backend_run pip list --format=json | backend_run safety check --stdin; \
				;; \
			poetry) \
				poetry export -f requirements.txt --without-hashes | backend_run safety check --stdin; \
				;; \
		esac; \
	else \
		echo "$(YELLOW)WARNING: safety not available. Install with: make add-dev$(NC)"; \
	fi

# Install and launch Jupyter notebook
notebook: ## Environment - Setup and launch Jupyter notebook
	@echo "$(BLUE)Setting up Jupyter notebook...$(NC)"
	@source $(ABSTRACTION_LAYER); \
	if ! backend_run python -c "import notebook" 2>/dev/null; then \
		echo "Installing Jupyter..."; \
		backend_add_dev notebook ipykernel matplotlib; \
	fi
	@echo "$(BLUE)Launching Jupyter notebook...$(NC)"
	@source $(ABSTRACTION_LAYER) && backend_run jupyter notebook

# Install Jupyter kernel for this project
kernel: ## Environment - Install Jupyter kernel for this project
	@echo "$(BLUE)Installing Jupyter kernel...$(NC)"
	@source $(ABSTRACTION_LAYER) && backend_run python -m ipykernel install --user --name="$(PROJECT_NAME)" --display-name="$(PROJECT_NAME)"
	@echo "$(GREEN)SUCCESS: Kernel '$(PROJECT_NAME)' installed!$(NC)"

# Apply a template to the current project
template: ## Project - Apply a template (use TEMPLATE=name)
	@if [ -z "$(TEMPLATE)" ]; then \
		echo "$(RED)ERROR: Please specify a template: make template TEMPLATE=notebook$(NC)"; \
		echo "$(BLUE)Available templates:$(NC)"; \
		ls "$$HOME/.local/uvstart/templates/features" | sed 's/^/  - /'; \
		exit 1; \
	fi
	@TEMPLATE_ROOT="$$HOME/.local/uvstart/templates"; \
	TEMPLATE_SRC="$$TEMPLATE_ROOT/features/$(TEMPLATE)"; \
	if [ ! -d "$$TEMPLATE_SRC" ]; then \
		echo "$(RED)ERROR: Template '$(TEMPLATE)' not found in $$TEMPLATE_SRC$(NC)"; \
		echo "$(BLUE)Available templates:$(NC)"; \
		ls "$$TEMPLATE_ROOT/features" | sed 's/^/  - /'; \
		exit 1; \
	fi; \
	echo "$(BLUE)Applying template: $(TEMPLATE)$(NC)"; \
	cp -r "$$TEMPLATE_SRC"/* .; \
	if [ -f "$$TEMPLATE_SRC/requirements.txt" ]; then \
		echo "$(BLUE)Adding template dependencies...$(NC)"; \
		source $(ABSTRACTION_LAYER) && backend_install_template_dependencies "$$TEMPLATE_SRC/requirements.txt"; \
	fi; \
	echo "$(GREEN)SUCCESS: Template '$(TEMPLATE)' applied successfully!$(NC)"; \
	if [ -f "$$TEMPLATE_SRC/README.md" ]; then \
		echo "$(BLUE)Template instructions:$(NC)"; \
		cat "$$TEMPLATE_SRC/README.md"; \
	fi

# List available templates
templates: ## Project - List available templates
	@echo "$(BLUE)Available templates:$(NC)"
	@ls "$$HOME/.local/uvstart/templates/features" | sed 's/^/  /'

# Clean up generated files and caches
clean: ## Development - Clean up generated files and caches
	@echo "$(BLUE)Cleaning up...$(NC)"
	@source $(ABSTRACTION_LAYER) && backend_clean
	@echo "$(GREEN)SUCCESS: Cleanup complete!$(NC)"

# Show project info
info: ## Project - Show project information
	@echo "$(BLUE)Project Information$(NC)"
	@echo "====================="
	@echo "Name: $(PROJECT_NAME)"
	@echo "Python: $(PYTHON_VERSION)"
	@source $(ABSTRACTION_LAYER) && backend_info

# Update uvstart itself
update-uvstart: ## Project - Update uvstart to latest version
	@echo "$(BLUE)Updating uvstart...$(NC)"
	@if [ -d "$$HOME/.local/uvstart/.git" ]; then \
		cd "$$HOME/.local/uvstart" && git pull; \
		echo "$(GREEN)SUCCESS: uvstart updated!$(NC)"; \
	else \
		echo "$(YELLOW)WARNING: uvstart not installed as git repository. Please reinstall.$(NC)"; \
	fi

# Health check for development environment
doctor: ## Project - Run environment health check
	@echo "$(BLUE)Environment Health Check$(NC)"
	@echo "=========================="
	@echo
	@source $(ABSTRACTION_LAYER); \
	ERRORS=0; \
	echo -n "Python $(PYTHON_VERSION): "; \
	if backend_python_version | grep -q "$(PYTHON_VERSION)"; then \
		echo "$(GREEN)FOUND$(NC)"; \
	else \
		echo "$(RED)NOT FOUND$(NC)"; \
		ERRORS=$$((ERRORS + 1)); \
	fi; \
	backend_doctor_info; \
	DOCTOR_ERRORS=$$?; \
	ERRORS=$$((ERRORS + DOCTOR_ERRORS)); \
	echo -n "Git repository: "; \
	if git rev-parse --git-dir >/dev/null 2>&1; then \
		echo "$(GREEN)INITIALIZED$(NC)"; \
	else \
		echo "$(YELLOW)WARNING: Not a git repository$(NC)"; \
	fi; \
	echo; \
	if [ $$ERRORS -eq 0 ]; then \
		echo "$(GREEN)Quick start: make sync && make run$(NC)"; \
	else \
		echo "$(RED)Fix the errors above for optimal experience$(NC)"; \
	fi 