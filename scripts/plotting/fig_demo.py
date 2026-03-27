"""Single demo plotting script for the blank thesis template."""

# %% 导入依赖
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import XiDianPlots as xp

# %% 运行配置与主题设置
SHOW = os.getenv("PLOT_SHOW", "1") == "1"
SAVE_FIGURES = os.getenv("SAVE_FIGURES", "1") == "1"

fig_dir = Path(__file__).resolve().parents[2] / "figures" / "example"
fig_name = "fig_demo"

xp.use_style("xidian")

# %% 生成示例数据
x = np.linspace(0.0, 2.0 * np.pi, 256)
y = np.sin(x)

# %% 绘制示例图
fig, ax = plt.subplots(figsize=(5.8, 3.2))
ax.plot(x, y, linewidth=2)
ax.set_title("Demo Figure")
ax.set_xlabel("x")
ax.set_ylabel("sin(x)")
ax.grid(alpha=0.3)

# %% 按配置保存图片到 figures/example
if SAVE_FIGURES:
    xp.savefig(fig, fig_dir / f"{fig_name}.pdf", bbox_inches="tight")

# %% 按配置展示或关闭图像窗口
if SHOW:
    plt.show()
else:
    plt.close(fig)
