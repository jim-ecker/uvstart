"""
Template system for uvstart project generation
Demonstrates Python's advanced template processing and project scaffolding capabilities
"""

import re
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from string import Template
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TemplateContext:
    """Context variables for template rendering"""
    project_name: str
    description: str = ""
    version: str = "0.1.0"
    author: str = "Your Name"
    email: str = "your.email@example.com"
    license: str = "MIT"
    python_version: str = "3.8"
    backend: str = "uv"
    year: str = ""
    features: Optional[List[str]] = None
    
    def __post_init__(self):
        if not self.year:
            self.year = str(datetime.now().year)
        if self.features is None:
            self.features = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template substitution"""
        return {
            'project_name': self.project_name,
            'project_name_underscore': self.project_name.replace('-', '_'),
            'project_name_title': self.project_name.replace('-', ' ').title(),
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'email': self.email,
            'license': self.license,
            'python_version': self.python_version,
            'backend': self.backend,
            'year': self.year,
            'features': self.features,
            'has_cli': 'cli' in (self.features or []),
            'has_web': 'web' in (self.features or []),
            'has_notebook': 'notebook' in (self.features or []),
            'has_pytorch': 'pytorch' in (self.features or [])
        }


class SimpleTemplateEngine:
    """Simple template engine using Python's string.Template"""
    
    def __init__(self):
        self.template_cache = {}
    
    def render_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a template string with context variables"""
        # Handle conditional blocks
        processed = self._process_conditionals(template_str, context)
        
        # Handle loops
        processed = self._process_loops(processed, context)
        
        # Standard variable substitution
        template = Template(processed)
        return template.safe_substitute(context)
    
    def render_file(self, template_path: Path, context: Dict[str, Any]) -> str:
        """Render a template file with context variables"""
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return self.render_string(template_content, context)
    
    def _process_conditionals(self, template_str: str, context: Dict[str, Any]) -> str:
        """Process conditional blocks like {% if condition %}...{% endif %}"""
        # Simple if/endif processing
        pattern = r'\{\%\s*if\s+(\w+)\s*\%\}(.*?)\{\%\s*endif\s*\%\}'
        
        def replace_conditional(match):
            condition = match.group(1)
            content = match.group(2)
            
            # Check if condition is true in context
            if context.get(condition, False):
                return content
            else:
                return ""
        
        return re.sub(pattern, replace_conditional, template_str, flags=re.DOTALL)
    
    def _process_loops(self, template_str: str, context: Dict[str, Any]) -> str:
        """Process loop blocks like {% for item in list %}...{% endfor %}"""
        pattern = r'\{\%\s*for\s+(\w+)\s+in\s+(\w+)\s*\%\}(.*?)\{\%\s*endfor\s*\%\}'
        
        def replace_loop(match):
            item_var = match.group(1)
            list_var = match.group(2)
            content = match.group(3)
            
            items = context.get(list_var, [])
            if not isinstance(items, list):
                return ""
            
            result = []
            for item in items:
                # Create context with loop variable
                loop_context = context.copy()
                loop_context[item_var] = item
                
                # Simple substitution for loop content
                loop_template = Template(content)
                result.append(loop_template.safe_substitute(loop_context))
            
            return ''.join(result)
        
        return re.sub(pattern, replace_loop, template_str, flags=re.DOTALL)


class ProjectGenerator:
    """Generate projects from templates"""
    
    def __init__(self, template_engine: Optional[SimpleTemplateEngine] = None):
        self.template_engine = template_engine or SimpleTemplateEngine()
    
    def generate_pyproject_toml(self, context: TemplateContext) -> str:
        """Generate pyproject.toml for different backends"""
        ctx = context.to_dict()
        
        if context.backend == "uv":
            return self._generate_uv_pyproject(ctx)
        elif context.backend == "poetry":
            return self._generate_poetry_pyproject(ctx)
        elif context.backend == "pdm":
            return self._generate_pdm_pyproject(ctx)
        else:
            return self._generate_generic_pyproject(ctx)
    
    def _generate_uv_pyproject(self, ctx: Dict[str, Any]) -> str:
        """Generate uv-specific pyproject.toml"""
        template = '''[project]
name = "$project_name"
description = "$description"
version = "$version"
requires-python = ">=$python_version"
dependencies = []

{% if has_cli %}
[project.scripts]
$project_name_underscore = "$project_name_underscore.main:main"
{% endif %}

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "black>=22.0",
    "mypy>=1.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
'''
        return self.template_engine.render_string(template, ctx)
    
    def _generate_poetry_pyproject(self, ctx: Dict[str, Any]) -> str:
        """Generate Poetry-specific pyproject.toml"""
        template = '''[tool.poetry]
name = "$project_name"
version = "$version"
description = "$description"
authors = ["$author <$email>"]
license = "$license"

[tool.poetry.dependencies]
python = "^$python_version"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
black = "^22.0"
mypy = "^1.0"

{% if has_cli %}
[tool.poetry.scripts]
$project_name_underscore = "$project_name_underscore.main:main"
{% endif %}

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
'''
        return self.template_engine.render_string(template, ctx)
    
    def _generate_pdm_pyproject(self, ctx: Dict[str, Any]) -> str:
        """Generate PDM-specific pyproject.toml"""
        template = '''[project]
name = "$project_name"
description = "$description"
version = "$version"
requires-python = ">=$python_version"
dependencies = []

{% if has_cli %}
[project.scripts]
$project_name_underscore = "$project_name_underscore.main:main"
{% endif %}

[tool.pdm]

[tool.pdm.dev-dependencies]
test = [
    "pytest>=7.0",
]
lint = [
    "black>=22.0",
    "mypy>=1.0",
]

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"
'''
        return self.template_engine.render_string(template, ctx)
    
    def _generate_generic_pyproject(self, ctx: Dict[str, Any]) -> str:
        """Generate generic pyproject.toml"""
        template = '''[project]
name = "$project_name"
description = "$description"
version = "$version"
requires-python = ">=$python_version"
dependencies = []

{% if has_cli %}
[project.scripts]
$project_name_underscore = "$project_name_underscore.main:main"
{% endif %}

[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
'''
        return self.template_engine.render_string(template, ctx)
    
    def generate_main_py(self, context: TemplateContext) -> str:
        """Generate main.py file"""
        ctx = context.to_dict()
        
        if 'cli' in context.features:
            return self._generate_cli_main(ctx)
        elif 'web' in context.features:
            return self._generate_web_main(ctx)
        else:
            return self._generate_simple_main(ctx)
    
    def _generate_cli_main(self, ctx: Dict[str, Any]) -> str:
        """Generate CLI main.py"""
        template = '''"""
$project_name_title - $description
"""

import argparse
import sys


def main():
    """Main entry point for $project_name"""
    parser = argparse.ArgumentParser(
        prog="$project_name",
        description="$description"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"$project_name $version"
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        help="Command to run"
    )
    
    args = parser.parse_args()
    
    if args.command:
        print(f"Running command: {args.command}")
    else:
        print("Hello from $project_name_title!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
        return self.template_engine.render_string(template, ctx)
    
    def _generate_web_main(self, ctx: Dict[str, Any]) -> str:
        """Generate web main.py"""
        template = '''"""
$project_name_title - $description
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class RequestHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            html = f"""
            <html>
            <head><title>$project_name_title</title></head>
            <body>
                <h1>$project_name_title</h1>
                <p>$description</p>
                <p>Version: $version</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        
        elif self.path == "/api/info":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            info = {
                "name": "$project_name",
                "description": "$description",
                "version": "$version"
            }
            self.wfile.write(json.dumps(info, indent=2).encode())
        
        else:
            self.send_response(404)
            self.end_headers()


def main():
    """Main entry point"""
    port = 8000
    server = HTTPServer(("localhost", port), RequestHandler)
    
    print(f"Starting $project_name_title server on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    main()
'''
        return self.template_engine.render_string(template, ctx)
    
    def _generate_simple_main(self, ctx: Dict[str, Any]) -> str:
        """Generate simple main.py"""
        template = '''"""
$project_name_title - $description
"""


def main():
    """Main function"""
    print("Hello from $project_name_title!")
    print("Description: $description")
    print("Version: $version")


if __name__ == "__main__":
    main()
'''
        return self.template_engine.render_string(template, ctx)
    
    def generate_readme(self, context: TemplateContext) -> str:
        """Generate README.md"""
        ctx = context.to_dict()
        
        template = '''# $project_name_title

$description

## Installation

```bash
# Using $backend
$backend install
```

## Usage

{% if has_cli %}
```bash
# Run the CLI
$project_name --help
```
{% endif %}

{% if has_web %}
```bash
# Start the web server
python main.py
```

Then visit http://localhost:8000
{% endif %}

```bash
# Run the main module
python main.py
```

## Development

```bash
# Install development dependencies
{% if backend == "poetry" %}
poetry install --with dev
{% endif %}
{% if backend == "uv" %}
uv sync --group dev
{% endif %}
{% if backend == "pdm" %}
pdm sync --dev
{% endif %}

# Run tests
pytest

# Format code
black .

# Type checking
mypy .
```

## Features

{% for feature in features %}
- $feature
{% endfor %}

## License

$license

## Author

$author <$email>
'''
        return self.template_engine.render_string(template, ctx)
    
    def generate_project_structure(self, context: TemplateContext) -> Dict[str, str]:
        """Generate complete project structure"""
        files = {}
        
        # Core files
        files['pyproject.toml'] = self.generate_pyproject_toml(context)
        files['main.py'] = self.generate_main_py(context)
        files['README.md'] = self.generate_readme(context)
        
        # Package structure
        pkg_name = context.project_name.replace('-', '_')
        files[f'{pkg_name}/__init__.py'] = f'"""$project_name_title package"""\n\n__version__ = "{context.version}"\n'
        files[f'{pkg_name}/main.py'] = self.generate_main_py(context)
        
        # Test structure
        files['tests/__init__.py'] = ""
        files[f'tests/test_{pkg_name}.py'] = f'''"""Tests for {context.project_name}"""

import pytest
from {pkg_name}.main import main


def test_main():
    """Test main function"""
    # Add your tests here
    assert main is not None
'''
        
        # Additional files
        files['.gitignore'] = self._generate_gitignore()
        
        return files
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore file"""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
__pypackages__/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.coverage
.pytest_cache/
.tox/
htmlcov/

# Backend-specific
poetry.lock
pdm.lock
uv.lock
requirements.lock
.pdm-python
'''


# Demo function
def demo_template_system():
    """Demonstrate the template system capabilities"""
    print("Template System Demo")
    print("=" * 50)
    
    # Create context
    context = TemplateContext(
        project_name="awesome-cli",
        description="An awesome CLI application",
        version="1.0.0",
        author="John Doe",
        email="john@example.com",
        backend="uv",
        features=["cli"]
    )
    
    # Generate project
    generator = ProjectGenerator()
    
    print("\nGenerated pyproject.toml:")
    print("-" * 30)
    print(generator.generate_pyproject_toml(context))
    
    print("\nGenerated main.py:")
    print("-" * 20)
    print(generator.generate_main_py(context))
    
    print("\nGenerated README.md:")
    print("-" * 20)
    print(generator.generate_readme(context))


if __name__ == "__main__":
    demo_template_system() 