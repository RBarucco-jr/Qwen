"""Main CLI entry point."""

import typer

app = typer.Typer(
    name="config-manager",
    help="Validate, convert, merge and template configuration files.",
    add_completion=False,
)


@app.command()
def validate(
    config: str = typer.Argument(..., help="Path to configuration file"),
    schema: str = typer.Option(None, "--schema", "-s", help="Path to JSON schema file"),
) -> None:
    """Validate a configuration file against a schema."""
    from config_manager.validators.runner import run_validate

    run_validate(config, schema)


@app.command()
def convert(
    source: str = typer.Argument(..., help="Path to source config file"),
    to: str = typer.Option(..., "--to", "-t", help="Target format (json, yaml, toml, ini, env)"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (default: stdout)"),
) -> None:
    """Convert a configuration file to another format."""
    from config_manager.converters.runner import run_convert

    run_convert(source, to, output)


@app.command()
def merge(
    base: str = typer.Argument(..., help="Path to base configuration file"),
    overrides: list[str] = typer.Argument(None, help="Override configuration files"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (default: stdout)"),
) -> None:
    """Merge multiple configuration files (later files override earlier ones)."""
    from config_manager.utils.merger import run_merge

    run_merge(base, tuple(overrides or []), output)


@app.command()
def template(
    template_file: str = typer.Argument(..., help="Path to template file"),
    env_file: str = typer.Option(None, "--env", "-e", help="Path to .env file"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (default: stdout)"),
) -> None:
    """Apply environment variable substitution to a template file."""
    from config_manager.utils.templater import run_template

    run_template(template_file, env_file, output)


@app.command()
def diff(
    file_a: str = typer.Argument(..., help="First configuration file"),
    file_b: str = typer.Argument(..., help="Second configuration file"),
) -> None:
    """Show differences between two configuration files."""
    from config_manager.utils.differ import run_diff

    run_diff(file_a, file_b)


def main() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
