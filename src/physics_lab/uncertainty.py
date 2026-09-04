from math import sqrt

import numpy as np

from .method import get_std


def type_a(data: np.ndarray) -> float:
    """A 类不确定度：u_A = S / sqrt(n)，即平均值的标准偏差。"""
    data = np.asarray(data, dtype=float)
    if data.size < 2:
        raise ValueError("A 类不确定度至少需要 2 个测量数据")
    return float(get_std(data) / sqrt(data.size))


def type_b(ins_error: float) -> float:
    """B 类不确定度：按均匀分布近似，u_B = 仪器误差 / sqrt(3)。"""
    if ins_error <= 0:
        raise ValueError("仪器误差必须为正数")
    return ins_error / sqrt(3)


def get_uncertainty(data: np.ndarray, ins_error: float) -> float:
    """合成标准不确定度：u = sqrt(u_A^2 + u_B^2)。"""
    ua = type_a(data)
    ub = type_b(ins_error)
    return sqrt(ua * ua + ub * ub)
