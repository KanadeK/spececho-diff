# SpecEcho Diff

SpecEcho Diff 会把真实 API 响应与 OpenAPI 3.x 契约逐项核对，并比较 staging 与 production 的语义差异。

当前状态：`v0.1.0`

## 快速开始

```bash
python -m pip install -e '.[dev]'
python scripts/demo.py
```

演示会使用仓库内的 Petstore fixture，生成 `site/index.html`、Markdown 和 JSON 报告。

## 核心能力

- 导入 OpenAPI 3.x YAML/JSON。
- 检测缺字段、类型变化、枚举变化、状态码差异、环境独有字段和值变化。
- 提供 CLI 与本地 FastAPI 报告页。
- 支持 Markdown、JSON、HTML 报告。
- 敏感 Header 只从环境变量读取，不落盘。

## 安全边界

默认只允许探测 `localhost`、`127.0.0.1` 和 `::1`。要访问其他主机，必须显式传入 `--allow-host`，且你必须拥有测试授权。

## 验收命令

```bash
make verify
make demo
make package
make release-check
```

Windows 没有 `make` 时可使用 `scripts/*.ps1` 或 Python 脚本。

## 差异化

公开 GitHub 仓库抽样检索未发现同名且高度同构的活跃项目。相邻项目多聚焦 OpenAPI 规格文件之间的差异或单框架校验；SpecEcho Diff 把真实响应契约校验和 staging/production 语义差异合并在一个可离线复现的流程中。

