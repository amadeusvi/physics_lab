from math import fabs, sqrt

import numpy as np
from scipy.stats import t

from .method import get_mean, get_std


def _get_t_critical(n: int, alpha: float) -> float:
    """t 分布临界值，自由度 n-2。

    采用国内《大学物理实验》教材约定的单侧公式（显著性水平 alpha/n），
    使临界值与教材附录的格拉布斯系数表一致。
    """
    return t.ppf(q=1 - alpha / n, df=n - 2)


def _calculate_grub(n: int, alpha: float) -> float:
    """由 t 分布临界值换算 Grubbs 临界值 G。"""
    t_value = _get_t_critical(n, alpha)
    return (n - 1) / sqrt(n) * sqrt(t_value * t_value / (n - 2 + t_value * t_value))


def _find_maxdis_index(data: np.ndarray) -> int:
    """返回与平均值偏差最大的数据所在下标。"""
    return int(np.argmax(np.abs(data - get_mean(data))))


def grubbs_test(
    data: np.ndarray, alpha: float = 0.05
) -> tuple[np.ndarray, list[tuple[float, float, float]]]:
    """Grubbs 准则剔除粗大误差。

    重复检验与平均值偏差最大的数据：若统计量 G 大于临界值则剔除，
    直到无异常值或剩余数据不足 3 个为止。

    返回 (清洗后的数据, 剔除记录)，剔除记录中每条为
    (被剔除值, G 统计量, 临界值)。
    """
    data = np.asarray(data, dtype=float)
    if data.size < 3:
        raise ValueError("Grubbs 检验至少需要 3 个测量数据")

    removed: list[tuple[float, float, float]] = []

    while data.size >= 3:
        std = get_std(data)
        if std == 0:
            break
        g_crit = _calculate_grub(data.size, alpha)
        idx = _find_maxdis_index(data)
        value = float(data[idx])
        g_stat = fabs(get_mean(data) - value) / std
        if g_stat <= g_crit:
            break
        removed.append((value, g_stat, g_crit))
        data = np.delete(data, idx)

    return data, removed
