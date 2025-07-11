# uvstart

**The Ultimate Python Project Initializer** - Create, manage, and scale Python projects with modern tools and reproducible workflows.

`uvstart` is a comprehensive project management system that goes beyond simple boilerplate generation. It provides **experimental reproducibility**, **template-driven development**, and **intelligent project analysis** for Python projects of any scale.

---

## Key Features

### Project Generation & Management
- **Unified Interface:** One command for all project types and workflows
- **Auto-Detection:** Intelligent project naming from directory names  
- **Backend Agnostic:** Seamless support for `uv`, `poetry`, and `pdm`
- **Template System:** Built-in + custom templates for any use case

### Experimental Workflows
- **Reproducible Experiments:** Create templates from existing directories
- **Configuration Tracking:** Intelligent analysis of experiment parameters
- **Template Origin Tracking:** Know which template created each experiment
- **Parameter Isolation:** Clean separation between experiment runs

### Intelligent Analysis
- **Project Health:** Comprehensive project structure and configuration analysis
- **Experiment Detection:** Automatic identification of experiment configurations
- **Development Environment:** CI/CD, tooling, and quality checks analysis
- **Smart Recommendations:** Actionable suggestions for project improvements

### Advanced Template System
- **From-Directory Templates:** Create templates from any existing project
- **Enhanced Templating:** Support for Jinja2, YAML, and complex configurations
- **User Templates:** Personal template library with registry management
- **Template Information:** Detailed template metadata and usage information

---

## Quick Start

### Installation
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

### Basic Usage
```bash
# Create a new project (auto-detects name from directory)
mkdir my-awesome-project && cd my-awesome-project
uvstart init --backend uv --features web

# Create in a new directory
uvstart generate my-api --features web --backend uv

# Analyze any project
uvstart analyze
```

---

## Complete Command Reference

### Project Creation

#### `uvstart init` - Initialize Current Directory
```bash
# Basic initialization (auto-detects project name from directory)
uvstart init --backend uv

# With features and custom settings
uvstart init --features web,cli --backend poetry --python-version 3.12

# Override auto-detected name
uvstart init --name custom-name --backend uv
```

#### `uvstart generate` - Create New Projects
```bash
# Create new project in dedicated directory
uvstart generate my-project --features web --backend uv

# In-place generation (current directory)
uvstart generate . --name my-project --features cli

# Comprehensive project setup
uvstart generate api-server \
  --features web \
  --backend uv \
  --python-version 3.12 \
  --description "My awesome API" \
  --author "Your Name" \
  --email "you@example.com"
```

### Project Analysis

#### `uvstart analyze` - Comprehensive Project Intelligence
```bash
# Analyze current project
uvstart analyze

# Analyze specific directory
uvstart analyze --path /path/to/project
```

**What `analyze` shows:**
- **Project Structure:** Files, packages, tests, documentation
- **Backend & Dependencies:** Package manager, versions, lock files, virtual environments
- **Project Metadata:** Name, version, description, author (from `pyproject.toml`)
- **Version Control:** Git status, branch, commits, remote repository
- **Development Environment:** CI/CD, dev tools, code quality tools
- **Detected Features:** Web frameworks, CLI tools, notebooks, ML libraries
- **Experiment Configuration:** Config files, parameters, scripts, template origin
- **Smart Recommendations:** Actionable suggestions for improvements

### Experimental Workflows

#### Template Creation from Directories
```bash
# Create a template from any existing directory
uvstart template from-directory my-template \
  --source /path/to/experiment \
  --description "My experiment template"

# Create from current directory
uvstart template from-directory experiment-template \
  --description "Reproducible experiment setup"
```

#### Template Management
```bash
# List all available templates
uvstart template list

# Get detailed template information
uvstart template info template-name

# Delete a user template
uvstart template delete template-name
```

### Dependency Management
```bash
# Add packages
uvstart add requests pandas numpy

# Add development dependencies  
uvstart add --dev pytest black mypy

# Remove packages
uvstart remove unused-package

# Sync all dependencies
uvstart sync
uvstart sync --dev  # Include dev dependencies
```

### Project Operations
```bash
# Show backend information
uvstart info

# List installed packages
uvstart list

# Run commands in project environment
uvstart run python main.py
uvstart run pytest

# Get backend version
uvstart version

# Clean project files
uvstart clean
```

### System Health
```bash
# Comprehensive system check
uvstart doctor

# Check for updates
uvstart update --check

# Apply updates
uvstart update
```

---

## Experimental Workflow Guide

Perfect for research, ML experiments, and reproducible analysis:

### 1. Create Initial Experiment
```bash
mkdir transformer-baseline
cd transformer-baseline

# Set up experiment configuration
cat > config.yaml << EOF
experiment:
  name: "transformer-baseline"
  learning_rate: 0.001
  batch_size: 32
  epochs: 100

model:
  type: "transformer"
  layers: 6
  hidden_size: 512
  attention_heads: 8

data:
  dataset: "wikitext-2"
  max_length: 512
EOF

# Create experiment structure
mkdir data models logs outputs
echo 'print("Training model...")' > train.py
echo 'print("Evaluating model...")' > evaluate.py
```

### 2. Create Template from Experiment
```bash
# This enhances your directory with Python project files AND creates a reusable template
uvstart template from-directory transformer-baseline \
  --description "Transformer experiment with configurable parameters"
```

### 3. Spawn New Experiment Runs
```bash
# Create experiment run 1
mkdir ../experiment-lr-0001 && cd ../experiment-lr-0001
uvstart init --features transformer-baseline --backend uv

# Modify parameters for this run
sed -i 's/learning_rate: 0.001/learning_rate: 0.0001/' config.yaml

# Run experiment
python train.py

# Analyze the experiment configuration
uvstart analyze
```

**Output shows experiment details:**
```
EXPERIMENT CONFIGURATION
  Config file: config.yaml
  Parameters:
    experiment: {'name': 'transformer-baseline', 'learning_rate': 0.0001, 'batch_size': 32, 'epochs': 100}
    model: {'type': 'transformer', 'layers': 6, 'hidden_size': 512, 'attention_heads': 8}
    data: {'dataset': 'wikitext-2', 'max_length': 512}
  Experiment scripts: train.py, evaluate.py
  Experiment directories: data, models, logs, outputs
  Template origin: Created from template: transformer-baseline
```

### 4. Create More Experiment Variations
```bash
# Experiment with different batch size
mkdir ../experiment-bs-64 && cd ../experiment-bs-64
uvstart init --features transformer-baseline --backend uv
sed -i 's/batch_size: 32/batch_size: 64/' config.yaml

# Experiment with more layers
mkdir ../experiment-layers-12 && cd ../experiment-layers-12  
uvstart init --features transformer-baseline --backend uv
sed -i 's/layers: 6/layers: 12/' config.yaml

# Each experiment has clean isolation and full project setup
uvstart analyze  # Shows unique configuration for each
```

---

## Built-in Templates

### Web Applications
```bash
uvstart init --features web
```
- FastAPI REST API with modern Python patterns
- Automatic API documentation with Swagger/OpenAPI
- Request/response models with Pydantic
- Database integration examples
- Authentication framework
- Testing setup with pytest

### CLI Applications
```bash
uvstart init --features cli
```
- Click-based command-line interface
- Argument parsing and validation
- Configuration file support
- Rich output formatting
- Testing framework for CLI apps
- Distribution and packaging setup

### Data Science & Notebooks
```bash
uvstart init --features notebook
```
- Jupyter notebook environment
- Data analysis libraries (pandas, numpy, matplotlib)
- Experiment tracking setup
- Data pipeline templates
- Visualization templates
- Report generation

### Machine Learning
```bash
uvstart init --features pytorch
```
- PyTorch project structure
- Training and evaluation scripts
- Model architecture templates
- Dataset handling
- Experiment tracking (TensorBoard)
- Model deployment examples

### Microservices
```bash
uvstart init --features microservice
```
- Docker containerization
- Health check endpoints
- Metrics and monitoring
- Configuration management
- Service discovery patterns
- Kubernetes deployment files

### MLOps Workflows
```bash
uvstart init --features mlops
```
- Complete ML pipeline structure
- Model versioning and registry
- Training orchestration
- Automated testing for ML models
- Deployment and serving
- Monitoring and drift detection

---

## Backend Support

uvstart provides unified operations across all major Python package managers:

| Backend | Speed | Environment | Lock Files | Best For |
|---------|-------|-------------|------------|----------|
| **uv** | Extremely fast | `__pypackages__/` | `uv.lock` | Modern projects, CI/CD |
| **poetry** | Mature | `.venv/` | `poetry.lock` | Traditional workflows |
| **pdm** | Fast | `.venv/` | `pdm.lock` | PEP 582 supporters |

**Features:**
- **Auto-detection:** Automatically detects your preferred backend
- **Unified commands:** Same commands work with any backend
- **Easy switching:** Change backends without losing functionality
- **Version management:** Proper Python version constraints

---

## Advanced Features

### Configuration Management
```bash
# Set default preferences
uvstart init  # Uses configured defaults for backend, python version, etc.

# Environment variables
export UVSTART_DEFAULT_BACKEND="uv"
export UVSTART_DEFAULT_PYTHON="3.12"
export UVSTART_DEFAULT_AUTHOR="Your Name"
export UVSTART_DEFAULT_EMAIL="you@example.com"
```

### Template Development
```bash
# List all templates with detailed info
uvstart template list

# Get comprehensive template information
uvstart template info web
# Shows: description, features, files generated, variables, author, version

# Create templates from any directory structure
uvstart template from-directory my-custom-template --source /path/to/source
```

### Project Intelligence
```bash
# Get complete project analysis
uvstart analyze

# Detect experiment configurations automatically
# Supports: JSON, YAML, TOML config files
# Recognizes: ML scripts, data directories, model checkpoints
# Tracks: Template origins, parameter changes, experiment metadata
```

### Makefile Integration
Every project includes a comprehensive `Makefile`:

```bash
make sync         # Install dependencies
make run          # Run main application  
make test         # Run test suite
make fmt          # Format code with black/ruff
make lint         # Lint and type check
make clean        # Clean build artifacts
make add          # Add dependencies interactively
make repl         # Start Python REPL
make notebook     # Launch Jupyter (if available)
make doctor       # Health check
```

---

## Complete Example Workflows

### API Development
```bash
# Create and set up API project
mkdir awesome-api && cd awesome-api
uvstart init --features web --backend uv
make sync

# Start development server
make run
# Server running at http://localhost:8000/docs

# Add database support
uvstart add sqlalchemy psycopg2-binary
# Update main.py with database integration

# Deploy
uvstart add --dev docker
# Add Dockerfile and deployment configs
```

### Data Science Project
```bash
# Set up analysis project  
uvstart generate analysis-project --features notebook --backend poetry
cd analysis-project && make sync

# Start Jupyter environment
make notebook

# Add ML libraries as needed
uvstart add scikit-learn tensorflow
uvstart add --dev mlflow wandb

# Analyze project health
uvstart analyze
```

### Machine Learning Experiment
```bash
# Create initial experiment
mkdir ml-experiment && cd ml-experiment
uvstart init --features pytorch --backend uv

# Set up experiment configuration
cat > experiment.yaml << EOF
model:
  architecture: "resnet50"
  pretrained: true
training:
  learning_rate: 0.001
  batch_size: 32
  epochs: 50
data:
  dataset: "imagenet"
  augmentation: true
EOF

# Create experiment template for reproducibility  
uvstart template from-directory resnet-experiment \
  --description "ResNet image classification experiments"

# Create variations
mkdir ../experiment-lr-high && cd ../experiment-lr-high
uvstart init --features resnet-experiment --backend uv
sed -i 's/learning_rate: 0.001/learning_rate: 0.01/' experiment.yaml

# Track experiment configurations
uvstart analyze  # Shows parameters, scripts, template origin
```

---

## System Health & Troubleshooting

### Health Check
```bash
uvstart doctor
```

**Comprehensive checks:**
- Python installations (3.8+)
- Package managers (uv, poetry, pdm)
- Development tools (git, make, docker)
- uvstart installation integrity
- Template system health
- Configuration validation

### Update Management
```bash
# Check for updates
uvstart update --check

# Apply updates with backup
uvstart update --backup

# Force update
uvstart update --force
```

### Common Issues

**Backend not detected:**
```bash
# Check available backends
uvstart info

# Install missing backend
# For uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# For poetry: curl -sSL https://install.python-poetry.org | python3 -
```

**Template not found:**
```bash
# List available templates
uvstart template list

# Check template location
uvstart template info template-name
```

**Project analysis issues:**
```bash
# Verify project structure
uvstart analyze

# Check for configuration files
ls -la *.toml *.yaml *.json
```

---

## Contributing

We welcome contributions! Areas where you can help:

### Template Development
- Create new project templates
- Improve existing templates
- Add support for new frameworks

### Backend Integration
- Add support for new package managers
- Improve backend detection
- Enhance command abstractions

### Experiment Workflows
- ML/AI experiment templates
- Research reproducibility features
- Configuration management tools

### Development Setup
```bash
git clone https://github.com/jim-ecker/uvstart.git
cd uvstart
uvstart init --backend uv --python-version 3.12
make sync && make test
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Why Choose uvstart?

### Traditional Python Setup:
- Manual directory creation and configuration
- Copy-paste boilerplate code
- Hunt for the right dependencies and settings
- Hours spent on project setup
- Hope everything works together
- No experiment reproducibility

### uvstart Experience:
- **One command** creates complete projects
- **Professional templates** with best practices
- **Automatic dependency management** 
- **Experiment reproducibility** out of the box
- **Intelligent project analysis**
- **Focus on building**, not configuring

### Start Building Today:

```bash
# Create your next project in seconds
uvstart generate my-project --features web --backend uv

# Or enhance existing work
cd existing-project && uvstart analyze

# Scale with reproducible experiments
uvstart template from-directory my-experiment
```

**uvstart: Where great Python projects begin.**

