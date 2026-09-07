from dataclasses import dataclass

import numpy as np


@dataclass
class LinearFit:
    """最小二乘线性拟合结果，附带中间量便于报告透明展示。"""

    a: float
    b: float
    R: float
    n: int
    x_mean: float
    y_mean: float
    Lxy: float
    Lxx: float
    Lyy: float

    def equation(self, x_label: str = "x", y_label: str = "y") -> str:
        return f"{y_label} = {self.a:.6g}·{x_label} + {self.b:.6g}"


@dataclass
class Point:
    x: float
    y: float

    def __str__(self) -> str:
        return f"({self.x:.4g}, {self.y:.4g})"


@dataclass
class GraphicalResult:
    """图解法结果：在拟合直线上取两点求斜率，另取一点求截距。"""

    point_a: Point
    point_b: Point
    point_c: Point
    slope: float
    intercept: float


def least_squares(x: np.ndarray, y: np.ndarray) -> LinearFit:
    """按教材公式对 (x, y) 数据做最小二乘线性拟合。

    斜率 a = Lxy / Lxx，截距 b = y_bar - a*x_bar，
    相关系数 R = Lxy / sqrt(Lxx * Lyy)。
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("x 和 y 必须是一维数组")
    if x.size != y.size:
        raise ValueError("x 和 y 的数据个数必须相同")
    if x.size < 3:
        raise ValueError("最小二乘拟合至少需要 3 组数据")

    n = x.size
    x_mean = float(np.mean(x))
    y_mean = float(np.mean(y))
    Lxy = float(np.sum(x * y)) / n - x_mean * y_mean
    Lxx = float(np.sum(x * x)) / n - x_mean * x_mean
    Lyy = float(np.sum(y * y)) / n - y_mean * y_mean
    if Lxx == 0:
        raise ValueError("x 数据无变化，无法拟合直线")
    a = Lxy / Lxx
    b = y_mean - a * x_mean
    R = Lxy / (Lxx * Lyy) ** 0.5 if Lxx > 0 and Lyy > 0 else float("nan")
    return LinearFit(a=a, b=b, R=R, n=n, x_mean=x_mean, y_mean=y_mean,
                     Lxy=Lxy, Lxx=Lxx, Lyy=Lyy)


def graphical_result(fit: LinearFit, x_min: float, x_max: float) -> GraphicalResult:
    """图解法：在拟合直线的两端取两点 A、B 用两点式求斜率，另取中点 C 求截距。

    取点避开采样点（取 x_min/x_max 处的直线上点），
    斜率为 a = (y_B - y_A) / (x_B - x_A)，截距为 b = y_C - a * x_C。
    """
    point_a = Point(x_min, fit.a * x_min + fit.b)
    point_b = Point(x_max, fit.a * x_max + fit.b)
    x_c = (x_min + x_max) / 2
    point_c = Point(x_c, fit.a * x_c + fit.b)
    if x_max == x_min:
        raise ValueError("x 数据无变化，无法用图解法求斜率")
    slope = (point_b.y - point_a.y) / (point_b.x - point_a.x)
    intercept = point_c.y - slope * point_c.x
    return GraphicalResult(
        point_a=point_a, point_b=point_b, point_c=point_c,
        slope=slope, intercept=intercept,
    )


def format_slope_unit(y_unit: str, x_unit: str) -> str:
    """组合斜率单位，如 (y_unit='mV', x_unit='mA') -> 'mV/mA'。"""
    if y_unit and x_unit:
        return f"{y_unit}/{x_unit}"
    if y_unit:
        return y_unit
    if x_unit:
        return f"1/{x_unit}"
    return ""
