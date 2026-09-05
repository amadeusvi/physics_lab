from dataclasses import dataclass

import sympy


@dataclass(frozen=True)
class Constant:
    """数学/物理常数。

    symbol: 公式中使用的符号
    name:   中文名称
    value:  数值（CODATA 2018 推荐值，标注 exact 的为定义值）
    unit:   pint 单位字符串
    uncertainty: 常数的标准不确定度（定义值/数学常数为 None）
    """

    symbol: str
    name: str
    value: float
    unit: str
    uncertainty: float | None = None


CONSTANTS: dict[str, Constant] = {
    "pi": Constant("pi", "圆周率", 3.141592653589793, ""),
    "e": Constant("e", "自然常数（欧拉数）", 2.718281828459045, ""),
    "c": Constant("c", "真空光速", 299792458.0, "m/s"),
    "h": Constant("h", "普朗克常数", 6.62607015e-34, "J*s"),
    "hbar": Constant("hbar", "约化普朗克常数", 1.0545718176461565e-34, "J*s"),
    "k_B": Constant("k_B", "玻尔兹曼常数", 1.380649e-23, "J/K"),
    "N_A": Constant("N_A", "阿伏伽德罗常数", 6.02214076e23, "1/mol"),
    "G": Constant("G", "万有引力常数", 6.67430e-11, "m^3/(kg*s^2)", 1.5e-15),
    "e_q": Constant("e_q", "元电荷", 1.602176634e-19, "C"),
    "epsilon_0": Constant("epsilon_0", "真空介电常数", 8.8541878128e-12, "F/m"),
    "mu_0": Constant("mu_0", "真空磁导率", 1.25663706212e-6, "N/A^2"),
    "R": Constant("R", "摩尔气体常数", 8.31446261815324, "J/(mol*K)"),
    "g_n": Constant("g_n", "标准重力加速度", 9.80665, "m/s^2"),
    "sigma": Constant("sigma", "斯特藩-玻尔兹曼常数", 5.670374419e-8, "W/(m^2*K^4)"),
}

_ALIASES = {"π": "pi", "ħ": "hbar"}


def constant_symbol(name: str) -> Constant | None:
    """按符号或别名查找常数（π -> pi，ħ -> hbar），找不到返回 None。"""
    return CONSTANTS.get(name) or CONSTANTS.get(_ALIASES.get(name, ""))


def sympy_namespace() -> dict[str, sympy.Expr]:
    """生成注入 sympy 解析器的符号命名空间。

    pi 与 e 直接映射到 sympy 的 NumberSymbol，其余常数为普通 Symbol。
    """
    ns: dict[str, sympy.Expr] = {"pi": sympy.pi, "e": sympy.E}
    for symbol, c in CONSTANTS.items():
        if symbol in ("pi", "e"):
            continue
        ns[symbol] = sympy.Symbol(symbol)
    return ns


def format_constants_table() -> str:
    """格式化常数表（用于交互提示与报告）。"""
    rows = [("符号", "名称", "数值", "单位")]
    for c in CONSTANTS.values():
        value = f"{c.value:g}"
        if c.uncertainty is not None:
            value += f" ± {c.uncertainty:g}"
        rows.append((c.symbol, c.name, value, c.unit if c.unit else "（无量纲）"))
    widths = [max(len(row[i]) for row in rows) for i in range(4)]
    lines = []
    for row in rows:
        lines.append(
            "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip()
        )
    lines.insert(1, "-" * (sum(widths) + 6))
    return "\n".join(lines)
