# `scripts/` 目录 Agent 指南

本文件适用于 `scripts/` 目录树。

## Python 环境

- 以仓库内 `.venv/`、`uv.lock`、`pyproject.toml` 为准。
- 运行脚本优先使用项目虚拟环境的 Python 解释器。

## 相对路径约定（重要）

- 当命令在仓库根目录执行时，相对路径以仓库根为基准。
- 当命令在 `scripts/` 或其子目录执行时，相对路径以当前工作目录为基准，不是仓库根。

## 常用命令示例

从仓库根目录执行：

```sh
.venv/Scripts/Activate.ps1
.venv/Scripts/python.exe scripts/toc_to_markdown.py -o build/论文正文标题.md
```

从 `scripts/` 目录执行：

```sh
../.venv/Scripts/Activate.ps1
../.venv/Scripts/python.exe toc_to_markdown.py -o ../build/论文正文标题.md
```
