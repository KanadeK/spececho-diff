from __future__ import annotations

from fastapi.testclient import TestClient

import spececho_diff.app as app_module
from spececho_diff.domain.models import Difference, DifferenceKind, Report, Severity


def test_home_renders_local_report_form() -> None:
    client = TestClient(app_module.app)
    response = client.get("/")
    assert response.status_code == 200
    assert "SpecEcho Diff" in response.text
    assert "Generate report" in response.text


def test_report_route_renders_analyzed_report(monkeypatch, tmp_path) -> None:
    async def fake_analyze_openapi(*args, **kwargs) -> Report:
        return Report(
            project="SpecEcho Diff",
            differences=[
                Difference(
                    kind=DifferenceKind.status_code,
                    severity=Severity.breaking,
                    endpoint="GET /pets/1",
                    environment="staging",
                    path="$status",
                    message="bad status",
                )
            ],
        )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(app_module, "analyze_openapi", fake_analyze_openapi)
    client = TestClient(app_module.app)
    response = client.get(
        "/report",
        params={
            "spec": "examples/petstore/openapi.yaml",
            "staging": "http://localhost:8011",
            "production": "http://localhost:8012",
        },
    )
    assert response.status_code == 200
    assert "bad status" in response.text
    assert (tmp_path / "site" / "spececho-report.html").exists()


def test_report_route_maps_configuration_error(monkeypatch) -> None:
    async def fake_analyze_openapi(*args, **kwargs) -> Report:
        raise ValueError("bad configuration")

    monkeypatch.setattr(app_module, "analyze_openapi", fake_analyze_openapi)
    client = TestClient(app_module.app)
    response = client.get(
        "/report",
        params={
            "spec": "bad.yaml",
            "staging": "http://localhost:8011",
            "production": "http://localhost:8012",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "bad configuration"
