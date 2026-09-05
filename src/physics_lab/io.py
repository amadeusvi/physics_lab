from datetime import datetime
from pathlib import Path

import numpy as np

from .units import UnitError, format_unit, parse_unit

_SEPARATORS = ("，", "、", "；", ";", "\u3000")

REPORT_DIR = Path("reports")


def print_welcome() -> None:
    print("=" * 56)
    print("大学物理实验数据处理工具")
    print("直接测量法：均值 | 样本标准差 | Grubbs 检验 | 不确定度")
    print("间接测量法：公式解析 | 误差传递 | 单位换算 | 有效数字修约")
    print("=" * 56)


def input_mode() -> str:
    """读取处理模式：1 直接测量，2 间接测量。"""
    while True:
        raw = input("请选择处理模式：1) 直接测量法  2) 间接测量法: ").strip()
        if raw == "1":
            return "direct"
        if raw == "2":
            return "indirect"
        print("请输入 1 或 2。")


def input_choice(prompt: str, options: list[str]) -> int:
    """列出选项并读取 1 起的序号。"""
    for i, option in enumerate(options, start=1):
        print(f"  {i}) {option}")
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw)
        print(f"请输入 1 到 {len(options)} 之间的序号。")


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


def input_float(prompt: str) -> float:
    """读取任意实数。"""
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("请输入一个数字。")


def input_nonneg_float(prompt: str) -> float:
    """读取非负实数（不确定度可为 0 表示精确量）。"""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print("请输入一个数字。")
            continue
        if value < 0:
            print("不能为负数，请重新输入。")
            continue
        return value


def input_formula() -> str:
    """读取一行公式文本。"""
    return input(
        "请输入公式（如 g = 4*pi^2*L/T^2，支持 ^ 幂、sin/ln/sqrt 等函数）: "
    ).strip()


def input_unit(prompt: str, allow_empty: bool = False) -> str:
    """读取单位字符串并用 pint 校验，非法时提示重试。"""
    while True:
        raw = input(prompt).strip()
        if not raw:
            if allow_empty:
                return ""
            print("单位不能为空。")
            continue
        try:
            parse_unit(raw)
        except UnitError as exc:
            print(f"{exc}，请重新输入。")
            continue
        return raw


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
) -> str:
    """打印完整的数据处理报告（含中间过程，保证透明性），并返回报告文本。"""
    line = "-" * 56
    lines = [
        "=" * 56,
        f"原始数据 (n={data_original.size}): {np.round(data_original, 6).tolist()}",
        f"仪器误差: {ins_error}",
        line,
        f"Grubbs 检验（显著性水平 alpha={alpha}）:",
    ]
    if removed:
        for value, g_stat, g_crit in removed:
            lines.append(f"  剔除 {value:g}：G = {g_stat:.4f} > 临界值 {g_crit:.4f}")
    else:
        lines.append("  无异常值")
    lines += [
        f"剔除后数据 (n={data_cleaned.size}): {np.round(data_cleaned, 6).tolist()}",
        line,
        "统计量计算:",
        f"  算术平均值 x_bar = {mean:.6f}",
        f"  样本标准差 S     = {std:.6f}",
        f"  A 类不确定度 u_A = S / sqrt(n)     = {ua:.6f}",
        f"  B 类不确定度 u_B = delta / sqrt(3) = {ub:.6f}",
        f"  合成不确定度 u_C = sqrt(u_A^2 + u_B^2) = {u:.6f}",
        line,
        "修约（不确定度保留 1 位有效数字，只进不舍）:",
        f"  u_C   = {u:.6f} -> {u_r:g}",
        f"  x_bar = {mean:.6f} -> {mean_r:g}（末位对齐）",
        line,
        f"最终结果: x = {result}",
        "=" * 56,
    ]
    text = "\n".join(lines)
    print(text)
    print()
    return text


def save_report(text: str, filename: str = "") -> Path:
    """将报告文本保存到专门的 reports 文件夹，返回保存路径。

    filename 为空时使用带时间戳的默认文件名，自动补全 .txt 后缀。
    """
    name = filename.strip().replace("/", "_").replace("\\", "_").replace(" ", "_")
    if not name:
        name = datetime.now().strftime("report_%Y%m%d_%H%M%S")
    if not name.lower().endswith(".txt"):
        name += ".txt"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / name
    path.write_text(text, encoding="utf-8")
    return path.resolve()


def _variable_lines(var) -> list[str]:
    """生成间接测量报告中单个变量的段落。"""
    lines = []
    if var.mode == "A":
        lines.append(f"变量 {var.name} [完整流程]:")
        lines.append(f"  原始数据 (n={var.data_original.size}): "
                     f"{np.round(var.data_original, 6).tolist()}")
        lines.append(f"  仪器误差: {var.ins_error:g}")
        if var.removed:
            for value, g_stat, g_crit in var.removed:
                lines.append(
                    f"  Grubbs 剔除 {value:g}：G = {g_stat:.4f} > 临界值 {g_crit:.4f}"
                )
        else:
            lines.append("  Grubbs 检验: 无异常值")
        lines.append(
            f"  剔除后数据 (n={var.data_cleaned.size}): "
            f"{np.round(var.data_cleaned, 6).tolist()}"
        )
        lines.append(f"  平均值 {var.name}_bar = {var.mean:.6f}")
        lines.append(f"  样本标准差 S     = {var.std:.6f}")
        lines.append(f"  u_A = S/sqrt(n) = {var.ua:.6f}")
        lines.append(f"  u_B = delta/sqrt(3) = {var.ub:.6f}")
        lines.append(f"  合成不确定度 u_{var.name} = {var.u:.6f}")
    else:
        lines.append(f"变量 {var.name} [直接输入]:")
        lines.append(f"  平均值 {var.name}_bar = {var.mean:g}")
        lines.append(f"  不确定度 u_{var.name} = {var.u:g}")
    unit_text = format_unit(parse_unit(var.unit)) if var.unit else ""
    from .result import format_result

    lines.append(f"  测量结果: {var.name} = {format_result(var.mean, var.u, unit_text)}")
    return lines


def print_indirect_report(
    formula_text: str,
    label: str,
    formula,
    variables: list,
    prop,
    target_unit: str,
    result_text: str,
    final_N: float | None = None,
    final_uN: float | None = None,
) -> str:
    """打印间接测量法完整报告（含各变量统计、误差传递与修约过程）。

    final_N/final_uN 为单位换算后的值；缺省时使用 prop 中的原始值。
    """
    line = "-" * 56
    lines = [
        "=" * 56,
        "间接测量法数据处理报告",
        line,
        f"公式: {formula_text}",
    ]
    if formula.constants:
        lines.append(
            "已识别内置常数: "
            + "、".join(f"{c.symbol}（{c.name}）" for c in formula.constants)
        )
    lines.append(line)
    for var in variables:
        lines += _variable_lines(var)
        lines.append(line)
    lines.append("误差传递（一般式 u_N^2 = sum((dN/dx_i)^2 * u_i^2)）:")
    for term in prop.terms:
        unit_txt = f" {term.deriv_unit}" if term.deriv_unit else ""
        lines.append(
            f"  dN/d{term.var} = {term.deriv_text} = {term.deriv_value:.6g}{unit_txt}"
        )
    lines.append("  传递项:")
    for term in prop.terms:
        lines.append(
            f"    |dN/d{term.var}| * u_{term.var} = "
            f"{abs(term.deriv_value):.6g} * {term.u:g} = {term.contribution:.6g}"
        )
    unit_txt = f" {prop.result_unit}" if prop.result_unit else ""
    lines.append(f"  N   = {prop.N:.6g}{unit_txt}")
    if prop.powers is not None and prop.rel_formula and prop.N != 0:
        rel = prop.uN_rel / prop.N
        lines.append("教材捷径（幂单项式 u_N/N = sqrt(sum((k_i*u_i/x_i)^2))）:")
        lines.append(f"  {prop.rel_formula} = {rel:.6g}")
        lines.append(
            f"  u_N = N * {rel:.6g} = {prop.uN_rel:.6g}（与一般式一致）"
        )
    lines.append(f"  u_N = sqrt(sum(贡献^2)) = {prop.uN:.6g}{unit_txt}")
    lines.append(line)
    n_final = prop.N if final_N is None else final_N
    u_final = prop.uN if final_uN is None else final_uN
    if target_unit:
        lines.append(f"已换算到目标单位: {format_unit(parse_unit(target_unit))}")
        lines.append(f"  换算后 N = {n_final:.6g}，u_N = {u_final:.6g}")
        lines.append(line)
    lines.append("修约（不确定度保留 1 位有效数字，只进不舍）:")
    from .result import round_result, round_uncertainty

    lines.append(f"  u_N = {u_final:.6g} -> {round_uncertainty(u_final):g}")
    n_r, _ = round_result(n_final, u_final)
    lines.append(f"  N   = {n_final:.6g} -> {n_r:g}（末位对齐）")
    lines.append(line)
    lines.append(f"最终结果: {result_text}")
    lines.append("=" * 56)
    text = "\n".join(lines)
    print(text)
    print()
    return text
