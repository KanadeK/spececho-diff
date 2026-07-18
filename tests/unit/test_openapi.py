from pathlib import Path

import pytest

from spececho_diff.domain.openapi import OpenApiError, extract_endpoints, load_openapi


def test_extracts_resolved_endpoints() -> None:
    spec = load_openapi(Path("examples/petstore/openapi.yaml"))
    endpoints = extract_endpoints(spec)
    assert [endpoint.key for endpoint in endpoints] == ["GET /orders/1", "GET /pets", "GET /pets/1"]
    pet = next(endpoint for endpoint in endpoints if endpoint.path == "/pets/1")
    assert pet.response_schema["properties"]["species"]["enum"] == ["cat", "dog", "bird"]


def test_rejects_missing_file() -> None:
    with pytest.raises(OpenApiError):
        load_openapi(Path("missing.yaml"))


def test_rejects_invalid_and_empty_specs(tmp_path: Path) -> None:
    invalid = tmp_path / "bad.yaml"
    invalid.write_text("openapi: [", encoding="utf-8")
    with pytest.raises(OpenApiError):
        load_openapi(invalid)

    empty = tmp_path / "empty.yaml"
    empty.write_text("openapi: 3.0.3\ninfo: {}\n", encoding="utf-8")
    with pytest.raises(OpenApiError):
        extract_endpoints(load_openapi(empty))


def test_rejects_bad_refs(tmp_path: Path) -> None:
    spec_path = tmp_path / "bad-ref.yaml"
    spec_path.write_text(
        """
openapi: 3.0.3
info: {title: bad, version: 1}
paths:
  /x:
    get:
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Missing"
""",
        encoding="utf-8",
    )
    with pytest.raises(OpenApiError):
        extract_endpoints(load_openapi(spec_path))
