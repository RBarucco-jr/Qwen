"""Config differ — show differences between two configuration files."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from config_manager.utils.format_detector import load_config

console = Console()


def _flatten(data: dict, prefix: str = "") -> dict[str, str]:
    """Flatten a nested dict into dot-notation keys."""
    result = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(_flatten(value, full_key))
        else:
            result[full_key] = repr(value)
    return result


def run_diff(file_a: str, file_b: str) -> None:
    """Show differences between two configuration files."""
    path_a = Path(file_a)
    path_b = Path(file_b)

    if not path_a.exists():
        console.print(f"[red]Error:[/red] File not found: {file_a}")
        raise typer.Exit(1)
    if not path_b.exists():
        console.print(f"[red]Error:[/red] File not found: {file_b}")
        raise typer.Exit(1)

    flat_a = _flatten(load_config(path_a))
    flat_b = _flatten(load_config(path_b))

    all_keys = sorted(set(flat_a.keys()) | set(flat_b.keys()))
    diffs = []

    for key in all_keys:
        in_a = key in flat_a
        in_b = key in flat_b

        if in_a and in_b and flat_a[key] != flat_b[key]:
            changed = (
                f"[yellow]~ {key}[/yellow]\n"
                f"    [red]- {flat_a[key]}[/red]\n"
                f"    [green]+ {flat_b[key]}[/green]"
            )
            diffs.append(changed)
        elif in_a and not in_b:
            diffs.append(f"[red]- {key}[/red] = {flat_a[key]}")
        elif in_b and not in_a:
            diffs.append(f"[green]+ {key}[/green] = {flat_b[key]}")

    if diffs:
        console.print(
            Panel("\n".join(diffs), title=f"Diff: {file_a} vs {file_b}")
        )
    else:
        console.print("[green]✓ No differences[/green]")
