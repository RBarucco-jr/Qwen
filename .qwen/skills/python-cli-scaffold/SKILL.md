---
name: python-cli-scaffold
description: Scaffold a modern Python CLI project with Typer, src layout, pyproject.toml, pytest, and ruff
source: auto-skill
extracted_at: '2026-06-05T23:53:44.448Z'
---

## When to apply

The user wants to create a new Python CLI tool from scratch or needs a standard project layout for a CLI application.

## Project structure

```
project/
├── README.md
├── QWEN.md
├── pyproject.toml
├── .gitignore
├── src/
│   └── <package_name>/
│       ├── __init__.py
│       ├── cli.py              # Typer app + command definitions
│       ├── validators/         # Format-specific validators
│       │   └── __init__.py
│       ├── converters/         # Format-specific converters
│       │   └── __init__.py
│       └── utils/              # Shared utilities
│           └── __init__.py
└── tests/
    ├── __init__.py
    └── test_*.py
```

## pyproject.toml template

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "<project-name>"
version = "0.1.0"
description = "<description>"
requires-python = ">=3.10"
dependencies = [
    "typer>=0.9.0",
    "rich>=13.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "ruff>=0.1.0",
]

[project.scripts]
<cli-command> = "<package_name>.cli:app"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## Key conventions

- **src layout** — code lives in `src/<package_name>/`, never at root
- **Typer for CLI** — use `typer.Typer()` with `@app.command()` decorators; entry point points to the `app` object
- **Type hints mandatory** — all functions must have type annotations (`-> None`, `-> str`, etc.)
- **Rich for output** — use `rich.console.Console()` for colored output and `Panel` for structured messages
- **pytest for tests** — fixtures in `tests/`, test files named `test_*.py`
- **ruff for linting** — selects E, F, I, N, W, UP (errors, flakes, imports, naming, warnings, pyupgrade)
- **Editable install** — `pip install -e ".[dev]"` for development workflow

## .gitignore essentials

```
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/
.pytest_cache/
.coverage
.vscode/
.idea/
```

## CLI module pattern (cli.py)

```python
import typer

app = typer.Typer(
    name="<cli-name>",
    help="<description>",
    add_completion=False,
)

@app.command()
def command_name(
    arg: str = typer.Argument(..., help="..."),
    option: str = typer.Option(None, "--option", "-o", help="..."),
) -> None:
    """Command docstring (shown in --help)."""
    from <package>.submodule import run_function
    run_function(arg, option)

def main() -> None:
    app()

if __name__ == "__main__":
    main()
```

## Initialization order

1. Create directory structure (`src/<package>/`, `tests/`, submodules)
2. Write `pyproject.toml` with dependencies and tool config
3. Write `__init__.py` files (with `__version__` in root)
4. Write `cli.py` with Typer app skeleton
5. Write utility modules (format detectors, loaders, serializers)
6. Write runner modules for each command (validators, converters, etc.)
7. Write initial test file for core utilities
8. Write `.gitignore`
9. Update `README.md` and `QWEN.md` with project specifics
