"""Config merger — deep merge multiple configuration files."""

import json
from pathlib import Path

import typer
import yaml
from rich.console import Console

from config_manager.utils.format_detector import detect_format, load_config

console = Console()


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries. Override values take precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _serialize(data: dict, fmt: str) -> str:
    """Serialize a dict to the given format."""
    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    if fmt in ("yaml", "yml"):
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)
    return json.dumps(data, indent=2, ensure_ascii=False)


def run_merge(
    base: str,
    overrides: tuple[str, ...],
    output: str | None = None,
) -> None:
    """Merge base config with override configs."""
    base_file = Path(base)
    if not base_file.exists():
        console.print(f"[red]Error:[/red] File not found: {base}")
        raise typer.Exit(1)

    fmt = detect_format(base_file)
    result = load_config(base_file)

    for override_path in overrides:
        override_file = Path(override_path)
        if not override_file.exists():
            console.print(f"[red]Error:[/red] File not found: {override_path}")
            raise typer.Exit(1)
        result = deep_merge(result, load_config(override_file))

    serialized = _serialize(result, fmt)

    if output:
        Path(output).write_text(serialized, encoding="utf-8")
        console.print(f"[green]✓ Merged[/green] → {output}")
    else:
        console.print(serialized)
