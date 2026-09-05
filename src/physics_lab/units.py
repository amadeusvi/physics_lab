from typing import Any

import pint
import sympy
from pint.errors import UndefinedUnitError

ureg = pint.UnitRegistry()


class UnitError(ValueError):
    """单位解析或量纲运算错误。"""


_DIMENSIONLESS_FUNCTIONS = {
    "sin", "cos", "tan", "sec", "csc", "cot",
    "asin", "acos", "atan",
    "sinh", "cosh", "tanh",
    "ln", "log", "exp",
}


def parse_unit(text: str) -> pint.Unit:
    """解析单位字符串为 pint Unit，失败时抛出 UnitError。"""
    raw = text.strip()
    if not raw:
        return ureg.dimensionless
    try:
        return ureg.Unit(raw)
    except (UndefinedUnitError, pint.errors.PintError, ValueError, TypeError) as exc:
        raise UnitError(f"无法识别单位 '{raw}': {exc}") from exc


def format_unit(unit: Any) -> str:
    """格式化单位为美观的字符串，无量纲返回空字符串。"""
    try:
        text = f"{unit:~P}"
    except (ValueError, TypeError):
        text = str(unit)
    return text.strip()


def make_quantity(value: float, unit_text: str) -> pint.Quantity:
    """用数值与单位字符串构造 pint Quantity。"""
    unit = parse_unit(unit_text)
    return ureg.Quantity(value, unit)


def is_dimensionless(quantity: pint.Quantity) -> bool:
    """判断 Quantity 是否无量纲。"""
    try:
        quantity.to(ureg.dimensionless)
        return True
    except pint.errors.DimensionalityError:
        return False


def convert(value: float, unit: pint.Unit, target_text: str) -> float:
    """把数值从 unit 换算到目标单位，返回目标单位下的数值。"""
    try:
        target = parse_unit(target_text)
        quantity = ureg.Quantity(value, unit)
        return float(quantity.to(target).magnitude)
    except pint.errors.OffsetUnitCalculusError as exc:
        raise UnitError(
            f"单位 '{format_unit(unit)}' 是偏移量单位，公式运算请使用温差单位 "
            f"(如 delta_degC) 或开尔文: {exc}"
        ) from exc
    except pint.errors.PintError as exc:
        raise UnitError(f"单位换算失败: {exc}") from exc


def eval_units(expr: sympy.Expr, unit_map: dict[str, pint.Unit]) -> pint.Quantity:
    """沿 sympy 表达式推导结果的单位。

    unit_map: 符号名 -> pint Unit（须包含自由变量与所用常数）。
    运算中若发生量纲冲突（如 m + s），抛出 UnitError。
    """
    expr = sympy.sympify(expr)
    try:
        quantity = _eval_units(expr, unit_map)
    except pint.errors.OffsetUnitCalculusError as exc:
        raise UnitError(
            "偏移量单位（如 degC）不能参与乘除运算，请改用温差单位 delta_degC "
            "或开尔文 K"
        ) from exc
    except pint.errors.DimensionalityError as exc:
        raise UnitError(f"公式中存在量纲不一致的运算: {exc}") from exc
    except pint.errors.PintError as exc:
        raise UnitError(f"单位运算失败: {exc}") from exc
    return quantity


def _eval_units(expr: sympy.Expr, unit_map: dict[str, pint.Unit]) -> pint.Quantity:
    if expr.is_Symbol:
        name = expr.name
        if name not in unit_map:
            raise UnitError(f"未知符号 '{name}' 没有对应的单位")
        return ureg.Quantity(1.0, unit_map[name])
    if expr.is_number:
        return float(expr) * ureg.dimensionless
    if isinstance(expr, sympy.Pow):
        base = _eval_units(expr.base, unit_map)
        if not expr.exp.is_number:
            raise UnitError("幂指数必须为常数")
        return base ** float(expr.exp)
    if isinstance(expr, sympy.Mul):
        result = ureg.Quantity(1.0)
        for arg in expr.args:
            result *= _eval_units(arg, unit_map)
        return result
    if isinstance(expr, sympy.Add):
        result = _eval_units(expr.args[0], unit_map)
        for arg in expr.args[1:]:
            result += _eval_units(arg, unit_map)
        return result
    if isinstance(expr, sympy.Function):
        fname = type(expr).__name__.lower()
        if fname == "abs":
            return abs(_eval_units(expr.args[0], unit_map))
        if fname in _DIMENSIONLESS_FUNCTIONS:
            for arg in expr.args:
                _eval_units(arg, unit_map).to(ureg.dimensionless)
            return ureg.Quantity(1.0)
        raise UnitError(f"无法对函数 '{fname}' 进行量纲推导")
    raise UnitError(f"无法对表达式 {expr} 进行量纲推导")
