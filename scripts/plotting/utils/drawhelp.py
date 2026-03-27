"""绘图脚本通用 Plotly 辅助函数。"""

from typing import Any, Optional, Sequence, Tuple, Union

import numpy as np
import plotly.graph_objects as go

Curve2D = Tuple[np.ndarray, np.ndarray]
Curve3D = Tuple[np.ndarray, np.ndarray, np.ndarray]


def draw_spectrum(
    spec: np.ndarray,
    x: Optional[np.ndarray] = None,
    y: Optional[np.ndarray] = None,
    title: str = "default",
) -> None:
    """绘制三维频谱曲面并立即展示。"""
    if x is None:
        x = np.arange(spec.shape[-1])
    if y is None:
        y = np.arange(spec.shape[-2])

    x_grid, y_grid = np.meshgrid(x, y, indexing="xy")
    fig = go.Figure(data=[go.Surface(z=spec, x=x_grid, y=y_grid)])
    fig.update_layout(
        title=title,
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
    )
    fig.show()


def _frame_args(duration: int) -> dict[str, Any]:
    """生成 Plotly 动画控制参数。"""
    return {
        "frame": {"duration": duration},
        "mode": "immediate",
        "fromcurrent": True,
        "transition": {"duration": duration, "easing": "linear"},
    }


def draw_animation(list_data: Sequence[Any], title: str = "未命名") -> go.Figure:
    """根据帧序列构建动画图。"""
    if not list_data:
        raise ValueError("list_data must contain at least one frame")

    fig = go.Figure(
        data=list_data[0],
        frames=[go.Frame(data=list_data[idx], name=str(idx)) for idx in range(len(list_data))],
    )

    sliders = [
        {
            "pad": {"b": 10, "t": 60},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "currentvalue": {
                "font": {"size": 20},
                "prefix": "frame:",
                "visible": True,
                "xanchor": "right",
            },
            "steps": [
                {
                    "args": [[frame.name], _frame_args(0)],
                    "label": str(idx),
                    "method": "animate",
                }
                for idx, frame in enumerate(fig.frames)
            ],
        }
    ]

    fig.update_layout(
        title=title,
        scene=dict(camera=dict(projection=dict(type="orthographic"))),
        updatemenus=[
            {
                "buttons": [
                    {"args": [None, _frame_args(0)], "label": "&#9654;", "method": "animate"},
                    {"args": [[None], _frame_args(0)], "label": "&#9724;", "method": "animate"},
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "type": "buttons",
                "x": 0.1,
                "y": 0,
            }
        ],
        sliders=sliders,
    )
    return fig


def draw_complex_scatter_3d(
    complex_series: np.ndarray, title: str = "未命名"
) -> go.Figure:
    """绘制复数序列的三维轨迹图（索引-实部-虚部）。"""
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=np.arange(len(complex_series)),
                y=np.real(complex_series),
                z=np.imag(complex_series),
                mode="lines+markers",
                marker=dict(size=1.2),
                line=dict(width=1),
            )
        ]
    )
    fig.update_layout(
        scene=dict(
            aspectmode="manual",
            aspectratio=dict(x=5, y=1, z=1),
            xaxis=dict(title="Index"),
            yaxis=dict(title="Real Part"),
            zaxis=dict(title="Imaginary Part"),
        ),
        title=title,
    )
    return fig


def plot_trajectory_over_time(
    curves: Sequence[Union[Curve3D, Curve2D]],
    names: Optional[Sequence[str]] = None,
) -> go.Figure:
    """绘制多条随时间变化的三维轨迹。"""
    fig = go.Figure()
    if names is None:
        names = [f"curve_{idx}" for idx in range(len(curves))]
    if len(names) != len(curves):
        raise ValueError("names length must match curves length")

    for idx, curve in enumerate(curves):
        if len(curve) == 3:
            t, x, y = curve
        elif len(curve) == 2:
            x, y = curve
            t = np.arange(len(x))
        else:
            raise ValueError("curve must be (t, x, y) or (x, y)")

        fig.add_trace(
            go.Scatter3d(
                x=np.asarray(t),
                y=np.asarray(y),
                z=np.asarray(x),
                mode="lines",
                name=names[idx],
                line=dict(width=5),
            )
        )

    fig.update_layout(
        template="plotly_white",
        scene=dict(
            xaxis_title="t",
            yaxis_title="y",
            zaxis_title="x",
            aspectmode="manual",
            aspectratio=dict(x=4, y=1, z=1),
        ),
    )
    return fig
