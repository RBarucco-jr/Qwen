"""Tests for validation runner."""

import json
from pathlib import Path

import pytest
import typer
import yaml

from config_manager.validators.runner import run_validate


@pytest.fixture
def valid_json(tmp_path: Path) -> Path:
    """Create a valid JSON config."""
    f = tmp_path / "valid.json"
    f.write_text(json.dumps({"database": {"host": "localhost", "port": 5432}}))
    return f


@pytest.fixture
def valid_yaml(tmp_path: Path) -> Path:
    """Create a valid YAML config."""
    f = tmp_path / "valid.yaml"
    f.write_text(yaml.dump({"database": {"host": "localhost", "port": 5432}}))
    return f


@pytest.fixture
def schema(tmp_path: Path) -> Path:
    """Create a valid JSON schema."""
    f = tmp_path / "schema.json"
    f.write_text(json.dumps({
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["database"],
        "properties": {
            "database": {
                "type": "object",
                "required": ["host", "port"],
                "properties": {
                    "host": {"type": "string"},
                    "port": {"type": "integer"},
                },
            },
        },
    }))
    return f


@pytest.fixture
def strict_schema(tmp_path: Path) -> Path:
    """Create a strict schema that requires port to be integer."""
    f = tmp_path / "strict.json"
    f.write_text(json.dumps({
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["database"],
        "properties": {
            "database": {
                "type": "object",
                "required": ["host", "port"],
                "properties": {
                    "host": {"type": "string"},
                    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                },
            },
        },
    }))
    return f


class TestRunValidate:
    def test_validate_basic_json(self, valid_json: Path) -> None:
        run_validate(str(valid_json))

    def test_validate_basic_yaml(self, valid_yaml: Path) -> None:
        run_validate(str(valid_yaml))

    def test_validate_with_schema_passes(
        self, valid_json: Path, schema: Path
    ) -> None:
        run_validate(str(valid_json), str(schema))

    def test_validate_schema_fails_wrong_type(
        self, tmp_path: Path, schema: Path
    ) -> None:
        config = tmp_path / "bad.json"
        config.write_text(json.dumps({"database": {"host": "localhost", "port": "not_a_number"}}))
        with pytest.raises((SystemExit, typer.Exit)):
            run_validate(str(config), str(schema))

    def test_validate_schema_fails_missing_required(
        self, tmp_path: Path, schema: Path
    ) -> None:
        config = tmp_path / "missing.json"
        config.write_text(json.dumps({"database": {"host": "localhost"}}))
        with pytest.raises((SystemExit, typer.Exit)):
            run_validate(str(config), str(schema))

    def test_validate_schema_fails_nested_path(
        self, tmp_path: Path, strict_schema: Path
    ) -> None:
        config = tmp_path / "nested_bad.json"
        config.write_text(json.dumps({
            "database": {"host": "localhost", "port": 99999},
        }))
        with pytest.raises((SystemExit, typer.Exit)):
            run_validate(str(config), str(strict_schema))

    def test_validate_file_not_found(self) -> None:
        with pytest.raises((SystemExit, typer.Exit)):
            run_validate("/nonexistent/config.json")

    def test_validate_schema_file_not_found(self, valid_json: Path) -> None:
        with pytest.raises((SystemExit, typer.Exit)):
            run_validate(str(valid_json), "/nonexistent/schema.json")
