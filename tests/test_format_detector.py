"""Tests for format detection and config loading."""

import json
from pathlib import Path

import pytest
import toml
import yaml

from config_manager.utils.format_detector import detect_format, load_config


@pytest.fixture
def tmp_configs(tmp_path: Path) -> dict[str, Path]:
    """Create temporary config files in various formats."""
    configs = {}

    configs["json"] = tmp_path / "test.json"
    configs["json"].write_text(json.dumps({"database": {"host": "localhost", "port": 5432}}))

    configs["yaml"] = tmp_path / "test.yaml"
    configs["yaml"].write_text(yaml.dump({"database": {"host": "localhost", "port": 5432}}))

    configs["toml"] = tmp_path / "test.toml"
    configs["toml"].write_text(toml.dumps({"database": {"host": "localhost", "port": 5432}}))

    configs["env"] = tmp_path / ".env"
    configs["env"].write_text("DATABASE_HOST=localhost\nDATABASE_PORT=5432\n")

    return configs


class TestDetectFormat:
    def test_detect_json(self, tmp_path: Path) -> None:
        assert detect_format(tmp_path / "config.json") == "json"

    def test_detect_yaml(self, tmp_path: Path) -> None:
        assert detect_format(tmp_path / "config.yaml") == "yaml"
        assert detect_format(tmp_path / "config.yml") == "yaml"

    def test_detect_toml(self, tmp_path: Path) -> None:
        assert detect_format(tmp_path / "config.toml") == "toml"

    def test_detect_ini(self, tmp_path: Path) -> None:
        assert detect_format(tmp_path / "config.ini") == "ini"
        assert detect_format(tmp_path / "config.cfg") == "ini"
        assert detect_format(tmp_path / "config.conf") == "ini"

    def test_detect_env(self, tmp_path: Path) -> None:
        assert detect_format(tmp_path / ".env") == "env"
        assert detect_format(tmp_path / ".env.local") == "env"

    def test_unknown_format(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Unknown config format"):
            detect_format(tmp_path / "config.txt")


class TestLoadConfig:
    def test_load_json(self, tmp_configs: dict[str, Path]) -> None:
        data = load_config(tmp_configs["json"])
        assert data["database"]["host"] == "localhost"
        assert data["database"]["port"] == 5432

    def test_load_yaml(self, tmp_configs: dict[str, Path]) -> None:
        data = load_config(tmp_configs["yaml"])
        assert data["database"]["host"] == "localhost"
        assert data["database"]["port"] == 5432

    def test_load_yaml_non_dict_returns_empty(self, tmp_path: Path) -> None:
        f = tmp_path / "list.yaml"
        f.write_text("- item1\n- item2\n")
        data = load_config(f)
        assert data == {}

    def test_load_toml(self, tmp_configs: dict[str, Path]) -> None:
        data = load_config(tmp_configs["toml"])
        assert data["database"]["host"] == "localhost"
        assert data["database"]["port"] == 5432

    def test_load_ini(self, tmp_path: Path) -> None:
        f = tmp_path / "config.ini"
        f.write_text("[database]\nhost = localhost\nport = 5432\n")
        data = load_config(f)
        assert data["database"]["host"] == "localhost"
        assert data["database"]["port"] == "5432"

    def test_load_ini_cfg_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "config.cfg"
        f.write_text("[database]\nhost = localhost\n")
        data = load_config(f)
        assert data["database"]["host"] == "localhost"

    def test_load_ini_conf_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "config.conf"
        f.write_text("[database]\nhost = localhost\n")
        data = load_config(f)
        assert data["database"]["host"] == "localhost"

    def test_load_env(self, tmp_configs: dict[str, Path]) -> None:
        data = load_config(tmp_configs["env"])
        assert data["DATABASE_HOST"] == "localhost"
        assert data["DATABASE_PORT"] == "5432"
