"""Module entry point so ``python -m nasim`` runs the CLI.

Example:
    >>> # python -m nasim doctor
"""

from __future__ import annotations

import sys

from nasim.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
