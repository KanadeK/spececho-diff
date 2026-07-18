from __future__ import annotations

from typing import Any

from spececho_diff.domain.models import Difference, DifferenceKind, Observation, Severity


def validate_observation(observation: Observation) -> list[Difference]:
    endpoint = observation.endpoint
    if observation.error is not None:
        return [
            Difference(
                kind=DifferenceKind.probe_error,
                severity=Severity.breaking,
                endpoint=endpoint.key,
                environment=observation.environment,
                path="$",
                message=observation.error,
            )
        ]
    diffs: list[Difference] = []
    if observation.status_code not in endpoint.expected_statuses:
        diffs.append(
            Difference(
                kind=DifferenceKind.status_code,
                severity=Severity.breaking,
                endpoint=endpoint.key,
                environment=observation.environment,
                path="$status",
                message="Response status code is not declared in the OpenAPI contract.",
                expected=list(endpoint.expected_statuses),
                actual=observation.status_code,
            )
        )
    diffs.extend(
        validate_schema(
            endpoint.response_schema,
            observation.json_body,
            endpoint=endpoint.key,
            environment=observation.environment,
            path="$",
        )
    )
    return diffs


def validate_schema(
    schema: dict[str, Any],
    value: Any,
    *,
    endpoint: str,
    environment: str,
    path: str,
) -> list[Difference]:
    if not schema:
        return []
    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(value, dict):
            return [_type_diff(endpoint, environment, path, "object", value)]
        return _validate_object(
            schema, value, endpoint=endpoint, environment=environment, path=path
        )
    if expected_type == "array":
        if not isinstance(value, list):
            return [_type_diff(endpoint, environment, path, "array", value)]
        item_schema = schema.get("items", {})
        diffs: list[Difference] = []
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                diffs.extend(
                    validate_schema(
                        item_schema,
                        item,
                        endpoint=endpoint,
                        environment=environment,
                        path=f"{path}[{index}]",
                    )
                )
        return diffs
    if expected_type in {"string", "integer", "number", "boolean"}:
        if not _type_matches(expected_type, value):
            return [_type_diff(endpoint, environment, path, expected_type, value)]
        enum = schema.get("enum")
        if isinstance(enum, list) and value not in enum:
            return [
                Difference(
                    kind=DifferenceKind.enum_change,
                    severity=Severity.breaking,
                    endpoint=endpoint,
                    environment=environment,
                    path=path,
                    message="Value is outside the OpenAPI enum.",
                    expected=enum,
                    actual=value,
                )
            ]
    return []


def compare_environments(staging: Observation, production: Observation) -> list[Difference]:
    endpoint = staging.endpoint.key
    diffs: list[Difference] = []
    if staging.status_code != production.status_code:
        diffs.append(
            Difference(
                kind=DifferenceKind.status_code,
                severity=Severity.breaking,
                endpoint=endpoint,
                environment="staging_vs_production",
                path="$status",
                message="Staging and production returned different status codes.",
                expected=production.status_code,
                actual=staging.status_code,
            )
        )
    diffs.extend(_compare_values(staging.json_body, production.json_body, endpoint, "$"))
    return diffs


def _validate_object(
    schema: dict[str, Any],
    value: dict[str, Any],
    *,
    endpoint: str,
    environment: str,
    path: str,
) -> list[Difference]:
    diffs: list[Difference] = []
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    if isinstance(required, list):
        for field in required:
            if isinstance(field, str) and field not in value:
                diffs.append(
                    Difference(
                        kind=DifferenceKind.missing_field,
                        severity=Severity.breaking,
                        endpoint=endpoint,
                        environment=environment,
                        path=f"{path}.{field}",
                        message="Required response field is missing.",
                        expected="present",
                        actual="missing",
                    )
                )
    if isinstance(properties, dict):
        for field, field_schema in properties.items():
            if field in value and isinstance(field_schema, dict):
                diffs.extend(
                    validate_schema(
                        field_schema,
                        value[field],
                        endpoint=endpoint,
                        environment=environment,
                        path=f"{path}.{field}",
                    )
                )
    return diffs


def _compare_values(staging: Any, production: Any, endpoint: str, path: str) -> list[Difference]:
    if isinstance(staging, dict) and isinstance(production, dict):
        diffs: list[Difference] = []
        for key in sorted(set(staging) | set(production)):
            child_path = f"{path}.{key}"
            if key not in staging:
                diffs.append(
                    Difference(
                        kind=DifferenceKind.environment_only,
                        severity=Severity.warning,
                        endpoint=endpoint,
                        environment="production",
                        path=child_path,
                        message="Field exists only in production.",
                        expected="also in staging",
                        actual=production[key],
                    )
                )
            elif key not in production:
                diffs.append(
                    Difference(
                        kind=DifferenceKind.environment_only,
                        severity=Severity.warning,
                        endpoint=endpoint,
                        environment="staging",
                        path=child_path,
                        message="Field exists only in staging.",
                        expected="also in production",
                        actual=staging[key],
                    )
                )
            else:
                diffs.extend(_compare_values(staging[key], production[key], endpoint, child_path))
        return diffs
    if isinstance(staging, list) and isinstance(production, list):
        diffs = []
        for index, (left, right) in enumerate(zip(staging, production, strict=False)):
            diffs.extend(_compare_values(left, right, endpoint, f"{path}[{index}]"))
        if len(staging) != len(production):
            diffs.append(
                Difference(
                    kind=DifferenceKind.value_change,
                    severity=Severity.warning,
                    endpoint=endpoint,
                    environment="staging_vs_production",
                    path=f"{path}.length",
                    message="Array lengths differ between staging and production.",
                    expected=len(production),
                    actual=len(staging),
                )
            )
        return diffs
    if type(staging) is not type(production):
        return [
            Difference(
                kind=DifferenceKind.type_change,
                severity=Severity.breaking,
                endpoint=endpoint,
                environment="staging_vs_production",
                path=path,
                message="Staging and production response types differ.",
                expected=type(production).__name__,
                actual=type(staging).__name__,
            )
        ]
    if staging != production:
        return [
            Difference(
                kind=DifferenceKind.value_change,
                severity=Severity.info,
                endpoint=endpoint,
                environment="staging_vs_production",
                path=path,
                message="Scalar response value differs.",
                expected=production,
                actual=staging,
            )
        ]
    return []


def _type_matches(expected_type: str, value: Any) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return (isinstance(value, int | float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True


def _type_diff(
    endpoint: str, environment: str, path: str, expected: str, actual: Any
) -> Difference:
    return Difference(
        kind=DifferenceKind.type_change,
        severity=Severity.breaking,
        endpoint=endpoint,
        environment=environment,
        path=path,
        message="Response field type does not match the OpenAPI contract.",
        expected=expected,
        actual=type(actual).__name__,
    )
