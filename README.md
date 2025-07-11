# uvstart

`uvstart` is a **fast Python project initializer** that makes creating and sharing reproducible projects simple. From basic scripts to complex applications, uvstart handles everything with modern tools like [`uv`](https://github.com/astral-sh/uv) and [`poetry`](https://python-poetry.org/).

**v2.0 Update:** Streamlined project generation with unified command interface.

---

## Key Features

### **Project Generation**
- **Unified Interface:** Single `generate` command for all project types
- **Backend Agnostic:** Works with `uv`, `poetry`, and `pdm`
- **Template System:** Built-in templates for common project types
- **Interactive Setup:** Step-by-step project initialization
- **Modern Tooling:** Integrated testing, linting, and development tools

### **Performance and Compatibility**
- Python-based CLI with minimal dependencies
- Support for `uv`, `poetry`, and `pdm` backends
- Enhanced `Makefile` task runner (universal compatibility)
- Backend abstraction layer for unified operations

### **Project Structure and Tooling**
- Backend abstraction layer (works with any supported Python package manager)
- Comprehensive project templates for common use cases
- Built-in testing, linting, and development tools
- Git-ready with proper `.gitignore` and configuration

---

## Quick Install

```bash
git clone https://github.com/jim-ecker/uvstart.git
cd uvstart
./installer.sh
```

Ensure `~/.local/bin` is in your `$PATH`:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
uvstart doctor  # Verify installation
```

---

## Project Generation

### **Create New Projects**
```bash
# Generate from built-in templates
uvstart generate my-api --features web --backend uv
uvstart generate my-tool --features cli --backend poetry
uvstart generate my-analysis --features notebook --backend pdm
uvstart generate my-model --features pytorch --backend uv

# Customize project details
uvstart generate my-project --features cli --backend uv --description "My awesome project" --author "Your Name"
```

### **Initialize in Current Directory**
```bash
mkdir MyProject && cd MyProject
uvstart init . --python-version 3.12 --backend uv --features cli
```

### **Available Features**
- **cli:** Command-line application with Click
- **web:** FastAPI web application
- **notebook:** Data science project with Jupyter
- **pytorch:** Deep learning project with PyTorch

### **Supported Backends**
- **uv:** Extremely fast package manager
- **poetry:** Mature dependency management
- **pdm:** Fast Python package manager

---

## Project Management

### **Dependency Management**
```bash
# Add packages
uvstart add requests pandas

# Add development dependencies
uvstart add --dev pytest black

# Remove packages
uvstart remove unused-package

# Sync dependencies
uvstart sync
uvstart sync --dev
```

### **Running Projects**
```bash
# Run the main application
uvstart run python main.py

# Run with arguments
uvstart run python main.py --help

# Run tests
uvstart run pytest
```

### **Project Information**
```bash
# Show backend information
uvstart info

# List installed packages
uvstart list

# Analyze current project
uvstart analyze
```

---

## Development Workflow

Every `uvstart` project includes a comprehensive `Makefile`:

```bash
# Development commands
make sync         # Install dependencies
make run          # Run main application
make test         # Run test suite
make fmt          # Format code
make lint         # Lint and type check
make clean        # Clean build artifacts

# Environment management
make add          # Add dependencies interactively
make repl         # Start Python REPL
make notebook     # Launch Jupyter
make doctor       # Health check

# Template operations
make template TEMPLATE=web    # Apply template
make templates               # List templates
```

---

## Built-in Templates

### **Web Applications**
- **web:** FastAPI REST APIs with authentication, docs, testing

### **CLI Applications**
- **cli:** Modern command-line tools with Click and argparse

### **Data Science**
- **notebook:** Jupyter with pandas, matplotlib, analysis pipeline

### **Machine Learning**
- **pytorch:** Deep learning with training pipelines, TensorBoard

### **Advanced Templates**
- **microservice:** Cloud-native services with Docker, Kubernetes
- **mlops:** Complete ML workflow with tracking and deployment

---

## Backend Support

uvstart works seamlessly with modern Python package managers:

| Backend | Speed | Environment | Lock Files | Publishing |
|---------|-------|-------------|------------|------------|
| **uv** | Extremely fast | `__pypackages__/` | `uv.lock` | External tools |
| **poetry** | Mature | `.venv/` | `poetry.lock` | `poetry publish` |
| **pdm** | Fast | `.venv/` | `pdm.lock` | `pdm publish` |

**Auto-detection:** uvstart automatically detects your preferred backend and provides unified commands.

---

## System Health

```bash
uvstart doctor                    # Comprehensive environment check
```

**Checks include:**
- Python versions and installations
- Package managers (uv, poetry, pdm)
- Development tools (git, make, editors)
- uvstart installation health
- System compatibility

---

## Examples

### **Quick API Development**
```bash
uvstart generate test-api --features web --backend uv
cd test-api && make sync && make run
# FastAPI server running at http://localhost:8000
```

### **CLI Tool Creation**
```bash
uvstart generate awesome-cli --features cli --backend uv
cd awesome-cli && make sync
make run hello --name "World"
```

### **Data Analysis Project**
```bash
uvstart generate analysis --features notebook --backend poetry
cd analysis && make sync
make notebook
```

### **Machine Learning Project**
```bash
uvstart generate ml-project --features pytorch --backend uv
cd ml-project && make sync
make run python train.py
```

---

## Advanced Features

### **Environment Variables**
```bash
export UVSTART_DEFAULT_BACKEND="uv"
export UVSTART_AUTO_UPDATE="true"
export UVSTART_TEMPLATES_DIR="$HOME/my-templates"
```

### **Custom Template Directory**
```bash
# Create custom templates
mkdir ~/.local/uvstart/templates/features/my-template
# Add template files and template.yaml
# Then use with existing features: --features cli,web,notebook,pytorch
```

---

## Contributing

We welcome contributions! Here's how to get started:

```bash
git clone https://github.com/jim-ecker/uvstart.git
cd uvstart
uvstart init . --python-version 3.12 --backend uv
make sync && make test
```

**Development areas:**
- New template presets
- Backend integrations
- Documentation and examples

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Why uvstart?

**Traditional project setup:**
- Manual directory creation
- Copy-paste configuration files
- Hunt for the right dependencies
- Hope the setup works
- Spend hours on reproducibility

**uvstart experience:**
- One command creates everything
- Professional templates with best practices
- Automatic dependency management
- Perfect reproducibility out of the box
- Focus on building, not configuring

**Get started:**

```bash
uvstart generate my-project --features cli --backend uv
# Start building your application
```

