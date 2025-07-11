#!/usr/bin/env python3
"""
Simple template system for uvstart
Works without dependencies, enhanced when Jinja2 is available
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class SimpleTemplateEngine:
    """Simple template engine using basic string substitution"""
    
    def __init__(self):
        self.has_jinja2 = self._check_jinja2()
        if self.has_jinja2:
            try:
                from jinja2 import Environment, FileSystemLoader, select_autoescape
                self.jinja_env = Environment(
                    autoescape=select_autoescape(['html', 'xml']),
                    keep_trailing_newline=True
                )
            except ImportError:
                self.has_jinja2 = False
                self.jinja_env = None
        else:
            self.jinja_env = None
    
    def _check_jinja2(self) -> bool:
        """Check if Jinja2 is available"""
        try:
            import jinja2
            return True
        except ImportError:
            return False
    
    def render_string(self, template: str, context: Dict[str, Any]) -> str:
        """Render a template string with context"""
        if self.has_jinja2 and self._is_complex_template(template):
            # Use Jinja2 for complex templates
            return self._render_with_jinja2(template, context)
        else:
            # Use simple substitution for basic templates
            return self._render_simple(template, context)
    
    def _is_complex_template(self, template: str) -> bool:
        """Check if template needs Jinja2 (has loops, conditionals, etc.)"""
        complex_patterns = [
            r'{%\s*(for|if|set|macro)',  # Jinja2 control structures
            r'{{.*\|.*}}',               # Jinja2 filters
            r'{%.*%}',                   # Any Jinja2 statement
        ]
        
        for pattern in complex_patterns:
            if re.search(pattern, template):
                return True
        return False
    
    def _render_simple(self, template: str, context: Dict[str, Any]) -> str:
        """Simple template rendering using string substitution"""
        result = template
        
        # Handle simple {{variable}} substitutions
        for key, value in context.items():
            # Convert value to string
            str_value = str(value) if value is not None else ""
            
            # Replace {{key}} patterns
            patterns = [
                f"{{{{{key}}}}}",           # {{key}}
                f"{{{{ {key} }}}}",         # {{ key }}
            ]
            
            for pattern in patterns:
                result = result.replace(pattern, str_value)
        
        return result
    
    def _render_with_jinja2(self, template: str, context: Dict[str, Any]) -> str:
        """Render template using Jinja2"""
        if not self.jinja_env:
            return self._render_simple(template, context)
        
        try:
            jinja_template = self.jinja_env.from_string(template)
            return jinja_template.render(**context)
        except Exception:
            # Fall back to simple rendering if Jinja2 fails
            return self._render_simple(template, context)
    
    def render_file(self, template_path: Path, context: Dict[str, Any]) -> str:
        """Render a template file"""
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        template_content = template_path.read_text(encoding='utf-8')
        return self.render_string(template_content, context)


class TemplateContext:
    """Template context with project information"""
    
    def __init__(self, project_name: str, **kwargs):
        self.project_name = project_name
        self.package_name = self._to_package_name(project_name)
        self.project_name_title = self._to_title_case(project_name)
        self.project_name_upper = project_name.upper().replace('-', '_')
        
        # Default values
        self.description = kwargs.get('description', f"A Python project: {project_name}")
        self.version = kwargs.get('version', '0.1.0')
        self.author = kwargs.get('author', 'Developer')
        self.email = kwargs.get('email', 'dev@example.com')
        self.backend = kwargs.get('backend', 'uv')
        self.features = kwargs.get('features', [])
        self.python_version = kwargs.get('python_version', '3.11')
        
        # Auto-generated values
        self.year = str(datetime.now().year)
        self.date = datetime.now().strftime('%Y-%m-%d')
        self.datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _to_package_name(self, name: str) -> str:
        """Convert project name to valid Python package name"""
        # Replace hyphens and spaces with underscores
        package = re.sub(r'[-\s]+', '_', name.lower())
        # Remove invalid characters
        package = re.sub(r'[^a-z0-9_]', '', package)
        # Ensure it doesn't start with a number
        if package and package[0].isdigit():
            package = f"project_{package}"
        return package or "project"
    
    def _to_title_case(self, name: str) -> str:
        """Convert project name to title case"""
        return ' '.join(word.capitalize() for word in re.split(r'[-_\s]+', name))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering"""
        return {
            'project_name': self.project_name,
            'package_name': self.package_name,
            'project_name_title': self.project_name_title,
            'project_name_upper': self.project_name_upper,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'email': self.email,
            'backend': self.backend,
            'features': self.features,
            'python_version': self.python_version,
            'year': self.year,
            'date': self.date,
            'datetime': self.datetime,
        }


class SimpleTemplateManager:
    """Manages simple templates without complex dependencies"""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        self.engine = SimpleTemplateEngine()
    
    def get_builtin_templates(self) -> List[str]:
        """Get list of built-in template names"""
        return ["cli", "web", "notebook", "pytorch"]
    
    def generate_project_files(self, context: TemplateContext, features: List[str]) -> Dict[str, str]:
        """Generate project files for given features"""
        files = {}
        
        # Always generate basic project structure
        files.update(self._generate_basic_structure(context))
        
        # Add feature-specific files
        for feature in features:
            if feature in self.get_builtin_templates():
                files.update(self._generate_feature_files(context, feature))
        
        return files
    
    def _generate_basic_structure(self, context: TemplateContext) -> Dict[str, str]:
        """Generate basic project structure files"""
        ctx = context.to_dict()
        
        files = {
            "pyproject.toml": self._generate_pyproject_toml(ctx),
            "README.md": self._generate_readme(ctx),
            ".gitignore": self._generate_gitignore(ctx),
            "main.py": self._generate_main_py(ctx),
            f"{ctx['package_name']}/__init__.py": self._generate_init_py(ctx),
            f"{ctx['package_name']}/main.py": self._generate_package_main(ctx),
            "tests/__init__.py": "",
            f"tests/test_{ctx['package_name']}.py": self._generate_test_file(ctx),
        }
        
        return files
    
    def _generate_feature_files(self, context: TemplateContext, feature: str) -> Dict[str, str]:
        """Generate feature-specific files"""
        # For now, features just modify the main files
        # In a full implementation, this would load feature templates
        return {}
    
    def _generate_pyproject_toml(self, ctx: Dict[str, Any]) -> str:
        """Generate pyproject.toml file"""
        backend = ctx['backend']
        
        if backend == "uv":
            return f'''[project]
name = "{ctx['project_name']}"
description = "{ctx['description']}"
version = "{ctx['version']}"
authors = [
    {{name = "{ctx['author']}", email = "{ctx['email']}"}},
]
dependencies = []
requires-python = ">={ctx['python_version']}"
readme = "README.md"
license = {{text = "MIT"}}

[project.scripts]
{ctx['package_name']} = "{ctx['package_name']}.main:main"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "black>=22.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
        elif backend == "poetry":
            return f'''[tool.poetry]
name = "{ctx['project_name']}"
version = "{ctx['version']}"
description = "{ctx['description']}"
authors = ["{ctx['author']} <{ctx['email']}>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^{ctx['python_version']}"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
black = "^22.0"
ruff = "^0.1.0"

[tool.poetry.scripts]
{ctx['package_name']} = "{ctx['package_name']}.main:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
'''
        else:  # pdm
            return f'''[project]
name = "{ctx['project_name']}"
description = "{ctx['description']}"
version = "{ctx['version']}"
authors = [
    {{name = "{ctx['author']}", email = "{ctx['email']}"}},
]
dependencies = []
requires-python = ">={ctx['python_version']}"
readme = "README.md"
license = {{text = "MIT"}}

[project.scripts]
{ctx['package_name']} = "{ctx['package_name']}.main:main"

[tool.pdm.dev-dependencies]
test = [
    "pytest>=7.0",
]
lint = [
    "black>=22.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"
'''
    
    def _generate_readme(self, ctx: Dict[str, Any]) -> str:
        """Generate README.md file"""
        return f'''# {ctx['project_name_title']}

{ctx['description']}

## Installation

```bash
{ctx['backend']} sync
```

## Usage

```bash
{ctx['backend']} run {ctx['package_name']}
```

## Development

```bash
# Install dependencies
{ctx['backend']} sync

# Run tests
{ctx['backend']} run pytest

# Format code
{ctx['backend']} run black .

# Lint code
{ctx['backend']} run ruff check .
```

## Author

{ctx['author']} <{ctx['email']}>
'''
    
    def _generate_gitignore(self, ctx: Dict[str, Any]) -> str:
        """Generate .gitignore file"""
        return '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
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
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
'''
    
    def _generate_main_py(self, ctx: Dict[str, Any]) -> str:
        """Generate main.py file"""
        return f'''#!/usr/bin/env python3
"""
{ctx['project_name_title']} - {ctx['description']}
"""

from {ctx['package_name']}.main import main

if __name__ == "__main__":
    main()
'''
    
    def _generate_init_py(self, ctx: Dict[str, Any]) -> str:
        """Generate package __init__.py file"""
        return f'''"""
{ctx['project_name_title']} - {ctx['description']}
"""

__version__ = "{ctx['version']}"
__author__ = "{ctx['author']}"
'''
    
    def _generate_package_main(self, ctx: Dict[str, Any]) -> str:
        """Generate package main.py file"""
        return f'''"""
Main module for {ctx['project_name_title']}
"""

import sys


def main():
    """Main entry point for {ctx['project_name_title']}"""
    print("Hello from {ctx['project_name_title']}!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
    
    def _generate_test_file(self, ctx: Dict[str, Any]) -> str:
        """Generate test file"""
        return f'''"""
Tests for {ctx['project_name_title']}
"""

import pytest
from {ctx['package_name']}.main import main


def test_main():
    """Test main function"""
    result = main()
    assert result == 0
''' 