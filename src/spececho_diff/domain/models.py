from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

VERSION = "0.1.0"
SENSITIVE_HEADER_NAMES = {"authorization", "cookie", "x-api-key", "x-auth-token"}


class Severity(StrEnum):
    info = "info"
    warning = "warning"
    breaking = "breaking"


class DifferenceKind(StrEnum):
    missing_field = "missing_field"
    type_change = "type_change"
    enum_change = "enum_change"
    status_code = "status_code"
    environment_only = "environment_only"
    value_change = "value_change"
    probe_error = "probe_error"


class Endpoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    method: str
    path: str
    operation_id: str
    expected_statuses: tuple[int, ...]
    request_path: str
    response_schema: dict[str, Any] = Field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.method.upper()} {self.path}"


class ProbeTarget(BaseModel):
    name: str
    base_url: str
    headers_env: tuple[str, ...] = ()


class Observation(BaseModel):
    endpoint: Endpoint
    environment: str
    status_code: int | None = None
    json_body: Any | None = None
    error: str | None = None


class Difference(BaseModel):
    kind: DifferenceKind
    severity: Severity
    endpoint: str
    environment: str
    path: str
    message: str
    expected: Any | None = None
    actual: Any | None = None


class Report(BaseModel):
    project: str
    version: str = VERSION
    differences: list[Difference]

    @property
    def breaking_count(self) -> int:
        return sum(1 for item in self.differences if item.severity is Severity.breaking)

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.differences if item.severity is Severity.warning)

    @property
    def exit_code(self) -> int:
        return 2 if self.breaking_count else 0


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    redacted: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADER_NAMES:
            redacted[key] = "***"
        else:
            redacted[key] = value
    return redacted
