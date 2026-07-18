from pathlib import Path

from typer.testing import CliRunner

from spececho_diff.cli import app


def test_cli_rejects_unsafe_target(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "compare",
            "--spec",
            "examples/petstore/openapi.yaml",
            "--staging",
            "https://api.example.com",
            "--production",
            "https://api.example.com",
            "--output",
            str(tmp_path / "report.md"),
        ],
    )
    assert result.exit_code == 3
    assert "configuration error" in result.stderr
