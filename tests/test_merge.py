"""Tests for config merge."""

import json
from pathlib import Path

import pytest
import typer
import yaml

from config_manager.utils.merger import deep_merge, run_merge


class TestDeepMerge:
    def test_merge_flat_dicts(self) -> None:
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_nested_dicts(self) -> None:
        base = {"db": {"host": "localhost", "port": 5432}}
        override = {"db": {"host": "prod.example.com"}}
        result = deep_merge(base, override)
        assert result == {"db": {"host": "prod.example.com", "port": 5432}}

    def test_merge_override_replaces_non_dict(self) -> None:
        base = {"key": "value1"}
        override = {"key": "value2"}
        result = deep_merge(base, override)
        assert result == {"key": "value2"}

    def test_merge_does_not_modify_base(self) -> None:
        base = {"a": 1, "nested": {"x": 10}}
        override = {"nested": {"y": 20}}
        original_base = base.copy()
        deep_merge(base, override)
        assert base == original_base

    def test_merge_empty_override(self) -> None:
        base = {"a": 1}
        result = deep_merge(base, {})
        assert result == {"a": 1}

    def test_merge_empty_base(self) -> None:
        result = deep_merge({}, {"a": 1})
        assert result == {"a": 1}

    def test_merge_nested_override_replaces_dict_with_scalar(self) -> None:
        base = {"db": {"host": "localhost", "port": 5432}}
        override = {"db": "string_value"}
        result = deep_merge(base, override)
        assert result == {"db": "string_value"}


class TestRunMerge:
    def test_merge_yaml_files(self, tmp_path: Path) -> None:
        base = tmp_path / "base.yaml"
        override = tmp_path / "override.yaml"
        output = tmp_path / "merged.yaml"

        base.write_text(yaml.dump({"database": {"host": "localhost", "port": 5432}}))
        override.write_text(yaml.dump({"database": {"host": "dev.local"}}))

        run_merge(str(base), (str(override),), str(output))

        data = yaml.safe_load(output.read_text())
        assert data["database"]["host"] == "dev.local"
        assert data["database"]["port"] == 5432

    def test_merge_json_files(self, tmp_path: Path) -> None:
        base = tmp_path / "base.json"
        override = tmp_path / "override.json"
        output = tmp_path / "merged.json"

        base.write_text(json.dumps({"database": {"host": "localhost", "port": 5432}}))
        override.write_text(json.dumps({"database": {"host": "dev.local"}}))

        run_merge(str(base), (str(override),), str(output))

        data = json.loads(output.read_text())
        assert data["database"]["host"] == "dev.local"
        assert data["database"]["port"] == 5432

    def test_merge_multiple_overrides(self, tmp_path: Path) -> None:
        base = tmp_path / "base.yaml"
        dev = tmp_path / "dev.yaml"
        staging = tmp_path / "staging.yaml"
        output = tmp_path / "merged.yaml"

        base.write_text(yaml.dump({"db": {"host": "localhost", "port": 5432}}))
        dev.write_text(yaml.dump({"db": {"host": "dev.local"}}))
        staging.write_text(yaml.dump({"db": {"port": 5433}, "logging": {"level": "warn"}}))

        run_merge(str(base), (str(dev), str(staging)), str(output))

        data = yaml.safe_load(output.read_text())
        assert data["db"]["host"] == "dev.local"
        assert data["db"]["port"] == 5433
        assert data["logging"]["level"] == "warn"

    def test_merge_base_not_found(self) -> None:
        with pytest.raises((SystemExit, typer.Exit)):
            run_merge("/nonexistent/base.yaml", (), None)

    def test_merge_override_not_found(self, tmp_path: Path) -> None:
        base = tmp_path / "base.yaml"
        base.write_text(yaml.dump({"a": 1}))
        with pytest.raises((SystemExit, typer.Exit)):
            run_merge(str(base), ("/nonexistent/override.yaml",), None)
