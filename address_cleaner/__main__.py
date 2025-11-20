"""
CLI entry point for address_cleaner package.

This allows the package to be run as a module:
  python -m address_cleaner --input file.csv --output cleaned.csv
"""

from .cli import main

if __name__ == '__main__':
    main()
