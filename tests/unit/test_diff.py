from spececho_diff.domain.diff import compare_environments, validate_observation
from spececho_diff.domain.models import DifferenceKind, Endpoint, Observation, Severity


def _endpoint() -> Endpoint:
    return Endpoint(
        method="GET",
        path="/pets/1",
        operation_id="getPet",
        expected_statuses=(200,),
        request_path="/pets/1",
        response_schema={
            "type": "object",
            "required": ["id", "name", "species", "status"],
            "properties": {
                "id": {"type": "integer"},
                "species": {"type": "string", "enum": ["cat", "dog"]},
                "status": {"type": "string", "enum": ["available", "adopted"]},
            },
        },
    )


def test_validate_observation_detects_missing_type_enum_and_status() -> None:
    observation = Observation(
        endpoint=_endpoint(),
        environment="staging",
        status_code=202,
        json_body={"id": "1", "name": "Miso", "species": "fox"},
    )
    diffs = validate_observation(observation)
    kinds = {diff.kind for diff in diffs}
    assert DifferenceKind.status_code in kinds
    assert DifferenceKind.type_change in kinds
    assert DifferenceKind.enum_change in kinds
    assert DifferenceKind.missing_field in kinds
    assert all(diff.severity is Severity.breaking for diff in diffs)


def test_compare_environments_detects_status_type_and_extra_fields() -> None:
    endpoint = _endpoint()
    staging = Observation(
        endpoint=endpoint,
        environment="staging",
        status_code=200,
        json_body={"id": "1", "name": "Miso", "debug": True},
    )
    prod = Observation(
        endpoint=endpoint,
        environment="production",
        status_code=404,
        json_body={"id": 1, "name": "Miso", "species": "cat"},
    )
    diffs = compare_environments(staging, prod)
    assert {diff.kind for diff in diffs} >= {
        DifferenceKind.status_code,
        DifferenceKind.type_change,
        DifferenceKind.environment_only,
    }


def test_schema_validation_covers_arrays_and_scalar_root_type() -> None:
    endpoint = Endpoint(
        method="GET",
        path="/pets",
        operation_id="listPets",
        expected_statuses=(200,),
        request_path="/pets",
        response_schema={"type": "array", "items": {"type": "integer"}},
    )
    diffs = validate_observation(
        Observation(endpoint=endpoint, environment="staging", status_code=200, json_body=["1"])
    )
    assert diffs[0].kind is DifferenceKind.type_change

    bad_root = endpoint.model_copy(update={"response_schema": {"type": "object"}})
    root_diffs = validate_observation(
        Observation(endpoint=bad_root, environment="staging", status_code=200, json_body=[])
    )
    assert root_diffs[0].path == "$"
