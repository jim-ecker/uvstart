"""
Directory-to-Template Generator for uvstart
The ULTIMATE in simplicity - generate templates from existing project directories

Usage:
1. Set up your project directory exactly how you want it
2. Run: uvstart template from-directory my-template-name
3. Done! Template is created from your current directory structure
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class DetectedFile:
    """Represents a file detected in the directory"""
    path: Path
    relative_path: str
    should_template: bool
    template_vars: Set[str]
    file_type: str


class DirectoryTemplateGenerator:
    """Generate templates from existing project directories"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "features"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Files to ignore when creating templates
        self.ignore_patterns = {
            '__pycache__',
            '.git',
            '.gitignore',
            'node_modules',
            '.env',
            '.venv',
            'venv',
            'env',
            '.pytest_cache',
            '.coverage',
            '*.pyc',
            '*.pyo',
            '*.egg-info',
            'dist/',
            'build/',
            '.DS_Store',
            'Thumbs.db'
        }
        
        # Common template variables to detect and replace
        self.template_vars = {
            'project_name': r'(?i)my[-_]?project|example[-_]?project|test[-_]?project|demo[-_]?app',
            'package_name': r'(?i)my[-_]?package|example[-_]?package|main[-_]?package',
            'author': r'(?i)your[-_]?name|author[-_]?name|john[-_]?doe',
            'email': r'(?i)your\.email@example\.com|author@example\.com',
            'description': r'(?i)my[-_ ]description|example[-_ ]description|project[-_ ]description',
            'version': r'0\.1\.0|1\.0\.0',
        }
        
        # File extensions that should be templated
        self.templatable_extensions = {
            '.py', '.md', '.txt', '.yml', '.yaml', '.json', 
            '.toml', '.cfg', '.ini', '.sh', '.bat', '.html', 
            '.css', '.js', '.ts', '.jsx', '.tsx', '.vue'
        }
    
    def generate_from_directory(self, source_dir: Path, template_name: str, 
                               description: Optional[str] = None) -> Path:
        """Generate a template from an existing directory"""
        if not source_dir.exists() or not source_dir.is_dir():
            raise ValueError(f"Source directory {source_dir} does not exist or is not a directory")
        
        # Analyze the directory
        print(f"Analyzing directory: {source_dir}")
        detected_files = self._analyze_directory(source_dir)
        dependencies = self._detect_dependencies(source_dir)
        category = self._detect_category(detected_files, dependencies)
        
        if not description:
            description = f"Template generated from {source_dir.name}"
        
        print(f"Detected {len(detected_files)} files")
        print(f"Found {len(dependencies)} dependencies")
        print(f"Category: {category}")
        
        # Create template directory
        template_path = self.templates_dir / template_name
        if template_path.exists():
            response = input(f"Template '{template_name}' exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                raise FileExistsError(f"Template '{template_name}' already exists")
            shutil.rmtree(template_path)
        
        template_path.mkdir(parents=True)
        
        # Generate template files
        print("Creating template files...")
        self._create_template_files(detected_files, template_path, source_dir)
        
        # Create template.yaml
        self._create_template_config(template_path, template_name, description, 
                                   category, dependencies, detected_files)
        
        print(f"Template '{template_name}' created at {template_path}")
        return template_path
    
    def _analyze_directory(self, source_dir: Path) -> List[DetectedFile]:
        """Analyze directory and detect files to include in template"""
        detected_files = []
        
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            for file in files:
                if self._should_ignore(file):
                    continue
                
                file_path = root_path / file
                relative_path = file_path.relative_to(source_dir)
                
                # Determine if file should be templated
                should_template = file_path.suffix in self.templatable_extensions
                
                # Detect template variables in content
                template_vars = set()
                if should_template and file_path.is_file():
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        template_vars = self._detect_template_vars(content)
                    except Exception:
                        # If we can't read it, don't template it
                        should_template = False
                
                detected_files.append(DetectedFile(
                    path=file_path,
                    relative_path=str(relative_path),
                    should_template=should_template,
                    template_vars=template_vars,
                    file_type=self._detect_file_type(file_path)
                ))
        
        return detected_files
    
    def _should_ignore(self, name: str) -> bool:
        """Check if a file or directory should be ignored"""
        for pattern in self.ignore_patterns:
            if pattern.endswith('/'):
                if name == pattern[:-1]:
                    return True
            elif '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(name, pattern):
                    return True
            elif name == pattern:
                return True
        return False
    
    def _detect_template_vars(self, content: str) -> Set[str]:
        """Detect template variables in file content"""
        found_vars = set()
        
        for var_name, pattern in self.template_vars.items():
            if re.search(pattern, content):
                found_vars.add(var_name)
        
        return found_vars
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detect the type of file"""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()
        
        if suffix == '.py':
            if 'main' in name:
                return 'main'
            elif 'test' in name:
                return 'test'
            elif '__init__' in name:
                return 'init'
            else:
                return 'python'
        elif suffix in ['.md', '.rst']:
            return 'documentation'
        elif suffix in ['.yml', '.yaml']:
            return 'config'
        elif suffix in ['.json', '.toml', '.cfg', '.ini']:
            return 'config'
        elif suffix in ['.txt', '.license']:
            return 'text'
        else:
            return 'other'
    
    def _detect_dependencies(self, source_dir: Path) -> List[str]:
        """Detect dependencies from common files"""
        dependencies = []
        
        # Check for requirements.txt
        req_file = source_dir / 'requirements.txt'
        if req_file.exists():
            try:
                content = req_file.read_text(encoding='utf-8')
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before any version specifiers)
                        package = re.split(r'[>=<!=]', line)[0].strip()
                        if package:
                            dependencies.append(package)
            except Exception:
                pass
        
        # Check for pyproject.toml
        pyproject_file = source_dir / 'pyproject.toml'
        if pyproject_file.exists():
            try:
                content = pyproject_file.read_text(encoding='utf-8')
                # Simple regex to find dependencies
                dep_pattern = r'dependencies\s*=\s*\[(.*?)\]'
                match = re.search(dep_pattern, content, re.DOTALL)
                if match:
                    deps_str = match.group(1)
                    for line in deps_str.split(','):
                        line = line.strip().strip('"\'')
                        if line and not line.startswith('#'):
                            package = re.split(r'[>=<!=]', line)[0].strip()
                            if package:
                                dependencies.append(package)
            except Exception:
                pass
        
        # Remove duplicates and common packages
        dependencies = list(set(dependencies))
        dependencies = [dep for dep in dependencies if dep not in ['python', 'pip', 'setuptools', 'wheel']]
        
        return dependencies
    
    def _detect_category(self, detected_files: List[DetectedFile], dependencies: List[str]) -> str:
        """Detect the category of the project"""
        # Check dependencies for category hints
        web_packages = {'fastapi', 'flask', 'django', 'starlette', 'uvicorn', 'gunicorn'}
        cli_packages = {'click', 'argparse', 'typer', 'fire'}
        data_packages = {'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'scipy'}
        ml_packages = {'torch', 'tensorflow', 'scikit-learn', 'keras', 'transformers'}
        scraping_packages = {'requests', 'beautifulsoup4', 'scrapy', 'selenium'}
        
        dep_set = set(dep.lower() for dep in dependencies)
        
        if dep_set & web_packages:
            return 'web'
        elif dep_set & cli_packages:
            return 'application'
        elif dep_set & ml_packages:
            return 'machine-learning'
        elif dep_set & data_packages:
            return 'data-science'
        elif dep_set & scraping_packages:
            return 'automation'
        
        # Check file patterns
        has_main = any(f.file_type == 'main' for f in detected_files)
        has_api = any('api' in f.relative_path.lower() for f in detected_files)
        has_cli = any('cli' in f.relative_path.lower() for f in detected_files)
        has_notebooks = any('.ipynb' in f.relative_path for f in detected_files)
        
        if has_api:
            return 'web'
        elif has_cli:
            return 'application'
        elif has_notebooks:
            return 'data-science'
        elif has_main:
            return 'application'
        else:
            return 'custom'
    
    def _create_template_files(self, detected_files: List[DetectedFile], 
                              template_path: Path, source_dir: Path) -> None:
        """Create template files with variable substitution"""
        for file_info in detected_files:
            dest_path = template_path / file_info.relative_path
            
            if file_info.should_template:
                # Create .j2 template file
                dest_path = dest_path.with_suffix(dest_path.suffix + '.j2')
            
            # Create directory structure
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if file_info.should_template and file_info.template_vars:
                # Process file content and add template variables
                try:
                    content = file_info.path.read_text(encoding='utf-8')
                    template_content = self._process_template_content(content, file_info.template_vars)
                    dest_path.write_text(template_content, encoding='utf-8')
                except Exception as e:
                    print(f"Warning: Could not process {file_info.relative_path}: {e}")
                    # Fallback to copying
                    shutil.copy2(file_info.path, dest_path.with_suffix(''))
            else:
                # Copy file as-is
                if file_info.should_template:
                    dest_path = dest_path.with_suffix('')  # Remove .j2 extension
                shutil.copy2(file_info.path, dest_path)
    
    def _process_template_content(self, content: str, template_vars: Set[str]) -> str:
        """Process file content to add Jinja2 template variables"""
        # Replace detected patterns with Jinja2 variables
        for var_name in template_vars:
            if var_name in self.template_vars:
                pattern = self.template_vars[var_name]
                replacement = f'{{{{ {var_name} }}}}'
                content = re.sub(pattern, replacement, content)
        
        return content
    
    def _create_template_config(self, template_path: Path, template_name: str, 
                               description: str, category: str, dependencies: List[str],
                               detected_files: List[DetectedFile]) -> None:
        """Create template.yaml configuration"""
        # Generate file list for template.yaml
        files_to_generate = []
        for file_info in detected_files:
            if file_info.should_template:
                files_to_generate.append({
                    'path': file_info.relative_path,
                    'template': file_info.relative_path + '.j2'
                })
        
        template_config = {
            'metadata': {
                'name': template_name,
                'description': description,
                'category': category,
                'version': '1.0.0',
                'author': 'Directory Generator',
                'tags': [category, 'generated-from-directory'],
                'dependencies': ['uv', 'poetry', 'pdm', 'rye', 'hatch'],
                'features': [template_name],
                'min_python': '3.8',
                'includes_ci': False,
                'includes_docker': False,
                'includes_tests': any(f.file_type == 'test' for f in detected_files)
            },
            'requirements': {
                'dependencies': dependencies,
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
                    "echo '2. {{backend}} run python main.py'"
                ]
            }
        }
        
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
                elif isinstance(value, bool):
                    f.write(f"  {key}: {str(value).lower()}\n")
                else:
                    f.write(f"  {key}: \"{value}\"\n")
            
            f.write("\nrequirements:\n")
            f.write("  dependencies:\n")
            for dep in data['requirements']['dependencies']:
                f.write(f"    - \"{dep}\"\n")
            f.write("  dev_dependencies:\n")
            for dep in data['requirements']['dev_dependencies']:
                f.write(f"    - \"{dep}\"\n")


def generate_template_from_current_directory(template_name: str, 
                                           description: Optional[str] = None) -> str:
    """One-liner to generate template from current directory"""
    generator = DirectoryTemplateGenerator()
    current_dir = Path.cwd()
    
    template_path = generator.generate_from_directory(current_dir, template_name, description)
    
    print(f"\nTemplate '{template_name}' created successfully!")
    print(f"Location: {template_path}")
    print(f"\nTest it with:")
    print(f"  uvstart generate test-{template_name} {template_name}")
    
    return str(template_path)


def demo_directory_template():
    """Demo the directory template generator"""
    print("Directory-to-Template Generator Demo")
    print("=" * 50)
    
    print("This is the ULTIMATE in template creation simplicity:")
    print()
    print("1. Set up your project directory exactly how you want it")
    print("2. Run: uvstart template from-directory my-template-name")
    print("3. Done! Template is created from your directory structure")
    print()
    
    print("The system will:")
    print("- Analyze your directory structure")
    print("- Detect dependencies from requirements.txt/pyproject.toml")
    print("- Identify template variables in your code")
    print("- Generate .j2 template files with proper substitutions")
    print("- Create a complete template.yaml configuration")
    print("- Skip .git, __pycache__, .env, and other common files")
    print()
    
    print("Example:")
    print("$ cd my-awesome-api-project")
    print("$ uvstart template from-directory awesome-api")
    print("Template 'awesome-api' created!")
    print()
    
    print("The template will include all your files, but with smart")
    print("variable substitutions for project names, authors, etc.")


if __name__ == "__main__":
    demo_directory_template() 