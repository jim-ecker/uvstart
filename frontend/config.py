"""
Configuration parsing and management for uvstart
Demonstrates Python ecosystem capabilities with YAML, TOML, and JSON support
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Try to import optional dependencies
try:
    import tomllib
    HAS_TOML = True
except ImportError:
    HAS_TOML = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class ProjectConfig:
    """Project configuration structure"""
    name: str
    description: str = ""
    version: str = "0.1.0"
    backend: str = ""
    python_version: str = "3.8"
    dependencies: Optional[List[str]] = None
    dev_dependencies: Optional[List[str]] = None
    features: Optional[List[str]] = None
    template_vars: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.dev_dependencies is None:
            self.dev_dependencies = []
        if self.features is None:
            self.features = []
        if self.template_vars is None:
            self.template_vars = {}


class ConfigParser:
    """Configuration parser supporting multiple formats"""
    
    def __init__(self):
        self.supported_formats = {
            '.json': self._parse_json
        }
        
        if HAS_YAML:
            self.supported_formats['.yaml'] = self._parse_yaml
            self.supported_formats['.yml'] = self._parse_yaml
        
        if HAS_TOML:
            self.supported_formats['.toml'] = self._parse_toml
    
    def parse_file(self, config_path: Path) -> Optional[ProjectConfig]:
        """Parse configuration file based on extension"""
        if not config_path.exists():
            return None
        
        suffix = config_path.suffix.lower()
        parser = self.supported_formats.get(suffix)
        
        if not parser:
            raise ValueError(f"Unsupported config format: {suffix}")
        
        try:
            data = parser(config_path)
            return self._dict_to_config(data)
        except Exception as e:
            raise ValueError(f"Error parsing {config_path}: {e}")
    
    def _parse_yaml(self, path: Path) -> Dict[str, Any]:
        """Parse YAML configuration"""
        if not HAS_YAML:
            raise ValueError("YAML support not available. Install PyYAML: pip install PyYAML")
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _parse_toml(self, path: Path) -> Dict[str, Any]:
        """Parse TOML configuration"""
        if not HAS_TOML:
            raise ValueError("TOML support not available (Python 3.11+ required)")
        with open(path, 'rb') as f:
            return tomllib.load(f)
    
    def _parse_json(self, path: Path) -> Dict[str, Any]:
        """Parse JSON configuration"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _dict_to_config(self, data: Dict[str, Any]) -> ProjectConfig:
        """Convert dictionary to ProjectConfig"""
        # Handle nested uvstart configuration
        uvstart_config = data.get('uvstart', data)
        
        return ProjectConfig(
            name=uvstart_config.get('name', ''),
            description=uvstart_config.get('description', ''),
            version=uvstart_config.get('version', '0.1.0'),
            backend=uvstart_config.get('backend', ''),
            python_version=uvstart_config.get('python_version', '3.8'),
            dependencies=uvstart_config.get('dependencies', []),
            dev_dependencies=uvstart_config.get('dev_dependencies', []),
            features=uvstart_config.get('features', []),
            template_vars=uvstart_config.get('template_vars', {})
        )


class ProjectDetector:
    """Detect existing project configuration"""
    
    def __init__(self):
        self.config_parser = ConfigParser()
        self.config_files = [
            'uvstart.yaml',
            'uvstart.yml', 
            'uvstart.toml',
            'uvstart.json',
            '.uvstart.yaml',
            '.uvstart.yml',
            '.uvstart.toml',
            '.uvstart.json'
        ]
    
    def detect_config(self, project_path: Optional[Path] = None) -> Optional[ProjectConfig]:
        """Detect and parse project configuration"""
        if project_path is None:
            project_path = Path.cwd()
        
        for config_file in self.config_files:
            config_path = project_path / config_file
            if config_path.exists():
                return self.config_parser.parse_file(config_path)
        
        return None
    
    def detect_project_info(self, project_path: Optional[Path] = None) -> Dict[str, Any]:
        """Detect comprehensive project information"""
        if project_path is None:
            project_path = Path.cwd()
        
        info = {
            'path': str(project_path),
            'name': project_path.name,
            'has_pyproject': (project_path / 'pyproject.toml').exists(),
            'has_requirements': (project_path / 'requirements.txt').exists(),
            'has_setup': (project_path / 'setup.py').exists(),
            'has_git': (project_path / '.git').exists(),
            'has_venv': any([
                (project_path / '.venv').exists(),
                (project_path / 'venv').exists(),
                (project_path / '__pypackages__').exists()
            ]),
            'lock_files': [],
            'config_files': []
        }
        
        # Detect lock files
        lock_patterns = [
            'poetry.lock',
            'pdm.lock', 
            'uv.lock',
            'requirements.lock',
            'Pipfile.lock'
        ]
        
        for pattern in lock_patterns:
            if (project_path / pattern).exists():
                info['lock_files'].append(pattern)
        
        # Detect config files
        for config_file in self.config_files:
            if (project_path / config_file).exists():
                info['config_files'].append(config_file)
        
        return info


def create_sample_configs() -> Dict[str, str]:
    """Create sample configuration files in different formats"""
    
    sample_data = {
        'uvstart': {
            'name': 'my-project',
            'description': 'A sample Python project',
            'version': '0.1.0',
            'backend': 'uv',
            'python_version': '3.11',
            'dependencies': [
                'requests',
                'click'
            ],
            'dev_dependencies': [
                'pytest',
                'black',
                'mypy'
            ],
            'features': [
                'cli',
                'web'
            ],
            'template_vars': {
                'author': 'Your Name',
                'email': 'your.email@example.com',
                'license': 'MIT'
            }
        }
    }
    
    configs = {}
    
    # JSON format (always available)
    json_content = json.dumps(sample_data, indent=2)
    configs['uvstart.json'] = json_content
    
    # YAML format (if available)
    if HAS_YAML:
        yaml_content = yaml.dump(sample_data, default_flow_style=False, indent=2)
        configs['uvstart.yaml'] = yaml_content
    
    # TOML format (simplified structure for TOML compatibility)
    toml_content = """[uvstart]
name = "my-project"
description = "A sample Python project"
version = "0.1.0"
backend = "uv"
python_version = "3.11"
dependencies = ["requests", "click"]
dev_dependencies = ["pytest", "black", "mypy"]
features = ["cli", "web"]

[uvstart.template_vars]
author = "Your Name"
email = "your.email@example.com"
license = "MIT"
"""
    configs['uvstart.toml'] = toml_content
    
    return configs


def format_project_info(info: Dict[str, Any]) -> str:
    """Format project information for display"""
    lines = []
    lines.append(f"Project: {info['name']}")
    lines.append(f"Path: {info['path']}")
    
    # File indicators
    indicators = []
    if info['has_pyproject']:
        indicators.append('pyproject.toml')
    if info['has_requirements']:
        indicators.append('requirements.txt')
    if info['has_setup']:
        indicators.append('setup.py')
    if info['has_git']:
        indicators.append('git')
    if info['has_venv']:
        indicators.append('venv')
    
    if indicators:
        lines.append(f"Features: {', '.join(indicators)}")
    
    if info['lock_files']:
        lines.append(f"Lock files: {', '.join(info['lock_files'])}")
    
    if info['config_files']:
        lines.append(f"Config files: {', '.join(info['config_files'])}")
    
    return '\n'.join(lines)


# Example usage and testing
if __name__ == "__main__":
    # Create sample configs
    samples = create_sample_configs()
    print("Sample configuration formats:")
    print("=" * 50)
    
    for filename, content in samples.items():
        print(f"\n{filename}:")
        print("-" * len(filename))
        print(content)
    
    # Test project detection
    detector = ProjectDetector()
    info = detector.detect_project_info()
    print(f"\nCurrent project info:")
    print("-" * 20)
    print(format_project_info(info)) 