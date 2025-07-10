"""
Research Template Generator for uvstart
Specialized for experiment replication and scientific reproducibility

Features:
- Captures complete experimental environments
- Preserves data pipelines and analysis workflows  
- Extracts experimental parameters and configurations
- Generates reproducible research templates
- Handles scientific computing dependencies
"""

import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from directory_template import DirectoryTemplateGenerator, DetectedFile


@dataclass
class ResearchConfig:
    """Configuration for research experiments"""
    experiment_name: str
    hypothesis: Optional[str] = None
    methodology: Optional[str] = None
    datasets: List[str] = None
    parameters: Dict[str, Any] = None
    random_seeds: List[int] = None
    environment_files: List[str] = None
    
    def __post_init__(self):
        if self.datasets is None:
            self.datasets = []
        if self.parameters is None:
            self.parameters = {}
        if self.random_seeds is None:
            self.random_seeds = []
        if self.environment_files is None:
            self.environment_files = []


class ResearchTemplateGenerator(DirectoryTemplateGenerator):
    """Enhanced template generator for research reproducibility"""
    
    def __init__(self):
        super().__init__()
        
        # Research-specific patterns to ignore
        self.ignore_patterns.update({
            'data/',
            'datasets/',
            'results/',
            'outputs/',
            'logs/',
            'checkpoints/',
            'models/',
            '.wandb/',
            'mlruns/',
            'tensorboard_logs/',
            '*.pkl',
            '*.joblib',
            '*.h5',
            '*.ckpt',
            '*.pth',
            '*.model',
            '*.csv',
            '*.parquet',
            '*.hdf5'
        })
        
        # Research-specific template variables
        self.template_vars.update({
            'experiment_name': r'(?i)experiment[-_]?name|exp[-_]?name',
            'dataset_name': r'(?i)dataset[-_]?name|data[-_]?name',
            'model_name': r'(?i)model[-_]?name|arch[-_]?name',
            'random_seed': r'(?i)seed|random[-_]?state',
            'epochs': r'(?i)epochs|iterations|steps',
            'learning_rate': r'(?i)lr|learning[-_]?rate',
            'batch_size': r'(?i)batch[-_]?size',
        })
        
        # Research file patterns
        self.research_patterns = {
            'config': r'.*config.*\.(json|yaml|yml|toml|ini|cfg)',
            'notebook': r'.*\.(ipynb)',
            'script': r'.*(train|test|eval|experiment|analysis).*\.py',
            'requirements': r'(requirements|environment|conda|pipfile).*\.(txt|yml|yaml|lock)',
            'data_script': r'.*(data|dataset|preprocess|etl).*\.py',
            'model': r'.*(model|network|arch).*\.py',
            'utils': r'.*(utils|helpers|tools).*\.py',
            'readme': r'readme.*\.(md|rst|txt)',
            'paper': r'.*(paper|manuscript|article).*\.(tex|md|pdf)',
            'results': r'.*(results|metrics|evaluation|benchmark).*\.(json|csv|txt)',
        }
        
        # Scientific computing dependencies
        self.scientific_packages = {
            # Core scientific computing
            'numpy', 'scipy', 'pandas', 'matplotlib', 'seaborn', 'plotly',
            
            # Machine learning
            'scikit-learn', 'sklearn', 'xgboost', 'lightgbm', 'catboost',
            
            # Deep learning
            'torch', 'torchvision', 'tensorflow', 'keras', 'jax', 'flax',
            'transformers', 'datasets', 'accelerate', 'lightning', 'pytorch-lightning',
            
            # Experiment tracking
            'wandb', 'mlflow', 'tensorboard', 'neptune', 'comet-ml',
            
            # Data processing
            'dask', 'polars', 'pyarrow', 'h5py', 'zarr', 'xarray',
            
            # Statistics & analysis
            'statsmodels', 'pymc3', 'pymc', 'arviz', 'pingouin',
            
            # Visualization
            'bokeh', 'altair', 'holoviews', 'datashader', 'plotnine',
            
            # Jupyter & notebooks
            'jupyter', 'jupyterlab', 'ipywidgets', 'papermill', 'nbconvert',
            
            # Utils
            'tqdm', 'click', 'hydra-core', 'omegaconf', 'python-dotenv'
        }
    
    def generate_research_template(self, source_dir: Path, template_name: str,
                                 description: Optional[str] = None,
                                 preserve_data_structure: bool = False) -> Path:
        """Generate research template with enhanced reproducibility features"""
        
        print("Analyzing research project...")
        research_config = self._analyze_research_project(source_dir)
        
        print(f"Experiment: {research_config.experiment_name}")
        if research_config.hypothesis:
            print(f"Hypothesis: {research_config.hypothesis}")
        if research_config.datasets:
            print(f"Datasets: {', '.join(research_config.datasets)}")
        if research_config.parameters:
            print(f"Parameters: {len(research_config.parameters)} detected")
        
        # Use parent method but with research enhancements
        template_path = self.generate_from_directory(source_dir, template_name, description)
        
        # Add research-specific enhancements
        self._add_research_metadata(template_path, research_config, preserve_data_structure)
        self._create_replication_guide(template_path, research_config)
        
        return template_path
    
    def _analyze_research_project(self, source_dir: Path) -> ResearchConfig:
        """Analyze project to extract research-specific information"""
        
        experiment_name = source_dir.name
        hypothesis = None
        methodology = None
        datasets = []
        parameters = {}
        random_seeds = []
        environment_files = []
        
        # Scan for configuration files
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                relative_path = file_path.relative_to(source_dir)
                
                # Extract information from different file types
                if self._matches_pattern(file, 'config'):
                    params = self._extract_config_parameters(file_path)
                    parameters.update(params)
                    
                elif self._matches_pattern(file, 'notebook'):
                    info = self._extract_notebook_info(file_path)
                    if info.get('hypothesis'):
                        hypothesis = info['hypothesis']
                    if info.get('datasets'):
                        datasets.extend(info['datasets'])
                    parameters.update(info.get('parameters', {}))
                    
                elif self._matches_pattern(file, 'script'):
                    params = self._extract_script_parameters(file_path)
                    parameters.update(params)
                    seeds = self._extract_random_seeds(file_path)
                    random_seeds.extend(seeds)
                    
                elif self._matches_pattern(file, 'requirements'):
                    environment_files.append(str(relative_path))
                    
                elif self._matches_pattern(file, 'readme'):
                    readme_info = self._extract_readme_info(file_path)
                    if readme_info.get('hypothesis'):
                        hypothesis = readme_info['hypothesis']
                    if readme_info.get('methodology'):
                        methodology = readme_info['methodology']
        
        # Detect datasets from directory structure
        for item in source_dir.iterdir():
            if item.is_dir() and item.name.lower() in ['data', 'datasets', 'dataset']:
                for data_item in item.iterdir():
                    if data_item.is_file() or data_item.is_dir():
                        datasets.append(data_item.name)
        
        return ResearchConfig(
            experiment_name=experiment_name,
            hypothesis=hypothesis,
            methodology=methodology,
            datasets=list(set(datasets)),  # Remove duplicates
            parameters=parameters,
            random_seeds=list(set(random_seeds)),
            environment_files=environment_files
        )
    
    def _matches_pattern(self, filename: str, pattern_type: str) -> bool:
        """Check if filename matches a research pattern"""
        if pattern_type not in self.research_patterns:
            return False
        
        pattern = self.research_patterns[pattern_type]
        return bool(re.match(pattern, filename, re.IGNORECASE))
    
    def _extract_config_parameters(self, file_path: Path) -> Dict[str, Any]:
        """Extract parameters from configuration files"""
        parameters = {}
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            if file_path.suffix.lower() in ['.json']:
                data = json.loads(content)
                parameters = self._flatten_dict(data)
                
            elif file_path.suffix.lower() in ['.yml', '.yaml'] and HAS_YAML:
                data = yaml.safe_load(content)
                if data:
                    parameters = self._flatten_dict(data)
                    
            elif file_path.suffix.lower() in ['.toml']:
                # Simple TOML parsing
                for line in content.splitlines():
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.split('=', 1)
                        parameters[key.strip()] = value.strip().strip('"\'')
                        
        except Exception:
            # If parsing fails, try to extract key-value pairs with regex
            key_value_pattern = r'(\w+)\s*[=:]\s*([^\n,]+)'
            matches = re.findall(key_value_pattern, content)
            for key, value in matches:
                parameters[key.strip()] = value.strip().strip('"\'')
        
        return parameters
    
    def _extract_notebook_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract information from Jupyter notebooks"""
        info = {'parameters': {}, 'datasets': []}
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Look for hypothesis in markdown cells
            hypothesis_patterns = [
                r'(?i)hypothesis[:\s]*(.+)',
                r'(?i)research question[:\s]*(.+)',
                r'(?i)objective[:\s]*(.+)'
            ]
            
            for pattern in hypothesis_patterns:
                match = re.search(pattern, content)
                if match:
                    info['hypothesis'] = match.group(1).strip()
                    break
            
            # Look for parameter assignments
            param_pattern = r'(\w+)\s*=\s*([^\n]+)'
            matches = re.findall(param_pattern, content)
            for key, value in matches:
                if any(keyword in key.lower() for keyword in ['lr', 'epoch', 'batch', 'seed', 'rate']):
                    info['parameters'][key] = value.strip()
            
            # Look for dataset references
            dataset_patterns = [
                r'(?i)load.*dataset.*["\']([^"\']+)["\']',
                r'(?i)read_csv.*["\']([^"\']+)["\']',
                r'(?i)dataset.*["\']([^"\']+)["\']'
            ]
            
            for pattern in dataset_patterns:
                matches = re.findall(pattern, content)
                info['datasets'].extend(matches)
                
        except Exception:
            pass
        
        return info
    
    def _extract_script_parameters(self, file_path: Path) -> Dict[str, Any]:
        """Extract parameters from Python scripts"""
        parameters = {}
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Look for argparse arguments
            arg_pattern = r'add_argument.*["\']--(\w+)["\'].*default\s*=\s*([^,)]+)'
            matches = re.findall(arg_pattern, content)
            for key, value in matches:
                parameters[key] = value.strip()
            
            # Look for variable assignments
            var_pattern = r'^(\w+)\s*=\s*([^\n#]+)'
            matches = re.findall(var_pattern, content, re.MULTILINE)
            for key, value in matches:
                if any(keyword in key.lower() for keyword in ['lr', 'epoch', 'batch', 'seed', 'rate']):
                    parameters[key] = value.strip()
                    
        except Exception:
            pass
        
        return parameters
    
    def _extract_random_seeds(self, file_path: Path) -> List[int]:
        """Extract random seeds from files"""
        seeds = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Look for seed assignments
            seed_patterns = [
                r'(?i)seed\s*=\s*(\d+)',
                r'(?i)random_state\s*=\s*(\d+)',
                r'(?i)set_seed\s*\(\s*(\d+)\s*\)',
                r'(?i)torch\.manual_seed\s*\(\s*(\d+)\s*\)',
                r'(?i)np\.random\.seed\s*\(\s*(\d+)\s*\)'
            ]
            
            for pattern in seed_patterns:
                matches = re.findall(pattern, content)
                seeds.extend([int(seed) for seed in matches])
                
        except Exception:
            pass
        
        return seeds
    
    def _extract_readme_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract research information from README files"""
        info = {}
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Look for hypothesis/research question
            hypothesis_patterns = [
                r'(?i)## hypothesis\s*\n(.+?)(?:\n##|\n\n|\Z)',
                r'(?i)hypothesis[:\s]*(.+)',
                r'(?i)research question[:\s]*(.+)'
            ]
            
            for pattern in hypothesis_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    info['hypothesis'] = match.group(1).strip()
                    break
            
            # Look for methodology
            methodology_patterns = [
                r'(?i)## methodology\s*\n(.+?)(?:\n##|\n\n|\Z)',
                r'(?i)## method\s*\n(.+?)(?:\n##|\n\n|\Z)',
                r'(?i)methodology[:\s]*(.+)'
            ]
            
            for pattern in methodology_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    info['methodology'] = match.group(1).strip()
                    break
                    
        except Exception:
            pass
        
        return info
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for key, value in d.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
        return dict(items)
    
    def _detect_category(self, detected_files: List[DetectedFile], dependencies: List[str]) -> str:
        """Enhanced category detection for research projects"""
        dep_set = set(dep.lower() for dep in dependencies)
        
        # Check for research-specific patterns
        if dep_set & {'torch', 'tensorflow', 'keras', 'jax'}:
            if dep_set & {'transformers', 'datasets'}:
                return 'nlp-research'
            elif dep_set & {'torchvision', 'opencv-python', 'pillow'}:
                return 'computer-vision'
            else:
                return 'deep-learning'
        
        elif dep_set & {'scikit-learn', 'sklearn', 'xgboost', 'lightgbm'}:
            return 'machine-learning'
        
        elif dep_set & {'pandas', 'numpy', 'scipy', 'matplotlib'}:
            if any('.ipynb' in f.relative_path for f in detected_files):
                return 'data-analysis'
            else:
                return 'computational-science'
        
        elif dep_set & {'statsmodels', 'pymc3', 'pymc', 'arviz'}:
            return 'statistical-analysis'
        
        elif any('.tex' in f.relative_path for f in detected_files):
            return 'research-paper'
        
        # Check file patterns
        has_notebooks = any('.ipynb' in f.relative_path for f in detected_files)
        has_training = any('train' in f.relative_path.lower() for f in detected_files)
        has_experiments = any('experiment' in f.relative_path.lower() for f in detected_files)
        
        if has_experiments or has_training:
            return 'experimental-research'
        elif has_notebooks:
            return 'exploratory-analysis'
        else:
            return 'research'
    
    def _add_research_metadata(self, template_path: Path, config: ResearchConfig,
                             preserve_data_structure: bool) -> None:
        """Add research-specific metadata to template"""
        
        # Load existing template.yaml
        template_yaml = template_path / 'template.yaml'
        if template_yaml.exists():
            if HAS_YAML:
                with open(template_yaml, 'r', encoding='utf-8') as f:
                    template_config = yaml.safe_load(f)
            else:
                # Fallback parsing
                template_config = {'metadata': {}, 'requirements': {}, 'files': {}}
        else:
            template_config = {'metadata': {}, 'requirements': {}, 'files': {}}
        
        # Add research metadata
        research_metadata = {
            'research': {
                'experiment_name': config.experiment_name,
                'hypothesis': config.hypothesis,
                'methodology': config.methodology,
                'datasets': config.datasets,
                'parameters': config.parameters,
                'random_seeds': config.random_seeds,
                'environment_files': config.environment_files,
                'reproducible': True,
                'preserve_data_structure': preserve_data_structure
            }
        }
        
        template_config['metadata'].update(research_metadata)
        
        # Add research-specific tags
        existing_tags = template_config['metadata'].get('tags', [])
        research_tags = ['research', 'reproducible', 'experiment']
        template_config['metadata']['tags'] = list(set(existing_tags + research_tags))
        
        # Save updated template.yaml
        if HAS_YAML:
            with open(template_yaml, 'w', encoding='utf-8') as f:
                yaml.dump(template_config, f, default_flow_style=False, sort_keys=False)
    
    def _create_replication_guide(self, template_path: Path, config: ResearchConfig) -> None:
        """Create a replication guide for the research template"""
        
        guide_content = f"""# Experiment Replication Guide

## Experiment: {config.experiment_name}

This template was generated from a research project to ensure complete reproducibility.

### Quick Start

1. **Generate project from this template:**
   ```bash
   uvstart generate my-experiment {template_path.name}
   cd my-experiment
   ```

2. **Set up environment:**
   ```bash
   # Install dependencies
   {{{{ backend }}}} sync
   
   # If using conda environment file:
   # conda env create -f environment.yml
   ```

3. **Run experiment:**
   ```bash
   {{{{ backend }}}} run python main.py  # or your main script
   ```

### Research Details

"""
        
        if config.hypothesis:
            guide_content += f"""
**Hypothesis:** {config.hypothesis}
"""
        
        if config.methodology:
            guide_content += f"""
**Methodology:** {config.methodology}
"""
        
        if config.datasets:
            guide_content += f"""
### Datasets Required

"""
            for dataset in config.datasets:
                guide_content += f"- {dataset}\n"
            
            guide_content += """
**Note:** Original datasets are not included in this template. You need to:
1. Obtain the required datasets
2. Place them in the appropriate directories
3. Update data paths in configuration files if needed
"""
        
        if config.parameters:
            guide_content += f"""
### Key Parameters

The following parameters were detected in the original experiment:

"""
            for key, value in config.parameters.items():
                guide_content += f"- **{key}:** `{value}`\n"
        
        if config.random_seeds:
            guide_content += f"""
### Reproducibility

For exact reproduction, use these random seeds:
"""
            for seed in config.random_seeds:
                guide_content += f"- `{seed}`\n"
        
        guide_content += """
### Environment Files

The following environment/requirements files were preserved:
"""
        
        for env_file in config.environment_files:
            guide_content += f"- {env_file}\n"
        
        guide_content += """
### Directory Structure

This template preserves the original project structure while making it reusable.
Files containing hard-coded values have been templated with variables.

### Customization

Edit the following files to adapt the experiment:
- Configuration files for parameters
- Data loading scripts for different datasets  
- Template variables in generated files

### Citation

If you use this experimental setup, please cite the original research work.
"""
        
        # Write replication guide
        guide_path = template_path / 'REPLICATION.md.j2'
        guide_path.write_text(guide_content, encoding='utf-8')


def generate_research_template_from_directory(template_name: str, 
                                            description: Optional[str] = None,
                                            preserve_data_structure: bool = False) -> str:
    """Generate research template from current directory with enhanced features"""
    
    generator = ResearchTemplateGenerator()
    current_dir = Path.cwd()
    
    template_path = generator.generate_research_template(
        current_dir, template_name, description, preserve_data_structure
    )
    
    print(f"\nResearch template '{template_name}' created successfully!")
    print(f"Location: {template_path}")
    print(f"\nReplication guide created: {template_path}/REPLICATION.md.j2")
    print(f"\nTest the template:")
    print(f"  uvstart generate test-{template_name} {template_name}")
    
    return str(template_path)


def demo_research_template():
    """Demo the research template generator"""
    print("Research Template Generator Demo")
    print("=" * 50)
    
    print("Perfect for EXPERIMENT REPLICATION and REPRODUCIBLE RESEARCH!")
    print()
    
    print("What it extracts automatically:")
    print("- Experimental parameters and configurations")
    print("- Dataset requirements and data pipeline")  
    print("- Random seeds for reproducibility")
    print("- Environment and dependency specifications")
    print("- Research hypothesis and methodology")
    print("- Jupyter notebooks and analysis scripts")
    print()
    
    print("Usage:")
    print("# Set up your experiment exactly as you want")
    print("# Then generate a replicable template:")
    print("uvstart template research my-experiment")
    print()
    
    print("Creates:")
    print("- Complete project template")
    print("- REPLICATION.md guide with instructions")
    print("- Parameter extraction and templating")
    print("- Environment preservation")
    print("- Research metadata in template.yaml")
    print()
    
    print("Perfect for:")
    print("- Sharing experimental setups")
    print("- Reproducing research results")
    print("- Creating experiment variations")
    print("- Archiving research methodologies")
    print("- Collaborative research projects")


if __name__ == "__main__":
    demo_research_template() 