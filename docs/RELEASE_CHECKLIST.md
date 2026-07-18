# Release Checklist

- `gh auth status` confirms `KanadeK`.
- Local git author and committer are `KanadeK <121669563+KanadeK@users.noreply.github.com>`.
- `python -m pip install -e '.[dev]'`.
- `make verify`.
- `make demo`.
- `make package`.
- Commit history contains only KanadeK author and committer identities.
- Push `main` to `https://github.com/KanadeK/spececho-diff.git`.
- Wait for CI, security, and Pages workflows to pass.
- Create annotated tag `v0.1.0` on the same SHA as `main`.
- Create GitHub Release with all `dist-release/*` assets.
- Confirm Contributors API contains only `KanadeK`.

