"""Tests for config template substitution."""

import os
from pathlib import Path

import pytest
import typer

from config_manager.utils.templater import TEMPLATE_PATTERN, run_template


class TestTemplatePattern:
    def test_pattern_braces_var(self) -> None:
        match = TEMPLATE_PATTERN.search("${HOST}")
        assert match is not None
        assert match.group(1) == "HOST"

    def test_pattern_dollar_var(self) -> None:
        match = TEMPLATE_PATTERN.search("$HOST")
        assert match is not None
        assert match.group(2) == "HOST"

    def test_pattern_double_braces(self) -> None:
        match = TEMPLATE_PATTERN.search("{{HOST}}")
        assert match is not None
        assert match.group(3) == "HOST"

    def test_pattern_no_match(self) -> None:
        match = TEMPLATE_PATTERN.search("plain text")
        assert match is None


class TestRunTemplate:
    def test_template_with_env_file(self, tmp_path: Path) -> None:
        tpl = tmp_path / "config.tpl"
        env = tmp_path / ".env"
        output = tmp_path / "result.yaml"

        tpl.write_text("host: ${DB_HOST}\nport: ${DB_PORT}\n")
        env.write_text("DB_HOST=prod.example.com\nDB_PORT=5432\n")

        run_template(str(tpl), str(env), str(output))

        result = output.read_text()
        assert "host: prod.example.com" in result
        assert "port: 5432" in result

    def test_template_with_dollar_syntax(self, tmp_path: Path) -> None:
        tpl = tmp_path / "config.tpl"
        env = tmp_path / ".env"
        output = tmp_path / "result.yaml"

        tpl.write_text("host: $DB_HOST\n")
        env.write_text("DB_HOST=prod.example.com\n")

        run_template(str(tpl), str(env), str(output))

        result = output.read_text()
        assert "host: prod.example.com" in result

    def test_template_with_double_braces(self, tmp_path: Path) -> None:
        tpl = tmp_path / "config.tpl"
        env = tmp_path / ".env"
        output = tmp_path / "result.yaml"

        tpl.write_text("host: {{DB_HOST}}\n")
        env.write_text("DB_HOST=prod.example.com\n")

        run_template(str(tpl), str(env), str(output))

        result = output.read_text()
        assert "host: prod.example.com" in result

    def test_template_unset_var_preserved(self, tmp_path: Path) -> None:
        tpl = tmp_path / "config.tpl"
        output = tmp_path / "result.yaml"

        tpl.write_text("host: ${MISSING_VAR}\n")

        # No .env file, no env var — should preserve original
        run_template(str(tpl), None, str(output))

        result = output.read_text()
        assert "${MISSING_VAR}" in result

    def test_template_uses_os_env_as_fallback(self, tmp_path: Path) -> None:
        tpl = tmp_path / "config.tpl"
        output = tmp_path / "result.yaml"

        tpl.write_text("home: ${HOME}\n")
        os.environ["TEMPLATE_TEST_VAR"] = "test_value"

        # HOME is always set in Linux; no .env needed
        run_template(str(tpl), None, str(output))

        result = output.read_text()
        assert "home:" in result
        assert "${HOME}" not in result

        del os.environ["TEMPLATE_TEST_VAR"]

    def test_template_file_not_found(self) -> None:
        with pytest.raises((SystemExit, typer.Exit)):
            run_template("/nonexistent/template.tpl", None, None)

    def test_template_env_file_not_found(self, tmp_path: Path) -> None:
        tpl = tmp_path / "config.tpl"
        tpl.write_text("host: ${DB_HOST}\n")
        with pytest.raises((SystemExit, typer.Exit)):
            run_template(str(tpl), "/nonexistent/.env", None)

    def test_template_no_output_prints_to_stdout(self, tmp_path: Path) -> None:
        tpl = tmp_path / "config.tpl"
        env = tmp_path / ".env"

        tpl.write_text("host: ${DB_HOST}\n")
        env.write_text("DB_HOST=prod.example.com\n")

        # No output file — prints to console (no crash)
        run_template(str(tpl), str(env), None)
