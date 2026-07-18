from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

import spececho_diff.services.analyzer as analyzer


def test_analyzer_uses_http_adapter_and_returns_breaking_report(monkeypatch) -> None:
    class FakeClient:
        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def request(self, method: str, url: str, headers: dict[str, str]) -> httpx.Response:
            if "staging" in url and "/orders/1" in url:
                return httpx.Response(202, json={"id": 1, "petId": 1, "status": "cancelled"})
            return httpx.Response(200, json={"id": 1, "petId": 1, "status": "paid", "total": 42})

    monkeypatch.setattr(analyzer.httpx, "AsyncClient", lambda timeout: FakeClient())
    report = asyncio.run(
        analyzer.analyze_openapi(
            Path("examples/petstore/openapi.yaml"),
            "http://staging.local",
            "http://production.local",
            allowed_hosts={"staging.local", "production.local"},
        )
    )
    assert report.breaking_count > 0
