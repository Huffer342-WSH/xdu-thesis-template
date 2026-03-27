# 西电专业硕士论文空白模板

本仓库已清理为可编译空白模板，适用于在现有结构基础上撰写新的毕业论文。

## 1. 准备工作

- 安装 [TeX Live](https://www.tug.org/texlive/)，使用在线安装器非常的慢（选择国内镜像站也很慢），建议去<https://mirror.ctan.org/systems/texlive/Images/>下载ISO镜像
- 安装 VS Code 扩展 [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop)
- 建议通过 `.vscode/Article.code-workspace` 打开 VS Code 工作区，以加载仓库预设的主题和扩展配置。`Ctrl+P`输入 `Extensions: Show Recommended Extensions`指令展示建议安装的扩展，里面包含了`LaTeX Workshop`。

如需使用 Python 绘图脚本（一般放在 `scripts/plotting/`目录下），使用 `uv`创建venv：

```sh
uv sync
```

安装到Python包见`pyproject.toml`，其中包含为西电论文图片要求设计的 Matplotlib 风格模板项目：
[https://github.com/Huffer342-WSH/XiDianPlots](https://github.com/Huffer342-WSH/XiDianPlots)

## 2. 正文编译

一般在 VS Code 中配置好 LaTeX Workshop 后会自动编译。

如需手动编译，可在仓库根目录执行：

```sh
make build
```

盲审版手动编译：

```sh
make build-blind
```

## 3. 目录与文件说明

- `chapters/`：章节正文
- `figures/`：论文图目录
- `references.bib`：参考文献（使用zotero管理）
- `scripts/plotting/`：绘图脚本

---

- `main.tex` / `main_blind.tex`：论文入口

---

- **`xdupgthesis.cls`：当前使用的论文模板类文件。**
- `Makefile`：常用命令入口（`build`、`build-blind`、`plotting`、`xduts-*`）。
- `pyproject.toml`：Python 依赖与工具配置（配合 `uv` 使用）。
- `uv.lock`：Python 依赖锁定文件，保证环境可复现。
- `.python-version`：本地 Python 版本提示文件。
- `.gitignore`：Git 忽略规则（构建产物、临时文件等）。
- `.gitattributes`：Git 文本属性配置（换行符等）。
- `.gitmodules`：Git 子模块定义文件（记录子模块路径与来源）。
- `.chktexrc`：ChkTeX 检查规则配置。
- `latexindent.yaml`：LaTeX 自动格式化配置。
- **`.vscode/Article.code-workspace`：工作区配置，包含：主题微调、LaTeX Workshop扩展配置、扩展推荐**
-

## 4. 使用建议

- 注意在 `main.tex` 中填写题目、作者、导师、关键词等信息。
- `draft/`目录下存放撰写论文的草稿，包含给AI的prompt，和AI写的初稿
- `scripts/plotting/`目录下放置绘图脚本。建议准备好绘图需要的数据后直接将数据保存成文件而不是每次都计算出需要的数据。matplotlib选择pgf后端生成pdf到 `figures/`目录下，pgf后端调用latex来绘图，可以确保图片上的字符和论文标准一致。
- 使用matplotlib绘图的时候图片宽度5.8in比较合适，切勿使用较大的宽度导致图片插入后被缩小以至于字体大小不一致。

## 5. 参考文献管理建议

- 推荐使用 Zotero 管理参考文献。
- 推荐安装 Zotero 扩展 Better BibTeX：[https://github.com/retorquere/zotero-better-bibtex](https://github.com/retorquere/zotero-better-bibtex)
- 将文献库通过 Better BibTeX 导出为本项目根目录下的 `references.bib`，并开启自动更新（Auto-export），保持论文引用与文献库同步。
- 扩展使用方法可参考视频教程：[https://www.bilibili.com/video/BV1Tx4MzQEJA/](https://www.bilibili.com/video/BV1Tx4MzQEJA/)

## 6. Submodule 说明（`template/xduts`）

本项目使用 `template/xduts` 作为模板上游子模块，便于同步模板更新。

- 模板原作者仓库：[https://github.com/note286/xduts](https://github.com/note286/xduts)
- 当前项目维护者修改版仓库：[https://github.com/Huffer342-WSH/xduts](https://github.com/Huffer342-WSH/xduts)
- 首次克隆后建议初始化子模块：

  ```sh
  git submodule update --init --recursive
  ```
- 如需更新子模块到远端最新提交：

  ```sh
  git submodule update --remote --recursive
  ```
- 若你希望用子模块重新生成并覆盖根目录 `xdupgthesis.cls`，可执行：

  ```sh
  make xduts-apply
  ```
