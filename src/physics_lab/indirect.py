from dataclasses import dataclass, field

import numpy as np
import pint

from .constants import format_constants_table
from .formula import FormulaError, expr_text, parse_formula
from .io import (
    input_choice,
    input_confirm,
    input_data,
    input_float,
    input_formula,
    input_nonneg_float,
    input_positive_float,
    input_unit,
    print_indirect_report,
    save_report,
)
from .outlier import grubbs_test
from .propagation import propagate
from .result import format_result
from .uncertainty import get_uncertainty, type_a, type_b
from .units import UnitError, format_unit, parse_unit, ureg

ALPHA = 0.05


@dataclass
class Variable:
    """一个测量变量及其不确定度与单位。"""

    name: str
    unit: str
    mean: float
    u: float
    mode: str = "A"
    data_original: np.ndarray | None = None
    data_cleaned: np.ndarray | None = None
    removed: list = field(default_factory=list)
    ins_error: float = 0.0
    std: float = 0.0
    ua: float = 0.0
    ub: float = 0.0

    def result_text(self) -> str:
        return format_result(self.mean, self.u, self.unit)


def _input_variable_mode_a(name: str) -> Variable:
    """完整流程：多次测量 -> Grubbs -> 均值/标准差 -> uA/uB -> 合成。"""
    data = input_data(f"请输入变量 {name} 的测量数据（空格或逗号分隔）: ")
    ins_error = input_positive_float(f"请输入变量 {name} 的仪器误差: ")
    if data.size >= 3:
        cleaned, removed = grubbs_test(data, alpha=ALPHA)
    else:
        cleaned, removed = data, []
        print("数据少于 3 个，跳过 Grubbs 检验。")
    mean = float(np.mean(cleaned))
    std = float(np.std(cleaned, ddof=1))
    ua = type_a(cleaned)
    ub = type_b(ins_error)
    u = get_uncertainty(cleaned, ins_error)
    unit = input_unit(f"请输入变量 {name} 的单位（无量纲直接回车）: ", allow_empty=True)
    return Variable(
        name=name,
        unit=unit,
        mean=mean,
        u=u,
        mode="A",
        data_original=data,
        data_cleaned=cleaned,
        removed=removed,
        ins_error=ins_error,
        std=std,
        ua=ua,
        ub=ub,
    )


def _input_variable_mode_b(name: str) -> Variable:
    """直接输入已处理好的 均值/不确定度/单位。"""
    mean = input_float(f"请输入变量 {name} 的测量平均值: ")
    u = input_nonneg_float(f"请输入变量 {name} 的不确定度 u_{name}（无不确定度输 0）: ")
    unit = input_unit(f"请输入变量 {name} 的单位（无量纲直接回车）: ", allow_empty=True)
    return Variable(name=name, unit=unit, mean=mean, u=u, mode="B")


def _build_unit_map(variables: list[Variable]) -> dict[str, pint.Unit]:
    from .constants import CONSTANTS

    unit_map = {v.name: parse_unit(v.unit) for v in variables}
    for c in CONSTANTS.values():
        unit_map[c.symbol] = parse_unit(c.unit)
    return unit_map


def run_indirect() -> None:
    print()
    print("内置常数表（公式中可直接使用这些符号）:")
    print(format_constants_table())
    print()

    while True:
        raw = input_formula()
        try:
            formula = parse_formula(raw)
        except FormulaError as exc:
            print(f"公式错误: {exc}")
            continue
        if not formula.vars:
            print("公式中没有测量变量，请至少包含一个需要测量的量。")
            continue
        break

    print(f"解析成功: {expr_text(formula.expr)}")
    print(f"测量变量: {'、'.join(formula.vars)}")
    if formula.constants:
        print(
            "已识别内置常数: "
            + "、".join(f"{c.symbol}（{c.name}）" for c in formula.constants)
        )
    print()
    choice = input_choice(
        "所有变量的输入方式（对每个变量统一生效）: ",
        ["输入多次测量的原始数据（走完整处理流程）", "直接输入 均值与不确定度"],
    )
    input_function = _input_variable_mode_a if choice == 1 else _input_variable_mode_b

    variables = [input_function(name) for name in formula.vars]

    target_unit = input_unit(
        "请输入期望的输出单位（回车使用推导出的单位）: ", allow_empty=True
    )

    unit_map = _build_unit_map(variables)
    values = {v.name: v.mean for v in variables}
    uncs = {v.name: v.u for v in variables}

    try:
        prop = propagate(formula.expr, formula.vars, values, uncs, unit_map)
    except (UnitError, ValueError) as exc:
        print(f"误差传递失败: {exc}")
        return

    result_unit = prop.result_unit
    N_c, uN_c = prop.N, prop.uN
    if target_unit:
        try:
            target = parse_unit(target_unit)
            n_t = float(ureg.Quantity(prop.N, prop.unit_obj).to(target).magnitude)
            factor = n_t / prop.N if prop.N != 0 else 1.0
            N_c, uN_c = prop.N * factor, prop.uN * factor
            result_unit = format_unit(target)
        except (UnitError, pint.errors.PintError) as exc:
            print(f"输出单位换算失败: {exc}，使用推导单位。")

    result_text = format_result(N_c, uN_c, result_unit)
    label = formula.label or "N"

    report_text = print_indirect_report(
        formula_text=raw,
        label=label,
        formula=formula,
        variables=variables,
        prop=prop,
        target_unit=target_unit,
        result_text=f"{label} = {result_text}",
        final_N=N_c,
        final_uN=uN_c,
    )

    if input_confirm("是否保存本次报告？(y/n): "):
        from .io import input_optional_text

        filename = input_optional_text("请输入文件名（回车使用默认名）: ")
        path = save_report(report_text, filename)
        print(f"报告已保存至: {path}")
