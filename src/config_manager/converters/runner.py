"""Conversion runner — dispatch to format-specific converters."""

import json
from pathlib import Path

import toml
import typer
import yaml
from rich.console import Console

from config_manager.utils.format_detector import load_config

console = Console()

SUPPORTED_FORMATS = {"json", "yaml", "yml", "toml", "ini", "env"}


def _serialize(data: dict, fmt: str) -> str:
    """Serialize a dict to the target format."""
    fmt = fmt.lower()
    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    if fmt in ("yaml", "yml"):
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)
    if fmt == "toml":
        return toml.dumps(data)
    if fmt in ("ini", "env"):
        raise NotImplementedError(f"Serialization to {fmt} is not yet implemented")
    raise ValueError(f"Unsupported format: {fmt}")


def run_convert(source: str, target_fmt: str, output: str | None = None) -> None:
    """Convert a configuration file to another format."""
    source_file = Path(source)
    if not source_file.exists():
        console.print(f"[red]Error:[/red] File not found: {source}")
        raise typer.Exit(1)

    if target_fmt.lower() not in SUPPORTED_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_FORMATS))
        console.print(
            f"[red]Error:[/red] Unsupported format '{target_fmt}'."
            f" Supported: {supported}"
        )
        raise typer.Exit(1)

    data = load_config(source_file)
    result = _serialize(data, target_fmt)

    if output:
        Path(output).write_text(result, encoding="utf-8")
        console.print(f"[green]✓ Converted[/green] {source} → {output} ({target_fmt})")
    else:
        console.print(result)
