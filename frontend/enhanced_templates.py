"""
Enhanced Template System for uvstart
Modern template engine with YAML definitions, advanced conditionals, loops, includes, and CI/CD generation
"""

import re
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from string import Template
from datetime import datetime
from dataclasses import dataclass, field
from collections.abc import Mapping

# Optional dependencies for enhanced features
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import jinja2  # type: ignore
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False
    jinja2 = None  # type: ignore


@dataclass
class TemplateMetadata:
    """Metadata for a template"""
    name: str
    description: str
    category: str = "general"
    version: str = "1.0.0"
    author: str = "uvstart"
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Required backends
    features: List[str] = field(default_factory=list)      # Provided features
    min_python: str = "3.8"
    includes_ci: bool = False
    includes_docker: bool = False
    includes_tests: bool = True


@dataclass 
class EnhancedTemplateContext:
    """Enhanced context with more capabilities"""
    project_name: str
    description: str = ""
    version: str = "0.1.0"
    author: str = "Your Name"
    email: str = "your.email@example.com"
    license: str = "MIT"
    python_version: str = "3.8"
    backend: str = "uv"
    year: str = ""
    features: List[str] = field(default_factory=list)
    
    # Enhanced context variables
    github_username: str = ""
    repository_url: str = ""
    package_name: str = ""
    module_name: str = ""
    class_name: str = ""
    
    # CI/CD options
    enable_github_actions: bool = True
    enable_pre_commit: bool = True
    enable_dependabot: bool = True
    enable_docker: bool = False
    enable_devcontainer: bool = False
    
    # Code quality options
    enable_black: bool = True
    enable_ruff: bool = True
    enable_mypy: bool = True
    enable_pytest: bool = True
    enable_coverage: bool = True
    
    def __post_init__(self):
        if not self.year:
            self.year = str(datetime.now().year)
        if not self.package_name:
            self.package_name = self.project_name.replace('-', '_')
        if not self.module_name:
            self.module_name = self.package_name
        if not self.class_name:
            self.class_name = ''.join(word.capitalize() for word in self.project_name.replace('-', '_').split('_'))
        if not self.github_username:
            self.github_username = self.author.lower().replace(' ', '')
        if not self.repository_url and self.github_username:
            self.repository_url = f"https://github.com/{self.github_username}/{self.project_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template substitution"""
        return {
            # Basic project info
            'project_name': self.project_name,
            'project_name_underscore': self.project_name.replace('-', '_'),
            'project_name_title': self.project_name.replace('-', ' ').title(),
            'project_name_upper': self.project_name.upper().replace('-', '_'),
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'email': self.email,
            'license': self.license,
            'python_version': self.python_version,
            'backend': self.backend,
            'year': self.year,
            'features': self.features,
            
            # Enhanced variables
            'github_username': self.github_username,
            'repository_url': self.repository_url,
            'package_name': self.package_name,
            'module_name': self.module_name,
            'class_name': self.class_name,
            
            # Feature flags
            'has_cli': 'cli' in self.features,
            'has_web': 'web' in self.features,
            'has_notebook': 'notebook' in self.features,
            'has_pytorch': 'pytorch' in self.features,
            'has_fastapi': 'fastapi' in self.features,
            'has_django': 'django' in self.features,
            'has_streamlit': 'streamlit' in self.features,
            'has_mlflow': 'mlflow' in self.features,
            'has_docker': 'docker' in self.features,
            'has_kubernetes': 'kubernetes' in self.features,
            
            # CI/CD flags
            'enable_github_actions': self.enable_github_actions,
            'enable_pre_commit': self.enable_pre_commit,
            'enable_dependabot': self.enable_dependabot,
            'enable_docker': self.enable_docker,
            'enable_devcontainer': self.enable_devcontainer,
            
            # Code quality flags
            'enable_black': self.enable_black,
            'enable_ruff': self.enable_ruff,
            'enable_mypy': self.enable_mypy,
            'enable_pytest': self.enable_pytest,
            'enable_coverage': self.enable_coverage,
            
            # Backend-specific info
            'is_uv': self.backend == 'uv',
            'is_poetry': self.backend == 'poetry',
            'is_pdm': self.backend == 'pdm',
            'is_rye': self.backend == 'rye',
            'is_hatch': self.backend == 'hatch',
            
            # Utility functions for templates
            'now': datetime.now(),
            'current_year': datetime.now().year,
        }


class EnhancedTemplateEngine:
    """Enhanced template engine with YAML support and advanced features"""
    
    def __init__(self, use_jinja2: Optional[bool] = None):
        self.use_jinja2 = use_jinja2 if use_jinja2 is not None else HAS_JINJA2
        self.template_cache = {}
        
        if self.use_jinja2 and HAS_JINJA2 and jinja2 is not None:
            self.jinja_env = jinja2.Environment(
                loader=jinja2.BaseLoader(),
                trim_blocks=True,
                lstrip_blocks=True,
                undefined=jinja2.StrictUndefined
            )
            # Add custom filters
            self.jinja_env.filters['snake_case'] = self._snake_case
            self.jinja_env.filters['camel_case'] = self._camel_case
            self.jinja_env.filters['kebab_case'] = self._kebab_case
            self.jinja_env.filters['title_case'] = self._title_case
        else:
            self.jinja_env = None
    
    def _snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        return re.sub(r'[^a-zA-Z0-9]', '_', text).lower()
    
    def _camel_case(self, text: str) -> str:
        """Convert text to CamelCase"""
        return ''.join(word.capitalize() for word in re.split(r'[^a-zA-Z0-9]', text))
    
    def _kebab_case(self, text: str) -> str:
        """Convert text to kebab-case"""
        return re.sub(r'[^a-zA-Z0-9]', '-', text).lower()
    
    def _title_case(self, text: str) -> str:
        """Convert text to Title Case"""
        return ' '.join(word.capitalize() for word in re.split(r'[^a-zA-Z0-9]', text))
    
    def render_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a template string with context variables"""
        if self.use_jinja2 and HAS_JINJA2:
            return self._render_jinja2(template_str, context)
        else:
            return self._render_simple(template_str, context)
    
    def _render_jinja2(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render using Jinja2 for advanced features"""
        if self.jinja_env is None:
            return self._render_simple(template_str, context)
        template = self.jinja_env.from_string(template_str)
        return template.render(**context)
    
    def _render_simple(self, template_str: str, context: Dict[str, Any]) -> str:
        """Fallback to simple template engine"""
        # Handle conditional blocks
        processed = self._process_conditionals(template_str, context)
        
        # Handle loops
        processed = self._process_loops(processed, context)
        
        # Handle includes (basic version)
        processed = self._process_includes(processed, context)
        
        # Standard variable substitution
        template = Template(processed)
        return template.safe_substitute(context)
    
    def _process_conditionals(self, template_str: str, context: Dict[str, Any]) -> str:
        """Process conditional blocks like {% if condition %}...{% endif %}"""
        # Enhanced if/elif/else/endif processing
        pattern = r'\{\%\s*if\s+([^%]+)\s*\%\}(.*?)(?:\{\%\s*elif\s+([^%]+)\s*\%\}(.*?))*(?:\{\%\s*else\s*\%\}(.*?))?\{\%\s*endif\s*\%\}'
        
        def replace_conditional(match):
            condition = match.group(1).strip()
            content = match.group(2)
            
            # Evaluate condition
            if self._evaluate_condition(condition, context):
                return content
            else:
                return ""
        
        return re.sub(pattern, replace_conditional, template_str, flags=re.DOTALL)
    
    def _process_loops(self, template_str: str, context: Dict[str, Any]) -> str:
        """Process loop blocks like {% for item in items %}...{% endfor %}"""
        pattern = r'\{\%\s*for\s+(\w+)\s+in\s+(\w+)\s*\%\}(.*?)\{\%\s*endfor\s*\%\}'
        
        def replace_loop(match):
            var_name = match.group(1)
            list_name = match.group(2)
            content = match.group(3)
            
            items = context.get(list_name, [])
            if not isinstance(items, (list, tuple)):
                return ""
            
            result = []
            for item in items:
                loop_context = context.copy()
                loop_context[var_name] = item
                # Simple variable substitution in loop content
                loop_template = Template(content)
                result.append(loop_template.safe_substitute(loop_context))
            
            return '\n'.join(result)
        
        return re.sub(pattern, replace_loop, template_str, flags=re.DOTALL)
    
    def _process_includes(self, template_str: str, context: Dict[str, Any]) -> str:
        """Process include directives like {% include 'file.txt' %}"""
        pattern = r'\{\%\s*include\s+[\'"]([^\'"]+)[\'"]\s*\%\}'
        
        def replace_include(match):
            include_file = match.group(1)
            # For now, just return a placeholder
            return f"# Include: {include_file}"
        
        return re.sub(pattern, replace_include, template_str)
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a simple condition"""
        # Handle simple boolean variables
        if condition in context:
            return bool(context[condition])
        
        # Handle "not variable"
        if condition.startswith('not '):
            var = condition[4:].strip()
            return not bool(context.get(var, False))
        
        # Handle "variable == 'value'"
        if ' == ' in condition:
            left, right = condition.split(' == ', 1)
            left = left.strip()
            right = right.strip('\'"')
            return str(context.get(left, '')) == right
        
        return False
    
    def render_file(self, template_path: Path, context: Dict[str, Any]) -> str:
        """Render a template file with context variables"""
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return self.render_string(template_content, context)


class YAMLTemplateLoader:
    """Load templates defined in YAML format with inheritance support"""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self._template_cache = {}
    
    def load_template_config(self, template_name: str) -> Dict[str, Any]:
        """Load template configuration from YAML with inheritance resolution"""
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        config = self._load_raw_template_config(template_name)
        
        # Handle inheritance
        if 'inheritance' in config and 'extends' in config['inheritance']:
            base_template = config['inheritance']['extends']
            base_config = self.load_template_config(base_template)
            config = self._merge_template_configs(base_config, config)
        
        self._template_cache[template_name] = config
        return config
    
    def _load_raw_template_config(self, template_name: str) -> Dict[str, Any]:
        """Load raw template configuration without inheritance resolution"""
        # Check in features directory first
        config_file = self.template_dir / "features" / template_name / "template.yaml"
        
        # Then check in base directory
        if not config_file.exists():
            config_file = self.template_dir / "base" / template_name / "template.yaml"
        
        if not config_file.exists():
            # Fallback to generating config from directory structure
            return self._generate_config_from_directory(template_name)
        
        if not HAS_YAML:
            raise ImportError("PyYAML is required for YAML template configurations")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _merge_template_configs(self, base_config: Dict[str, Any], child_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge child template configuration with base template"""
        merged = base_config.copy()
        
        # Get inheritance rules from child config
        inheritance_rules = child_config.get('inheritance', {})
        override_sections = inheritance_rules.get('override_sections', [])
        merge_strategies = inheritance_rules.get('merge_strategies', {})
        
        for key, value in child_config.items():
            if key == 'inheritance':
                continue  # Skip inheritance metadata
            
            if key in override_sections:
                # Complete override
                merged[key] = value
            elif key in merge_strategies:
                # Custom merge strategy
                strategy = merge_strategies[key]
                merged[key] = self._apply_merge_strategy(
                    merged.get(key), value, strategy
                )
            elif isinstance(value, dict) and key in merged:
                # Deep merge dictionaries
                merged[key] = self._deep_merge_dict(merged[key], value)
            else:
                # Simple override
                merged[key] = value
        
        return merged
    
    def _apply_merge_strategy(self, base_value: Any, child_value: Any, strategy: str) -> Any:
        """Apply merge strategy for specific fields"""
        if strategy == "append" and isinstance(base_value, list) and isinstance(child_value, list):
            return base_value + child_value
        elif strategy == "prepend" and isinstance(base_value, list) and isinstance(child_value, list):
            return child_value + base_value
        elif strategy == "merge" and isinstance(base_value, dict) and isinstance(child_value, dict):
            return self._deep_merge_dict(base_value, child_value)
        else:
            # Default to override
            return child_value
    
    def _deep_merge_dict(self, base_dict: Dict[str, Any], child_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base_dict.copy()
        
        for key, value in child_dict.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dict(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                # Append lists by default
                result[key] = result[key] + value
            else:
                result[key] = value
        
        return result
    
    def _generate_config_from_directory(self, template_name: str) -> Dict[str, Any]:
        """Generate basic config from directory structure (backward compatibility)"""
        # Check features directory first
        template_path = self.template_dir / "features" / template_name
        
        if not template_path.exists():
            template_path = self.template_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template directory not found: {template_path}")
        
        # Read README for description
        readme_file = template_path / "README.md"
        description = f"A {template_name} project template"
        if readme_file.exists():
            with open(readme_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines and not lines[0].startswith('#'):
                    description = lines[0].strip()
        
        return {
            'metadata': {
                'name': template_name,
                'description': description,
                'category': 'legacy',
                'version': '1.0.0'
            },
            'files': {
                'copy': ['**/*']  # Copy all files
            }
        }


def demo_enhanced_templates():
    """Demonstrate enhanced template capabilities"""
    print("Enhanced Template System Demo")
    print("=" * 50)
    
    # Create enhanced context
    context = EnhancedTemplateContext(
        project_name="awesome-ml-api",
        description="Machine learning API with FastAPI and MLflow",
        author="Jane Doe",
        email="jane@example.com",
        backend="uv",
        features=["fastapi", "mlflow", "docker"],
        enable_github_actions=True,
        enable_docker=True
    )
    
    # Create enhanced engine
    engine = EnhancedTemplateEngine()
    
    # Demo template with advanced features
    template = '''# {{ project_name_title }}

{{ description }}

## Features
{% for feature in features %}
- {{ feature|title }}
{% endfor %}

## Setup

{% if is_uv %}
```bash
uv sync
```
{% elif is_poetry %}
```bash
poetry install
```
{% endif %}

{% if has_fastapi %}
## API Documentation

The API documentation will be available at http://localhost:8000/docs
{% endif %}

{% if enable_docker %}
## Docker

```bash
docker build -t {{ project_name }} .
docker run -p 8000:8000 {{ project_name }}
```
{% endif %}

## Author

{{ author }} <{{ email }}>
'''
    
    print("Generated README.md:")
    print("-" * 30)
    print(engine.render_string(template, context.to_dict()))


if __name__ == "__main__":
    demo_enhanced_templates() 