import numpy as np


def get_mean(data: np.ndarray) -> np.float64:
    """计算样本的算术平均值。"""
    return data.mean()


def get_std(data: np.ndarray) -> np.float64:
    """计算样本标准差（贝塞尔公式，自由度为 n-1）。"""
    return data.std(ddof=1)
