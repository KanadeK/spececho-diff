from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from spececho_diff.adapters.files import write_report
from spececho_diff.adapters.http import DEFAULT_ALLOWED_HOSTS, UnsafeTargetError
from spececho_diff.domain.openapi import OpenApiError
from spececho_diff.report.html import render_html_report
from spececho_diff.services.analyzer import analyze_openapi

app = FastAPI(title="SpecEcho Diff")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SpecEcho Diff</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:0;color:#17202a;background:#fff}
main{max-width:860px;margin:0 auto;padding:36px 24px}
label{display:block;margin-top:14px;font-weight:700}
input{width:100%;padding:10px;border:1px solid #cbd5e1;border-radius:6px}
button{margin-top:18px;padding:10px 14px;border:0;border-radius:6px;background:#166534;
color:white;font-weight:700}
</style></head>
<body><main>
<h1>SpecEcho Diff</h1>
<p>Run a local OpenAPI response check and render a shareable HTML report.</p>
<form action="/report" method="get">
<label>OpenAPI spec path<input name="spec" value="examples/petstore/openapi.yaml"></label>
<label>Staging URL<input name="staging" value="http://localhost:8011"></label>
<label>Production URL<input name="production" value="http://localhost:8012"></label>
<button type="submit">Generate report</button>
</form>
</main></body></html>"""


@app.get("/report", response_class=HTMLResponse)
async def report(
    spec: Annotated[str, Query()],
    staging: Annotated[str, Query()],
    production: Annotated[str, Query()],
    allow_host: Annotated[list[str] | None, Query()] = None,
) -> str:
    allowed_hosts = set(DEFAULT_ALLOWED_HOSTS) | set(allow_host or [])
    try:
        result = await analyze_openapi(Path(spec), staging, production, allowed_hosts=allowed_hosts)
    except (OpenApiError, UnsafeTargetError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    write_report(result, Path("site/spececho-report.html"), "html")
    return render_html_report(result)
