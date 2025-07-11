"""
Integrated Template Manager for uvstart
Combines existing simple templates with enhanced YAML-based templates and user customization
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import shutil
from datetime import datetime

# Import existing template system
from templates import (
    SimpleTemplateEngine, 
    ProjectGenerator, 
    TemplateContext
)

# Import enhanced template system
try:
    from enhanced_templates import (
        EnhancedTemplateEngine, 
        YAMLTemplateLoader, 
        TemplateMetadata,
        HAS_YAML,
        HAS_JINJA2
    )
    from user_templates import UserTemplateManager
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    print("Enhanced template features not available (missing dependencies)")


@dataclass
class TemplateSource:
    """Represents a template source"""
    name: str
    type: str  # 'system', 'user', 'builtin'
    path: Optional[Path] = None
    description: str = ""
    category: str = "custom"
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []


class IntegratedTemplateManager:
    """Unified template management system"""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        
        # Initialize engines
        self.simple_engine = SimpleTemplateEngine()
        self.project_generator = ProjectGenerator(self.simple_engine)
        
        # Initialize enhanced features if available
        if ENHANCED_AVAILABLE:
            self.enhanced_engine = EnhancedTemplateEngine(use_jinja2=True)
            self.yaml_loader = YAMLTemplateLoader(self.templates_dir)
            self.user_manager = UserTemplateManager()
        else:
            self.enhanced_engine = None
            self.yaml_loader = None
            self.user_manager = None
    
    def list_available_templates(self) -> List[TemplateSource]:
        """List all available templates from all sources"""
        templates = []
        
        # Built-in simple templates (always available)
        builtin_templates = [
            TemplateSource(
                name="simple",
                type="builtin",
                description="Simple Python project with basic structure",
                category="basic",
                features=["python", "testing"]
            ),
            TemplateSource(
                name="cli",
                type="builtin", 
                description="Command-line application with argparse",
                category="application",
                features=["cli", "argparse"]
            ),
            TemplateSource(
                name="web",
                type="builtin",
                description="Web application with FastAPI",
                category="web",
                features=["web", "fastapi"]
            ),
            TemplateSource(
                name="notebook",
                type="builtin",
                description="Data science project with Jupyter notebooks",
                category="data-science",
                features=["notebook", "jupyter", "pandas"]
            )
        ]
        templates.extend(builtin_templates)
        
        # Enhanced YAML templates
        if self.yaml_loader:
            try:
                # Check for feature templates
                features_dir = self.templates_dir / "features"
                if features_dir.exists():
                    for template_dir in features_dir.iterdir():
                        if template_dir.is_dir():
                            try:
                                config = self.yaml_loader.load_template_config(template_dir.name)
                                metadata = config.get('metadata', {})
                                templates.append(TemplateSource(
                                    name=template_dir.name,
                                    type="system",
                                    path=template_dir,
                                    description=metadata.get('description', ''),
                                    category=metadata.get('category', 'custom'),
                                    features=metadata.get('features', [])
                                ))
                            except Exception as e:
                                print(f"Warning: Could not load template {template_dir.name}: {e}")
                
                # Check for base templates
                base_dir = self.templates_dir / "base"
                if base_dir.exists():
                    for template_dir in base_dir.iterdir():
                        if template_dir.is_dir():
                            try:
                                config = self.yaml_loader.load_template_config(template_dir.name)
                                metadata = config.get('metadata', {})
                                templates.append(TemplateSource(
                                    name=template_dir.name,
                                    type="system",
                                    path=template_dir,
                                    description=metadata.get('description', ''),
                                    category=metadata.get('category', 'base'),
                                    features=metadata.get('features', [])
                                ))
                            except Exception as e:
                                print(f"Warning: Could not load base template {template_dir.name}: {e}")
            except Exception as e:
                print(f"Warning: Could not scan system templates: {e}")
        
        # User templates
        if self.user_manager:
            try:
                user_templates = self.user_manager.list_user_templates()
                for template in user_templates:
                    templates.append(TemplateSource(
                        name=template.name,
                        type="user",
                        path=template.path,
                        description=template.description,
                        category=template.category,
                        features=[]  # Could extract from template config
                    ))
            except Exception as e:
                print(f"Warning: Could not load user templates: {e}")
        
        return templates
    
    def generate_project(self, template_name: str, context: TemplateContext, 
                        output_dir: Path) -> bool:
        """Generate a project using the specified template"""
        # Find template
        templates = self.list_available_templates()
        template = next((t for t in templates if t.name == template_name), None)
        
        if not template:
            print(f"Template '{template_name}' not found")
            return False
        
        try:
            if template.type == "builtin":
                return self._generate_builtin_project(template_name, context, output_dir)
            elif template.type in ["system", "user"] and self.enhanced_engine:
                return self._generate_enhanced_project(template_name, context, output_dir)
            else:
                print(f"Cannot generate project with template type: {template.type}")
                return False
        except Exception as e:
            print(f"Error generating project: {e}")
            return False
    
    def _generate_builtin_project(self, template_name: str, context: TemplateContext, 
                                 output_dir: Path) -> bool:
        """Generate project using built-in simple templates"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate project files using the existing system
        project_files = self.project_generator.generate_project_structure(context)
        
        for file_path, content in project_files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"Generated '{template_name}' project at {output_dir}")
        return True
    
    def _generate_enhanced_project(self, template_name: str, context: TemplateContext, 
                                  output_dir: Path) -> bool:
        """Generate project using enhanced YAML templates"""
        if not self.enhanced_engine or not self.yaml_loader:
            return False
        
        try:
            # Load template configuration
            config = self.yaml_loader.load_template_config(template_name)
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert context to dictionary and add template-specific variables
            context_dict = context.to_dict()
            
            # Add additional context from template metadata
            metadata = config.get('metadata', {})
            context_dict.update({
                'template_name': template_name,
                'template_description': metadata.get('description', ''),
                'template_version': metadata.get('version', '1.0.0'),
                'template_author': metadata.get('author', ''),
                'package_name': context.project_name.replace('-', '_'),
                'project_name_title': context.project_name.replace('-', ' ').title(),
            })
            
            # Process files from template configuration
            files_config = config.get('files', {})
            
            # Handle file generation
            if 'generate' in files_config:
                for file_config in files_config['generate']:
                    self._generate_file_from_config(
                        file_config, context_dict, output_dir, template_name
                    )
            
            # Handle file copying
            if 'copy' in files_config:
                self._copy_files_from_config(
                    files_config['copy'], context_dict, output_dir, template_name
                )
            
            # Execute post-generation hooks
            hooks = config.get('hooks', {})
            if 'post_generate' in hooks:
                for hook in hooks['post_generate']:
                    # Replace template variables in hook commands
                    processed_hook = hook
                    for key, value in context_dict.items():
                        processed_hook = processed_hook.replace(f'{{{{{key}}}}}', str(value))
                    
                    # Execute the hook command
                    if processed_hook.startswith('echo '):
                        # Handle echo commands specially - just print the message
                        message = processed_hook[5:].strip().strip("'\"")
                        print(message)
                    else:
                        # For other commands, you could execute them with subprocess
                        print(f"Hook: {processed_hook}")
            
            # Add template metadata for experiment tracking
            metadata_file = output_dir / ".uvstart-template"
            with open(metadata_file, 'w') as f:
                f.write(f"{template_name}\n")
                f.write(f"Generated on: {datetime.now().isoformat()}\n")
                f.write(f"Template type: user\n")
            
            print(f"Generated '{template_name}' project at {output_dir}")
            return True
            
        except Exception as e:
            print(f"Error generating enhanced project: {e}")
            return False
    
    def _generate_file_from_config(self, file_config: Dict[str, Any], context: Dict[str, Any], 
                                  output_dir: Path, template_name: str) -> None:
        """Generate a file from template configuration"""
        file_path = file_config.get('path', '')
        
        # Replace template variables in path
        for key, value in context.items():
            file_path = file_path.replace(f'{{{{{key}}}}}', str(value))
        
        target_file = output_dir / file_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        if 'template' in file_config:
            # Generate from template file
            template_file = file_config['template']
            template_path = self._find_template_file(template_name, template_file)
            
            if template_path and template_path.exists():
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                    
                    # Replace template variables
                    for key, value in context.items():
                        template_content = template_content.replace(f'{{{{{key}}}}}', str(value))
                    
                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write(template_content)
                        
                except Exception as e:
                    print(f"Warning: Could not process template {template_file}: {e}")
            else:
                print(f"Warning: Template file not found: {template_file}")
                
        elif 'source' in file_config:
            # Copy from source file
            source_file = file_config['source']
            source_path = self._find_template_file(template_name, source_file)
            
            if source_path and source_path.exists():
                try:
                    shutil.copy2(source_path, target_file)
                except Exception as e:
                    print(f"Warning: Could not copy source file {source_file}: {e}")
            else:
                print(f"Warning: Source file not found: {source_file}")
                
        elif 'content' in file_config:
            # Generate with static content
            content = file_config['content']
            
            # Replace template variables in content
            for key, value in context.items():
                content = content.replace(f'{{{{{key}}}}}', str(value))
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _find_template_file(self, template_name: str, template_file: str) -> Optional[Path]:
        """Find a template file in the template directories"""
        search_paths = [
            self.templates_dir / "features" / template_name / template_file,
            self.templates_dir / "base" / template_name / template_file,
        ]
        
        # Also check user templates if available
        if self.user_manager:
            user_dir = self.user_manager.user_templates_dir / "templates"
            search_paths.extend([
                user_dir / "features" / template_name / template_file,
                user_dir / "base" / template_name / template_file,
            ])
        
        for path in search_paths:
            if path.exists():
                return path
        
        return None
    
    def _copy_files_from_config(self, copy_config: List[str], context: Dict[str, Any], 
                               output_dir: Path, template_name: str) -> None:
        """Copy files based on copy configuration"""
        # Implementation for copying files with glob patterns
        # This would handle patterns like ['**/*', '!*.template']
        pass
    
    def create_user_template(self, name: str, description: str, 
                           category: str = "custom") -> bool:
        """Create a new user template"""
        if not self.user_manager:
            print("User template management not available")
            return False
        
        try:
            self.user_manager.create_template(name, description, category)
            print(f"User template '{name}' created successfully")
            return True
        except Exception as e:
            print(f"Error creating user template: {e}")
            return False
    
    def delete_user_template(self, name: str) -> bool:
        """Delete a user template"""
        if not self.user_manager:
            print("User template management not available")
            return False
        
        try:
            success = self.user_manager.delete_template(name)
            if success:
                print(f"User template '{name}' deleted successfully")
            return success
        except Exception as e:
            print(f"Error deleting user template: {e}")
            return False
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a template"""
        templates = self.list_available_templates()
        template = next((t for t in templates if t.name == template_name), None)
        
        if not template:
            return None
        
        info = {
            'name': template.name,
            'type': template.type,
            'description': template.description,
            'category': template.category,
            'features': template.features,
            'path': str(template.path) if template.path else None
        }
        
        # Add enhanced info if available
        if template.type in ["system", "user"] and self.yaml_loader:
            try:
                config = self.yaml_loader.load_template_config(template_name)
                metadata = config.get('metadata', {})
                info.update({
                    'version': metadata.get('version', '1.0.0'),
                    'author': metadata.get('author', ''),
                    'tags': metadata.get('tags', []),
                    'min_python': metadata.get('min_python', '3.8'),
                    'includes_ci': metadata.get('includes_ci', False),
                    'includes_docker': metadata.get('includes_docker', False),
                    'includes_tests': metadata.get('includes_tests', True),
                    'requirements': config.get('requirements', {}),
                    'prompts': config.get('prompts', [])
                })
            except Exception as e:
                print(f"Warning: Could not load enhanced template info: {e}")
        
        return info


def demo_integrated_templates():
    """Demonstrate the integrated template system"""
    print("Integrated Template Manager Demo")
    print("=" * 50)
    
    manager = IntegratedTemplateManager()
    
    # List all available templates
    templates = manager.list_available_templates()
    print(f"Found {len(templates)} templates:")
    
    for template in templates:
        print(f"  {template.name} ({template.type}): {template.description}")
    
    # Show enhanced features availability
    if ENHANCED_AVAILABLE:
        print("\nEnhanced features available:")
        print("- YAML template configurations")
        print("- Template inheritance")
        print("- User template management")
        print("- Advanced template engine (Jinja2)")
    else:
        print("\nEnhanced features not available (install PyYAML and Jinja2)")


if __name__ == "__main__":
    demo_integrated_templates() 