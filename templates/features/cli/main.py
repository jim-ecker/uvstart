"""CLI application template with modern Python practices."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

__version__ = "0.1.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="A modern CLI application template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --name "World" --count 3
  %(prog)s --verbose --config config.json
  %(prog)s hello --uppercase
        """,
    )
    
    parser.add_argument(
        "--version",
        action="version", 
        version=f"%(prog)s {__version__}",
        help="Show version and exit"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to configuration file"
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND"
    )
    
    # Hello command
    hello_parser = subparsers.add_parser(
        "hello",
        help="Print a greeting message"
    )
    hello_parser.add_argument(
        "--name", "-n",
        default="World",
        help="Name to greet (default: World)"
    )
    hello_parser.add_argument(
        "--count", "-c",
        type=int,
        default=1,
        help="Number of times to greet (default: 1)"
    )
    hello_parser.add_argument(
        "--uppercase", "-u",
        action="store_true",
        help="Make greeting uppercase"
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show application information"
    )
    info_parser.add_argument(
        "--system",
        action="store_true",
        help="Include system information"
    )
    
    return parser


def handle_hello(args: argparse.Namespace) -> int:
    """Handle the hello command."""
    greeting = f"Hello, {args.name}!"
    
    if args.uppercase:
        greeting = greeting.upper()
    
    for i in range(args.count):
        if args.count > 1:
            print(f"{i+1}. {greeting}")
        else:
            print(greeting)
    
    logger.info(f"Greeted {args.name} {args.count} time(s)")
    return 0


def handle_info(args: argparse.Namespace) -> int:
    """Handle the info command."""
    print(f"Application: CLI Template")
    print(f"Version: {__version__}")
    print(f"Python: {sys.version}")
    
    if args.system:
        import platform
        print(f"Platform: {platform.platform()}")
        print(f"Architecture: {platform.architecture()[0]}")
        print(f"Processor: {platform.processor()}")
    
    return 0


def load_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from file."""
    try:
        import json
        with config_path.open() as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        return {}


def main() -> int:
    """Main application entry point."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Load configuration if specified
    config = {}
    if args.config:
        config = load_config(args.config)
        logger.debug(f"Loaded configuration: {config}")
    
    # Handle commands
    try:
        if args.command == "hello":
            return handle_hello(args)
        elif args.command == "info":
            return handle_info(args)
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
