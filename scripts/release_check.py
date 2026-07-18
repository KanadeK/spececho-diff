from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from spececho_diff.domain.models import VERSION


def _capture(command: list[str]) -> str:
    return subprocess.check_output(command, text=True, encoding="utf-8").strip()


def _run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> int:
    status = _capture(["git", "status", "--short"])
    if status:
        print("worktree is not clean")
        print(status)
        return 1
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")
    if f"v{VERSION}" not in changelog:
        print(f"CHANGELOG.md does not mention v{VERSION}")
        return 1
    required = [
        "dist-release/SHA256SUMS.txt",
        "dist-release/spececho-diff-0.1.0-example-report.zip",
    ]
    for file_name in required:
        if not Path(file_name).exists():
            print(f"missing release artifact: {file_name}")
            return 1
    terms = ["TO" + "DO", "FIX" + "ME", "Not" + "Implemented", "place" + "holder"]
    terms.extend(["coming " + "soon", "lorem " + "ipsum"])
    forbidden = re.compile("|".join(re.escape(term) for term in terms), re.I)
    for path in Path(".").rglob("*"):
        if path.is_file() and not any(
            part in {".git", ".mypy_cache", ".pytest_cache", "dist-release"} for part in path.parts
        ):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if forbidden.search(text):
                print(f"forbidden marker found in {path}")
                return 1
    author = _capture(["git", "config", "--local", "user.name"])
    email = _capture(["git", "config", "--local", "user.email"])
    if author != "KanadeK" or not email.endswith("+KanadeK@users.noreply.github.com"):
        print(f"unexpected git identity: {author} <{email}>")
        return 1
    _run([sys.executable, "scripts/verify.py"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
