# Benchmark

Date: 2026-07-18

Environment: Windows, Python 3.14 local runtime, deterministic in-process FastAPI ASGI fixtures.

Dataset: 3 endpoints, 2 environments, 1 OpenAPI document.

Command:

```bash
python scripts/demo.py
```

Expected result: completes in under 2 seconds on a typical laptop and generates HTML, Markdown, and JSON reports in `site/`.

