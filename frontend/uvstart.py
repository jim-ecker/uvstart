#!/usr/bin/env python3
"""
uvstart - Python project initializer with backend abstraction
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

# Import our advanced modules
from config import ProjectDetector, ConfigParser, format_project_info
from templates import ProjectGenerator, TemplateContext
from easy_templates import EasyTemplateCreator, quick_template
from template_manager import IntegratedTemplateManager
from directory_template import DirectoryTemplateGenerator, generate_template_from_current_directory
from research_templates import ResearchTemplateGenerator, generate_research_template_from_directory


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
    """Generate new project using template system"""
    # Create template context
    context = TemplateContext(
        project_name=args.name,
        description=args.description or f"A Python project: {args.name}",
        version=args.version,
        author=args.author,
        email=args.email,
        backend=args.backend,
        features=args.features or []
    )
    
    # Generate project structure
    generator = ProjectGenerator()
    files = generator.generate_project_structure(context)
    
    # Create project directory
    project_dir = Path(args.output) / args.name
    if project_dir.exists() and not args.force:
        print(f"Error: Directory {project_dir} already exists. Use --force to overwrite.", file=sys.stderr)
        return 1
    
    try:
        project_dir.mkdir(parents=True, exist_ok=args.force)
        
        # Write all files
        created_files = []
        for file_path, content in files.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(file_path)
        
        print(f"Project generated successfully in {project_dir}")
        print(f"Created {len(created_files)} files:")
        for file_path in sorted(created_files):
            print(f"  {file_path}")
        
        print(f"\nNext steps:")
        print(f"  cd {args.name}")
        print(f"  {args.backend} sync")
        
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
    """Initialize a new Python project (migrated from shell script)"""
    import shutil
    
    # Initialize validator
    validator = InitValidator()
    
    print("uvstart - Initializing Python project")
    print("=" * 40)
    
    # Validate all inputs
    valid = True
    valid &= validator.validate_python_version(args.python_version)
    valid &= validator.validate_backend(args.backend)
    valid &= validator.validate_features(args.features)
    valid &= validator.validate_directory(args.path)
    valid &= validator.validate_git(args.no_git)
    
    # Print any issues
    validator.print_issues()
    
    if not valid:
        print("\nInitialization failed due to validation errors.")
        return 1
    
    # Determine project name
    if not args.project_name:
        args.project_name = os.path.basename(os.path.abspath(args.path))
    
    print(f"\nProject configuration:")
    print(f"  Name: {args.project_name}")
    print(f"  Python: {args.python_version}")
    print(f"  Backend: {args.backend}")
    print(f"  Features: {', '.join(args.features) if args.features else 'none'}")
    print(f"  Path: {os.path.abspath(args.path)}")
    print(f"  Git: {'disabled' if args.no_git else 'enabled'}")
    
    # Generate project using existing generate functionality
    try:
        original_cwd = os.getcwd()
        os.chdir(args.path)
        
        # Create a mock args object for generate_project
        from types import SimpleNamespace
        generate_args = SimpleNamespace(
            name=args.project_name,
            description=f"A Python project: {args.project_name}",
            version="0.1.0",
            author="Your Name",
            email="your.email@example.com",
            backend=args.backend,
            features=args.features,
            output=".",
            force=True  # We already validated the directory
        )
        
        result = generate_project(generate_args)
        if result != 0:
            return result
        
        # Change to the new project directory
        os.chdir(args.project_name)
        
        # Initialize git if requested
        if not args.no_git and shutil.which("git"):
            try:
                subprocess.run(["git", "init"], check=True, capture_output=True)
                subprocess.run(["git", "add", "."], check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", f"Initial commit for {args.project_name}"], 
                             check=True, capture_output=True)
                print("Git repository initialized")
            except subprocess.CalledProcessError as e:
                print(f"Warning: Git initialization failed: {e}")
        
        os.chdir(original_cwd)
        
        print(f"\nProject '{args.project_name}' initialized successfully!")
        print(f"Next steps:")
        print(f"  cd {args.project_name}")
        print(f"  {args.backend} sync")
        if args.features:
            print(f"  # Explore the generated {', '.join(args.features)} features")
        
        return 0
        
    except Exception as e:
        print(f"Error during project generation: {e}")
        return 1


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
            
            # Check if uvstart executable exists
            uvstart_exec = script_path / "uvstart"
            if uvstart_exec.exists() and os.access(uvstart_exec, os.X_OK):
                print(f"SUCCESS: uvstart executable: {uvstart_exec}")
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
                                print(f"   {line.split('=', 1)[1].strip('\"\\n')}")
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
    detector = ProjectDetector()
    
    # Basic project info
    info = detector.detect_project_info(Path(args.path))
    print("Project Analysis")
    print("=" * 50)
    print(format_project_info(info))
    
    # Configuration detection
    config = detector.detect_config(Path(args.path))
    if config:
        print(f"\nConfiguration found:")
        print(f"  Backend: {config.backend}")
        print(f"  Python: {config.python_version}")
        print(f"  Features: {', '.join(config.features or [])}")
        print(f"  Dependencies: {len(config.dependencies or [])} packages")
        print(f"  Dev Dependencies: {len(config.dev_dependencies or [])} packages")
    else:
        print(f"\nNo uvstart configuration found")
    
    # Backend detection via C++ engine
    try:
        engine = UVStartEngine(args.path)
        backend_info = format_backend_info(engine)
        print(f"\n{backend_info}")
    except Exception as e:
        print(f"\nEngine error: {e}", file=sys.stderr)
    
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all commands and options"""
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
        help="Force specific backend (uv, poetry, pdm, rye, hatch)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show backend information")
    
    # Analyze command (new advanced feature)
    analyze_parser = subparsers.add_parser("analyze", help="Analyze project with Python ecosystem capabilities")
    
    # Generate command (new advanced feature)
    generate_parser = subparsers.add_parser("generate", help="Generate new project from templates")
    generate_parser.add_argument("name", help="Project name")
    generate_parser.add_argument("--description", help="Project description")
    generate_parser.add_argument("--version", default="0.1.0", help="Project version")
    generate_parser.add_argument("--author", default="Your Name", help="Author name")
    generate_parser.add_argument("--email", default="your.email@example.com", help="Author email")
    generate_parser.add_argument("--backend", default="uv", choices=["uv", "poetry", "pdm"], help="Backend to use")
    generate_parser.add_argument("--features", nargs="*", choices=["cli", "web", "notebook", "pytorch"], help="Features to include")
    generate_parser.add_argument("--output", default=".", help="Output directory")
    generate_parser.add_argument("--force", action="store_true", help="Overwrite existing directory")
    
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
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new Python project")
    init_parser.add_argument("path", help="Project path")
    init_parser.add_argument("--project-name", help="Project name (defaults to path basename)")
    init_parser.add_argument("--python-version", default="3.11", help="Python version to use (e.g., 3.11, 3.12)")
    init_parser.add_argument("--backend", default="uv", choices=["uv", "poetry", "pdm"], help="Backend to use")
    init_parser.add_argument("--features", nargs="*", choices=["cli", "web", "notebook", "pytorch"], help="Features to include")
    init_parser.add_argument("--no-git", action="store_true", help="Do not initialize git repository")
    
    # Doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Check system health and uvstart installation")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Check for and apply uvstart updates")
    update_parser.add_argument("--check", action="store_true", help="Only check for updates, don't apply")
    update_parser.add_argument("--force", action="store_true", help="Force update even if already up to date")
    update_parser.add_argument("--backup", action="store_true", help="Create a backup of the current installation before updating")
    
    # Template management commands (EASY!)
    template_parser = subparsers.add_parser("template", help="Easy template creation and management")
    template_subparsers = template_parser.add_subparsers(dest="template_action", help="Template actions")
    
    # Create new template interactively
    template_new_parser = template_subparsers.add_parser("new", help="Create a new template (interactive wizard)")
    
    # Quick template creation with presets
    template_quick_parser = template_subparsers.add_parser("quick", help="Create template quickly with presets")
    template_quick_parser.add_argument("name", help="Template name")
    template_quick_parser.add_argument("type", nargs="?", default="simple", 
                                      help="Template type: api, cli-tool, data-app, web-scraper, bot, simple")
    template_quick_parser.add_argument("--description", help="Custom description")
    
    # List template presets
    template_presets_parser = template_subparsers.add_parser("presets", help="List available template presets")
    
    # List templates  
    template_list_parser = template_subparsers.add_parser("list", help="List all available templates")
    
    # Template info
    template_info_parser = template_subparsers.add_parser("info", help="Show detailed template information")
    template_info_parser.add_argument("template", help="Template name")
    
    # Generate template from current directory (ULTIMATE SIMPLICITY!)
    template_from_dir_parser = template_subparsers.add_parser("from-directory", help="Generate template from current directory")
    template_from_dir_parser.add_argument("name", help="Template name")
    template_from_dir_parser.add_argument("--description", help="Template description")
    
    # Research template generation (EXPERIMENT REPLICATION!)
    template_research_parser = template_subparsers.add_parser("research", help="Generate research template for experiment replication")
    template_research_parser.add_argument("name", help="Template name")
    template_research_parser.add_argument("--description", help="Template description")
    template_research_parser.add_argument("--preserve-data", action="store_true", help="Preserve data directory structure")
    
    return parser


def template_command(args) -> int:
    """Handle template management commands"""
    if not hasattr(args, 'template_action') or not args.template_action:
        print("Error: No template action specified", file=sys.stderr)
        return 1
    
    try:
        if args.template_action == "new":
            # Interactive template creation
            creator = EasyTemplateCreator()
            template_name = creator.create_template_interactive()
            print(f"\nTemplate '{template_name}' created successfully!")
            print(f"Test it with: ./uvstart generate test-{template_name} {template_name}")
            return 0
        
        elif args.template_action == "quick":
            # Quick template creation
            description = getattr(args, 'description', None)
            try:
                template_path = quick_template(args.name, args.type)
                print(f"Quick template '{args.name}' created!")
                print(f"Test it with: ./uvstart generate test-{args.name} {args.name}")
                return 0
            except Exception as e:
                print(f"Error creating template: {e}", file=sys.stderr)
                return 1
        
        elif args.template_action == "from-directory":
            # Generate template from current directory (ULTIMATE SIMPLICITY!)
            try:
                description = getattr(args, 'description', None)
                template_path = generate_template_from_current_directory(args.name, description)
                return 0
            except Exception as e:
                print(f"Error creating template from directory: {e}", file=sys.stderr)
                return 1
        
        elif args.template_action == "research":
            # Generate research template for experiment replication
            try:
                description = getattr(args, 'description', None)
                preserve_data = getattr(args, 'preserve_data', False)
                
                # Use research template generator
                generator = ResearchTemplateGenerator()
                current_dir = Path.cwd()
                template_path = generator.generate_research_template(
                    current_dir, args.name, description, preserve_data
                )
                
                print(f"\nResearch template '{args.name}' created successfully!")
                print(f"Location: {template_path}")
                print(f"Replication guide: {template_path}/REPLICATION.md.j2")
                print(f"\nTest: uvstart generate test-{args.name} {args.name}")
                return 0
            except Exception as e:
                print(f"Error creating research template: {e}", file=sys.stderr)
                return 1
        
        elif args.template_action == "presets":
            # List available presets
            creator = EasyTemplateCreator()
            print("Available Template Presets:")
            print("=" * 40)
            for name, preset in creator.template_presets.items():
                print(f"  {name:12} - {preset['description']}")
                print(f"               Category: {preset['category']}")
                if preset['dependencies']:
                    print(f"               Dependencies: {', '.join(preset['dependencies'])}")
                print()
            
            print("Usage:")
            print("  ./uvstart template quick my-api api")
            print("  ./uvstart template quick my-tool cli-tool")
            print()
            print("OR generate from your current directory:")
            print("  ./uvstart template from-directory my-template")
            return 0
        
        elif args.template_action == "list":
            # List all templates
            try:
                manager = IntegratedTemplateManager()
                templates = manager.list_available_templates()
                
                print("Available Templates:")
                print("=" * 50)
                
                # Group by type
                by_type = {}
                for template in templates:
                    if template.type not in by_type:
                        by_type[template.type] = []
                    by_type[template.type].append(template)
                
                for template_type, template_list in by_type.items():
                    print(f"\n{template_type.upper()} Templates:")
                    for template in template_list:
                        print(f"  {template.name:15} - {template.description}")
                
                print(f"\nTotal: {len(templates)} templates")
                return 0
            except Exception as e:
                print(f"Error listing templates: {e}", file=sys.stderr)
                return 1
        
        elif args.template_action == "info":
            # Show template info
            try:
                manager = IntegratedTemplateManager()
                info = manager.get_template_info(args.template)
                
                if not info:
                    print(f"Template '{args.template}' not found", file=sys.stderr)
                    return 1
                
                print(f"Template: {info['name']}")
                print("=" * 50)
                print(f"Type:        {info['type']}")
                print(f"Description: {info['description']}")
                print(f"Category:    {info['category']}")
                print(f"Features:    {', '.join(info['features'])}")
                
                if 'version' in info:
                    print(f"Version:     {info['version']}")
                if 'author' in info:
                    print(f"Author:      {info['author']}")
                if 'path' in info and info['path']:
                    print(f"Path:        {info['path']}")
                
                return 0
            except Exception as e:
                print(f"Error getting template info: {e}", file=sys.stderr)
                return 1
        
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