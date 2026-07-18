from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> int:
    source = Path("site/index.html").resolve()
    target = Path("docs/assets/spececho-report.png")
    target.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 820})
        page.goto(source.as_uri())
        page.screenshot(path=str(target), full_page=True)
        browser.close()
    print(f"captured {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
