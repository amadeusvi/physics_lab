import numpy as np

_SEPARATORS = ("，", "、", "；", ";", "\u3000")


def print_welcome() -> None:
    print("=" * 56)
    print("大学物理实验数据处理工具")
    print("直接测量法：均值 | 样本标准差 | Grubbs 检验 | 不确定度")
    print("=" * 56)


def input_data(prompt: str = "请输入实验数据（空格或逗号分隔）: ") -> np.ndarray:
    """读取一行测量数据并解析为 numpy 数组，非法输入时提示重试。"""
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("输入为空，请重新输入。")
            continue
        for sep in _SEPARATORS:
            raw = raw.replace(sep, " ")
        raw = raw.replace(",", " ")
        try:
            data = np.array([float(item) for item in raw.split()])
        except ValueError:
            print("包含无法识别的数字，请检查后重新输入。")
            continue
        if data.size < 2:
            print("至少需要 2 个测量数据，请重新输入。")
            continue
        return data


def input_positive_float(prompt: str) -> float:
    """读取一个正数（如仪器误差），带校验与重试。"""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print("请输入一个数字。")
            continue
        if value <= 0:
            print("必须为正数，请重新输入。")
            continue
        return value


def input_confirm(prompt: str = "是否继续？(y/n): ") -> bool:
    """读取 y/n 确认。"""
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("y", "yes", "是"):
            return True
        if raw in ("n", "no", "否"):
            return False
        print("请输入 y 或 n。")


def input_optional_text(prompt: str = "请输入单位（可直接回车跳过）: ") -> str:
    return input(prompt).strip()


def print_report(
    data_original: np.ndarray,
    data_cleaned: np.ndarray,
    removed: list[tuple[float, float, float]],
    ins_error: float,
    alpha: float,
    mean: float,
    std: float,
    ua: float,
    ub: float,
    u: float,
    mean_r: float,
    u_r: float,
    result: str,
) -> None:
    """打印完整的数据处理报告（含中间过程，保证透明性）。"""
    line = "-" * 56
    print()
    print("=" * 56)
    print(f"原始数据 (n={data_original.size}): {np.round(data_original, 6).tolist()}")
    print(f"仪器误差: {ins_error}")
    print(line)
    print(f"Grubbs 检验（显著性水平 alpha={alpha}）:")
    if removed:
        for value, g_stat, g_crit in removed:
            print(f"  剔除 {value:g}：G = {g_stat:.4f} > 临界值 {g_crit:.4f}")
    else:
        print("  无异常值")
    print(f"剔除后数据 (n={data_cleaned.size}): {np.round(data_cleaned, 6).tolist()}")
    print(line)
    print("统计量计算:")
    print(f"  算术平均值 x_bar = {mean:.6f}")
    print(f"  样本标准差 S     = {std:.6f}")
    print(f"  A 类不确定度 u_A = S / sqrt(n)     = {ua:.6f}")
    print(f"  B 类不确定度 u_B = delta / sqrt(3) = {ub:.6f}")
    print(f"  合成不确定度 u_C = sqrt(u_A^2 + u_B^2) = {u:.6f}")
    print(line)
    print("修约（不确定度保留 1 位有效数字，只进不舍）:")
    print(f"  u_C   = {u:.6f} -> {u_r:g}")
    print(f"  x_bar = {mean:.6f} -> {mean_r:g}（末位对齐）")
    print(line)
    print(f"最终结果: x = {result}")
    print("=" * 56)
    print()
