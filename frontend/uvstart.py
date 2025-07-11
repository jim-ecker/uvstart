#!/usr/bin/env python3
"""
uvstart - Python project initializer with backend abstraction
Enhanced with isolated environment and configuration management
"""

import argparse
import subprocess
import sys
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Import our modules
from config_manager import get_config
from simple_templates import SimpleTemplateManager, TemplateContext

# Try to import enhanced features (optional)
try:
    from template_commands import TemplateManager
    ENHANCED_TEMPLATES = True
except ImportError:
    ENHANCED_TEMPLATES = False


class UVStartEngine:
    """Wrapper for the C++ engine providing a clean Python interface"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = project_path
        # Find the engine binary
        script_dir = Path(__file__).parent
        self.engine_path = script_dir.parent / "engine" / "uvstart-engine"
        
        if not self.engine_path.exists():
            raise RuntimeError(f"Engine not found at {self.engine_path}")
    
    def _run_engine(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run the C++ engine with given command"""
        full_command = [str(self.engine_path)] + command
        if self.project_path != ".":
            full_command.extend(["--path", self.project_path])
        
        return subprocess.run(
            full_command,
            capture_output=True,
            text=True
        )
    
    def detect_backend(self) -> Optional[str]:
        """Detect the current backend"""
        result = self._run_engine(["detect"])
        if result.returncode == 0:
            backend = result.stdout.strip()
            return backend if backend != "none" else None
        return None
    
    def get_available_backends(self) -> List[str]:
        """Get list of all available backends"""
        result = self._run_engine(["backends"])
        if result.returncode == 0:
            return result.stdout.strip().split("\n")
        return []
    
    def add_package(self, package: str, dev: bool = False, backend: str = "") -> bool:
        """Add a package"""
        command = ["add", package]
        if dev:
            command.append("--dev")
        if backend:
            command.extend(["--backend", backend])
        
        result = self._run_engine(command)
        if result.returncode != 0:
            print(f"Error adding package: {result.stderr}", file=sys.stderr)
            return False
        
        if result.stdout:
            print(result.stdout, end="")
        return True
    
    def remove_package(self, package: str, backend: str = "") -> bool:
        """Remove a package"""
        command = ["remove", package]
        if backend:
            command.extend(["--backend", backend])
        
        result = self._run_engine(command)
        if result.returncode != 0:
            print(f"Error removing package: {result.stderr}", file=sys.stderr)
            return False
        
        if result.stdout:
            print(result.stdout, end="")
        return True
    
    def sync_packages(self, dev: bool = False, backend: str = "") -> bool:
        """Sync packages"""
        command = ["sync"]
        if dev:
            command.append("--dev")
        if backend:
            command.extend(["--backend", backend])
        
        result = self._run_engine(command)
        if result.returncode != 0:
            print(f"Error syncing packages: {result.stderr}", file=sys.stderr)
            return False
        
        if result.stdout:
            print(result.stdout, end="")
        return True
    
    def run_command(self, command: List[str], backend: str = "") -> bool:
        """Run a command"""
        run_cmd = ["run"] + command
        if backend:
            run_cmd.extend(["--backend", backend])
        
        result = self._run_engine(run_cmd)
        if result.returncode != 0:
            print(f"Error running command: {result.stderr}", file=sys.stderr)
            return False
        
        if result.stdout:
            print(result.stdout, end="")
        return True
    
    def list_packages(self, backend: str = "") -> bool:
        """List packages"""
        command = ["list"]
        if backend:
            command.extend(["--backend", backend])
        
        result = self._run_engine(command)
        if result.returncode != 0:
            print(f"Error listing packages: {result.stderr}", file=sys.stderr)
            return False
        
        if result.stdout:
            print(result.stdout, end="")
        return True
    
    def get_version(self, backend: str = "") -> Optional[str]:
        """Get backend version"""
        command = ["version"]
        if backend:
            command.extend(["--backend", backend])
        
        result = self._run_engine(command)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    
    def clean_project(self, backend: str = "") -> bool:
        """Clean project files"""
        command = ["clean"]
        if backend:
            command.extend(["--backend", backend])
        
        result = self._run_engine(command)
        if result.returncode != 0:
            print(f"Error cleaning project: {result.stderr}", file=sys.stderr)
            return False
        
        if result.stdout:
            print(result.stdout, end="")
        return True
    
    def get_install_command(self, backend: str) -> Optional[str]:
        """Get installation command for a backend"""
        result = self._run_engine(["install-cmd", backend])
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    
    def get_clean_files(self, backend: str) -> List[str]:
        """Get list of files that would be cleaned for a backend"""
        result = self._run_engine(["clean-files", backend])
        if result.returncode == 0:
            return result.stdout.strip().split("\n")
        return []


def format_backend_info(engine: UVStartEngine) -> str:
    """Format backend information for display"""
    current = engine.detect_backend()
    available = engine.get_available_backends()
    
    output = []
    output.append("Backend Information:")
    output.append(f"  Current: {current or 'None detected'}")
    output.append(f"  Available: {', '.join(available)}")
    
    if current:
        version = engine.get_version()
        if version:
            output.append(f"  Version: {version}")
    
    return "\n".join(output)


def generate_project(args) -> int:
    """Generate new project using template system (handles both new projects and in-place init)"""
    import shutil
    
    # Get configuration for defaults
    config = get_config()
    
    # Apply configuration defaults if not specified
    backend = getattr(args, 'backend', None) or config.get_backend()
    python_version = getattr(args, 'python_version', None) or config.get_python_version()
    author = getattr(args, 'author', None) or config.get_author()
    email = getattr(args, 'email', None) or config.get_email()
    
    # Determine if this is in-place initialization or new project creation
    is_in_place = args.name_or_path == "." or Path(args.name_or_path).resolve() == Path.cwd().resolve()
    
    # Determine project name and target directory
    if is_in_place:
        # In-place initialization
        if not args.name:
            # Auto-detect project name from directory
            project_name = os.path.basename(os.path.abspath("."))
        else:
            project_name = args.name
        
        target_dir = Path(".")
        output_hint = f"cd {project_name}" if args.name else "# Project initialized in current directory"
    else:
        # New project creation
        project_name = args.name or args.name_or_path
        target_dir = Path(args.output) / project_name
        output_hint = f"cd {project_name}"
    
    # Enhanced validation for in-place initialization
    if is_in_place:
        print("uvstart - Initializing Python project")
        print("=" * 40)
        
        # Initialize validator for comprehensive checks
        validator = InitValidator()
        
        # Validate all inputs
        valid = True
        valid &= validator.validate_python_version(python_version)
        valid &= validator.validate_backend(backend)
        valid &= validator.validate_features(args.features)
        valid &= validator.validate_directory(str(target_dir.resolve()))
        valid &= validator.validate_git(args.no_git)
        
        # Print any issues
        validator.print_issues()
        
        if not valid:
            print("\nInitialization failed due to validation errors.")
            return 1
        
        print(f"\nProject configuration:")
        print(f"  Name: {project_name}")
        print(f"  Python: {python_version}")
        print(f"  Backend: {backend}")
        print(f"  Features: {', '.join(args.features) if args.features else 'none'}")
        print(f"  Path: {target_dir.resolve()}")
        print(f"  Git: {'disabled' if args.no_git else 'enabled'}")
    else:
        # For new projects, show brief summary
        features_str = f" with {', '.join(args.features)}" if args.features else ""
        print(f"Creating {project_name}: backend={backend}, python={python_version}{features_str}")
    
    # Create template context
    context = TemplateContext(
        project_name=project_name,
        description=args.description or f"A Python project: {project_name}",
        version=args.version,
        author=author,
        email=email,
        backend=backend,
        features=args.features or [],
        python_version=python_version
    )
    
    # Generate project structure using integrated template system that supports user templates
    if ENHANCED_TEMPLATES:
        try:
            from template_manager import IntegratedTemplateManager
            manager = IntegratedTemplateManager()
            
            # Check if we have any user template features
            user_features = []
            builtin_features = []
            
            for feature in (args.features or []):
                templates = manager.list_available_templates()
                feature_template = next((t for t in templates if t.name == feature), None)
                
                if feature_template and feature_template.type == "user":
                    user_features.append(feature)
                else:
                    builtin_features.append(feature)
            
            # Generate project files
            if user_features:
                # For user templates, we need to use the enhanced system
                files = {}
                
                # First generate basic project structure
                simple_manager = SimpleTemplateManager()
                basic_files = simple_manager.generate_project_files(context, builtin_features)
                files.update(basic_files)
                
                # Then apply user templates
                for user_feature in user_features:
                    success = manager.generate_project(user_feature, context, target_dir)
                    if not success:
                        print(f"Warning: Failed to apply user template '{user_feature}'")
                
                # For user templates, we've already written files, so set files to empty
                files = {}
            else:
                # Use simple manager for builtin features only
                simple_manager = SimpleTemplateManager()
                files = simple_manager.generate_project_files(context, args.features or [])
        except ImportError as e:
            # Fallback to simple template system
            manager = SimpleTemplateManager()
            files = manager.generate_project_files(context, args.features or [])
    else:
        # Use simple template system as fallback
        manager = SimpleTemplateManager()
        files = manager.generate_project_files(context, args.features or [])
    
    # Handle directory creation and validation
    if not is_in_place:
        # New project creation - check if directory already exists
        if target_dir.exists() and not args.force:
            print(f"Error: Directory {target_dir} already exists. Use --force to overwrite.", file=sys.stderr)
            return 1
        
        try:
            target_dir.mkdir(parents=True, exist_ok=args.force)
        except Exception as e:
            print(f"Error creating directory {target_dir}: {e}", file=sys.stderr)
            return 1
    
    try:
        # Remember original directory for git operations
        original_cwd = os.getcwd()
        
        # Write all files
        created_files = []
        for file_path, content in files.items():
            full_path = target_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(file_path)
        
        # Initialize git if requested and not disabled
        if not args.no_git and shutil.which("git"):
            try:
                # Change to project directory for git operations
                os.chdir(target_dir)
                
                subprocess.run(["git", "init"], check=True, capture_output=True)
                subprocess.run(["git", "add", "."], check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", f"Initial commit for {project_name}"], 
                             check=True, capture_output=True)
                if is_in_place:
                    print("Git repository initialized")
            except subprocess.CalledProcessError as e:
                if is_in_place:
                    print(f"Warning: Git initialization failed: {e}")
            finally:
                os.chdir(original_cwd)
        
        # Success message
        if is_in_place:
            print(f"\nProject '{project_name}' initialized successfully!")
        else:
            print(f" Project created: {target_dir.name}/ ({len(created_files)} files)")
        
        if is_in_place:
            print(f"Created {len(created_files)} files:")
            for file_path in sorted(created_files):
                print(f"  {file_path}")
        
        print(f"Next: {output_hint} && {backend} sync")
        
        return 0
    
    except Exception as e:
        print(f"Error generating project: {e}", file=sys.stderr)
        return 1


class InitValidator:
    """Validation functions for project initialization"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_python_version(self, version: str) -> bool:
        """Validate Python version format and availability"""
        import re, shutil
        
        # Check format (e.g., 3.11, 3.12)
        if not re.match(r'^3\.\d+$', version):
            self.errors.append(f"Invalid Python version format: {version}. Expected format: 3.11, 3.12, etc.")
            return False
        
        # Check if version is supported (3.8+)
        major, minor = map(int, version.split('.'))
        if major < 3 or (major == 3 and minor < 8):
            self.errors.append(f"Python {version} is not supported. Minimum version is 3.8")
            return False
        
        # Try to find the Python executable
        python_cmds = [f"python{version}", f"python3.{minor}", "python3", "python"]
        python_cmd = None
        
        for cmd in python_cmds:
            if shutil.which(cmd):
                try:
                    result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
                    found_version = result.stdout.strip().split()[1]
                    if found_version.startswith(version + "."):
                        python_cmd = cmd
                        break
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, IndexError):
                    continue
        
        if not python_cmd:
            self.errors.append(f"Python {version} not found on system")
            self.errors.append("Please install the required Python version or use a different version")
            # Show available Python versions
            available = []
            for cmd in ["python3", "python"]:
                if shutil.which(cmd):
                    try:
                        result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
                        available.append(result.stdout.strip())
                    except:
                        pass
            if available:
                self.errors.append(f"Available Python versions: {', '.join(available)}")
            return False
        
        print(f"Found Python {version} at: {shutil.which(python_cmd)}")
        return True
    
    def validate_backend(self, backend: str) -> bool:
        """Validate backend availability"""
        import shutil
        
        backend_configs = {
            "pdm": "curl -sSL https://pdm-project.org/install-pdm.py | python3 -",
            "uv": "curl -LsSf https://astral.sh/uv/install.sh | sh",
            "poetry": "curl -sSL https://install.python-poetry.org | python3 -"
        }
        
        if backend not in backend_configs:
            self.errors.append(f"Unknown backend: {backend}")
            self.errors.append(f"Supported backends: {', '.join(backend_configs.keys())}")
            return False
        
        if not shutil.which(backend):
            self.errors.append(f"Backend '{backend}' selected but {backend} is not installed")
            self.errors.append(f"Install {backend}: {backend_configs[backend]}")
            return False
        
        print(f"Found {backend}: {shutil.which(backend)}")
        return True
    
    def validate_features(self, features: Optional[List[str]]) -> bool:
        """Validate requested features"""
        # Get available features dynamically (same as argument parser)
        try:
            from template_commands import TemplateManager
            manager = TemplateManager()
            valid_features = [t.name for t in manager.list_templates()]
            
            # Also check integrated template manager for user templates
            try:
                from template_manager import IntegratedTemplateManager
                integrated_manager = IntegratedTemplateManager()
                user_templates = integrated_manager.list_available_templates()
                user_features = [t.name for t in user_templates if t.type == "user"]
                valid_features.extend(user_features)
            except ImportError:
                pass
        except:
            # Fallback to basic features if template manager fails
            valid_features = ["cli", "web", "notebook", "pytorch"]
        
        if features:
            for feature in features:
                if feature not in valid_features:
                    self.errors.append(f"Unknown feature: {feature}")
                    self.errors.append(f"Available features: {', '.join(valid_features)}")
                    return False
        
        print(f"Requested features: {', '.join(features) if features else 'none'}")
        return True
    
    def validate_directory(self, path: str) -> bool:
        """Validate directory for project creation"""
        # Check if directory is empty or only contains hidden files
        try:
            entries = os.listdir(path)
            visible_entries = [e for e in entries if not e.startswith('.')]
            
            if visible_entries:
                self.warnings.append(f"Directory is not empty: {len(visible_entries)} files found")
                print(f"Directory contains: {', '.join(visible_entries[:5])}")
                if len(visible_entries) > 5:
                    print(f"... and {len(visible_entries) - 5} more files")
                    
                response = input("Continue anyway? [y/N] ").strip().lower()
                if response not in ['y', 'yes']:
                    self.errors.append("Initialization cancelled by user")
                    return False
        except OSError as e:
            self.errors.append(f"Cannot read directory {path}: {e}")
            return False
        
        # Check write permissions
        if not os.access(path, os.W_OK):
            self.errors.append(f"No write permission in directory: {path}")
            return False
        
        return True
    
    def validate_git(self, no_git: bool = False) -> bool:
        """Validate git setup"""
        import shutil
        
        if no_git:
            return True
        
        if not shutil.which("git"):
            self.warnings.append("Git not found. Skipping git initialization")
            return False
        
        # Check if already in a git repo
        try:
            subprocess.run(["git", "rev-parse", "--git-dir"], 
                         capture_output=True, check=True, timeout=5)
            self.warnings.append("Already in a git repository")
            response = input("Initialize anyway? [y/N] ").strip().lower()
            if response not in ['y', 'yes']:
                return False
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass  # Not in a git repo, which is good
        
        print("Git is available")
        return True
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def print_issues(self):
        """Print all errors and warnings"""
        for error in self.errors:
            print(f"ERROR: {error}")
        for warning in self.warnings:
            print(f"WARNING: {warning}")


def init_project(args) -> int:
    """Initialize a new Python project (convenience alias for generate command)"""
    # Convert init arguments to generate arguments
    from types import SimpleNamespace
    
    # Create generate args from init args
    generate_args = SimpleNamespace(
        name_or_path=args.path,  # Use path as name_or_path
        name=args.name,  # Use explicit name if provided
        description=args.description,
        version=args.version,
        author=args.author,
        email=args.email,
        backend=args.backend,
        python_version=args.python_version,
        features=args.features,
        output=".",  # Not used for in-place init
        force=args.force,
        no_git=args.no_git
    )
    
    # Call the enhanced generate function
    return generate_project(generate_args)


class SystemChecker:
    """System health checker for uvstart doctor command"""
    
    def __init__(self):
        self.errors = 0
        self.warnings = 0
    
    def check_command(self, cmd: str, name: str, install_hint: str = "") -> bool:
        """Check if a command is available and get its version"""
        import shutil
        
        if shutil.which(cmd):
            try:
                result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
                # Try to extract version number
                version_line = result.stdout.split('\n')[0] if result.stdout else "unknown"
                # Simple version extraction
                import re
                version_match = re.search(r'[0-9]+\.[0-9]+(?:\.[0-9]+)?', version_line)
                version = version_match.group() if version_match else "unknown"
                
                print(f"SUCCESS: {name}: {version} ({shutil.which(cmd)})")
                return True
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                print(f"WARNING: {name}: found but version check failed")
                self.warnings += 1
                return True
        else:
            print(f"ERROR: {name}: Not found")
            if install_hint:
                print(f"   Install: {install_hint}")
            self.errors += 1
            return False
    
    def check_python_versions(self):
        """Check for Python installations"""
        print("INFO: Checking Python installations...")
        
        found_python = False
        python_cmds = ["python3.13", "python3.12", "python3.11", "python3.10", "python3.9", "python3.8", "python3", "python"]
        
        for py_cmd in python_cmds:
            if shutil.which(py_cmd):
                try:
                    result = subprocess.run([py_cmd, "--version"], capture_output=True, text=True, timeout=5)
                    version = result.stdout.strip().split()[1]
                    major_minor = ".".join(version.split(".")[:2])
                    
                    # Check if version is supported (3.8+)
                    version_parts = version.split(".")
                    major, minor = int(version_parts[0]), int(version_parts[1])
                    
                    if major == 3 and minor >= 8:
                        print(f"SUCCESS: Python {version} ({shutil.which(py_cmd)})")
                        found_python = True
                    elif major == 3 and minor < 8:
                        print(f"WARNING: Python {version} - outdated, recommend 3.8+")
                        self.warnings += 1
                        found_python = True
                    else:
                        print(f"WARNING: Python {version} - unsupported")
                        self.warnings += 1
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, IndexError):
                    continue
        
        if not found_python:
            print("ERROR: No Python 3 installation found")
            print("   Install Python: https://www.python.org/downloads/")
            self.errors += 1
    
    def check_package_managers(self):
        """Check package managers"""
        print("INFO: Checking package managers...")
        
        # Check uv
        if self.check_command("uv", "uv", "curl -LsSf https://astral.sh/uv/install.sh | sh"):
            # Additional check for uv configuration
            try:
                subprocess.run(["uv", "--help"], capture_output=True, check=True, timeout=5)
                print("SUCCESS: uv is properly configured")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print("WARNING: uv found but not properly configured")
                self.warnings += 1
        
        # Check poetry
        self.check_command("poetry", "Poetry", "curl -sSL https://install.python-poetry.org | python3 -")
        
        # Check pip
        pip_cmd = "pip3" if shutil.which("pip3") else "pip"
        if shutil.which(pip_cmd):
            try:
                result = subprocess.run([pip_cmd, "--version"], capture_output=True, text=True, timeout=5)
                version = result.stdout.split()[1] if result.stdout else "unknown"
                print(f"SUCCESS: pip: {version}")
            except:
                print("WARNING: pip found but version check failed")
                self.warnings += 1
        else:
            print("WARNING: pip: Not found (usually comes with Python)")
            self.warnings += 1
    
    def check_development_tools(self):
        """Check development tools"""
        print("INFO: Checking development tools...")
        
        # Essential tools
        self.check_command("git", "Git", "https://git-scm.com/downloads")
        
        # Optional but recommended tools
        if self.check_command("code", "VS Code", "https://code.visualstudio.com/"):
            print("   Recommended VS Code extensions: Python, Pylance, Ruff")
        
        # Other useful tools
        self.check_command("gh", "GitHub CLI", "https://cli.github.com/")
        self.check_command("docker", "Docker", "https://docs.docker.com/get-docker/")
    
    def check_uvstart_installation(self):
        """Check uvstart installation"""
        print("INFO: Checking uvstart installation...")
        
        # Get the script directory
        script_path = Path(__file__).parent.parent
        
        if script_path.exists():
            print(f"SUCCESS: uvstart directory: {script_path}")
            
            # Check if uvstart executable exists (new isolated installation structure)
            uvstart_exec = script_path / "bin" / "uvstart"
            if uvstart_exec.exists() and os.access(uvstart_exec, os.X_OK):
                print(f"SUCCESS: uvstart executable: {uvstart_exec}")
            else:
                # Fallback check for legacy installation
                legacy_exec = script_path / "uvstart"
                if legacy_exec.exists() and os.access(legacy_exec, os.X_OK):
                    print(f"SUCCESS: uvstart executable: {legacy_exec}")
                else:
                    print("ERROR: uvstart executable not found or not executable")
                    self.errors += 1
            
            # Check if it's accessible as a command
            if shutil.which("uvstart"):
                print("SUCCESS: uvstart is in PATH")
            else:
                print("WARNING: uvstart not in PATH")
                print("   Add to PATH or create symlink to make it globally available")
                self.warnings += 1
            
            # Check C++ engine
            engine_path = script_path / "engine" / "uvstart-engine"
            if engine_path.exists():
                print(f"SUCCESS: C++ engine: {engine_path}")
            else:
                print("ERROR: C++ engine not found")
                print("   Run: cd engine && make")
                self.errors += 1
            
            # Check template files
            templates_dir = script_path / "templates"
            if templates_dir.exists():
                print(f"SUCCESS: Templates directory found")
            else:
                print("ERROR: Templates directory not found")
                self.errors += 1
        else:
            print(f"ERROR: uvstart installation not found")
            self.errors += 1
    
    def check_system_info(self):
        """Show system information"""
        print("INFO: System information...")
        
        # Operating system
        import platform
        system = platform.system()
        if system == "Darwin":
            print("SUCCESS: Operating system: macOS")
            try:
                result = subprocess.run(["sw_vers"], capture_output=True, text=True, timeout=5)
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")
            except:
                pass
        elif system == "Linux":
            print("SUCCESS: Operating system: Linux")
            # Try to get distribution info
            try:
                result = subprocess.run(["lsb_release", "-d"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"   {result.stdout.strip()}")
                elif os.path.exists("/etc/os-release"):
                    with open("/etc/os-release") as f:
                        for line in f:
                            if line.startswith("PRETTY_NAME="):
                                # Extract and clean the OS name
                                os_name = line.split('=', 1)[1].strip('"\\n')
                                print(f"   {os_name}")
                                break
            except:
                pass
        else:
            print(f"SUCCESS: Operating system: {system}")
        
        # Shell
        shell = os.environ.get("SHELL", "unknown")
        print(f"SUCCESS: Shell: {shell}")
        
        # Architecture
        arch = platform.machine()
        print(f"SUCCESS: Architecture: {arch}")
        
        # Disk space
        try:
            import shutil as disk_util
            total, used, free = disk_util.disk_usage(".")
            free_gb = free // (1024**3)
            print(f"SUCCESS: Available disk space: {free_gb}GB")
        except:
            print("WARNING: Could not check disk space")
            self.warnings += 1


def doctor_command(args) -> int:
    """System health check (migrated from shell script)"""
    checker = SystemChecker()
    
    print("uvstart Environment Health Check")
    print("=" * 50)
    
    # Run all checks
    checker.check_python_versions()
    print()
    checker.check_package_managers() 
    print()
    checker.check_development_tools()
    print()
    checker.check_uvstart_installation()
    print()
    checker.check_system_info()
    
    # Summary
    print("\n" + "=" * 50)
    print("Health Check Summary:")
    if checker.errors == 0 and checker.warnings == 0:
        print("SUCCESS: All checks passed!")
        return 0
    else:
        if checker.errors > 0:
            print(f"ERRORS: {checker.errors} critical issues found")
        if checker.warnings > 0:
            print(f"WARNINGS: {checker.warnings} non-critical issues found")
        
        if checker.errors > 0:
            print("\nPlease address the errors above before using uvstart.")
            return 1
        else:
            print("\nSystem is functional but has some warnings to consider.")
            return 0


class UpdateManager:
    """Update manager for uvstart self-updating functionality"""
    
    def __init__(self):
        self.install_dir = Path(__file__).parent.parent
    
    def check_installation(self) -> bool:
        """Check if uvstart installation is valid for updating"""
        if not self.install_dir.exists():
            print(f"ERROR: uvstart is not installed in the expected location: {self.install_dir}")
            print("Please install uvstart first using the installer script.")
            return False
        
        git_dir = self.install_dir / ".git"
        if not git_dir.exists():
            print("ERROR: uvstart installation is not a git repository")
            print("Cannot update automatically. Please reinstall uvstart.")
            return False
        
        print(f"SUCCESS: Found uvstart installation at: {self.install_dir}")
        return True
    
    def get_current_version(self) -> str:
        """Get current version info"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                cwd=self.install_dir,
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                current_commit = result.stdout.strip()[:8]
                
                # Get current branch
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.install_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "detached"
                
                return f"{current_branch}@{current_commit}"
            else:
                return "unknown"
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return "unknown"
    
    def get_remote_version(self) -> str:
        """Get remote version info"""
        try:
            # Fetch latest information
            fetch_result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.install_dir,
                capture_output=True,
                timeout=30
            )
            
            if fetch_result.returncode != 0:
                return "unknown"
            
            # Get remote commit
            result = subprocess.run(
                ["git", "rev-parse", "origin/main"],
                cwd=self.install_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                remote_commit = result.stdout.strip()[:8]
                return f"main@{remote_commit}"
            else:
                return "unknown"
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return "unknown"
    
    def check_for_updates(self) -> int:
        """Check if updates are available"""
        print("INFO: Checking for updates...")
        
        # Get current version
        current_version = self.get_current_version()
        print(f"INFO: Current version: {current_version}")
        
        # Fetch latest from remote
        try:
            fetch_result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.install_dir,
                capture_output=True,
                timeout=30
            )
            
            if fetch_result.returncode != 0:
                print("WARNING: Could not fetch from remote repository")
                print("Check your internet connection or repository access")
                return 1
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            print("WARNING: Could not fetch from remote repository")
            print("Check your internet connection or repository access")
            return 1
        
        # Get remote version
        remote_version = self.get_remote_version()
        print(f"INFO: Remote version: {remote_version}")
        
        # Check if update is needed
        try:
            current_commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.install_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            remote_commit_result = subprocess.run(
                ["git", "rev-parse", "origin/main"],
                cwd=self.install_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if (current_commit_result.returncode == 0 and 
                remote_commit_result.returncode == 0 and
                current_commit_result.stdout.strip() == remote_commit_result.stdout.strip()):
                
                print("SUCCESS: uvstart is already up to date!")
                return 2  # Already up to date
            else:
                print("INFO: Update available!")
                
                # Show what's new
                print("\nINFO: Recent changes:")
                try:
                    log_result = subprocess.run(
                        ["git", "log", "--oneline", "--max-count=5", "HEAD..origin/main"],
                        cwd=self.install_dir,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if log_result.returncode == 0 and log_result.stdout:
                        for line in log_result.stdout.strip().split('\n'):
                            print(f"  {line}")
                    else:
                        print("  (Unable to show changes)")
                except:
                    print("  (Unable to show changes)")
                
                return 0  # Update available
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            print("WARNING: Could not compare versions")
            return 1
    
    def create_backup(self) -> str:
        """Create backup of current installation"""
        from datetime import datetime
        backup_name = f"uvstart.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir = self.install_dir.parent / backup_name
        
        print("INFO: Creating backup...")
        
        try:
            # Use cp -r to create backup
            result = subprocess.run(
                ["cp", "-r", str(self.install_dir), str(backup_dir)],
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"SUCCESS: Backup created: {backup_dir}")
                return str(backup_dir)
            else:
                print("ERROR: Failed to create backup")
                return ""
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            print("ERROR: Failed to create backup")
            return ""
    
    def perform_update(self) -> bool:
        """Perform the actual update"""
        print("INFO: Updating uvstart...")
        
        try:
            # Stash any local changes
            diff_result = subprocess.run(
                ["git", "diff", "--quiet"],
                cwd=self.install_dir,
                capture_output=True,
                timeout=10
            )
            
            if diff_result.returncode != 0:  # There are changes
                print("WARNING: Local changes detected, stashing them...")
                stash_result = subprocess.run(
                    ["git", "stash", "push", "-m", f"uvstart update {datetime.now().isoformat()}"],
                    cwd=self.install_dir,
                    capture_output=True,
                    timeout=10
                )
                if stash_result.returncode != 0:
                    print("WARNING: Could not stash local changes")
            
            # Pull latest changes
            pull_result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.install_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if pull_result.returncode == 0:
                print("SUCCESS: Successfully updated to latest version")
            else:
                print("ERROR: Failed to update uvstart")
                print("You may need to resolve conflicts manually")
                if pull_result.stderr:
                    print(f"Error details: {pull_result.stderr}")
                return False
            
            # Make sure the main script is executable
            uvstart_script = self.install_dir / "uvstart"
            # nosemgrep: python.lang.security.audit.insecure-file-permissions.insecure-file-permissions
            os.chmod(uvstart_script, 0o755)
            
            # Rebuild C++ engine if needed
            engine_dir = self.install_dir / "engine"
            if engine_dir.exists():
                print("INFO: Rebuilding C++ engine...")
                make_result = subprocess.run(
                    ["make"],
                    cwd=engine_dir,
                    capture_output=True,
                    timeout=120
                )
                if make_result.returncode == 0:
                    print("SUCCESS: C++ engine rebuilt successfully")
                else:
                    print("WARNING: Failed to rebuild C++ engine")
                    print("You may need to run 'cd engine && make' manually")
            
            return True
            
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            print(f"ERROR: Update failed: {e}")
            return False
    
    def show_post_update_info(self):
        """Show information after successful update"""
        print("\nINFO: Update summary:")
        print(f"  Location: {self.install_dir}")
        print(f"  Version: {self.get_current_version()}")
        
        # Check if uvstart command works
        try:
            version_result = subprocess.run(
                [str(self.install_dir / "uvstart"), "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if version_result.returncode == 0:
                print("SUCCESS: uvstart is working correctly after update")
            else:
                print("WARNING: uvstart may not be working correctly after update")
        except:
            print("WARNING: Could not verify uvstart functionality after update")


def update_command(args) -> int:
    """Update uvstart to latest version (migrated from shell script)"""
    updater = UpdateManager()
    
    print("uvstart Self-Update")
    print("=" * 40)
    
    # Check installation
    if not updater.check_installation():
        return 1
    
    # Handle check-only mode
    if hasattr(args, 'check') and args.check:
        result = updater.check_for_updates()
        if result == 2:
            return 0  # Up to date
        elif result == 0:
            print("\nUse 'uvstart update' to install the update.")
            return 0
        else:
            return 1  # Error checking
    
    # Check for updates
    update_status = updater.check_for_updates()
    
    if update_status == 2:
        # Already up to date
        if hasattr(args, 'force') and args.force:
            print("INFO: Forcing update even though already up to date...")
        else:
            return 0
    elif update_status == 1:
        # Error checking for updates
        if hasattr(args, 'force') and args.force:
            print("WARNING: Forcing update despite check errors...")
        else:
            return 1
    
    # Create backup if requested
    backup_path = ""
    if hasattr(args, 'backup') and args.backup:
        backup_path = updater.create_backup()
        if not backup_path:
            print("ERROR: Backup creation failed. Aborting update.")
            return 1
    
    # Perform update
    if updater.perform_update():
        updater.show_post_update_info()
        if backup_path:
            print(f"\nBackup available at: {backup_path}")
        print("\nUpdate completed successfully!")
        return 0
    else:
        print("\nUpdate failed!")
        if backup_path:
            print(f"Your backup is available at: {backup_path}")
        return 1


def analyze_project(args) -> int:
    """Analyze current project using Python ecosystem capabilities"""
    
    project_path = Path(args.path)
    project_name = project_path.name
    
    print(f"Project: {project_name}")
    print("=" * 60)
    print(f"Path: {project_path.resolve()}")
    
    # Project structure analysis
    print(f"\n PROJECT STRUCTURE")
    structure_info = _analyze_project_structure(project_path)
    for key, value in structure_info.items():
        if isinstance(value, bool):
            status = " Yes" if value else " No"
            print(f"  {key}: {status}")
        elif isinstance(value, list) and value:
            print(f"  {key}: {', '.join(value)}")
        elif value:
            print(f"  {key}: {value}")
    
    # Backend and dependency management
    print(f"\n BACKEND & DEPENDENCIES")
    backend_info = _analyze_backend_info(project_path)
    for key, value in backend_info.items():
        if value:
            print(f"  {key}: {value}")
    
    # Project metadata from pyproject.toml or setup.py
    print(f"\n PROJECT METADATA")
    metadata = _analyze_project_metadata(project_path)
    for key, value in metadata.items():
        if value:
            print(f"  {key}: {value}")
    
    # Git information
    print(f"\n VERSION CONTROL")
    git_info = _analyze_git_info(project_path)
    for key, value in git_info.items():
        if value:
            print(f"  {key}: {value}")
    
    # Development environment
    print(f"\n DEVELOPMENT ENVIRONMENT")
    dev_info = _analyze_dev_environment(project_path)
    for key, value in dev_info.items():
        if isinstance(value, bool):
            status = " Yes" if value else " No"
            print(f"  {key}: {status}")
        elif value:
            print(f"  {key}: {value}")
    
    # Possible uvstart features detection
    print(f"\n DETECTED FEATURES")
    features = _detect_project_features(project_path)
    if features:
        for feature in features:
            print(f"   {feature}")
    else:
        print("   No specific features detected")
    
    # Experiment configuration analysis (new!)
    print(f"\n EXPERIMENT CONFIGURATION")
    experiment_info = _analyze_experiment_config(project_path)
    if experiment_info:
        for key, value in experiment_info.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            elif isinstance(value, list) and value:
                print(f"  {key}: {', '.join(map(str, value))}")
            elif value:
                print(f"  {key}: {value}")
    else:
        print("   No experiment configuration detected")
    
    # Recommendations
    print(f"\n RECOMMENDATIONS")
    recommendations = _generate_recommendations(project_path, structure_info, backend_info, dev_info)
    if recommendations:
        for rec in recommendations:
            print(f"  • {rec}")
    else:
        print("   Project looks well configured!")
    
    return 0


def _analyze_project_structure(project_path: Path) -> Dict[str, Any]:
    """Analyze project file structure"""
    info = {}
    
    # Core Python project files
    info["Has pyproject.toml"] = (project_path / "pyproject.toml").exists()
    info["Has setup.py"] = (project_path / "setup.py").exists()
    info["Has requirements.txt"] = (project_path / "requirements.txt").exists()
    info["Has README"] = any((project_path / f"README{ext}").exists() for ext in [".md", ".rst", ".txt", ""])
    info["Has .gitignore"] = (project_path / ".gitignore").exists()
    
    # Find Python packages/modules
    packages = []
    for item in project_path.iterdir():
        if item.is_dir() and not item.name.startswith('.') and not item.name in ['__pycache__', 'tests', 'docs']:
            if (item / "__init__.py").exists():
                packages.append(item.name)
    info["Python packages"] = packages
    
    # Test directory
    test_dirs = []
    for test_name in ['tests', 'test', 'testing']:
        if (project_path / test_name).exists():
            test_dirs.append(test_name)
    info["Test directories"] = test_dirs
    
    # Documentation
    docs_dirs = []
    for doc_name in ['docs', 'doc', 'documentation']:
        if (project_path / doc_name).exists():
            docs_dirs.append(doc_name)
    info["Documentation"] = docs_dirs
    
    return info


def _analyze_backend_info(project_path: Path) -> Dict[str, str]:
    """Analyze backend and dependency management"""
    info = {}
    
    # Backend detection via C++ engine
    try:
        engine = UVStartEngine(str(project_path))
        backend = engine.detect_backend()
        if backend:
            info["Backend"] = backend
            version = engine.get_version()
            if version:
                info["Backend version"] = version
        else:
            info["Backend"] = "None detected"
    except Exception as e:
        info["Backend"] = f"Error: {e}"
    
    # Lock files detection
    lock_files = []
    lock_patterns = ['uv.lock', 'poetry.lock', 'pdm.lock', 'Pipfile.lock', 'requirements.lock']
    for pattern in lock_patterns:
        if (project_path / pattern).exists():
            lock_files.append(pattern)
    if lock_files:
        info["Lock files"] = ", ".join(lock_files)
    
    # Virtual environment detection
    venv_paths = []
    venv_names = ['.venv', 'venv', '.virtualenv', '__pypackages__']
    for venv_name in venv_names:
        if (project_path / venv_name).exists():
            venv_paths.append(venv_name)
    if venv_paths:
        info["Virtual environment"] = ", ".join(venv_paths)
    
    return info


def _analyze_project_metadata(project_path: Path) -> Dict[str, str]:
    """Extract project metadata from configuration files"""
    info = {}
    
    # Try to parse pyproject.toml
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists():
        try:
            content = pyproject_path.read_text()
            
            # Simple regex-based parsing (avoiding dependencies)
            import re
            
            # Extract name
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match:
                info["Name"] = name_match.group(1)
            
            # Extract version
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                info["Version"] = version_match.group(1)
            
            # Extract description
            desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            if desc_match:
                info["Description"] = desc_match.group(1)
            
            # Extract author
            author_match = re.search(r'authors\s*=\s*\[\s*["\']([^"\']+)["\']', content)
            if author_match:
                info["Author"] = author_match.group(1)
            else:
                author_simple_match = re.search(r'author\s*=\s*["\']([^"\']+)["\']', content)
                if author_simple_match:
                    info["Author"] = author_simple_match.group(1)
            
            # Extract Python requirement
            python_match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
            if python_match:
                info["Python requirement"] = python_match.group(1)
                
        except Exception:
            pass
    
    return info


def _analyze_git_info(project_path: Path) -> Dict[str, str]:
    """Analyze git repository information"""
    info = {}
    
    if not (project_path / ".git").exists():
        info["Git repository"] = " No"
        return info
    
    info["Git repository"] = " Yes"
    
    try:
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            info["Current branch"] = result.stdout.strip()
        
        # Get commit count
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            info["Commits"] = result.stdout.strip()
        
        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            if result.stdout.strip():
                info["Status"] = " Uncommitted changes"
            else:
                info["Status"] = " Clean"
        
        # Get remote info
        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            if lines:
                # Extract first remote URL
                remote_line = lines[0]
                if '\t' in remote_line:
                    remote_url = remote_line.split('\t')[1].split(' ')[0]
                    info["Remote"] = remote_url
                    
    except Exception:
        pass
    
    return info


def _analyze_dev_environment(project_path: Path) -> Dict[str, Any]:
    """Analyze development environment setup"""
    info = {}
    
    # CI/CD files
    ci_files = []
    github_actions = project_path / ".github" / "workflows"
    if github_actions.exists():
        ci_files.append("GitHub Actions")
    
    for ci_file in [".travis.yml", ".circleci", "azure-pipelines.yml", ".gitlab-ci.yml"]:
        if (project_path / ci_file).exists():
            ci_files.append(ci_file.replace(".", "").replace("-", " ").title())
    
    info["CI/CD"] = len(ci_files) > 0
    if ci_files:
        info["CI/CD systems"] = ", ".join(ci_files)
    
    # Development tools config
    dev_configs = []
    dev_tools = {
        ".pre-commit-config.yaml": "pre-commit",
        "pyproject.toml": "tool configs",
        ".flake8": "flake8", 
        ".pylintrc": "pylint",
        "tox.ini": "tox",
        "Dockerfile": "Docker",
        "docker-compose.yml": "Docker Compose",
        ".devcontainer": "Dev Container"
    }
    
    for file_name, tool_name in dev_tools.items():
        if (project_path / file_name).exists():
            dev_configs.append(tool_name)
    
    if dev_configs:
        info["Dev tools"] = ", ".join(dev_configs)
    
    # Check for common Python quality tools in pyproject.toml
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        quality_tools = []
        if "[tool.black]" in content:
            quality_tools.append("black")
        if "[tool.ruff]" in content:
            quality_tools.append("ruff")
        if "[tool.mypy]" in content:
            quality_tools.append("mypy")
        if "[tool.pytest]" in content:
            quality_tools.append("pytest")
        
        if quality_tools:
            info["Code quality tools"] = ", ".join(quality_tools)
    
    return info


def _detect_project_features(project_path: Path) -> List[str]:
    """Detect what uvstart features this project might have used"""
    features = []
    
    # Check for web framework files
    main_py = project_path / "main.py"
    if main_py.exists():
        content = main_py.read_text()
        if "fastapi" in content.lower() or "flask" in content.lower() or "django" in content.lower():
            features.append("web")
    
    # Check for CLI features
    if main_py.exists():
        content = main_py.read_text()
        if "click" in content.lower() or "argparse" in content.lower() or "typer" in content.lower():
            features.append("cli")
    
    # Check for notebook files
    if any(project_path.glob("*.ipynb")):
        features.append("notebook")
    
    # Check for PyTorch/ML files
    for file_path in project_path.rglob("*.py"):
        try:
            content = file_path.read_text()
            if "torch" in content.lower() or "pytorch" in content.lower():
                features.append("pytorch")
                break
        except:
            continue
    
    # Check for microservice indicators
    if (project_path / "Dockerfile").exists() and main_py.exists():
        features.append("microservice")
    
    return list(set(features))  # Remove duplicates


def _analyze_experiment_config(project_path: Path) -> Dict[str, Any]:
    """Analyze for experiment configuration files and parameters."""
    experiment_info = {}
    
    # Check for common experiment file patterns
    experiment_files = [
        "experiment.toml", "experiment.yaml", "experiment.json",
        "params.toml", "params.yaml", "params.json", 
        "config.toml", "config.yaml", "config.json"
    ]
    
    for file_name in experiment_files:
        config_path = project_path / file_name
        if config_path.exists():
            try:
                if file_name.endswith('.toml'):
                    try:
                        import tomllib
                        with open(config_path, 'rb') as f:
                            config_data = tomllib.load(f)
                        experiment_info[f"Config file"] = file_name
                        experiment_info[f"Parameters"] = config_data
                    except ImportError:
                        experiment_info[f"Config file"] = f"{file_name} (tomllib not available)"
                
                elif file_name.endswith(('.yaml', '.yml')):
                    try:
                        import yaml
                        with open(config_path, 'r') as f:
                            config_data = yaml.safe_load(f)
                        experiment_info[f"Config file"] = file_name
                        experiment_info[f"Parameters"] = config_data
                    except ImportError:
                        experiment_info[f"Config file"] = f"{file_name} (yaml not available)"
                
                elif file_name.endswith('.json'):
                    import json
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                    experiment_info[f"Config file"] = file_name
                    experiment_info[f"Parameters"] = config_data
                    
            except Exception as e:
                experiment_info[f"Config file"] = f"{file_name} (error: {e})"
            
            # Only process the first config file found
            break
    
    # Check for experiment-specific files
    experiment_scripts = []
    if (project_path / "train.py").exists():
        experiment_scripts.append("train.py")
    if (project_path / "evaluate.py").exists():
        experiment_scripts.append("evaluate.py")
    if (project_path / "predict.py").exists():
        experiment_scripts.append("predict.py")
    if any(project_path.glob("*.ipynb")):
        notebooks = list(project_path.glob("*.ipynb"))
        experiment_scripts.extend([nb.name for nb in notebooks[:3]])  # Show first 3
    
    if experiment_scripts:
        experiment_info["Experiment scripts"] = experiment_scripts
    
    # Check for experiment-specific directories
    experiment_dirs = []
    common_dirs = ["data", "models", "logs", "outputs", "results", "checkpoints"]
    for dir_name in common_dirs:
        if (project_path / dir_name).exists():
            experiment_dirs.append(dir_name)
    
    if experiment_dirs:
        experiment_info["Experiment directories"] = experiment_dirs
    
    # Look for template origin info (check if this experiment was created from a template)
    template_indicators = []
    
    # Check for uvstart template metadata
    if (project_path / ".uvstart-template").exists():
        try:
            with open(project_path / ".uvstart-template", 'r') as f:
                template_info = f.read().strip()
                template_indicators.append(f"Created from template: {template_info}")
        except:
            template_indicators.append("Created from uvstart template")
    
    # Check for common template files that indicate experiment origin
    template_files = [".template-origin", ".experiment-template", "TEMPLATE_INFO.md"]
    for template_file in template_files:
        if (project_path / template_file).exists():
            template_indicators.append(f"Template metadata: {template_file}")
    
    if template_indicators:
        experiment_info["Template origin"] = template_indicators
    
    return experiment_info


def _generate_recommendations(project_path: Path, structure_info: Dict, backend_info: Dict, dev_info: Dict) -> List[str]:
    """Generate recommendations for improving the project"""
    recommendations = []
    
    # Missing essential files
    if not structure_info.get("Has README"):
        recommendations.append("Add a README.md file to document your project")
    
    if not structure_info.get("Has .gitignore"):
        recommendations.append("Add a .gitignore file for Python projects")
    
    # Backend recommendations
    if backend_info.get("Backend") == "None detected":
        recommendations.append("Consider using a package manager like uv, poetry, or pdm")
    
    if not backend_info.get("Virtual environment"):
        recommendations.append("Set up a virtual environment for isolation")
    
    # Development improvements
    if not dev_info.get("CI/CD"):
        recommendations.append("Set up CI/CD pipeline (GitHub Actions, etc.)")
    
    if not structure_info.get("Test directories"):
        recommendations.append("Add a tests/ directory and write tests")
    
    if not dev_info.get("Code quality tools"):
        recommendations.append("Configure code quality tools (ruff, black, mypy)")
    
    # Git recommendations
    git_info = _analyze_git_info(project_path)
    if git_info.get("Git repository") == " No":
        recommendations.append("Initialize a git repository: git init")
    
    return recommendations


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all commands and options"""
    # Get configuration for defaults
    config = get_config()
    defaults = config.get_all_defaults()
    
    parser = argparse.ArgumentParser(
        prog="uvstart",
        description="Python project initializer with backend abstraction",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--path", "-p",
        help="Project path (default: current directory)",
        default="."
    )
    
    parser.add_argument(
        "--backend", "-b",
        help="Force specific backend (uv, poetry, pdm)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show backend information")
    
    # Analyze command (new advanced feature)
    analyze_parser = subparsers.add_parser("analyze", help="Analyze project with Python ecosystem capabilities")
    
    # Generate command (enhanced to handle both new projects and in-place initialization)
    generate_parser = subparsers.add_parser("generate", help="Generate new project from templates")
    generate_parser.add_argument("name_or_path", help="Project name or path (use '.' for current directory)")
    generate_parser.add_argument("--name", help="Project name (required when using '.' as name_or_path)")
    generate_parser.add_argument("--description", help="Project description")
    generate_parser.add_argument("--version", default="0.1.0", help="Project version")
    generate_parser.add_argument("--author", help=f"Author name (default: {defaults['author']})")
    generate_parser.add_argument("--email", help=f"Author email (default: {defaults['email']})")
    generate_parser.add_argument("--backend", choices=["uv", "poetry", "pdm"], help=f"Backend to use (default: {defaults['backend']})")
    generate_parser.add_argument("--python-version", help=f"Python version (default: {defaults['python_version']})")
    
    # Get available features dynamically
    available_features = ["cli", "web", "notebook", "pytorch"]  # Basic features always available
    if ENHANCED_TEMPLATES:
        try:
            manager = TemplateManager()
            enhanced_features = [t.name for t in manager.list_templates()]
            available_features = enhanced_features
        except:
            pass  # Fall back to basic features
    
    generate_parser.add_argument("--features", nargs="*", choices=available_features, help="Features to include")
    generate_parser.add_argument("--output", default=".", help="Output directory")
    generate_parser.add_argument("--force", action="store_true", help="Overwrite existing directory")
    generate_parser.add_argument("--no-git", action="store_true", help="Do not initialize git repository")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add package")
    add_parser.add_argument("package", help="Package name to add")
    add_parser.add_argument("--dev", action="store_true", help="Add as development dependency")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove package")
    remove_parser.add_argument("package", help="Package name to remove")
    
    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync dependencies")
    sync_parser.add_argument("--dev", action="store_true", help="Include development dependencies")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run command")
    run_parser.add_argument("cmd", nargs="+", help="Command to run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List packages")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show backend version")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean project files")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Show installation command for backend")
    install_parser.add_argument("backend", help="Backend name")
    
    # Init command (convenience alias for generate with in-place behavior)
    init_parser = subparsers.add_parser("init", help="Initialize a new Python project in current directory")
    init_parser.add_argument("path", nargs="?", default=".", help="Project path (default: current directory)")
    init_parser.add_argument("--name", help="Project name (defaults to directory basename)")
    init_parser.add_argument("--python-version", help=f"Python version (default: {defaults['python_version']})")
    init_parser.add_argument("--backend", choices=["uv", "poetry", "pdm"], help=f"Backend to use (default: {defaults['backend']})")
    init_parser.add_argument("--features", nargs="*", choices=available_features, help="Features to include")
    init_parser.add_argument("--no-git", action="store_true", help="Do not initialize git repository")
    init_parser.add_argument("--description", help="Project description")
    init_parser.add_argument("--version", default="0.1.0", help="Project version")
    init_parser.add_argument("--author", help=f"Author name (default: {defaults['author']})")
    init_parser.add_argument("--email", help=f"Author email (default: {defaults['email']})")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    
    # Doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Check system health and uvstart installation")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Check for and apply uvstart updates")
    update_parser.add_argument("--check", action="store_true", help="Only check for updates, don't apply")
    update_parser.add_argument("--force", action="store_true", help="Force update even if already up to date")
    update_parser.add_argument("--backup", action="store_true", help="Create a backup of the current installation before updating")
    
    # Template management commands
    template_parser = subparsers.add_parser("template", help="Template management and creation")
    template_subparsers = template_parser.add_subparsers(dest="template_action", help="Template actions")
    
    # List templates
    template_list_parser = template_subparsers.add_parser("list", help="List all available templates")
    
    # Template info
    template_info_parser = template_subparsers.add_parser("info", help="Show detailed template information")
    template_info_parser.add_argument("template", help="Template name")
    
    # Create template from current directory
    template_from_dir_parser = template_subparsers.add_parser("from-directory", help="Create template from current directory")
    template_from_dir_parser.add_argument("name", help="Template name")
    template_from_dir_parser.add_argument("--description", help="Template description")
    template_from_dir_parser.add_argument("--category", help="Template category")
    template_from_dir_parser.add_argument("--source", help="Source directory (default: current directory)", default=".")
    
    # Create research template
    template_research_parser = template_subparsers.add_parser("research", help="Create research reproducibility template")
    template_research_parser.add_argument("name", help="Template name")
    template_research_parser.add_argument("--description", help="Template description")
    template_research_parser.add_argument("--source", help="Source directory (default: current directory)", default=".")
    
    # Delete template
    template_delete_parser = template_subparsers.add_parser("delete", help="Delete a user template")
    template_delete_parser.add_argument("name", help="Template name to delete")
    
    return parser


def template_command(args) -> int:
    """Handle template management commands"""
    if not hasattr(args, 'template_action') or not args.template_action:
        print("Error: No template action specified", file=sys.stderr)
        print("Available actions: list, info, from-directory, research, delete")
        return 1
    
    try:
        manager = TemplateManager()
        
        if args.template_action == "list":
            templates = manager.list_templates()
            
            if not templates:
                print("No templates found")
                return 0
            
            print("Available Templates:")
            print("=" * 60)
            
            # Group by type
            by_type = {}
            for template in templates:
                if template.type not in by_type:
                    by_type[template.type] = []
                by_type[template.type].append(template)
            
            for template_type, template_list in by_type.items():
                print(f"\n{template_type.upper()} Templates:")
                for template in template_list:
                    features_str = f" [{', '.join(template.features)}]" if template.features else ""
                    print(f"  {template.name:20} - {template.description}{features_str}")
                    print(f"    Category: {template.category}")
            
            print(f"\nTotal: {len(templates)} templates")
            print("\nUsage:")
            print("  uvstart generate my-project --features TEMPLATE_NAME")
            print("  uvstart template info TEMPLATE_NAME")
            return 0
        
        elif args.template_action == "info":
            info = manager.get_template_info(args.template)
            
            if not info:
                print(f"Template '{args.template}' not found", file=sys.stderr)
                return 1
            
            print(f"Template: {info['name']}")
            print("=" * 60)
            print(f"Type:        {info['type']}")
            print(f"Description: {info['description']}")
            print(f"Category:    {info['category']}")
            print(f"Features:    {', '.join(info['features']) if info['features'] else 'None'}")
            print(f"Author:      {info['author']}")
            print(f"Version:     {info['version']}")
            
            if info.get('path'):
                print(f"Path:        {info['path']}")
            
            if info.get('template_variables'):
                print(f"Variables:   {', '.join(info['template_variables'])}")
            
            return 0
        
        elif args.template_action == "from-directory":
            source_path = Path(args.source).resolve()
            
            if not source_path.exists():
                print(f"Error: Source directory '{source_path}' does not exist", file=sys.stderr)
                return 1
            
            if not source_path.is_dir():
                print(f"Error: '{source_path}' is not a directory", file=sys.stderr)
                return 1
            
            success = manager.create_from_directory(
                source_path, 
                args.name, 
                args.description,
                args.category,
                is_research=False
            )
            
            return 0 if success else 1
        
        elif args.template_action == "research":
            source_path = Path(args.source).resolve()
            
            if not source_path.exists():
                print(f"Error: Source directory '{source_path}' does not exist", file=sys.stderr)
                return 1
            
            if not source_path.is_dir():
                print(f"Error: '{source_path}' is not a directory", file=sys.stderr)
                return 1
            
            success = manager.create_from_directory(
                source_path, 
                args.name, 
                args.description,
                category="research",
                is_research=True
            )
            
            return 0 if success else 1
        
        elif args.template_action == "delete":
            success = manager.delete_template(args.name)
            return 0 if success else 1
        
        else:
            print(f"Unknown template action: {args.template_action}", file=sys.stderr)
            return 1
    
    except Exception as e:
        print(f"Template command failed: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle advanced Python-powered commands first
    if args.command == "analyze":
        return analyze_project(args)
    
    elif args.command == "generate":
        return generate_project(args)
    
    elif args.command == "init":
        return init_project(args)
    
    elif args.command == "doctor":
        return doctor_command(args)
    
    elif args.command == "update":
        return update_command(args)
    
    elif args.command == "template":
        return template_command(args)
    
    # Handle C++ engine commands
    try:
        engine = UVStartEngine(args.path)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    if args.command == "info":
        print(format_backend_info(engine))
        return 0
    
    elif args.command == "add":
        success = engine.add_package(
            args.package, 
            dev=args.dev, 
            backend=args.backend or ""
        )
        return 0 if success else 1
    
    elif args.command == "remove":
        success = engine.remove_package(
            args.package, 
            backend=args.backend or ""
        )
        return 0 if success else 1
    
    elif args.command == "sync":
        success = engine.sync_packages(
            dev=args.dev, 
            backend=args.backend or ""
        )
        return 0 if success else 1
    
    elif args.command == "run":
        success = engine.run_command(
            args.cmd, 
            backend=args.backend or ""
        )
        return 0 if success else 1
    
    elif args.command == "list":
        success = engine.list_packages(backend=args.backend or "")
        return 0 if success else 1
    
    elif args.command == "version":
        version = engine.get_version(backend=args.backend or "")
        if version:
            print(version)
            return 0
        else:
            print("Could not get version", file=sys.stderr)
            return 1
    
    elif args.command == "clean":
        success = engine.clean_project(backend=args.backend or "")
        return 0 if success else 1
    
    elif args.command == "install":
        install_cmd = engine.get_install_command(args.backend)
        if install_cmd:
            print(f"To install {args.backend}, run:")
            print(f"  {install_cmd}")
            return 0
        else:
            print(f"Unknown backend: {args.backend}", file=sys.stderr)
            return 1
    
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 