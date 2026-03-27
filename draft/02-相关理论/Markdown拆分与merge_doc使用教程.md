# 相关理论章节：Markdown 拆分写作与 `merge_doc.py` 使用教程

本教程用于把“分小节 Markdown 草稿”合并并转换为 LaTeX 文件，适合 `draft/02-相关理论` 的章节写作。

## 1. 推荐目录组织

以 `draft/02-相关理论` 为例，可按小节拆分：

```text
draft/02-相关理论/
├─ 2-相关理论.md                  # 入口文件（主控）
├─ 2.1-心电监测技术.md
├─ 2.2-毫米波雷达理论.md
├─ 2.3-目标跟踪基础.md
└─ 2.4-深度学习基础.md
```

## 2. Markdown 互相引用写法

在入口文件 `2-相关理论.md` 中，用标准 Markdown 链接引入同目录子文件：

```md
# 2 相关理论

[2.1 心电监测技术](./2.1-心电监测技术.md)
[2.2 毫米波雷达理论](./2.2-毫米波雷达理论.md)
[2.3 目标跟踪基础](./2.3-目标跟踪基础.md)
[2.4 深度学习基础](./2.4-深度学习基础.md)
```

说明：

- `merge_doc.py` 会递归读取这种 `./xxx.md` 链接并展开内容。
- 子文件之间也可以继续用同样方式互相引用。

## 3. 执行合并与转换

### 方式 A：在仓库根目录执行（推荐）

```sh
.venv/Scripts/python.exe scripts/merge_doc.py ^
  -i draft/02-相关理论/2-相关理论.md ^
  -o draft/02-相关理论/chapter2
```

生成结果：

- `draft/02-相关理论/chapter2.tex`（最终可用于论文）
- 中间 `chapter2.md` 默认会被脚本删除

### 方式 B：在 `scripts/` 目录执行

```sh
../.venv/Scripts/python.exe merge_doc.py ^
  -i ../draft/02-相关理论/2-相关理论.md ^
  -o ../draft/02-相关理论/chapter2
```

## 4. 常用参数

- `--no-strip`：保留标题中的数字编号
- `--keep-tightlist`：保留 Pandoc 生成的 `\tightlist`
- `--skip-labels`：跳过 LaTeX label 优化
- `--label-style raw|trans`：label 风格（默认 `raw`）

示例（保留标题编号）：

```sh
.venv/Scripts/python.exe scripts/merge_doc.py ^
  -i draft/02-相关理论/2-相关理论.md ^
  -o draft/02-相关理论/chapter2 ^
  --no-strip
```

## 5. 接入论文正文

将生成的 `chapter2.tex` 内容整理后放入 `chapters/chapter2.tex`，或在正文中 `\input{...}` 引入对应文件。

## 6. 注意事项

- 需本机已安装 `pandoc`，否则脚本无法完成 `.tex` 转换。
- 子文件链接建议统一使用相对路径 `./xxx.md`，避免路径歧义。
- 先在 Markdown 阶段完成结构与引用，再做 LaTeX 微调，效率更高。
