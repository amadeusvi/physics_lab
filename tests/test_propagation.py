import math

import pytest

from physics_lab.formula import parse_formula
from physics_lab.propagation import propagate
from physics_lab.units import UnitError, parse_unit

UNIT_MAP = {
    "pi": parse_unit(""),
    "e": parse_unit(""),
    "c": parse_unit("m/s"),
    "h": parse_unit("J*s"),
    "hbar": parse_unit("J*s"),
    "k_B": parse_unit("J/K"),
    "N_A": parse_unit("1/mol"),
    "G": parse_unit("m^3/(kg*s^2)"),
    "e_q": parse_unit("C"),
    "epsilon_0": parse_unit("F/m"),
    "mu_0": parse_unit("N/A^2"),
    "R": parse_unit("J/(mol*K)"),
    "g_n": parse_unit("m/s^2"),
    "sigma": parse_unit("W/(m^2*K^4)"),
}


def test_gravity_formula_matches_hand_calculation():
    f = parse_formula("g = 4*pi^2*L/T^2")
    unit_map = dict(UNIT_MAP, L=parse_unit("m"), T=parse_unit("s"))
    prop = propagate(
        f.expr, f.vars, {"L": 1.080, "T": 2.080}, {"L": 0.005, "T": 0.004}, unit_map
    )
    expected_N = 4 * math.pi**2 * 1.080 / 2.080**2
    assert prop.N == pytest.approx(expected_N)
    dL = 4 * math.pi**2 / 2.080**2
    dT = -8 * math.pi**2 * 1.080 / 2.080**3
    expected_uN = math.sqrt((dL * 0.005) ** 2 + (dT * 0.004) ** 2)
    assert prop.uN == pytest.approx(expected_uN)
    assert prop.result_unit == "m/s²"


def test_relative_shortcut_agrees_with_general_formula():
    f = parse_formula("g = 4*pi^2*L/T^2")
    unit_map = dict(UNIT_MAP, L=parse_unit("m"), T=parse_unit("s"))
    prop = propagate(
        f.expr, f.vars, {"L": 1.080, "T": 2.080}, {"L": 0.005, "T": 0.004}, unit_map
    )
    assert prop.powers == {"L": 1.0, "T": -2.0}
    assert prop.uN_rel == pytest.approx(prop.uN, rel=1e-9)


def test_sum_propagation():
    f = parse_formula("N = x + y")
    unit_map = dict(UNIT_MAP, x=parse_unit("mm"), y=parse_unit("mm"))
    prop = propagate(f.expr, f.vars, {"x": 10.0, "y": 20.0}, {"x": 0.1, "y": 0.2}, unit_map)
    assert prop.N == pytest.approx(30.0)
    assert prop.uN == pytest.approx(math.sqrt(0.1**2 + 0.2**2))
    assert prop.powers is None


def test_kinetic_energy_units_and_values():
    f = parse_formula("E = m*v^2/2")
    unit_map = dict(UNIT_MAP, m=parse_unit("kg"), v=parse_unit("m/s"))
    prop = propagate(
        f.expr, f.vars, {"m": 2.0, "v": 3.0}, {"m": 0.01, "v": 0.05}, unit_map
    )
    assert prop.N == pytest.approx(9.0)
    assert prop.result_unit == "kg·m²/s²"
    assert prop.uN == pytest.approx(math.sqrt((4.5 * 0.01) ** 2 + (6.0 * 0.05) ** 2))


def test_dimension_error_raises():
    f = parse_formula("N = x + y")
    unit_map = dict(UNIT_MAP, x=parse_unit("m"), y=parse_unit("s"))
    with pytest.raises(UnitError):
        propagate(f.expr, f.vars, {"x": 1.0, "y": 2.0}, {"x": 0.1, "y": 0.1}, unit_map)


def test_constant_in_formula_has_unit():
    f = parse_formula("E = m*c^2")
    unit_map = dict(UNIT_MAP, m=parse_unit("kg"))
    prop = propagate(f.expr, f.vars, {"m": 1.0}, {"m": 0.01}, unit_map)
    assert prop.N == pytest.approx(299792458.0**2)
    assert prop.result_unit == "kg·m²/s²"


def test_zero_uncertainty_variable():
    f = parse_formula("N = x*y")
    unit_map = dict(UNIT_MAP, x=parse_unit("m"), y=parse_unit("m"))
    prop = propagate(f.expr, f.vars, {"x": 2.0, "y": 3.0}, {"x": 0.1, "y": 0.0}, unit_map)
    assert prop.uN == pytest.approx(0.3)
