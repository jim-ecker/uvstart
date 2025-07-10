"""
User Template Management System for uvstart
Allows users to create, manage, and use custom templates in their local environment
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class UserTemplate:
    """Represents a user-created template"""
    name: str
    description: str
    category: str
    author: str
    version: str
    created_at: datetime
    updated_at: datetime
    path: Path
    is_active: bool = True


class UserTemplateManager:
    """Manages user-created templates in the local environment"""
    
    def __init__(self, user_templates_dir: Optional[Path] = None):
        self.user_templates_dir = user_templates_dir or self._get_default_user_templates_dir()
        self.user_templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize subdirectories
        (self.user_templates_dir / "templates").mkdir(exist_ok=True)
        (self.user_templates_dir / "templates" / "features").mkdir(exist_ok=True)
        (self.user_templates_dir / "templates" / "base").mkdir(exist_ok=True)
        (self.user_templates_dir / "backups").mkdir(exist_ok=True)
        
        self.registry_file = self.user_templates_dir / "registry.json"
        self.config_file = self.user_templates_dir / "config.yaml"
        
        self._load_or_create_config()
    
    def _get_default_user_templates_dir(self) -> Path:
        """Get the default user templates directory"""
        home = Path.home()
        
        # Follow XDG Base Directory Specification on Linux/Mac
        if os.name == 'posix':
            config_home = os.environ.get('XDG_CONFIG_HOME', home / '.config')
            return Path(config_home) / 'uvstart' / 'user-templates'
        else:
            # Windows
            appdata = os.environ.get('APPDATA', home / 'AppData' / 'Roaming')
            return Path(appdata) / 'uvstart' / 'user-templates'
    
    def _load_or_create_config(self) -> None:
        """Load or create user template configuration"""
        if self.config_file.exists() and HAS_YAML:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            # Default configuration
            self.config = {
                'version': '1.0.0',
                'auto_backup': True,
                'max_backups': 10,
                'default_author': os.environ.get('USER', 'Unknown'),
                'default_license': 'MIT',
                'template_validation': True,
                'sync_with_git': False,
                'git_repository': '',
                'categories': [
                    'application',
                    'web',
                    'data-science', 
                    'machine-learning',
                    'cloud-native',
                    'custom'
                ]
            }
            self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        if HAS_YAML:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        else:
            # Fallback to JSON if YAML not available
            with open(self.config_file.with_suffix('.json'), 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
    
    def list_user_templates(self) -> List[UserTemplate]:
        """List all user-created templates"""
        registry = self._load_registry()
        templates = []
        
        for template_name, template_info in registry.items():
            template_path = self.user_templates_dir / "templates" / "features" / template_name
            if not template_path.exists():
                template_path = self.user_templates_dir / "templates" / "base" / template_name
            
            if template_path.exists():
                templates.append(UserTemplate(
                    name=template_name,
                    description=template_info.get('description', ''),
                    category=template_info.get('category', 'custom'),
                    author=template_info.get('author', 'Unknown'),
                    version=template_info.get('version', '1.0.0'),
                    created_at=datetime.fromisoformat(template_info.get('created_at', datetime.now().isoformat())),
                    updated_at=datetime.fromisoformat(template_info.get('updated_at', datetime.now().isoformat())),
                    path=template_path,
                    is_active=template_info.get('is_active', True)
                ))
        
        return templates
    
    def create_template(self, name: str, description: str, category: str = "custom", 
                       is_base_template: bool = False, copy_from: Optional[str] = None) -> Path:
        """Create a new user template"""
        # Validate template name
        if not name.isidentifier():
            raise ValueError(f"Template name '{name}' is not a valid identifier")
        
        # Determine template path
        template_dir = "base" if is_base_template else "features"
        template_path = self.user_templates_dir / "templates" / template_dir / name
        
        if template_path.exists():
            raise FileExistsError(f"Template '{name}' already exists at {template_path}")
        
        # Create template directory
        template_path.mkdir(parents=True)
        
        # Copy from existing template if specified
        if copy_from:
            source_template = self._find_template_path(copy_from)
            if source_template and source_template.exists():
                # Copy all files except template.yaml (we'll create a new one)
                for item in source_template.iterdir():
                    if item.name != 'template.yaml':
                        if item.is_dir():
                            shutil.copytree(item, template_path / item.name)
                        else:
                            shutil.copy2(item, template_path)
        
        # Create template.yaml configuration
        template_config = {
            'metadata': {
                'name': name,
                'description': description,
                'category': category,
                'version': '1.0.0',
                'author': self.config.get('default_author', 'Unknown'),
                'tags': [category, 'user-created'],
                'dependencies': ['uv', 'poetry', 'pdm', 'rye', 'hatch'],
                'features': [name],
                'min_python': '3.8',
                'includes_ci': False,
                'includes_docker': False,
                'includes_tests': True,
                'is_base_template': is_base_template
            },
            'requirements': {
                'dependencies': [],
                'dev_dependencies': [
                    'pytest>=7.0',
                    'black>=22.0',
                    'ruff>=0.1.0'
                ]
            },
            'files': {
                'generate': [
                    {
                        'path': '{{package_name}}/__init__.py',
                        'template': '__init__.py.j2'
                    },
                    {
                        'path': '{{package_name}}/main.py',
                        'template': 'main.py.j2'
                    },
                    {
                        'path': 'README.md',
                        'template': 'README.md.j2'
                    }
                ]
            },
            'hooks': {
                'pre_generate': [
                    f"echo 'Generating {name} project...'"
                ],
                'post_generate': [
                    f"echo '{name} project generated successfully!'"
                ]
            }
        }
        
        if is_base_template:
            template_config['inheritance'] = {
                'extendable_sections': [
                    'requirements.dependencies',
                    'requirements.dev_dependencies',
                    'files.generate'
                ],
                'merge_strategies': {
                    'requirements.dependencies': 'append',
                    'requirements.dev_dependencies': 'append',
                    'files.generate': 'append'
                }
            }
        
        # Write template configuration
        config_file = template_path / 'template.yaml'
        if HAS_YAML:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(template_config, f, default_flow_style=False)
        
        # Create basic template files
        self._create_basic_template_files(template_path, name, description)
        
        # Register template
        self._register_template(name, {
            'description': description,
            'category': category,
            'author': self.config.get('default_author', 'Unknown'),
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'is_active': True,
            'is_base_template': is_base_template
        })
        
        print(f"Template '{name}' created successfully at {template_path}")
        return template_path
    
    def _create_basic_template_files(self, template_path: Path, name: str, description: str) -> None:
        """Create basic template files for a new template"""
        # Create __init__.py.j2
        init_template = template_path / '__init__.py.j2'
        with open(init_template, 'w', encoding='utf-8') as f:
            f.write(f'''"""
{description}
"""

__version__ = "{{{{ version }}}}"
__author__ = "{{{{ author }}}}"
''')
        
        # Create main.py.j2
        main_template = template_path / 'main.py.j2'
        with open(main_template, 'w', encoding='utf-8') as f:
            f.write(f'''"""
{description}
"""

from __future__ import annotations


def main() -> None:
    """Main function for {{{{ project_name_title }}}}"""
    print("Hello from {{{{ project_name_title }}}}!")
    print("Description: {{{{ description }}}}")


if __name__ == "__main__":
    main()
''')
        
        # Create README.md.j2
        readme_template = template_path / 'README.md.j2'
        with open(readme_template, 'w', encoding='utf-8') as f:
            f.write(f'''# {{{{ project_name_title }}}}

{{{{ description }}}}

## Installation

```bash
{{{{ backend }}}} sync
```

## Usage

```bash
{{{{ backend }}}} run python main.py
```

## Development

```bash
# Install development dependencies
{{{{ backend }}}} sync --group dev

# Run tests
{{{{ backend }}}} run pytest

# Format code
{{{{ backend }}}} run black .

# Lint code
{{{{ backend }}}} run ruff check .
```

## License

{{{{ license }}}}

## Author

{{{{ author }}}} <{{{{ email }}}}>
''')
    
    def _find_template_path(self, template_name: str) -> Optional[Path]:
        """Find the path to an existing template"""
        # Check user templates first
        user_feature_path = self.user_templates_dir / "templates" / "features" / template_name
        if user_feature_path.exists():
            return user_feature_path
        
        user_base_path = self.user_templates_dir / "templates" / "base" / template_name
        if user_base_path.exists():
            return user_base_path
        
        # Check system templates
        system_templates_dir = Path(__file__).parent.parent / "templates"
        system_feature_path = system_templates_dir / "features" / template_name
        if system_feature_path.exists():
            return system_feature_path
        
        system_base_path = system_templates_dir / "base" / template_name
        if system_base_path.exists():
            return system_base_path
        
        return None
    
    def delete_template(self, name: str, create_backup: bool = True) -> bool:
        """Delete a user template"""
        template_path = self._find_template_path(name)
        if not template_path:
            return False
        
        # Only allow deletion of user templates
        if not str(template_path).startswith(str(self.user_templates_dir)):
            raise PermissionError("Cannot delete system templates")
        
        # Create backup if requested
        if create_backup and self.config.get('auto_backup', True):
            self._create_backup(name, template_path)
        
        # Remove template directory
        shutil.rmtree(template_path)
        
        # Unregister template
        registry = self._load_registry()
        if name in registry:
            del registry[name]
            self._save_registry(registry)
        
        print(f"Template '{name}' deleted successfully")
        return True
    
    def _create_backup(self, name: str, template_path: Path) -> None:
        """Create a backup of a template before deletion"""
        backup_dir = self.user_templates_dir / "backups"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{name}_{timestamp}"
        
        shutil.copytree(template_path, backup_path)
        
        # Clean up old backups if max_backups is set
        max_backups = self.config.get('max_backups', 10)
        if max_backups > 0:
            backups = sorted([p for p in backup_dir.iterdir() if p.name.startswith(f"{name}_")],
                           key=lambda x: x.stat().st_mtime)
            while len(backups) > max_backups:
                shutil.rmtree(backups.pop(0))
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load the template registry"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_registry(self, registry: Dict[str, Any]) -> None:
        """Save the template registry"""
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
    
    def _register_template(self, name: str, info: Dict[str, Any]) -> None:
        """Register a template in the registry"""
        registry = self._load_registry()
        registry[name] = info
        self._save_registry(registry)
    
    def export_template(self, name: str, output_path: Path) -> bool:
        """Export a template to a tar.gz file"""
        template_path = self._find_template_path(name)
        if not template_path:
            return False
        
        import tarfile
        
        with tarfile.open(output_path, 'w:gz') as tar:
            tar.add(template_path, arcname=name)
        
        print(f"Template '{name}' exported to {output_path}")
        return True
    
    def import_template(self, archive_path: Path, name: Optional[str] = None) -> bool:
        """Import a template from a tar.gz file"""
        import tarfile
        
        with tarfile.open(archive_path, 'r:gz') as tar:
            # Extract to temporary directory first
            temp_dir = self.user_templates_dir / "temp"
            temp_dir.mkdir(exist_ok=True)
            
            try:
                tar.extractall(temp_dir)
                
                # Find the extracted template directory
                extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
                if not extracted_dirs:
                    return False
                
                template_dir = extracted_dirs[0]
                template_name = name or template_dir.name
                
                # Move to final location
                final_path = self.user_templates_dir / "templates" / "features" / template_name
                if final_path.exists():
                    shutil.rmtree(final_path)
                
                shutil.move(str(template_dir), str(final_path))
                
                # Register template
                config_file = final_path / 'template.yaml'
                if config_file.exists() and HAS_YAML:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    
                    metadata = config.get('metadata', {})
                    self._register_template(template_name, {
                        'description': metadata.get('description', ''),
                        'category': metadata.get('category', 'custom'),
                        'author': metadata.get('author', 'Unknown'),
                        'version': metadata.get('version', '1.0.0'),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                        'is_active': True
                    })
                
                print(f"Template '{template_name}' imported successfully")
                return True
            
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        return False


def demo_user_templates():
    """Demonstrate user template management"""
    print("User Template Management Demo")
    print("=" * 50)
    
    manager = UserTemplateManager()
    
    # List existing templates
    templates = manager.list_user_templates()
    print(f"Found {len(templates)} user templates")
    
    # Create a sample template
    try:
        template_path = manager.create_template(
            name="my_custom_api",
            description="My custom API template with special features",
            category="web"
        )
        print(f"Created template at: {template_path}")
    except FileExistsError:
        print("Template already exists")
    
    # List templates again
    templates = manager.list_user_templates()
    for template in templates:
        print(f"- {template.name}: {template.description}")


if __name__ == "__main__":
    demo_user_templates() 