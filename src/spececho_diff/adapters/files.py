from __future__ import annotations

import json
from pathlib import Path

from spececho_diff.domain.models import Report
from spececho_diff.report.html import render_html_report


def write_report(report: Report, output: Path, fmt: str) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    elif fmt == "md":
        output.write_text(to_markdown(report), encoding="utf-8")
    elif fmt == "html":
        output.write_text(render_html_report(report), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported report format: {fmt}")
    return output


def to_markdown(report: Report) -> str:
    lines = [
        f"# {report.project} Report",
        "",
        f"- Version: `{report.version}`",
        f"- Breaking: `{report.breaking_count}`",
        f"- Warnings: `{report.warning_count}`",
        f"- Total differences: `{len(report.differences)}`",
        "",
        "| Severity | Kind | Endpoint | Environment | Path | Message |",
        "|---|---|---|---|---|---|",
    ]
    for diff in report.differences:
        lines.append(
            "| "
            + " | ".join(
                [
                    diff.severity.value,
                    diff.kind.value,
                    diff.endpoint,
                    diff.environment,
                    diff.path,
                    diff.message,
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))
