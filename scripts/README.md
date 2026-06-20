# Scripts

Bash scripts for development, quality gates, and environment setup for nasim.

All scripts can be run from any directory (they locate the project root).

## Scripts

| Script                  | Purpose |
|-------------------------|---------|
| `clean.sh`              | Remove `__pycache__`, `*.egg-info`, build artifacts, linter caches |
| `lint.sh`               | black + isort + ruff + pyright (strict) over `nasim/` and `scripts/` |
| `setup/setup_env.sh`    | Full provisioning (Miniconda, env, deps, VS Code, verify). See `setup/README.md` |

Run `bash scripts/setup/setup_env.sh --help` style (or read the script) for options.
