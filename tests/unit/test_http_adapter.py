from __future__ import annotations

import asyncio

import httpx

from spececho_diff.adapters.http import headers_from_environment, probe_target
from spececho_diff.domain.models import Endpoint, ProbeTarget


def _endpoint() -> Endpoint:
    return Endpoint(
        method="GET",
        path="/pets/1",
        operation_id="getPet",
        expected_statuses=(200,),
        request_path="/pets/1",
        response_schema={},
    )


def test_headers_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("SPECECHO_HEADER_AUTHORIZATION", "Bearer secret")
    assert headers_from_environment(("SPECECHO_HEADER_AUTHORIZATION",)) == {
        "AUTHORIZATION": "Bearer secret"
    }


def test_probe_target_returns_json_observation() -> None:
    async def run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url) == "http://localhost/pets/1"
            return httpx.Response(200, json={"id": 1})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            observation = await probe_target(
                client, ProbeTarget(name="staging", base_url="http://localhost"), _endpoint()
            )
        assert observation.status_code == 200
        assert observation.json_body == {"id": 1}
        assert observation.error is None

    asyncio.run(run())


def test_probe_target_records_network_error() -> None:
    async def run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("offline", request=request)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            observation = await probe_target(
                client, ProbeTarget(name="staging", base_url="http://localhost"), _endpoint()
            )
        assert observation.error is not None

    asyncio.run(run())
