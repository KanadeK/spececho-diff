from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from spececho_diff.adapters.files import write_report
from spececho_diff.adapters.http import DEFAULT_ALLOWED_HOSTS, UnsafeTargetError
from spececho_diff.domain.openapi import OpenApiError
from spececho_diff.services.analyzer import analyze_openapi

app = typer.Typer(help="Compare real API responses with OpenAPI contracts.")


@app.command()
def compare(
    spec: Annotated[
        Path, typer.Option("--spec", exists=True, readable=True, help="OpenAPI YAML/JSON.")
    ],
    staging: Annotated[str, typer.Option("--staging", help="Staging base URL.")],
    production: Annotated[str, typer.Option("--production", help="Production base URL.")],
    output: Annotated[Path, typer.Option("--output", help="Report path.")] = Path(
        "spececho-report.md"
    ),
    fmt: Annotated[str, typer.Option("--format", help="md, json, or html.")] = "md",
    allow_host: Annotated[
        list[str] | None,
        typer.Option("--allow-host", help="Additional host allowed for HTTP probing."),
    ] = None,
) -> None:
    allowed_hosts = set(DEFAULT_ALLOWED_HOSTS) | set(allow_host or [])
    try:
        report = asyncio.run(
            analyze_openapi(spec, staging, production, allowed_hosts=allowed_hosts)
        )
        write_report(report, output, fmt)
    except (OpenApiError, UnsafeTargetError, ValueError) as exc:
        typer.echo(f"configuration error: {exc}", err=True)
        raise typer.Exit(3) from exc
    typer.echo(f"wrote {fmt} report to {output} with {report.breaking_count} breaking differences")
    raise typer.Exit(report.exit_code)


@app.command()
def version() -> None:
    from spececho_diff.domain.models import VERSION

    typer.echo(VERSION)
