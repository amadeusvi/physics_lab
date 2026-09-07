import os
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

_has_display = bool(os.environ.get("DISPLAY")) or sys.platform in ("win32", "darwin")
if not _has_display:
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager

from .regression import GraphicalResult, LinearFit

FIGURES_DIR = Path("figures")


def configure_cjk_font() -> bool:
    """检测系统中文字体并配置 matplotlib，成功返回 True，否则回退英文。"""
    candidates = {font.name for font in font_manager.fontManager.ttflist}
    preferred = ["Noto Sans CJK SC", "Source Han Sans SC", "WenQuanYi Zen Hei"]
    chosen = next((name for name in preferred if name in candidates), None)
    if chosen is None:
        chosen = next(
            (name for name in sorted(candidates) if "CJK" in name or "Hei" in name
             or "Song" in name or "Kai" in name),
            None,
        )
    if chosen is None:
        return False
    plt.rcParams["font.sans-serif"] = [chosen, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    return True


def _axis_label(name: str, unit: str, default: str) -> str:
    name = name or default
    return f"{name} / {unit}" if unit else name


def plot_linear_fit(
    x,
    y,
    fit: LinearFit,
    x_label: str = "",
    y_label: str = "",
    x_unit: str = "",
    y_unit: str = "",
    title: str = "",
    marked: GraphicalResult | None = None,
    filename: str = "",
) -> Path:
    """绘制数据点、最小二乘拟合直线（可标记图解法取点）并保存 PNG。

    返回保存路径；有图形界面时同时弹出窗口显示。
    """
    x_line = [float(x.min()), float(x.max())]
    y_line = [fit.a * x_line[0] + fit.b, fit.a * x_line[1] + fit.b]

    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.plot(x, y, "+", color="black", markersize=9, markeredgewidth=1.4,
            label="实验数据点")
    ax.plot(x_line, y_line, "-", color="red", linewidth=1.6,
            label="最小二乘拟合直线")

    if marked is not None:
        xs = [marked.point_a.x, marked.point_b.x, marked.point_c.x]
        ys = [marked.point_a.y, marked.point_b.y, marked.point_c.y]
        ax.plot(xs, ys, "o", color="blue", markersize=7, fillstyle="none",
                markeredgewidth=1.6, label="图解法取点")
        for name, point in zip("ABC", [marked.point_a, marked.point_b,
                                       marked.point_c]):
            ax.annotate(
                f"{name}{point}",
                xy=(point.x, point.y),
                xytext=(8, 8),
                textcoords="offset points",
                fontsize=9,
                color="blue",
            )

    y_label_text = _axis_label(y_label, y_unit, "y")
    x_label_text = _axis_label(x_label, x_unit, "x")
    ax.set_xlabel(x_label_text)
    ax.set_ylabel(y_label_text)
    ax.set_title(title or f"{y_label_text} - {x_label_text} 曲线")

    from .regression import format_slope_unit

    slope_unit = format_slope_unit(y_unit, x_unit)
    slope_text = f"{y_label or 'y'} = {fit.a:.4g}·{x_label or 'x'} + {fit.b:.4g}"
    if slope_unit:
        slope_text += f" [{slope_unit}]"
    ax.text(0.05, 0.88, slope_text, transform=ax.transAxes, fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))
    ax.text(0.05, 0.80, f"R = {fit.R:.4f}", transform=ax.transAxes, fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="lower right")
    fig.tight_layout()

    name = filename.strip().replace("/", "_").replace("\\", "_").replace(" ", "_")
    if not name:
        name = datetime.now().strftime("fit_%Y%m%d_%H%M%S")
    if not name.lower().endswith(".png"):
        name += ".png"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / name
    fig.savefig(path, dpi=150)
    if plt.get_backend().lower() != "agg":
        try:
            plt.show()
        except Exception:
            pass
    plt.close(fig)
    return path.resolve()
