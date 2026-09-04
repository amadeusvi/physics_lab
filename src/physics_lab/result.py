from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal
from math import isfinite


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
    mean_d = Decimal(str(mean)).quantize(q, rounding=ROUND_HALF_UP)
    return float(mean_d), float(u_d.quantize(q))


def format_result(mean: float, u: float, unit: str = "") -> str:
    """生成最终结果字符串，如 "1.08 ± 0.05"（可附加单位）。"""
    mean_r, u_r = round_result(mean, u)
    places = max(0, -Decimal(str(u_r)).normalize().as_tuple().exponent)
    if places == 0:
        text = f"{int(mean_r)} ± {int(u_r)}"
    else:
        text = f"{mean_r:.{places}f} ± {u_r:.{places}f}"
    if unit:
        return f"({text}) {unit}"
    return text
