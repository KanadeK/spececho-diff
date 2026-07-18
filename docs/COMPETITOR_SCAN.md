# Competitor Scan

Date: 2026-07-18

Commands used:

```bash
gh auth status
gh api user --jq '{login: .login, id: .id}'
gh search repos "SpecEcho Diff" --sort stars --limit 10 --json fullName,url,stargazersCount,updatedAt,description
gh search repos "spececho-diff" --sort stars --limit 10 --json fullName,url,stargazersCount,updatedAt,description
gh search repos "openapi diff" --sort stars --limit 10 --json fullName,url,stargazersCount,updatedAt,description
gh search repos "openapi validator" --sort stars --limit 10 --json fullName,url,stargazersCount,updatedAt,description
```

Authenticated user: `KanadeK` (`121669563`).

Exact project name and exact slug searches returned no public repositories. `KanadeK/spececho-diff` did not exist at scan time.

| Repository | URL | Stars | Updated | Main function | Overlap |
|---|---:|---:|---|---|---|
| oasdiff/oasdiff | https://github.com/oasdiff/oasdiff | 1276 | 2026-07-17 | OpenAPI diff and breaking-change detection | Strong for spec-to-spec diff; does not focus on live staging/production response evidence. |
| OpenAPITools/openapi-diff | https://github.com/OpenAPITools/openapi-diff | 1091 | 2026-07-17 | Compare two OpenAPI specifications | Strong spec diff overlap; runtime probing is outside scope. |
| Azure/openapi-diff | https://github.com/Azure/openapi-diff | 289 | 2026-07-16 | CLI for breaking changes between specs | Adjacent spec diff tool; less focused on response observation reports. |
| mvegter/openapi-diff-action | https://github.com/mvegter/openapi-diff-action | 28 | 2026-02-23 | GitHub Action wrapping OpenAPI diff | CI wrapper, not a standalone runtime contract probe. |
| LimeFlight/openapi-diff | https://github.com/LimeFlight/openapi-diff | 7 | 2025-04-28 | OpenAPI v3 file comparison | Adjacent spec comparison; small overlap. |
| cdimascio/express-openapi-validator | https://github.com/cdimascio/express-openapi-validator | 1004 | 2026-07-08 | Express request/response validator | Strong validator but framework middleware, not environment drift reporting. |
| IBM/openapi-validator | https://github.com/IBM/openapi-validator | 629 | 2026-07-07 | Configurable OpenAPI document validator | Spec quality focus, not live response comparison. |
| pb33f/libopenapi-validator | https://github.com/pb33f/libopenapi-validator | 145 | 2026-07-11 | Request/response validation for Go ecosystem | Library focus; overlap on validation but not CLI demo diff workflow. |
| PayU/openapi-validator-middleware | https://github.com/PayU/openapi-validator-middleware | 144 | 2026-02-23 | Swagger/OpenAPI middleware validation | Middleware-specific overlap. |
| Xotabu4/response-openapi-validator | https://github.com/Xotabu4/response-openapi-validator | 17 | 2025-11-03 | Assert responses against OpenAPI docs | Response validation overlap; does not combine production/staging semantic diff reports. |

Conclusion: the default name `SpecEcho Diff` and slug `spececho-diff` are acceptable. The MVP differentiation is runtime response evidence plus staging/production semantic drift, not only OpenAPI spec-to-spec comparison.

