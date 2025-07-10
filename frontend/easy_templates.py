"""
Easy Template Creation System for uvstart
Makes it dummy stupid easy to add new template types with minimal effort
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class SimpleTemplateConfig:
    """Simple configuration for creating templates"""
    name: str
    description: str
    category: str = "custom"
    files: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    copy_from: Optional[str] = None
    
    def __post_init__(self):
        if self.files is None:
            self.files = ["main.py", "README.md", "__init__.py"]
        if self.dependencies is None:
            self.dependencies = []


class EasyTemplateCreator:
    """Super simple template creator"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "features"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Built-in template types with smart defaults
        self.template_presets = {
            "api": {
                "description": "REST API with FastAPI",
                "category": "web",
                "files": ["main.py", "api/routes.py", "api/models.py", "README.md"],
                "dependencies": ["fastapi", "uvicorn"]
            },
            "cli-tool": {
                "description": "Command-line tool with Click",
                "category": "application", 
                "files": ["main.py", "cli/commands.py", "README.md"],
                "dependencies": ["click", "rich"]
            },
            "data-app": {
                "description": "Data analysis application",
                "category": "data-science",
                "files": ["main.py", "data/loader.py", "analysis/analyzer.py", "README.md"],
                "dependencies": ["pandas", "matplotlib", "seaborn"]
            },
            "web-scraper": {
                "description": "Web scraping application",
                "category": "automation",
                "files": ["main.py", "scraper/spider.py", "data/processor.py", "README.md"],
                "dependencies": ["requests", "beautifulsoup4", "pandas"]
            },
            "bot": {
                "description": "Discord/Telegram bot",
                "category": "automation",
                "files": ["main.py", "bot/commands.py", "bot/handlers.py", "README.md"],
                "dependencies": ["discord.py", "python-telegram-bot"]
            },
            "simple": {
                "description": "Simple Python project",
                "category": "basic",
                "files": ["main.py", "README.md"],
                "dependencies": []
            }
        }
    
    def create_template_interactive(self) -> str:
        """Interactive template creation wizard"""
        print("Easy Template Creator")
        print("=" * 50)
        
        # Step 1: Template name
        name = input("Template name (e.g., 'my-api'): ").strip()
        if not name:
            name = "my-template"
        
        # Step 2: Choose preset or custom
        print("\nChoose a template type:")
        print("0. Custom (start from scratch)")
        for i, (preset_name, preset_info) in enumerate(self.template_presets.items(), 1):
            print(f"{i}. {preset_name}: {preset_info['description']}")
        
        choice = input(f"\nChoice (0-{len(self.template_presets)}): ").strip()
        
        if choice == "0":
            # Custom template
            description = input("Description: ").strip() or f"Custom {name} template"
            category = input("Category (web/cli/data/automation/basic): ").strip() or "custom"
            
            # Files to create
            print("\nWhat files should this template create? (one per line, empty line to finish)")
            files = []
            while True:
                file_input = input("File path: ").strip()
                if not file_input:
                    break
                files.append(file_input)
            
            if not files:
                files = ["main.py", "README.md"]
            
            # Dependencies
            deps_input = input("Dependencies (comma-separated, optional): ").strip()
            dependencies = [dep.strip() for dep in deps_input.split(",") if dep.strip()] if deps_input else []
            
            config = SimpleTemplateConfig(
                name=name,
                description=description,
                category=category,
                files=files,
                dependencies=dependencies
            )
        
        else:
            # Use preset
            try:
                preset_index = int(choice) - 1
                preset_name = list(self.template_presets.keys())[preset_index]
                preset = self.template_presets[preset_name]
                
                description = input(f"Description [{preset['description']}]: ").strip() or preset['description']
                
                config = SimpleTemplateConfig(
                    name=name,
                    description=description,
                    category=preset['category'],
                    files=preset['files'],
                    dependencies=preset['dependencies']
                )
            except (ValueError, IndexError):
                print("Invalid choice, using simple template")
                config = SimpleTemplateConfig(name=name, description=f"Simple {name} template")
        
        # Step 3: Copy from existing template (optional)
        copy_from = input("\nCopy from existing template (optional): ").strip()
        if copy_from:
            config.copy_from = copy_from
        
        # Create the template
        template_path = self.create_template(config)
        
        print(f"\nTemplate '{name}' created at {template_path}")
        print("\nNext steps:")
        print(f"1. Edit template files in {template_path}")
        print(f"2. Test: ./uvstart generate test-{name} {name}")
        print(f"3. Customize template.yaml if needed")
        
        return name
    
    def create_template(self, config: SimpleTemplateConfig) -> Path:
        """Create a template from simple configuration"""
        template_path = self.templates_dir / config.name
        
        if template_path.exists():
            response = input(f"Template '{config.name}' exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                raise FileExistsError(f"Template '{config.name}' already exists")
            shutil.rmtree(template_path)
        
        template_path.mkdir(parents=True)
        
        # Copy from existing template if specified
        if config.copy_from:
            source_path = self._find_existing_template(config.copy_from)
            if source_path:
                print(f"Copying from {config.copy_from}...")
                for item in source_path.iterdir():
                    if item.name != 'template.yaml':  # We'll create our own
                        if item.is_dir():
                            shutil.copytree(item, template_path / item.name)
                        else:
                            shutil.copy2(item, template_path)
        
        # Create template.yaml
        self._create_template_yaml(template_path, config)
        
        # Create template files
        self._create_template_files(template_path, config)
        
        return template_path
    
    def _find_existing_template(self, template_name: str) -> Optional[Path]:
        """Find an existing template to copy from"""
        search_paths = [
            self.templates_dir / template_name,
            self.templates_dir.parent / "base" / template_name,
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        print(f"Warning: Template '{template_name}' not found for copying")
        return None
    
    def _create_template_yaml(self, template_path: Path, config: SimpleTemplateConfig):
        """Create template.yaml configuration"""
        template_config = {
            'metadata': {
                'name': config.name,
                'description': config.description,
                'category': config.category,
                'version': '1.0.0',
                'author': 'Template Creator',
                'tags': [config.category, 'easy-template'],
                'dependencies': ['uv', 'poetry', 'pdm', 'rye', 'hatch'],
                'features': [config.name],
                'min_python': '3.8',
                'includes_ci': False,
                'includes_docker': False,
                'includes_tests': True
            },
            'requirements': {
                'dependencies': config.dependencies,
                'dev_dependencies': [
                    'pytest>=7.0',
                    'black>=22.0',
                    'ruff>=0.1.0'
                ]
            },
            'files': {
                'generate': []
            },
            'hooks': {
                'pre_generate': [
                    f"echo 'Generating {config.name} project...'"
                ],
                'post_generate': [
                    f"echo '{config.name} project created! 🎉'",
                    "echo 'Next steps:'",
                    "echo '1. {{backend}} sync'",
                    "echo '2. {{backend}} run python main.py'"
                ]
            }
        }
        
        # Add files to generate list
        for file_path in (config.files or []):
            template_config['files']['generate'].append({
                'path': file_path,
                'template': f"{file_path}.j2"
            })
        
        # Write YAML config
        config_file = template_path / 'template.yaml'
        if HAS_YAML:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(template_config, f, default_flow_style=False, sort_keys=False)
        else:
            # Fallback to manual YAML writing
            self._write_yaml_manually(config_file, template_config)
    
    def _write_yaml_manually(self, file_path: Path, data: Dict[str, Any]):
        """Write YAML manually when PyYAML not available"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("metadata:\n")
            for key, value in data['metadata'].items():
                if isinstance(value, list):
                    f.write(f"  {key}:\n")
                    for item in value:
                        f.write(f"    - \"{item}\"\n")
                else:
                    f.write(f"  {key}: \"{value}\"\n")
            
            f.write("\nrequirements:\n")
            f.write("  dependencies:\n")
            for dep in data['requirements']['dependencies']:
                f.write(f"    - \"{dep}\"\n")
            f.write("  dev_dependencies:\n")
            for dep in data['requirements']['dev_dependencies']:
                f.write(f"    - \"{dep}\"\n")
    
    def _create_template_files(self, template_path: Path, config: SimpleTemplateConfig):
        """Create template files (.j2) with smart defaults"""
        for file_path in config.files:
            template_file = template_path / f"{file_path}.j2"
            template_file.parent.mkdir(parents=True, exist_ok=True)
            
            content = self._generate_file_content(file_path, config)
            
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _generate_file_content(self, file_path: str, config: SimpleTemplateConfig) -> str:
        """Generate smart default content for template files"""
        file_name = Path(file_path).name
        
        if file_name == "main.py":
            return self._generate_main_py(config)
        elif file_name == "README.md":
            return self._generate_readme(config)
        elif file_name == "__init__.py":
            return self._generate_init_py(config)
        elif "routes.py" in file_name:
            return self._generate_routes_py(config)
        elif "commands.py" in file_name:
            return self._generate_commands_py(config)
        elif "models.py" in file_name:
            return self._generate_models_py(config)
        else:
            return self._generate_generic_file(file_path, config)
    
    def _generate_main_py(self, config: SimpleTemplateConfig) -> str:
        """Generate main.py template"""
        if "fastapi" in config.dependencies:
            return '''"""
{{ description }}
"""

from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="{{ project_name_title }}", description="{{ description }}")
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hello from {{ project_name_title }}!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        elif "click" in config.dependencies:
            return '''"""
{{ description }}
"""

import click
from cli.commands import main_group

@click.group()
def cli():
    """{{ project_name_title }} - {{ description }}"""
    pass

cli.add_command(main_group)

if __name__ == "__main__":
    cli()
'''
        
        else:
            return '''"""
{{ description }}
"""

def main():
    """Main function for {{ project_name_title }}"""
    print("Hello from {{ project_name_title }}!")
    print("Description: {{ description }}")
    
    # TODO: Add your main logic here

if __name__ == "__main__":
    main()
'''
    
    def _generate_readme(self, config: SimpleTemplateConfig) -> str:
        """Generate README.md template"""
        return '''# {{ project_name_title }}

{{ description }}

## Installation

```bash
# Install dependencies
{{ backend }} sync

# Activate environment (if needed)
{{ backend }} shell
```

## Usage

```bash
{{ backend }} run python main.py
```

## Development

```bash
# Install development dependencies
{{ backend }} sync --group dev

# Run tests
{{ backend }} run pytest

# Format code
{{ backend }} run black .

# Lint code
{{ backend }} run ruff check .
```

## Features

{% for feature in features %}
- {{ feature }}
{% endfor %}

## License

{{ license }}

## Author

{{ author }} <{{ email }}>
'''
    
    def _generate_init_py(self, config: SimpleTemplateConfig) -> str:
        """Generate __init__.py template"""
        return '''"""
{{ description }}
"""

__version__ = "{{ version }}"
__author__ = "{{ author }}"
'''
    
    def _generate_routes_py(self, config: SimpleTemplateConfig) -> str:
        """Generate routes.py for FastAPI"""
        return '''"""
API routes for {{ project_name_title }}
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
async def hello():
    """Hello endpoint"""
    return {"message": "Hello from {{ project_name_title }}!"}

@router.get("/info")
async def info():
    """Get application info"""
    return {
        "name": "{{ project_name_title }}",
        "description": "{{ description }}",
        "version": "{{ version }}"
    }
'''
    
    def _generate_commands_py(self, config: SimpleTemplateConfig) -> str:
        """Generate commands.py for Click CLI"""
        return '''"""
CLI commands for {{ project_name_title }}
"""

import click

@click.group()
def main_group():
    """Main command group"""
    pass

@main_group.command()
@click.option('--name', default='World', help='Name to greet')
def hello(name):
    """Say hello"""
    click.echo(f'Hello {name} from {{ project_name_title }}!')

@main_group.command()
def info():
    """Show application info"""
    click.echo("{{ project_name_title }}")
    click.echo("{{ description }}")
'''
    
    def _generate_models_py(self, config: SimpleTemplateConfig) -> str:
        """Generate models.py"""
        return '''"""
Data models for {{ project_name_title }}
"""

from pydantic import BaseModel
from typing import Optional

class ExampleModel(BaseModel):
    """Example data model"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    
    class Config:
        """Pydantic configuration"""
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Example Item",
                "description": "An example item for {{ project_name_title }}"
            }
        }
'''
    
    def _generate_generic_file(self, file_path: str, config: SimpleTemplateConfig) -> str:
        """Generate generic file template"""
        return f'''"""
{file_path} for {{{{ project_name_title }}}}
Generated by Easy Template Creator
"""

# TODO: Add your code here for {file_path}

def main():
    """Main function for {file_path}"""
    print("TODO: Implement {file_path}")

if __name__ == "__main__":
    main()
'''


def quick_template(name: str, template_type: str = "simple") -> str:
    """One-liner template creation"""
    creator = EasyTemplateCreator()
    
    if template_type in creator.template_presets:
        preset = creator.template_presets[template_type]
        config = SimpleTemplateConfig(
            name=name,
            description=preset['description'],
            category=preset['category'],
            files=preset['files'],
            dependencies=preset['dependencies']
        )
    else:
        config = SimpleTemplateConfig(
            name=name,
            description=f"Simple {name} template"
        )
    
    template_path = creator.create_template(config)
    print(f"✅ Quick template '{name}' created!")
    return str(template_path)


def demo_easy_templates():
    """Demo the easy template system"""
    print("🚀 Easy Template Creation Demo")
    print("=" * 50)
    
    creator = EasyTemplateCreator()
    
    print("Available template presets:")
    for name, preset in creator.template_presets.items():
        print(f"  {name}: {preset['description']}")
    
    print("\nTo create a template interactively:")
    print("from frontend.easy_templates import EasyTemplateCreator")
    print("creator = EasyTemplateCreator()")
    print("creator.create_template_interactive()")
    
    print("\nTo create a quick template:")
    print("from frontend.easy_templates import quick_template")
    print("quick_template('my-api', 'api')")


if __name__ == "__main__":
    demo_easy_templates() 