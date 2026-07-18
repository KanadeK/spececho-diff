# Architecture

SpecEcho Diff is organized around a pure domain core.

## Domain

`spececho_diff.domain.openapi` loads OpenAPI 3.x documents, resolves local `$ref` pointers, and extracts probeable endpoints.

`spececho_diff.domain.diff` validates observations against response schemas and compares staging and production observations.

## Adapters

`spececho_diff.adapters.http` is the only network boundary. It enforces a host allowlist before probing.

`spececho_diff.adapters.files` writes Markdown, JSON, and HTML reports.

## Services

`spececho_diff.services.analyzer` coordinates parsing, probing, validation, and report creation without embedding CLI or UI behavior.

