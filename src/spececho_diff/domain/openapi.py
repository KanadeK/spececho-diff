from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import yaml

from spececho_diff.domain.models import Endpoint


class OpenApiError(ValueError):
    """Raised when an OpenAPI document cannot be parsed into probeable endpoints."""


def load_openapi(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise OpenApiError(f"OpenAPI file not found: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OpenApiError(f"Cannot read OpenAPI file: {path}") from exc
    try:
        spec = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise OpenApiError(f"Invalid OpenAPI document: {path}") from exc
    if not isinstance(spec, dict):
        raise OpenApiError("OpenAPI document must be an object")
    version = str(spec.get("openapi", ""))
    if not version.startswith("3."):
        raise OpenApiError("Only OpenAPI 3.x documents are supported")
    return spec


def extract_endpoints(spec: dict[str, Any]) -> list[Endpoint]:
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        raise OpenApiError("OpenAPI document has no paths object")
    endpoints: list[Endpoint] = []
    for raw_path, path_item in sorted(paths.items()):
        if not isinstance(path_item, dict):
            continue
        for method, operation in sorted(path_item.items()):
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            if not isinstance(operation, dict):
                continue
            responses = operation.get("responses", {})
            expected_statuses = tuple(
                sorted(int(code) for code in responses if str(code).isdigit())
            )
            schema = _first_json_schema(responses)
            request_path = _sample_path(raw_path)
            endpoints.append(
                Endpoint(
                    method=method.upper(),
                    path=raw_path,
                    operation_id=str(operation.get("operationId") or f"{method}_{raw_path}"),
                    expected_statuses=expected_statuses or (200,),
                    request_path=request_path,
                    response_schema=resolve_refs(schema, spec),
                )
            )
    if not endpoints:
        raise OpenApiError("No HTTP operations found in OpenAPI document")
    return endpoints


def resolve_refs(schema: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in schema and isinstance(schema["$ref"], str):
        return resolve_refs(_lookup_ref(schema["$ref"], spec), spec)
    resolved: dict[str, Any] = {}
    for key, value in schema.items():
        if isinstance(value, dict):
            resolved[key] = resolve_refs(value, spec)
        elif isinstance(value, list):
            resolved[key] = [
                resolve_refs(item, spec) if isinstance(item, dict) else item for item in value
            ]
        else:
            resolved[key] = value
    return resolved


def _first_json_schema(responses: Any) -> dict[str, Any]:
    if not isinstance(responses, dict):
        return {}
    for status_code, response in sorted(responses.items()):
        if not str(status_code).isdigit() or not isinstance(response, dict):
            continue
        content = response.get("content", {})
        if not isinstance(content, dict):
            continue
        media = content.get("application/json")
        if isinstance(media, dict) and isinstance(media.get("schema"), dict):
            return cast(dict[str, Any], media["schema"])
    return {}


def _lookup_ref(ref: str, spec: dict[str, Any]) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise OpenApiError(f"Only local $ref values are supported: {ref}")
    node: Any = spec
    for part in ref.removeprefix("#/").split("/"):
        if not isinstance(node, dict) or part not in node:
            raise OpenApiError(f"Unresolvable OpenAPI $ref: {ref}")
        node = node[part]
    if not isinstance(node, dict):
        raise OpenApiError(f"OpenAPI $ref does not target an object: {ref}")
    return cast(dict[str, Any], node)


def _sample_path(path_template: str) -> str:
    parts: list[str] = []
    for part in path_template.split("/"):
        if part.startswith("{") and part.endswith("}"):
            name = part.strip("{}").lower()
            parts.append("1" if name.endswith("id") or name == "id" else "sample")
        else:
            parts.append(part)
    return "/".join(parts)
