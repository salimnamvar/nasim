"""Package entry point — ``python -m nasim <command>``.

Delegates to :func:`nasim.runtime.cli.main` and propagates its exit code so the
bash shim can react to success or failure.
"""

import sys

from nasim.runtime.cli import main

if __name__ == "__main__":
    sys.exit(main())
