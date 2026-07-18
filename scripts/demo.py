from __future__ import annotations

import asyncio
import sys
from importlib import import_module
from pathlib import Path

import httpx

from spececho_diff.adapters.files import write_report
from spececho_diff.domain.diff import compare_environments, validate_observation
from spececho_diff.domain.models import Observation, Report
from spececho_diff.domain.openapi import extract_endpoints, load_openapi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


async def _observe(
    app: object,
    base_url: str,
    environment: str,
) -> list[Observation]:
    spec = load_openapi(Path("examples/petstore/openapi.yaml"))
    endpoints = extract_endpoints(spec)
    transport = httpx.ASGITransport(app=app)
    observations: list[Observation] = []
    async with httpx.AsyncClient(transport=transport, base_url=base_url) as client:
        for endpoint in endpoints:
            response = await client.request(endpoint.method, endpoint.request_path)
            observations.append(
                Observation(
                    endpoint=endpoint,
                    environment=environment,
                    status_code=response.status_code,
                    json_body=response.json(),
                )
            )
    return observations


async def main() -> int:
    staging_app = import_module("examples.petstore.staging_app").app
    prod_app = import_module("examples.petstore.prod_app").app
    staging = await _observe(staging_app, "http://staging.local", "staging")
    production = await _observe(prod_app, "http://production.local", "production")
    differences = []
    for staging_observation, production_observation in zip(staging, production, strict=True):
        differences.extend(validate_observation(staging_observation))
        differences.extend(validate_observation(production_observation))
        differences.extend(compare_environments(staging_observation, production_observation))
    report = Report(project="SpecEcho Diff", differences=differences)
    Path("site").mkdir(exist_ok=True)
    write_report(report, Path("site/index.html"), "html")
    write_report(report, Path("site/spececho-report.md"), "md")
    write_report(report, Path("site/spececho-report.json"), "json")
    print(
        f"demo generated site/index.html with {report.breaking_count} breaking "
        f"and {report.warning_count} warning differences"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
