from decimal import ROUND_CEILING, ROUND_HALF_EVEN, Decimal
from math import floor, isfinite, log10

_SUPERSCRIPTS = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def round_uncertainty(u: float) -> float:
    """将不确定度修约为 1 位有效数字，末位只进不舍。

    例：0.0431 -> 0.05，0.021 -> 0.03，0.48 -> 0.5，1.2 -> 2。
    """
    if not isfinite(u) or u <= 0:
        raise ValueError("不确定度必须为有限正数")
    d = Decimal(str(u))
    factor = Decimal(1).scaleb(d.adjusted())
    rounded = (d / factor).to_integral_value(rounding=ROUND_CEILING) * factor
    return float(rounded)


def round_result(mean: float, u: float) -> tuple[float, float]:
    """按修约后的不确定度末位对齐测量值，返回 (mean, u)。"""
    u_d = Decimal(str(round_uncertainty(u))).normalize()
    places = max(0, -u_d.as_tuple().exponent)
    q = Decimal(1).scaleb(-places)
    mean_d = Decimal(str(mean)).quantize(q, rounding=ROUND_HALF_EVEN)
    return float(mean_d), float(u_d.quantize(q))


def _needs_scientific(mean_r: float, u_r: float, places: int) -> bool:
    """判断是否需要科学记数法表示（文档判据：尾随零歧义、数值过大/过小）。"""
    if u_r == 0:
        return False
    if places == 0 and u_r % 10 == 0:
        return True
    if abs(mean_r) >= 1e6:
        return True
    if u_r < 1e-6:
        return True
    return False


def _scientific_text(mean_r: float, u_r: float) -> str:
    """生成 '(9.65 ± 0.05)×10⁴' 形式中的数值部分。"""
    if mean_r != 0:
        exponent = int(floor(log10(abs(mean_r))))
    else:
        exponent = int(floor(log10(u_r)))
    mantissa = mean_r / 10**exponent
    u_mantissa = u_r / 10**exponent
    places = max(0, -Decimal(str(u_mantissa)).adjusted())
    text = f"{mantissa:.{places}f} ± {u_mantissa:.{places}f}"
    return f"({text})×10{str(exponent).translate(_SUPERSCRIPTS)}"


def format_result(mean: float, u: float, unit: str = "") -> str:
    """生成最终结果字符串，如 "1.08 ± 0.05"（可附加单位）。

    数值过大/过小或不确定度尾随零歧义时自动改用科学记数法，
    如 "(9.65 ± 0.05)×10⁴ g"。
    """
    mean_r, u_r = round_result(mean, u)
    places = max(0, -Decimal(str(u_r)).normalize().as_tuple().exponent)
    if _needs_scientific(mean_r, u_r, places):
        text = _scientific_text(mean_r, u_r)
    elif places == 0:
        text = f"{int(mean_r)} ± {int(u_r)}"
    else:
        text = f"{mean_r:.{places}f} ± {u_r:.{places}f}"
    if unit:
        if text.startswith("("):
            return f"{text} {unit}"
        return f"({text}) {unit}"
    return text
