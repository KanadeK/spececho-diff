from __future__ import annotations

from pathlib import Path

import httpx

from spececho_diff.adapters.http import probe_target
from spececho_diff.domain.diff import compare_environments, validate_observation
from spececho_diff.domain.models import ProbeTarget, Report
from spececho_diff.domain.openapi import extract_endpoints, load_openapi


async def analyze_openapi(
    spec_path: Path,
    staging_url: str,
    production_url: str,
    *,
    allowed_hosts: set[str],
    timeout: float = 5.0,
) -> Report:
    spec = load_openapi(spec_path)
    endpoints = extract_endpoints(spec)
    staging = ProbeTarget(name="staging", base_url=staging_url)
    production = ProbeTarget(name="production", base_url=production_url)
    differences = []
    async with httpx.AsyncClient(timeout=timeout) as client:
        for endpoint in endpoints:
            staging_observation = await probe_target(
                client, staging, endpoint, allowed_hosts=allowed_hosts
            )
            production_observation = await probe_target(
                client, production, endpoint, allowed_hosts=allowed_hosts
            )
            differences.extend(validate_observation(staging_observation))
            differences.extend(validate_observation(production_observation))
            differences.extend(compare_environments(staging_observation, production_observation))
    return Report(project="SpecEcho Diff", differences=differences)
