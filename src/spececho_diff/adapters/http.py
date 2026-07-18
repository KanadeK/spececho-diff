from __future__ import annotations

import os
from urllib.parse import urlparse

import httpx

from spececho_diff.domain.models import Endpoint, Observation, ProbeTarget

DEFAULT_ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}


class UnsafeTargetError(ValueError):
    """Raised when a probe target is outside the caller's explicit whitelist."""


def ensure_allowed(base_url: str, allowed_hosts: set[str]) -> None:
    parsed = urlparse(base_url)
    host = parsed.hostname
    if parsed.scheme not in {"http", "https"} or host is None:
        raise UnsafeTargetError("Probe target must be an HTTP(S) URL with a host")
    if host not in allowed_hosts:
        raise UnsafeTargetError(f"Host {host!r} is not in the safety whitelist")


def headers_from_environment(names: tuple[str, ...]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for name in names:
        value = os.environ.get(name)
        if value:
            header = name.removeprefix("SPECECHO_HEADER_").replace("_", "-")
            headers[header] = value
    return headers


async def probe_target(
    client: httpx.AsyncClient,
    target: ProbeTarget,
    endpoint: Endpoint,
    *,
    allowed_hosts: set[str] | None = None,
) -> Observation:
    allowed = set(DEFAULT_ALLOWED_HOSTS if allowed_hosts is None else allowed_hosts)
    ensure_allowed(target.base_url, allowed)
    headers = headers_from_environment(target.headers_env)
    url = target.base_url.rstrip("/") + endpoint.request_path
    try:
        response = await client.request(endpoint.method, url, headers=headers)
        try:
            body = response.json()
        except ValueError:
            body = None
        return Observation(
            endpoint=endpoint,
            environment=target.name,
            status_code=response.status_code,
            json_body=body,
        )
    except httpx.HTTPError as exc:
        return Observation(endpoint=endpoint, environment=target.name, error=str(exc))
