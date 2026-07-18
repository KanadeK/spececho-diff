from __future__ import annotations

from jinja2 import Template

from spececho_diff.domain.models import Report

HTML_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ report.project }} Report</title>
  <style>
    :root {
      color-scheme: light; --ink: #17202a; --muted: #52616f; --line: #d9e2ec;
      --bad: #b42318; --warn: #925400; --ok: #1f7a4d; --panel: #f7f9fb;
    }
    body {
      margin: 0; font-family: Arial, Helvetica, sans-serif;
      color: var(--ink); background: #ffffff;
    }
    header {
      padding: 32px max(24px, calc((100vw - 1080px) / 2));
      background: #eff6f3; border-bottom: 1px solid var(--line);
    }
    main { max-width: 1080px; margin: 0 auto; padding: 28px 24px 48px; }
    h1 { margin: 0 0 8px; font-size: 34px; letter-spacing: 0; }
    h2 { margin-top: 32px; font-size: 22px; }
    .summary {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px; margin-top: 20px;
    }
    .metric { border: 1px solid var(--line); border-radius: 8px; padding: 16px; background: #fff; }
    .metric strong { display: block; font-size: 26px; }
    table { border-collapse: collapse; width: 100%; table-layout: fixed; }
    th, td {
      border-bottom: 1px solid var(--line); padding: 10px; text-align: left;
      vertical-align: top; overflow-wrap: anywhere;
    }
    th { background: var(--panel); font-size: 13px; }
    .breaking { color: var(--bad); font-weight: 700; }
    .warning { color: var(--warn); font-weight: 700; }
    .info { color: var(--ok); font-weight: 700; }
    code { background: #edf2f7; border-radius: 4px; padding: 2px 5px; }
  </style>
</head>
<body>
  <header>
    <h1>{{ report.project }}</h1>
    <p>Real response contract validation plus staging/production semantic drift.</p>
    <div class="summary" aria-label="Report summary">
      <div class="metric"><span>Breaking</span><strong>{{ report.breaking_count }}</strong></div>
      <div class="metric"><span>Warnings</span><strong>{{ report.warning_count }}</strong></div>
      <div class="metric"><span>Total</span><strong>{{ report.differences|length }}</strong></div>
    </div>
  </header>
  <main>
    <h2>Differences</h2>
    <table>
      <thead><tr><th>Severity</th><th>Kind</th><th>Endpoint</th><th>Environment</th><th>Path</th><th>Message</th></tr></thead>
      <tbody>
      {% for diff in report.differences %}
        <tr>
          <td class="{{ diff.severity.value }}">{{ diff.severity.value }}</td>
          <td><code>{{ diff.kind.value }}</code></td>
          <td>{{ diff.endpoint }}</td>
          <td>{{ diff.environment }}</td>
          <td><code>{{ diff.path }}</code></td>
          <td>{{ diff.message }}</td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
  </main>
</body>
</html>"""
)


def render_html_report(report: Report) -> str:
    return HTML_TEMPLATE.render(report=report)
