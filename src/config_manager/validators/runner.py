"""Validation runner — dispatch to format-specific validators."""

from pathlib import Path

import typer
from jsonschema import ValidationError
from jsonschema import validate as json_validate
from rich.console import Console
from rich.panel import Panel

from config_manager.utils.format_detector import load_config

console = Console()


def run_validate(config_path: str, schema_path: str | None = None) -> None:
    """Validate a configuration file.

    If a schema is provided, validates against it.
    Otherwise, performs basic structural validation (parseable, non-empty).
    """
    config_file = Path(config_path)
    if not config_file.exists():
        console.print(f"[red]Error:[/red] File not found: {config_path}")
        raise typer.Exit(1)

    config = load_config(config_file)

    if schema_path:
        schema_file = Path(schema_path)
        if not schema_file.exists():
            console.print(f"[red]Error:[/red] Schema not found: {schema_path}")
            raise typer.Exit(1)

        schema = load_config(schema_file)
        try:
            json_validate(instance=config, schema=schema)
            console.print(Panel(f"[green]✓ Valid[/green] — {config_path}", title="Validation"))
        except ValidationError as e:
            console.print(f"[red]✗ Invalid[/red] — {e.message}")
            path_str = ".".join(str(p) for p in e.absolute_path)
            console.print(f"  Path: {path_str}")
            raise typer.Exit(1)
    else:
        console.print(Panel(f"[green]✓ Parseable[/green] — {config_path}", title="Basic Check"))
