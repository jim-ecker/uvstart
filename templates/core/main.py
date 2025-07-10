"""
uvstart project template - Core entry point.

This is the main entry point for your uvstart project.
"""

from __future__ import annotations

__version__ = "0.1.0"


def main() -> None:
    """Main application entry point."""
    print(f"Hello from uvstart! (version {__version__})")
    print("Your project is ready for development!")
    print()
    print("Next steps:")
    print("  1. Install dependencies: make sync")
    print("  2. Run tests: make test")
    print("  3. Apply a template: make template TEMPLATE=cli")
    print("  4. See all commands: make help")


if __name__ == "__main__":
    main()

