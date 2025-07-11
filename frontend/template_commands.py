"""
Comprehensive Template Management System for uvstart
Provides directory-to-template conversion, research reproducibility, and template management
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import tempfile
import re

# Handle optional PyYAML import
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class TemplateInfo:
    """Information about a template"""
    name: str
    type: str  # 'builtin', 'system', 'user'
    description: str
    category: str
    features: List[str]
    path: Optional[Path] = None
    author: str = "uvstart"
    version: str = "1.0.0"


class TemplateManager:
    """Comprehensive template management system"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        
        # Use consistent user templates directory (same as UserTemplateManager)
        home = Path.home()
        if os.name == 'posix':
            config_home = os.environ.get('XDG_CONFIG_HOME', home / '.config')
            self.user_templates_dir = Path(config_home) / 'uvstart' / 'user-templates'
        else:
            # Windows
            appdata = os.environ.get('APPDATA', home / 'AppData' / 'Roaming')
            self.user_templates_dir = Path(appdata) / 'uvstart' / 'user-templates'
        
        self.user_templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Template patterns to ignore when creating from directory
        self.ignore_patterns = {
            # Version control
            '.git', '.svn', '.hg', '.bzr',
            # Python
            '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.Python',
            '*.so', '.env', '.venv', 'venv', 'env',
            '.pytest_cache', '.coverage', 'htmlcov',
            # Build artifacts
            'build', 'dist', '*.egg-info', '.tox',
            # IDE files
            '.vscode', '.idea', '*.swp', '*.swo', '*~',
            # OS files
            '.DS_Store', 'Thumbs.db', 'desktop.ini',
            # Temporary files
            '*.tmp', '*.temp', '*.log',
            # Data files (for research templates)
            '*.csv', '*.json', '*.pkl', '*.h5', '*.parquet'
        }
    
    def list_templates(self) -> List[TemplateInfo]:
        """List all available templates"""
        templates = []
        
        # Builtin templates (from features directory)
        features_dir = self.templates_dir / "features"
        if features_dir.exists():
            for template_dir in features_dir.iterdir():
                if template_dir.is_dir():
                    info = self._extract_template_info(template_dir, "builtin")
                    if info:
                        templates.append(info)
        
        # User templates
        user_features_dir = self.user_templates_dir / "templates" / "features"
        if user_features_dir.exists():
            for template_dir in user_features_dir.iterdir():
                if template_dir.is_dir():
                    info = self._extract_template_info(template_dir, "user")
                    if info:
                        templates.append(info)
        
        return sorted(templates, key=lambda t: (t.type, t.category, t.name))
    
    def _extract_template_info(self, template_dir: Path, template_type: str) -> Optional[TemplateInfo]:
        """Extract template information from directory"""
        try:
            # Try to load template.yaml
            config_file = template_dir / "template.yaml"
            if config_file.exists() and HAS_YAML:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                metadata = config.get('metadata', {})
                return TemplateInfo(
                    name=template_dir.name,
                    type=template_type,
                    description=metadata.get('description', f'{template_dir.name} template'),
                    category=metadata.get('category', 'custom'),
                    features=metadata.get('features', []),
                    path=template_dir,
                    author=metadata.get('author', 'uvstart'),
                    version=metadata.get('version', '1.0.0')
                )
            
            # Fallback: infer from directory structure
            readme_file = None
            for name in ['README.md', 'readme.md', 'README.txt']:
                if (template_dir / name).exists():
                    readme_file = template_dir / name
                    break
            
            description = f"{template_dir.name} template"
            if readme_file:
                try:
                    with open(readme_file, 'r') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('#'):
                            description = first_line.lstrip('# ')
                except:
                    pass
            
            return TemplateInfo(
                name=template_dir.name,
                type=template_type,
                description=description,
                category=self._infer_category(template_dir),
                features=self._infer_features(template_dir),
                path=template_dir
            )
            
        except Exception as e:
            print(f"Warning: Could not extract info for {template_dir}: {e}")
            return None
    
    def _infer_category(self, template_dir: Path) -> str:
        """Infer template category from directory structure"""
        files = [f.name.lower() for f in template_dir.rglob('*') if f.is_file()]
        
        if any('fastapi' in f or 'flask' in f or 'django' in f for f in files):
            return 'web'
        elif any('click' in f or 'argparse' in f for f in files):
            return 'cli'
        elif any('jupyter' in f or '.ipynb' in f for f in files):
            return 'data-science'
        elif any('torch' in f or 'tensorflow' in f for f in files):
            return 'ml'
        else:
            return 'custom'
    
    def _infer_features(self, template_dir: Path) -> List[str]:
        """Infer template features from directory structure"""
        features = []
        files = [f.name.lower() for f in template_dir.rglob('*') if f.is_file()]
        content = ""
        
        # Sample some file contents
        for f in template_dir.rglob('*.py'):
            try:
                with open(f, 'r') as file:
                    content += file.read().lower()
                    break
            except:
                continue
        
        if 'fastapi' in content or any('fastapi' in f for f in files):
            features.append('web')
        if 'click' in content or any('click' in f for f in files):
            features.append('cli')
        if 'jupyter' in content or any('.ipynb' in f for f in files):
            features.append('notebook')
        if 'torch' in content or any('torch' in f for f in files):
            features.append('pytorch')
        
        return features
    
    def create_from_directory(self, source_dir: Path, template_name: str, 
                            description: Optional[str] = None,
                            category: Optional[str] = None,
                            is_research: bool = False) -> bool:
        """Create a template from an existing directory"""
        try:
            return self._create_directory_template(source_dir, template_name, description, category)
        except Exception as e:
            print(f"Error creating template: {e}")
            return False
    
    def _create_directory_template(self, source_dir: Path, template_name: str,
                                 description: Optional[str] = None,
                                 category: Optional[str] = None) -> bool:
        """Create a regular template from directory"""
        print(f"Creating template '{template_name}' from directory: {source_dir}")
        
        # STEP 1: Enhance the source directory with Python project files
        print("Step 1: Enhancing source directory with Python project structure...")
        self._enhance_source_directory(source_dir, template_name, description)
        
        # STEP 2: Create template directory
        template_dir = self.user_templates_dir / "templates" / "features" / template_name
        if template_dir.exists():
            response = input(f"Template '{template_name}' already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                return False
            shutil.rmtree(template_dir)
        
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # STEP 3: Analyze the enhanced source directory
        template_vars: Set[str] = set()
        files_to_process = []
        processed_files = []  # Track what files we actually create
        
        # First, handle all files
        for file_path in source_dir.rglob('*'):
            if file_path.is_file() and not self._should_ignore_file(file_path, source_dir):
                rel_path = file_path.relative_to(source_dir)
                files_to_process.append((file_path, rel_path))
        
        # Then, handle empty directories by creating .gitkeep files
        empty_dirs = []
        for dir_path in source_dir.rglob('*'):
            if dir_path.is_dir() and not self._should_ignore_file(dir_path, source_dir):
                # Check if directory is empty (no non-ignored files)
                has_files = False
                for item in dir_path.rglob('*'):
                    if item.is_file() and not self._should_ignore_file(item, source_dir):
                        has_files = True
                        break
                
                if not has_files:
                    rel_path = dir_path.relative_to(source_dir)
                    empty_dirs.append(rel_path)
                    print(f"Found empty directory: {rel_path}")
        
        print(f"Step 2: Processing {len(files_to_process)} files and {len(empty_dirs)} empty directories...")
        
        # Process files and extract template variables
        for source_file, rel_path in files_to_process:
            target_file_info = self._process_template_file(source_file, template_dir / rel_path, template_vars, template_name)
            if target_file_info:
                processed_files.append(target_file_info)
        
        # Create .gitkeep files for empty directories
        for empty_dir in empty_dirs:
            gitkeep_path = template_dir / empty_dir / '.gitkeep'
            gitkeep_path.parent.mkdir(parents=True, exist_ok=True)
            gitkeep_path.write_text('')
            
            processed_files.append({
                'source_path': str(source_dir / empty_dir),
                'target_path': str(gitkeep_path),
                'is_processed': True,
                'is_empty_dir_placeholder': True
            })
        
        # Create template.yaml with the actual files we processed
        self._create_template_yaml(template_dir, template_name, description, category, template_vars, processed_files)
        
        # Create README for the template
        self._create_template_readme(template_dir, template_name, description, template_vars)
        
        # Register the template (important for UserTemplateManager integration)
        self._register_template(template_name, {
            'description': description or f"Template generated from {source_dir.name}",
            'category': category or 'custom',
            'author': 'user',
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'is_active': True,
            'is_base_template': False
        })
        
        print(f" Template '{template_name}' created successfully!")
        print(f" Template location: {template_dir}")
        print(f" Enhanced source: {source_dir}")
        print(f" Test it: uvstart init --name test-{template_name} --features {template_name}")
        
        return True
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load the template registry"""
        registry_file = self.user_templates_dir / "registry.json"
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_registry(self, registry: Dict[str, Any]) -> None:
        """Save the template registry"""
        registry_file = self.user_templates_dir / "registry.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
    
    def _register_template(self, name: str, info: Dict[str, Any]) -> None:
        """Register a template in the registry"""
        registry = self._load_registry()
        registry[name] = info
        self._save_registry(registry)
    
    def _enhance_source_directory(self, source_dir: Path, template_name: str, description: Optional[str]) -> None:
        """Enhance the source directory with Python project files"""
        from simple_templates import SimpleTemplateManager, TemplateContext
        
        # Create a template context for the source directory
        context = TemplateContext(
            project_name=template_name,
            description=description or f"Project based on {template_name}",
            version="0.1.0",
            author="Developer",
            email="dev@example.com",
            backend="uv",
            features=[],
            python_version="3.11"
        )
        
        # Generate basic Python project structure
        simple_manager = SimpleTemplateManager()
        project_files = simple_manager.generate_project_files(context, [])
        
        # Write the Python project files to the source directory
        files_created = []
        for file_path, content in project_files.items():
            full_path = source_dir / file_path
            
            # Don't overwrite existing files
            if full_path.exists():
                continue
                
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            files_created.append(file_path)
        
        if files_created:
            print(f"   Added Python project files: {', '.join(files_created)}")
        else:
            print(f"  ℹ  Source directory already has Python project files")
    
    def _should_ignore_file(self, file_path: Path, source_dir: Path) -> bool:
        """Check if file should be ignored when creating template"""
        rel_path = file_path.relative_to(source_dir)
        
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                if str(rel_path).endswith(pattern[1:]):
                    return True
            elif pattern in str(rel_path):
                return True
        
        return False
    
    def _process_template_file(self, source_file: Path, target_file: Path, 
                             template_vars: Set[str], template_name: str) -> Optional[Dict[str, Any]]:
        """Process a file for template creation, extracting variables"""
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Read source file
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract and replace template variables
            processed_content = self._extract_and_replace_variables(content, template_vars, template_name)
            
            # Write processed file
            target_path = target_file
            if source_file.suffix in ['.py', '.md', '.txt', '.yaml', '.yml', '.toml', '.cfg']:
                target_path = target_file.with_suffix(target_file.suffix + '.j2')
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
                
            return {
                'source_path': str(source_file),
                'target_path': str(target_path),
                'is_processed': True
            }
                
        except UnicodeDecodeError:
            # Binary file, copy as-is
            shutil.copy2(source_file, target_file)
            return {
                'source_path': str(source_file),
                'target_path': str(target_file),
                'is_processed': True
            }
        except Exception as e:
            print(f"Warning: Could not process {source_file}: {e}")
            # Copy as-is on error
            shutil.copy2(source_file, target_file)
            return {
                'source_path': str(source_file),
                'target_path': str(target_file),
                'is_processed': True
            }
    
    def _extract_and_replace_variables(self, content: str, template_vars: Set[str], 
                                     template_name: str) -> str:
        """Extract template variables and replace with template syntax"""
        # Look for the template name itself in various forms
        template_name_patterns = [
            template_name,
            template_name.replace('-', '_'),
            template_name.replace('_', '-'),
            template_name.replace('-', ' ').title(),
            template_name.upper(),
        ]
        
        processed_content = content
        for pattern_name in template_name_patterns:
            if pattern_name in content:
                processed_content = processed_content.replace(pattern_name, '{{project_name}}')
                template_vars.add('project_name')
        
        # Look for email patterns
        email_matches = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', content)
        for email in email_matches:
            processed_content = processed_content.replace(email, '{{email}}')
            template_vars.add('email')
        
        # Look for year patterns
        year_matches = re.findall(r'\b20\d{2}\b', content)
        for year in year_matches:
            processed_content = processed_content.replace(year, '{{year}}')
            template_vars.add('year')
        
        return processed_content
    
    def _create_template_yaml(self, template_dir: Path, template_name: str,
                            description: Optional[str] = None,
                            category: Optional[str] = None,
                            template_vars: Optional[Set[str]] = None,
                            processed_files: Optional[List[Dict[str, Any]]] = None) -> None:
        """Create template.yaml configuration"""
        
        # Generate files section based on actually processed files
        files_to_generate = []
        
        if processed_files:
            for file_info in processed_files:
                target_path = Path(file_info['target_path'])
                # Make path relative to template directory
                rel_path = target_path.relative_to(template_dir)
                
                # Determine final path in generated project
                if rel_path.suffix == '.j2':
                    # Template file - remove .j2 extension for final path
                    final_path = str(rel_path.with_suffix(''))
                    file_entry = {
                        'path': final_path,
                        'template': str(rel_path)
                    }
                else:
                    # Static file - copy as-is
                    file_entry = {
                        'path': str(rel_path),
                        'source': str(rel_path)
                    }
                
                files_to_generate.append(file_entry)
        
        # If no files were processed, add a basic structure
        if not files_to_generate:
            files_to_generate = [
                {
                    'path': '{{package_name}}/__init__.py',
                    'content': ''
                }
            ]
        
        config = {
            'metadata': {
                'name': template_name,
                'description': description or f"Template generated from existing project",
                'category': category or 'custom',
                'version': '1.0.0',
                'author': 'user',
                'created_at': datetime.now().isoformat(),
                'tags': ['user-generated', 'from-directory'],
                'features': [template_name],
                'template_variables': list(template_vars) if template_vars else [],
                'min_python': '3.8',
                'includes_ci': False,
                'includes_docker': False,
                'includes_tests': any('test' in str(f.get('path', '')) for f in files_to_generate)
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
                'generate': files_to_generate
            },
            'hooks': {
                'pre_generate': [
                    f"echo 'Generating {template_name} project from directory template...'"
                ],
                'post_generate': [
                    f"echo '{template_name} project created!'",
                    "echo 'Next steps:'",
                    "echo '1. {{backend}} sync'",
                    "echo '2. Start working with your replicated structure!'"
                ]
            }
        }
        
        # Try to detect dependencies from common files
        dep_files = ['requirements.txt', 'pyproject.toml', 'setup.py', 'setup.cfg', 'poetry.lock', 'uv.lock']
        detected_deps = []
        
        for dep_file in dep_files:
            if (template_dir / dep_file).exists():
                config['requirements']['detected_from'] = dep_file
                # Could parse dependencies here in the future
                break
        
        if HAS_YAML:
            with open(template_dir / 'template.yaml', 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        else:
            # Fallback to JSON if YAML not available
            with open(template_dir / 'template.json', 'w') as f:
                json.dump(config, f, indent=2)
    
    def _create_template_readme(self, template_dir: Path, template_name: str,
                              description: Optional[str] = None,
                              template_vars: Optional[Set[str]] = None) -> None:
        """Create README for the template"""
        readme_content = f"""# {template_name.title()} Template

{description or f"Template for creating {template_name} projects"}

## Generated Template Variables

This template uses the following variables:

"""
        
        if template_vars:
            for var in sorted(template_vars):
                readme_content += f"- `{{{{{var}}}}}` - {var.replace('_', ' ').title()}\n"
        
        readme_content += f"""

## Usage

```bash
uvstart generate my-project --features {template_name}
```

## Template Structure

This template was automatically generated from an existing project directory.
All template variables are marked with `{{{{variable_name}}}}` syntax.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(template_dir / 'README.md', 'w') as f:
            f.write(readme_content)
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a template"""
        templates = self.list_templates()
        template = next((t for t in templates if t.name == template_name), None)
        
        if not template:
            return None
        
        info = {
            'name': template.name,
            'type': template.type,
            'description': template.description,
            'category': template.category,
            'features': template.features,
            'author': template.author,
            'version': template.version,
            'path': str(template.path) if template.path else None
        }
        
        # Load additional info from template.yaml if available
        if template.path and (template.path / 'template.yaml').exists() and HAS_YAML:
            try:
                with open(template.path / 'template.yaml', 'r') as f:
                    config = yaml.safe_load(f)
                    info.update(config.get('metadata', {}))
            except:
                pass
        
        return info
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a user template"""
        templates = self.list_templates()
        template = next((t for t in templates if t.name == template_name and t.type == 'user'), None)
        
        if not template:
            print(f"User template '{template_name}' not found")
            return False
        
        if not template.path:
            print(f"Cannot delete template without path")
            return False
        
        try:
            response = input(f"Are you sure you want to delete template '{template_name}'? (y/N): ")
            if response.lower() == 'y':
                shutil.rmtree(template.path)
                print(f" Template '{template_name}' deleted successfully")
                return True
            else:
                print("Deletion cancelled")
                return False
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False 