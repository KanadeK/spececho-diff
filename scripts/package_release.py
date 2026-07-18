from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from spececho_diff.domain.models import VERSION

SLUG = "spececho-diff"
DIST_RELEASE = Path("dist-release")


def _run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    DIST_RELEASE.mkdir(exist_ok=True)
    for path in DIST_RELEASE.iterdir():
        if path.is_file():
            path.unlink()
    _run([sys.executable, "-m", "build"])
    _run([sys.executable, "scripts/demo.py"])
    for artifact in Path("dist").glob("*"):
        if artifact.is_file():
            shutil.copy2(artifact, DIST_RELEASE / artifact.name)
    example_zip = DIST_RELEASE / f"{SLUG}-{VERSION}-example-report.zip"
    with ZipFile(example_zip, "w", ZIP_DEFLATED) as archive:
        for path in sorted(Path("site").glob("spececho-report.*")) + [Path("site/index.html")]:
            archive.write(path, path.as_posix())
    lines = []
    for path in sorted(DIST_RELEASE.iterdir()):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            lines.append(f"{_sha256(path)}  {path.name}")
    (DIST_RELEASE / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("release artifacts written to dist-release")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
