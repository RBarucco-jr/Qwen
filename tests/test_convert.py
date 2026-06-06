"""Tests for config conversion."""

import json
from pathlib import Path

import pytest
import toml
import typer
import yaml

from config_manager.converters.runner import _serialize, run_convert


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


class TestSerialize:
    def test_serialize_json(self) -> None:
        result = _serialize({"a": 1}, "json")
        assert json.loads(result) == {"a": 1}

    def test_serialize_yaml(self) -> None:
        result = _serialize({"a": 1}, "yaml")
        assert yaml.safe_load(result) == {"a": 1}

    def test_serialize_toml(self) -> None:
        result = _serialize({"database": {"host": "localhost", "port": 5432}}, "toml")
        assert toml.loads(result) == {"database": {"host": "localhost", "port": 5432}}

    def test_serialize_ini_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            _serialize({"a": 1}, "ini")

    def test_serialize_env_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            _serialize({"a": 1}, "env")

    def test_serialize_unknown_format(self) -> None:
        with pytest.raises(ValueError, match="Unsupported format"):
            _serialize({"a": 1}, "xml")


class TestRunConvert:
    def test_convert_json_to_yaml(self, sample_json: Path, tmp_path: Path) -> None:
        output = tmp_path / "output.yaml"
        run_convert(str(sample_json), "yaml", str(output))
        data = yaml.safe_load(output.read_text())
        assert data["database"]["host"] == "localhost"
        assert data["database"]["port"] == 5432

    def test_convert_yaml_to_json(self, sample_yaml: Path, tmp_path: Path) -> None:
        output = tmp_path / "output.json"
        run_convert(str(sample_yaml), "json", str(output))
        data = json.loads(output.read_text())
        assert data["database"]["host"] == "localhost"
        assert data["database"]["port"] == 5432

    def test_convert_toml_to_json(self, sample_toml: Path, tmp_path: Path) -> None:
        output = tmp_path / "output.json"
        run_convert(str(sample_toml), "json", str(output))
        data = json.loads(output.read_text())
        assert data["database"]["host"] == "localhost"
        assert data["database"]["port"] == 5432

    def test_convert_json_to_toml(self, sample_json: Path, tmp_path: Path) -> None:
        output = tmp_path / "output.toml"
        run_convert(str(sample_json), "toml", str(output))
        data = toml.loads(output.read_text())
        assert data["database"]["host"] == "localhost"
        assert data["database"]["port"] == 5432

    def test_convert_roundtrip_json_yaml(self, sample_json: Path, tmp_path: Path) -> None:
        yaml_out = tmp_path / "step1.yaml"
        json_out = tmp_path / "step2.json"
        run_convert(str(sample_json), "yaml", str(yaml_out))
        run_convert(str(yaml_out), "json", str(json_out))
        original = json.loads(sample_json.read_text())
        roundtrip = json.loads(json_out.read_text())
        assert original == roundtrip

    def test_convert_file_not_found(self) -> None:
        with pytest.raises((SystemExit, typer.Exit)):
            run_convert("/nonexistent/file.json", "yaml")

    def test_convert_unsupported_format(self, sample_json: Path) -> None:
        with pytest.raises((SystemExit, typer.Exit)):
            run_convert(str(sample_json), "xml")

    def test_convert_no_output_prints_to_stdout(self, sample_json: Path) -> None:
        # No output file — prints to console (no crash)
        run_convert(str(sample_json), "yaml", None)
