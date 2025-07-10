"""Tests for the CLI application template."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from main import handle_hello, handle_info, load_config, main, setup_parser


class TestSetupParser:
    """Test the argument parser setup."""
    
    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = setup_parser()
        assert parser is not None
        assert parser.description == "A modern CLI application template"
    
    def test_version_argument(self, capsys):
        """Test --version argument."""
        parser = setup_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "0.1.0" in captured.out
    
    def test_verbose_argument(self):
        """Test --verbose argument."""
        parser = setup_parser()
        args = parser.parse_args(["--verbose", "hello"])
        assert args.verbose is True
    
    def test_hello_command_defaults(self):
        """Test hello command with default arguments."""
        parser = setup_parser()
        args = parser.parse_args(["hello"])
        assert args.command == "hello"
        assert args.name == "World"
        assert args.count == 1
        assert args.uppercase is False
    
    def test_hello_command_with_args(self):
        """Test hello command with custom arguments."""
        parser = setup_parser()
        args = parser.parse_args(["hello", "--name", "Alice", "--count", "3", "--uppercase"])
        assert args.command == "hello"
        assert args.name == "Alice"
        assert args.count == 3
        assert args.uppercase is True
    
    def test_info_command(self):
        """Test info command."""
        parser = setup_parser()
        args = parser.parse_args(["info"])
        assert args.command == "info"
        assert args.system is False
    
    def test_info_command_with_system(self):
        """Test info command with system flag."""
        parser = setup_parser()
        args = parser.parse_args(["info", "--system"])
        assert args.command == "info"
        assert args.system is True


class TestHandleHello:
    """Test the hello command handler."""
    
    def test_simple_greeting(self, capsys):
        """Test simple greeting output."""
        from argparse import Namespace
        args = Namespace(name="World", count=1, uppercase=False)
        result = handle_hello(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello, World!" in captured.out
    
    def test_custom_name(self, capsys):
        """Test greeting with custom name."""
        from argparse import Namespace
        args = Namespace(name="Alice", count=1, uppercase=False)
        result = handle_hello(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello, Alice!" in captured.out
    
    def test_multiple_greetings(self, capsys):
        """Test multiple greetings."""
        from argparse import Namespace
        args = Namespace(name="Bob", count=3, uppercase=False)
        result = handle_hello(args)
        
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        assert len(lines) == 3
        assert "1. Hello, Bob!" in lines[0]
        assert "2. Hello, Bob!" in lines[1]
        assert "3. Hello, Bob!" in lines[2]
    
    def test_uppercase_greeting(self, capsys):
        """Test uppercase greeting."""
        from argparse import Namespace
        args = Namespace(name="charlie", count=1, uppercase=True)
        result = handle_hello(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "HELLO, CHARLIE!" in captured.out


class TestHandleInfo:
    """Test the info command handler."""
    
    def test_basic_info(self, capsys):
        """Test basic info output."""
        from argparse import Namespace
        args = Namespace(system=False)
        result = handle_info(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Application: CLI Template" in captured.out
        assert "Version: 0.1.0" in captured.out
        assert "Python:" in captured.out
    
    def test_system_info(self, capsys):
        """Test info with system information."""
        from argparse import Namespace
        args = Namespace(system=True)
        result = handle_info(args)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Application: CLI Template" in captured.out
        assert "Platform:" in captured.out
        assert "Architecture:" in captured.out


class TestLoadConfig:
    """Test configuration loading."""
    
    def test_load_valid_config(self):
        """Test loading valid JSON configuration."""
        config_data = {"key": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            result = load_config(config_path)
            assert result == config_data
        finally:
            config_path.unlink()
    
    def test_load_nonexistent_config(self):
        """Test loading non-existent configuration file."""
        config_path = Path("/nonexistent/config.json")
        result = load_config(config_path)
        assert result == {}
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_path = Path(f.name)
        
        try:
            result = load_config(config_path)
            assert result == {}
        finally:
            config_path.unlink()


class TestMain:
    """Test the main function."""
    
    def test_hello_command_integration(self, capsys):
        """Test full hello command integration."""
        with patch('sys.argv', ['main.py', 'hello', '--name', 'Integration']):
            result = main()
            assert result == 0
            captured = capsys.readouterr()
            assert "Hello, Integration!" in captured.out
    
    def test_info_command_integration(self, capsys):
        """Test full info command integration."""
        with patch('sys.argv', ['main.py', 'info']):
            result = main()
            assert result == 0
            captured = capsys.readouterr()
            assert "Application: CLI Template" in captured.out
    
    def test_no_command_shows_help(self, capsys):
        """Test that no command shows help."""
        with patch('sys.argv', ['main.py']):
            result = main()
            assert result == 1
            captured = capsys.readouterr()
            assert "usage:" in captured.out.lower()
    
    def test_keyboard_interrupt(self):
        """Test keyboard interrupt handling."""
        with patch('sys.argv', ['main.py', 'hello']):
            with patch('main.handle_hello', side_effect=KeyboardInterrupt):
                result = main()
                assert result == 130
    
    def test_general_exception(self):
        """Test general exception handling."""
        with patch('sys.argv', ['main.py', 'hello']):
            with patch('main.handle_hello', side_effect=Exception("Test error")):
                result = main()
                assert result == 1
    
    def test_verbose_logging(self, capsys):
        """Test verbose logging."""
        with patch('sys.argv', ['main.py', '--verbose', 'hello']):
            result = main()
            assert result == 0
            # Verbose mode should be enabled (hard to test logging level directly)


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing."""
    config_data = {"test": True, "debug": False}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = Path(f.name)
    
    yield config_path, config_data
    
    # Cleanup
    if config_path.exists():
        config_path.unlink()


def test_config_integration(temp_config_file, capsys):
    """Test configuration file integration."""
    config_path, config_data = temp_config_file
    
    with patch('sys.argv', ['main.py', '--config', str(config_path), 'hello']):
        result = main()
        assert result == 0 