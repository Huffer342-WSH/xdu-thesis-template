# 绘图脚本 Agent 指南（`scripts/plotting/`）

本文件仅适用于 `scripts/plotting/` 目录树

## 目录定位与职责

- 本目录用于**生成论文实验部分需要的图片**：
  - **一个脚本对应一组图片**（同一实验/同一主题的一系列 figure）。
  - 脚本命名建议 `fig_*.py`（与本目录 `Makefile` 的批量生成规则匹配）。
- 通用功能（插值、杂波估计、绘图辅助、公共样式封装等）放到 `utils/` 下，避免复制粘贴。
- 数据文件通常放在 `data/` 下；脚本内用相对路径读取（以脚本所在目录为基准）。
- 最终输出图片应保存到仓库根的 `figures/`（例如 `../../figures/clutter`、`../../figures/radar2ecg`）。

## Scope（操作范围）

- 除非明确要求，**只修改** `scripts/plotting/` 下文件（含 `utils/`、`data/`、本目录 `AGENTS.md`）。
- 不要改论文正文或模板文件；不要手动改 `figures/` 中的二进制图（优先改脚本再生成）。

## 代码风格

- 遵循 PEP 8。
- Docstring 使用 Google 风格（脚本文件头部必须有“脚本做什么 + 输出哪些图”说明）。
- 注释写“意图/约定/坑点”，不要解释显而易见的语句。

## 工作流与运行方式

- 每个脚本必须同时支持：
  - 直接运行（`python fig_xxx.py`）
  - VS Code 交互式调试（用 `# %%` 分段逐步执行）
- 不强制封装成函数；不要加 `main()`，除非明确要求。
- 脚本尽量可重复运行（同输入得到同输出），避免依赖手动 GUI 操作。
- 批量生成：保持脚本可被 `Makefile` 调用（环境变量见下文）。

## 环境变量与批量生成

- 统一用环境变量控制交互与落盘：
  - `PLOT_SHOW=1/0`：是否展示交互图（`plt.show()`、Plotly 的 `fig.show()`）
  - `SAVE_FIGURES=1/0`：是否保存最终图片到 `figures/`
- 批量生成（本目录 `Makefile` 会设置 `PLOT_SHOW=0 SAVE_FIGURES=1`）：
  - 生成全部：`make` 或 `make all`
  - 生成单个：`make fig_xxx`（不带 `.py` 后缀）

## 推荐脚本结构（请严格遵循）

一个脚本通常分为以下几个大段（用 `# %%` 分隔，便于逐步调试）：

1) **文件头 Docstring**：简要说明脚本内容、主要流程、会生成哪些图片、以及是否会打印 LaTeX 表格片段。
2) **导入包**：第三方库、项目工具（优先从 `utils` 导入），以及 `XiDianPlots` 样式初始化。
3) **配置项**：
   - 统一使用环境变量控制：
     - `SHOW = os.getenv("PLOT_SHOW", "1") == "1"`（是否 `plt.show()` / 是否弹出调试图）
     - `SAVE_FIGURES = os.getenv("SAVE_FIGURES", "1") == "1"`（是否落盘保存）
   - 统一设置输出路径与前缀：
     - `fig_dir = "../../figures/<topic>"`
     - `fig_name = "<base_name>"`（同脚本产出一组图时，用 `{fig_name}_xxx.pdf`）
4) **数据导入/生成 + 多步处理**：
   - 按“可逐步验证”的思路拆成多个 cell（加载 -> 预处理 -> 特征构造 -> 指标计算等）。
   - 允许生成中间变量并用 **Plotly** 快速可视化来调试（例如 3D surface、轨迹预览），调通后再进入最终出图。
5) **Matplotlib 最终出图**：
   - 最终论文用图必须由 `matplotlib` 生成。
   - 复用一致的颜色/字体/线宽等配置，保证同一组图风格统一。
6) **保存图片**：
   - 只在 `SAVE_FIGURES` 为真时保存。
7) **可选：打印 LaTeX 表格片段**：
   - 若需要表格：在脚本末尾组装 LaTeX（例如 `tabularray` 的 `tblr`）字符串并 `print()`。
   - 打印时用明确分隔符（Start/End），便于复制到论文中。

## 绘图与保存规范（最终用图）

使用 `matplotlib` + 项目样式（必须）：

```python
import XiDianPlots as xp
xp.use_style("xidian")
```

图宽规则（必须）：

- 标准图宽 ≤ **5.8 in**
- 小图图宽 ≤ **2.8 in**

保存图片（必须）：

```python
xp.savefig(fig, f"{fig_dir}/{fig_name}.pdf")
```

若需要精确裁切（例如 3D 图、colorbar 布局），允许传 `bbox_inches=...`。

## 调试可视化（中间步骤）

- Plotly 允许用于中间过程的交互式验证（例如 `go.Surface`、轨迹预览）。
- 最终论文图必须是 Matplotlib 输出并保存到 `figures/`。
