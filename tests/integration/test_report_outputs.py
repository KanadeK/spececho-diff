from pathlib import Path

from spececho_diff.adapters.files import write_report
from spececho_diff.domain.models import Difference, DifferenceKind, Report, Severity


def test_writes_markdown_json_and_html_reports(tmp_path: Path) -> None:
    report = Report(
        project="SpecEcho Diff",
        differences=[
            Difference(
                kind=DifferenceKind.missing_field,
                severity=Severity.breaking,
                endpoint="GET /pets/1",
                environment="staging",
                path="$.status",
                message="Required response field is missing.",
            )
        ],
    )
    for fmt in ["md", "json", "html"]:
        output = write_report(report, tmp_path / f"report.{fmt}", fmt)
        text = output.read_text(encoding="utf-8")
        assert "SpecEcho Diff" in text
        assert "missing_field" in text
