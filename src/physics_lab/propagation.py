from dataclasses import dataclass
from math import sqrt

import pint
import sympy

from .formula import detect_monomial, expr_text
from .units import UnitError, eval_units, format_unit


@dataclass
class Term:
    """误差传递中的一项：变量 x_i 对结果不确定度的贡献。"""

    var: str
    deriv_text: str
    deriv_value: float
    deriv_unit: str
    u: float
    contribution: float


@dataclass
class Propagation:
    """误差传递计算结果。"""

    N: float
    uN: float
    terms: list[Term]
    result_unit: str
    unit_obj: pint.Unit
    powers: dict[str, float] | None
    uN_rel: float | None
    rel_formula: str


def propagate(
    expr: sympy.Expr,
    variables: list[str],
    values: dict[str, float],
    uncs: dict[str, float],
    unit_map: dict[str, pint.Unit],
) -> Propagation:
    """按一般式 u_N = sqrt(sum((dN/dx_i)^2 * u_i^2)) 计算误差传递。

    unit_map 须包含所有变量与公式中用到的常数对应的 pint Unit。
    若公式为幂单项式，同时给出教材相对不确定度捷径的结果。
    """
    subs = {sympy.Symbol(name): value for name, value in values.items()}
    from .constants import CONSTANTS

    for name, c in CONSTANTS.items():
        subs.setdefault(sympy.Symbol(name), c.value)
    try:
        N = float(expr.evalf(subs=subs))
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"公式求值失败（请检查变量取值）: {exc}") from exc

    try:
        result_quantity = eval_units(expr, unit_map)
    except UnitError as exc:
        raise UnitError(f"公式量纲错误: {exc}") from exc
    result_unit = result_quantity.units

    terms: list[Term] = []
    for name in variables:
        deriv = sympy.diff(expr, sympy.Symbol(name))
        try:
            deriv_value = float(deriv.evalf(subs=subs))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"偏导数 dN/d{name} 求值失败: {exc}") from exc
        try:
            deriv_unit_text = format_unit(eval_units(deriv, unit_map).units)
        except UnitError as exc:
            raise UnitError(f"偏导数 dN/d{name} 量纲错误: {exc}") from exc
        u = float(uncs.get(name, 0.0))
        terms.append(
            Term(
                var=name,
                deriv_text=expr_text(deriv),
                deriv_value=deriv_value,
                deriv_unit=deriv_unit_text,
                u=u,
                contribution=abs(deriv_value) * u,
            )
        )

    uN = sqrt(sum(term.contribution**2 for term in terms))

    powers = detect_monomial(expr, variables)
    uN_rel: float | None = None
    rel_formula = ""
    if powers is not None:
        rel_terms = []
        for name, k in powers.items():
            x = values[name]
            u = uncs.get(name, 0.0)
            if x == 0:
                uN_rel = None
                rel_formula = ""
                break
            if k != 0:
                rel_terms.append((name, k, u / x))
        if rel_terms:
            rel_formula = "uN/N = sqrt(" + " + ".join(
                f"({k:g}*u_{name}/{name})^2" for name, k, _ in rel_terms
            ) + ")"
            uN_rel = N * sqrt(sum((k * r) ** 2 for _, k, r in rel_terms))
        else:
            powers = None

    return Propagation(
        N=N,
        uN=uN,
        terms=terms,
        result_unit=format_unit(result_unit),
        unit_obj=result_unit,
        powers=powers,
        uN_rel=uN_rel,
        rel_formula=rel_formula,
    )
