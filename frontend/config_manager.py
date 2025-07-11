#!/usr/bin/env python3
"""
Configuration manager for uvstart
Handles reading and parsing user preferences from config files
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import re


class ConfigManager:
    """Manages uvstart configuration and user preferences"""
    
    def __init__(self):
        self.config_path = Path.home() / ".local" / "uvstart" / "config.yaml"
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        if not self.config_path.exists():
            # Create default config if none exists
            self._config = self._get_default_config()
            return
        
        try:
            # Simple YAML parser (no dependencies!)
            self._config = self._parse_simple_yaml(self.config_path.read_text())
        except Exception as e:
            print(f"Warning: Could not read config file: {e}")
            print("Using default configuration...")
            self._config = self._get_default_config()
    
    def _parse_simple_yaml(self, content: str) -> Dict[str, Any]:
        """Simple YAML parser that handles basic key: value pairs"""
        config = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse key: value pairs
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                # Handle quoted strings
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                config[key] = value
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            'default_backend': 'uv',
            'default_python_version': '3.11',
            'author': 'Developer',
            'email': 'dev@example.com'
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def get_backend(self) -> str:
        """Get default backend"""
        return self.get('default_backend', 'uv')
    
    def get_python_version(self) -> str:
        """Get default Python version"""
        return self.get('default_python_version', '3.11')
    
    def get_author(self) -> str:
        """Get default author name"""
        return self.get('author', 'Developer')
    
    def get_email(self) -> str:
        """Get default email"""
        return self.get('email', 'dev@example.com')
    
    def get_all_defaults(self) -> Dict[str, str]:
        """Get all default values for project creation"""
        return {
            'backend': self.get_backend(),
            'python_version': self.get_python_version(),
            'author': self.get_author(),
            'email': self.get_email()
        }
    
    def is_configured(self) -> bool:
        """Check if configuration file exists"""
        return self.config_path.exists()


# Global config instance
_config_manager = None

def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager 