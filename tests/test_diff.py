"""Tests for config differ."""

import json
from pathlib import Path

import pytest
import typer
import yaml

from config_manager.utils.differ import _flatten, run_diff


class TestFlatten:
    def test_flatten_flat_dict(self) -> None:
        result = _flatten({"a": 1, "b": "hello"})
        assert result == {"a": "1", "b": "'hello'"}

    def test_flatten_nested_dict(self) -> None:
        result = _flatten({"db": {"host": "localhost", "port": 5432}})
        assert result == {"db.host": "'localhost'", "db.port": "5432"}

    def test_flatten_deeply_nested(self) -> None:
        data = {"level1": {"level2": {"level3": "value"}}}
        result = _flatten(data)
        assert result == {"level1.level2.level3": "'value'"}

    def test_flatten_empty_dict(self) -> None:
        result = _flatten({})
        assert result == {}


class TestRunDiff:
    def test_diff_identical_files(self, tmp_path: Path) -> None:
        file_a = tmp_path / "a.json"
        file_b = tmp_path / "b.json"
        data = {"database": {"host": "localhost", "port": 5432}}
        file_a.write_text(json.dumps(data))
        file_b.write_text(json.dumps(data))

        # Should print "No differences" — no crash
        run_diff(str(file_a), str(file_b))

    def test_diff_changed_value(self, tmp_path: Path) -> None:
        file_a = tmp_path / "a.yaml"
        file_b = tmp_path / "b.yaml"

        file_a.write_text(yaml.dump({"db": {"host": "localhost"}}))
        file_b.write_text(yaml.dump({"db": {"host": "prod.example.com"}}))

        # Should print diff — no crash
        run_diff(str(file_a), str(file_b))

    def test_diff_added_key(self, tmp_path: Path) -> None:
        file_a = tmp_path / "a.json"
        file_b = tmp_path / "b.json"

        file_a.write_text(json.dumps({"a": 1}))
        file_b.write_text(json.dumps({"a": 1, "b": 2}))

        run_diff(str(file_a), str(file_b))

    def test_diff_removed_key(self, tmp_path: Path) -> None:
        file_a = tmp_path / "a.json"
        file_b = tmp_path / "b.json"

        file_a.write_text(json.dumps({"a": 1, "b": 2}))
        file_b.write_text(json.dumps({"a": 1}))

        run_diff(str(file_a), str(file_b))

    def test_diff_file_a_not_found(self) -> None:
        with pytest.raises((SystemExit, typer.Exit)):
            run_diff("/nonexistent/a.json", "/nonexistent/b.json")

    def test_diff_file_b_not_found(self, tmp_path: Path) -> None:
        file_a = tmp_path / "a.json"
        file_a.write_text(json.dumps({"a": 1}))
        with pytest.raises((SystemExit, typer.Exit)):
            run_diff(str(file_a), "/nonexistent/b.json")
