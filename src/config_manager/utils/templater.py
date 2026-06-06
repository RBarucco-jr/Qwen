"""Config templater — substitute environment variables in template files."""

import os
import re
from pathlib import Path

import typer
from dotenv import dotenv_values
from rich.console import Console

console = Console()

# Pattern: ${VAR_NAME} or $VAR_NAME or {{VAR_NAME}}
TEMPLATE_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)|\{\{([^}]+)\}\}")


def run_template(template_file: str, env_file: str | None, output: str | None) -> None:
    """Apply environment variable substitution to a template file."""
    tpl_path = Path(template_file)
    if not tpl_path.exists():
        console.print(f"[red]Error:[/red] File not found: {template_file}")
        raise typer.Exit(1)

    # Load env vars
    env_vars = dict(os.environ)
    if env_file:
        env_path = Path(env_file)
        if not env_path.exists():
            console.print(f"[red]Error:[/red] .env file not found: {env_file}")
            raise typer.Exit(1)
        env_vars.update(dotenv_values(env_path))

    content = tpl_path.read_text(encoding="utf-8")

    def replacer(match: re.Match) -> str:
        var_name = match.group(1) or match.group(2) or match.group(3)
        return env_vars.get(var_name, match.group(0))

    result = TEMPLATE_PATTERN.sub(replacer, content)

    if output:
        Path(output).write_text(result, encoding="utf-8")
        console.print(f"[green]✓ Template applied[/green] → {output}")
    else:
        console.print(result)
