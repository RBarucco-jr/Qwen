"""Format detection and config loading utilities."""

import json
from pathlib import Path

import toml
import yaml
from dotenv import dotenv_values

FORMAT_EXTENSIONS = {
    "json": {".json"},
    "yaml": {".yaml", ".yml"},
    "toml": {".toml"},
    "ini": {".ini", ".cfg", ".conf"},
    "env": {".env"},
}


def detect_format(file_path: Path) -> str:
    """Detect the configuration format from file extension."""
    suffix = file_path.suffix.lower()
    name = file_path.name.lower()

    # Special case for .env files
    if name == ".env" or name.startswith(".env."):
        return "env"

    for fmt, extensions in FORMAT_EXTENSIONS.items():
        if suffix in extensions:
            return fmt

    raise ValueError(f"Unknown config format for: {file_path}")


def load_config(file_path: Path) -> dict:
    """Load a configuration file and return its contents as a dict."""
    fmt = detect_format(file_path)
    content = file_path.read_text(encoding="utf-8")

    if fmt == "json":
        return json.loads(content)
    if fmt in ("yaml", "yml"):
        result = yaml.safe_load(content)
        return result if isinstance(result, dict) else {}
    if fmt == "toml":
        return toml.loads(content)
    if fmt in ("ini", "cfg", "conf"):
        import configparser

        parser = configparser.ConfigParser()
        parser.read_string(content)
        return {section: dict(parser[section]) for section in parser.sections()}
    if fmt == "env":
        return dict(dotenv_values(dotenv_path=file_path))

    raise ValueError(f"Unsupported format: {fmt}")  # pragma: no cover
