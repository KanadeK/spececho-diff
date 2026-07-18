python -m ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m mypy src
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m pytest -q --cov=src --cov-report=term-missing --cov-fail-under=80
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m build
exit $LASTEXITCODE

