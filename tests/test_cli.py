"""Tests for CLI commands using Typer CliRunner."""

import json
from pathlib import Path

import pytest
import toml
import yaml
from typer.testing import CliRunner

from config_manager.cli import app

runner = CliRunner()


@pytest.fixture
def sample_json(tmp_path: Path) -> Path:
    """Create a sample JSON config file."""
    f = tmp_path / "config.json"
    f.write_text(json.dumps({"database": {"host": "localhost", "port": 5432}}))
    return f


@pytest.fixture
def sample_yaml(tmp_path: Path) -> Path:
    """Create a sample YAML config file."""
    f = tmp_path / "config.yaml"
    f.write_text(yaml.dump({"database": {"host": "localhost", "port": 5432}}))
    return f


@pytest.fixture
def sample_toml(tmp_path: Path) -> Path:
    """Create a sample TOML config file."""
    f = tmp_path / "config.toml"
    f.write_text(toml.dumps({"database": {"host": "localhost", "port": 5432}}))
    return f


@pytest.fixture
def override_yaml(tmp_path: Path) -> Path:
    """Create an override YAML config file."""
    f = tmp_path / "override.yaml"
    f.write_text(yaml.dump({"database": {"host": "dev.local", "port": 5433}}))
    return f


@pytest.fixture
def schema_json(tmp_path: Path) -> Path:
    """Create a JSON schema file."""
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
def template_tpl(tmp_path: Path) -> Path:
    """Create a template file."""
    f = tmp_path / "config.tpl"
    f.write_text("host: ${DB_HOST}\nport: ${DB_PORT}\n")
    return f


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    """Create a .env file."""
    f = tmp_path / ".env"
    f.write_text("DB_HOST=prod.example.com\nDB_PORT=5432\n")
    return f


class TestCLIHelp:
    def test_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "config-manager" in result.output

    def test_validate_help(self) -> None:
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate" in result.output

    def test_convert_help(self) -> None:
        result = runner.invoke(app, ["convert", "--help"])
        assert result.exit_code == 0
        assert "Convert" in result.output

    def test_merge_help(self) -> None:
        result = runner.invoke(app, ["merge", "--help"])
        assert result.exit_code == 0
        assert "Merge" in result.output

    def test_template_help(self) -> None:
        result = runner.invoke(app, ["template", "--help"])
        assert result.exit_code == 0
        assert "substitution" in result.output

    def test_diff_help(self) -> None:
        result = runner.invoke(app, ["diff", "--help"])
        assert result.exit_code == 0
        assert "differences" in result.output


class TestCLIValidate:
    def test_validate_basic(self, sample_json: Path) -> None:
        result = runner.invoke(app, ["validate", str(sample_json)])
        assert result.exit_code == 0
        assert "Parseable" in result.output

    def test_validate_with_schema(
        self, sample_json: Path, schema_json: Path
    ) -> None:
        result = runner.invoke(
            app, ["validate", str(sample_json), "--schema", str(schema_json)]
        )
        assert result.exit_code == 0
        assert "Valid" in result.output

    def test_validate_file_not_found(self) -> None:
        result = runner.invoke(app, ["validate", "/nonexistent.json"])
        assert result.exit_code == 1

    def test_validate_invalid_schema(
        self, sample_json: Path, tmp_path: Path
    ) -> None:
        bad_schema = tmp_path / "bad.json"
        bad_schema.write_text(json.dumps({"type": "string"}))
        result = runner.invoke(
            app, ["validate", str(sample_json), "--schema", str(bad_schema)]
        )
        assert result.exit_code == 1


class TestCLIConvert:
    def test_convert_json_to_yaml(
        self, sample_json: Path, tmp_path: Path
    ) -> None:
        output = tmp_path / "output.yaml"
        result = runner.invoke(
            app, ["convert", str(sample_json), "--to", "yaml", "--output", str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        data = yaml.safe_load(output.read_text())
        assert data["database"]["host"] == "localhost"

    def test_convert_yaml_to_json(
        self, sample_yaml: Path, tmp_path: Path
    ) -> None:
        output = tmp_path / "output.json"
        result = runner.invoke(
            app, ["convert", str(sample_yaml), "--to", "json", "--output", str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        data = json.loads(output.read_text())
        assert data["database"]["host"] == "localhost"

    def test_convert_toml_to_json(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        output = tmp_path / "output.json"
        result = runner.invoke(
            app, ["convert", str(sample_toml), "--to", "json", "--output", str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()

    def test_convert_file_not_found(self) -> None:
        result = runner.invoke(app, ["convert", "/nonexistent.json", "--to", "yaml"])
        assert result.exit_code == 1

    def test_convert_unsupported_format(self, sample_json: Path) -> None:
        result = runner.invoke(
            app, ["convert", str(sample_json), "--to", "xml"]
        )
        assert result.exit_code == 1


class TestCLIMerge:
    def test_merge_yaml_files(
        self, sample_yaml: Path, override_yaml: Path, tmp_path: Path
    ) -> None:
        output = tmp_path / "merged.yaml"
        result = runner.invoke(
            app, ["merge", str(sample_yaml), str(override_yaml), "--output", str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        data = yaml.safe_load(output.read_text())
        assert data["database"]["host"] == "dev.local"
        assert data["database"]["port"] == 5433

    def test_merge_base_not_found(self) -> None:
        result = runner.invoke(app, ["merge", "/nonexistent.yaml"])
        assert result.exit_code == 1


class TestCLITemplate:
    def test_template_with_env(
        self, template_tpl: Path, env_file: Path, tmp_path: Path
    ) -> None:
        output = tmp_path / "result.yaml"
        result = runner.invoke(
            app, ["template", str(template_tpl), "--env", str(env_file), "--output", str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        content = output.read_text()
        assert "prod.example.com" in content

    def test_template_file_not_found(self) -> None:
        result = runner.invoke(app, ["template", "/nonexistent.tpl"])
        assert result.exit_code == 1


class TestCLIDiff:
    def test_diff_identical(self, sample_json: Path, tmp_path: Path) -> None:
        copy = tmp_path / "copy.json"
        copy.write_text(sample_json.read_text())
        result = runner.invoke(app, ["diff", str(sample_json), str(copy)])
        assert result.exit_code == 0
        assert "No differences" in result.output

    def test_diff_changed(
        self, sample_yaml: Path, override_yaml: Path
    ) -> None:
        result = runner.invoke(app, ["diff", str(sample_yaml), str(override_yaml)])
        assert result.exit_code == 0

    def test_diff_file_not_found(self) -> None:
        result = runner.invoke(app, ["diff", "/nonexistent.json", "/other.json"])
        assert result.exit_code == 1
