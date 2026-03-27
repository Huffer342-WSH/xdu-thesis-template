# 项目 Agent 指南（全局）

本文件适用于仓库全局；若某个子目录存在自己的 `AGENTS.md`，则以更深层目录的规则为准（例如 `scripts/plotting/AGENTS.md`）。

## 项目结构速览

- 入口：`main.tex`
- 正文与章节：`chapters/`（实验部分主要在这里写）
- 图片资源：`figures/`（论文最终引用的图放这里）
- 脚本：`scripts/`（绘图脚本在 `scripts/plotting/`）
- 编译产物：`build/`（不要手动编辑其中内容）

## 默认工作流（建议）

### 写作（实验部分）

- 优先在 `chapters/` 下修改内容；进行中内容按 `chapters/AGENTS.md` 的 WIP 规则执行。
- 只在需要时修改：
  - `main.tex`（章节 include / includeonly）
  - `references.bib`（新增/修正文献）
  - `figures/`（新增引用的图文件，尽量由脚本生成）

### 润色与提示词

- 当任务是“保持原意前提下润色论文语句、段落或小节”时，优先遵循 `prompt/论文润色助手.md`。
- `prompt/论文润色助手.md` 适用于局部润色、改写、去除翻译腔、优化句式和提升中文学术表达，不用于整章诊断或结构性重写。
- 若任务重点是正文撰写、补写、扩写或按章节结构生成 LaTeX 内容，优先参考 `prompt/论文正文助手.md`。
- 若任务重点是系统检查重复、符号不一致、风格不一致、逻辑冲突等问题，优先参考 `prompt/论文优化助手.md`。
- 上述提示词均默认同时遵循 `prompt/论文撰写风格.md` 作为共享写作规范。

### 绘图

- 绘图相关改动默认只在 `scripts/plotting/` 下进行，并遵循 `scripts/plotting/AGENTS.md`（该目录规则优先生效）。
- 论文最终引用的图保存到 `figures/` 下合适的子目录（如 `figures/clutter/`、`figures/radar2ecg/`）。

## 安全护栏（重要）

- 不要修改生成物目录与文件：`build/`、`__pycache__/`、`.venv/`、各类临时/缓存文件。
- 不要进行与任务无关的大范围重构（例如批量重命名、移动目录、改变模板结构）。
- 模板与提交材料默认不改：见 `template/AGENTS.md`、`submission/AGENTS.md`。
