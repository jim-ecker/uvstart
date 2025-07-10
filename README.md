# uvstart

`uvstart` is a **revolutionary Python project initializer** that makes creating and sharing reproducible projects **ridiculously simple**. From basic scripts to complex research experiments, uvstart handles everything with modern tools like [`uv`](https://github.com/astral-sh/uv) and [`poetry`](https://python-poetry.org/).

**New in v2.0:** Revolutionary template system with **research reproducibility** and **one-command template creation**.

---

## Key Features

### **Template Revolution**
- **Research Reproducibility:** Generate replicable experiment templates in 30 seconds
- **Directory Magic:** Turn ANY project into a template with one command
- **Smart Presets:** Create professional templates instantly
- **Interactive Wizard:** Guided template creation for beginners
- **Power User Mode:** Advanced YAML-based templates with inheritance

### **Modern & Fast**
- Shell-based CLI with **minimal dependencies**
- Support for `uv`, `poetry`, `pdm`, `rye`, and `hatch`
- Enhanced `Makefile` task runner (universal compatibility)
- Hybrid Python+C++ architecture for performance

### **Production Ready**
- Backend abstraction layer (works with any Python package manager)
- Comprehensive project templates for every use case
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

## Template Creation - Five Levels of Power

### **Level 1: Research Experiment Replication**
**Perfect for scientific reproducibility - the ultimate game-changer!**

```bash
# Set up your research project exactly as you want
mkdir my-ml-experiment
cd my-ml-experiment
# Create train.py, config.yaml, requirements.txt, notebooks...

# Generate replicable research template in 30 seconds
uvstart template research my-experiment
```

**Automatically extracts:**
- Research hypothesis and methodology
- Experimental parameters (learning rates, epochs, batch sizes)
- Random seeds for exact reproducibility
- Dependencies and environment specs
- Dataset requirements
- Creates comprehensive REPLICATION.md guide

**Perfect for:**
- Machine learning experiments
- Data analysis pipelines
- Scientific computing projects
- Thesis and research papers
- Collaborative research sharing

### **Level 2: Ultimate Directory Simplicity**
**Turn ANY existing project into a template!**

```bash
# Set up your project directory exactly how you want
mkdir my-awesome-project
cd my-awesome-project
# Create all your files, structure, dependencies...

# One command turns it into a reusable template
uvstart template from-directory my-template
```

**Automatically handles:**
- Complete directory structure scanning
- Dependency detection from requirements files
- Smart variable substitution (names, emails, versions)
- Category auto-detection (web, CLI, data science, etc.)
- Ignores build artifacts, git files, caches
- Creates full template.yaml configuration

### **Level 3: Quick Presets**
**Professional templates with one command:**

```bash
uvstart template quick my-api api           # FastAPI REST API
uvstart template quick my-tool cli-tool     # Click CLI application
uvstart template quick scraper web-scraper  # Web scraping project
uvstart template quick analysis data-app    # Data analysis with pandas
uvstart template quick chatbot bot          # Discord/Telegram bot
uvstart template quick simple simple        # Basic Python project
```

### **Level 4: Interactive Wizard**
**Guided creation for beginners:**

```bash
uvstart template new
# Answer 3-4 simple questions, get a complete template!
```

### **Level 5: Power User Mode**
**Advanced YAML-based templates with:**
- Template inheritance systems
- Complex Jinja2 templating
- CI/CD pipeline generation
- Advanced dependency management
- Custom hooks and automation

---

## Project Generation

### **Create New Projects**
```bash
# Generate from any template
uvstart generate my-project template-name

# Built-in templates
uvstart generate my-api web          # FastAPI web application
uvstart generate my-tool cli         # Command-line application
uvstart generate my-analysis notebook # Data science project
uvstart generate my-model pytorch    # Deep learning project

# Your custom templates
uvstart generate my-experiment my-research-template
```

### **Initialize in Current Directory**
```bash
mkdir MyProject && cd MyProject
uvstart init 3.12 --backend uv --template cli
```

---

## Template Management

```bash
# List available templates
uvstart template list

# Show template details  
uvstart template info template-name

# View presets
uvstart template presets

# Create from directory (ultimate simplicity)
uvstart template from-directory my-template

# Research template (reproducibility)
uvstart template research my-experiment

# Quick preset
uvstart template quick my-api api

# Interactive creation
uvstart template new
```

---

## Research Reproducibility Example

**Traditional research sharing:**
```bash
# Email Python scripts
# Hope dependencies work
# Manually document setup
# Pray for reproducibility
```

**uvstart research templates:**
```bash
# 1. Set up experiment
mkdir cifar10-experiment
cd cifar10-experiment
# Create train.py, config.yaml, requirements.txt, README.md

# 2. Generate replicable template (30 seconds)
uvstart template research cifar10-classification

# 3. Share template (not raw code)
# Others can perfectly replicate with:
uvstart generate my-version cifar10-classification
```

**Generated replication package includes:**
- Complete project template with templated parameters
- REPLICATION.md with step-by-step instructions
- Extracted research metadata (hypothesis, methodology)
- Preserved environment and dependency specifications
- Random seed tracking for exact reproducibility

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
- **FastAPI:** REST APIs with authentication, docs, testing
- **Flask:** Lightweight web applications
- **Django:** Full-featured web framework setup

### **CLI Applications**
- **Click:** Modern command-line tools with subcommands
- **Argparse:** Traditional CLI applications
- **Rich:** Beautiful terminal applications

### **Data Science**
- **Notebook:** Jupyter with pandas, matplotlib, analysis pipeline
- **MLOps:** Complete ML workflow with tracking and deployment
- **Research:** LaTeX papers with bibliography and data integration

### **Machine Learning**
- **PyTorch:** Deep learning with training pipelines, TensorBoard
- **Computer Vision:** Image processing and CNN architectures
- **NLP:** Language models and text processing pipelines

### **Modern Development**
- **Microservice:** Cloud-native services with Docker, Kubernetes
- **DevContainers:** VS Code development environments
- **CI/CD:** GitHub Actions with security scanning and testing

---

## Backend Support

uvstart works seamlessly with all modern Python package managers:

| Backend | Speed | Environment | Lock Files | Publishing |
|---------|-------|-------------|------------|------------|
| **uv** | Extremely fast | `__pypackages__/` | `uv.lock` | External tools |
| **poetry** | Mature | `.venv/` | `poetry.lock` | `poetry publish` |
| **pdm** | Fast | `.venv/` | `pdm.lock` | `pdm publish` |
| **rye** | Modern | `.venv/` | `requirements.lock` | External tools |
| **hatch** | Flexible | `.venv/` | Custom | `hatch publish` |

**Auto-detection:** uvstart automatically detects your preferred backend and provides unified commands.

---

## System Health

```bash
uvstart doctor                    # Comprehensive environment check
uvstart doctor --verbose         # Detailed system information
```

**Checks include:**
- Python versions and installations
- Package managers (uv, poetry, pip, etc.)
- Development tools (git, make, editors)
- uvstart installation health
- System compatibility

---

## Examples

### **Research Experiment**
```bash
# Set up ML experiment
mkdir image-classification
cd image-classification
# Create train.py, config.yaml, model.py, requirements.txt

# Generate replicable template
uvstart template research image-classification

# Others replicate with:
uvstart generate my-experiment image-classification
cd my-experiment
make sync && make run
```

### **Quick API Development**
```bash
uvstart template quick my-api api
uvstart generate test-api my-api
cd test-api && make sync && make run
# FastAPI server running at http://localhost:8000
```

### **Data Analysis Project**
```bash
mkdir analysis && cd analysis
# Set up notebooks, data processing, visualization
uvstart template from-directory analysis-template

# Share with colleagues
uvstart generate team-analysis analysis-template
```

### **CLI Tool Creation**
```bash
uvstart template quick my-tool cli-tool
uvstart generate awesome-cli my-tool
cd awesome-cli && make sync
make run hello --name "World"
```

---

## Advanced Features

### **Template Inheritance**
```yaml
# Base template with common structure
extends: "base/python-project"
metadata:
  name: "my-specialized-template"
  features: ["web", "database"]
```

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
uvstart template list  # Shows your custom template
```

---

## Research Use Cases

**Perfect for:**
- **Academic Research:** Reproducible experiments, thesis projects
- **Industry R&D:** Systematic experimentation, parameter tracking
- **Machine Learning:** Model training, hyperparameter optimization
- **Data Science:** Analysis pipelines, statistical studies
- **Scientific Computing:** Simulations, numerical methods
- **Collaborative Research:** Team project standardization

**Supported Research Patterns:**
- Configuration-driven experiments
- Jupyter notebook workflows
- Training script automation
- Dataset management
- Results tracking and visualization
- Environment preservation

---

## Contributing

We welcome contributions! Here's how to get started:

```bash
git clone https://github.com/jim-ecker/uvstart.git
cd uvstart
uvstart init 3.12 --backend uv
make sync && make test
```

**Development areas:**
- New template presets
- Backend integrations
- Research workflow improvements
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

**Ready to revolutionize your Python development?**

```bash
uvstart template research my-breakthrough-experiment
# Science happens here
```
