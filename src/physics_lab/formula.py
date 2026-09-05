import re
from dataclasses import dataclass, field
from tokenize import TokenError

import sympy
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from .constants import Constant, constant_symbol, sympy_namespace

_TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)

_ALLOWED_FUNCTIONS = {
    "sin", "cos", "tan", "sec", "csc", "cot",
    "asin", "acos", "atan",
    "sinh", "cosh", "tanh",
    "ln", "log", "exp", "sqrt", "abs",
}


class FormulaError(ValueError):
    """公式解析或校验错误。"""


@dataclass
class Formula:
    """解析后的公式。

    expr: 等号右侧的 sympy 表达式
    label: 等号左侧的结果符号（可空字符串）
    vars: 自由变量（按在公式中首次出现的顺序）
    constants: 公式中用到的内置常数
    """

    expr: sympy.Expr
    label: str = ""
    vars: list[str] = field(default_factory=list)
    constants: list[Constant] = field(default_factory=list)


_NORMALIZE = [
    ("（", "("), ("）", ")"), ("＝", "="),
    ("×", "*"), ("÷", "/"), ("·", "*"),
    ("−", "-"),
    ("＾", "^"),
]
_REPLACE = {"π": "pi", "ħ": "hbar", "√": "sqrt"}

_GLOBAL_EXCLUDED = {"S", "N", "I", "E", "O", "Q", "C", "D"}


def _global_namespace() -> dict[str, object]:
    """sympy 命名空间（函数、常数），剔除会抢占用户变量名的单字母符号。

    剔除后 S/N/I/E/O/Q/C/D 会被 auto_symbol 识别为普通测量变量。
    """
    namespace = {name: getattr(sympy, name) for name in dir(sympy)}
    for name in _GLOBAL_EXCLUDED:
        namespace.pop(name, None)
    return namespace

def _normalize_text(text: str) -> str:
    raw = text.strip()
    for old, new in _NORMALIZE:
        raw = raw.replace(old, new)
    for old, new in _REPLACE.items():
        raw = raw.replace(old, new)
    return raw


def parse_formula(text: str) -> Formula:
    """解析用户输入的公式，如 'g = 4*pi^2*L/T^2' 或 '4*pi^2*L/T^2'。"""
    raw = _normalize_text(text)
    if not raw:
        raise FormulaError("公式不能为空")

    label = ""
    body = raw
    if "=" in raw:
        label, _, body = raw.partition("=")
        label = label.strip()
        if not label.isidentifier():
            raise FormulaError(f"等号左侧 '{label}' 不是合法的结果符号名")
        if constant_symbol(label):
            raise FormulaError(f"结果符号 '{label}' 与内置常数同名，请换一个名称")
        if not body.strip():
            raise FormulaError("等号右侧公式为空")

    try:
        expr = parse_expr(
            body,
            local_dict=sympy_namespace(),
            global_dict=_global_namespace(),
            transformations=_TRANSFORMATIONS,
        )
    except (SyntaxError, ValueError, TypeError, TokenError) as exc:
        raise FormulaError(f"公式无法解析: {exc}") from exc

    expr = _validate(expr)

    variables = [
        s.name for s in expr.free_symbols if constant_symbol(s.name) is None
    ]
    order = {name: idx for idx, name in enumerate(_find_order(body))}
    variables.sort(key=lambda name: order.get(name, len(order)))

    constants = [constant_symbol(name) for name in _used_constant_names(expr, body)]
    constants = [c for c in constants if c is not None]

    return Formula(expr=expr, label=label, vars=variables, constants=constants)


def _find_order(text: str) -> list[str]:
    """按出现顺序列出文本中的标识符（忽略括号后仍可靠的近似顺序）。"""
    return re.findall(r"[A-Za-z_]\w*", text)


_NUMBERSYMBOL_NAMES = {"Pi": "pi", "E": "e"}


def _used_constant_names(expr: sympy.Expr, text: str) -> list[str]:
    """返回表达式中出现的内置常数符号名（按公式文本中首次出现顺序）。"""
    names = {s.name for s in expr.free_symbols}
    names.update(
        _NUMBERSYMBOL_NAMES.get(type(s).__name__, "")
        for s in expr.atoms(sympy.NumberSymbol)
    )
    names = {n for n in names if constant_symbol(n)}
    order = {name: idx for idx, name in enumerate(_find_order(text))}
    return sorted(names, key=lambda n: order.get(n, len(order)))


def _validate(expr: sympy.Expr) -> sympy.Expr:
    if not expr.free_symbols:
        raise FormulaError("公式中没有测量变量（可能全部被识别为内置常数）")

    for atom in expr.atoms(sympy.Function):
        fname = type(atom).__name__.lower()
        if fname not in _ALLOWED_FUNCTIONS:
            raise FormulaError(f"不支持函数 '{fname}'")
    for atom in expr.atoms(sympy.Derivative, sympy.Integral, sympy.Sum):
        raise FormulaError("公式中不允许出现导数、积分或求和符号")
    if expr.has(sympy.I) or expr.has(sympy.zoo) or expr.has(sympy.nan):
        raise FormulaError("公式中包含复数或非法符号")
    return expr


def partial_derivatives(expr: sympy.Expr, variables: list[str]) -> dict[str, sympy.Expr]:
    """对每个变量求偏导数，返回 {变量名: 偏导表达式}。"""
    return {name: sympy.diff(expr, sympy.Symbol(name)) for name in variables}


def expr_text(expr: sympy.Expr) -> str:
    """把 sympy 表达式转成适合报告显示的文本（** 换成 ^）。"""
    from sympy.printing import StrPrinter

    return StrPrinter().doprint(expr).replace("**", "^")


def detect_monomial(expr: sympy.Expr, variables: list[str]) -> dict[str, float] | None:
    """检测表达式是否为幂单项式 N = C * prod(x_i^k_i)。

    是则返回 {变量名: 指数 k_i}（用于教材相对不确定度公式），否则返回 None。
    """
    if not variables or expr.has(sympy.Add):
        return None
    powers: dict[str, float] = {}
    for name in variables:
        var = sympy.Symbol(name)
        try:
            k = sympy.simplify(var * sympy.diff(expr, var) / expr)
        except (ZeroDivisionError, ValueError):
            return None
        if not k.is_number:
            return None
        value = float(k)
        powers[name] = value
    return powers
