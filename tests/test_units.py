import pint
import pytest
import sympy

from physics_lab.formula import parse_formula
from physics_lab.units import UnitError, eval_units, format_unit, parse_unit


class TestParseUnit:
    def test_simple(self):
        assert str(parse_unit("cm")) == "centimeter"
        assert str(parse_unit("m/s^2")) == "meter / second ** 2"

    def test_empty_is_dimensionless(self):
        assert parse_unit("").dimensionless

    def test_invalid_raises(self):
        with pytest.raises(UnitError):
            parse_unit("not_a_unit_xyz")


class TestEvalUnits:
    def test_derived_unit(self):
        f = parse_formula("g = 4*pi^2*L/T^2")
        q = eval_units(f.expr, {"L": parse_unit("m"), "T": parse_unit("s"), "pi": parse_unit("")})
        assert q.units == parse_unit("m/s^2")

    def test_energy_units(self):
        f = parse_formula("E = m*v^2/2")
        q = eval_units(f.expr, {"m": parse_unit("kg"), "v": parse_unit("m/s")})
        assert q.units == parse_unit("kg*m^2/s^2")

    def test_dimensionless_function(self):
        expr = sympy.sin(sympy.Symbol("x"))
        q = eval_units(expr, {"x": parse_unit("rad")})
        assert q.units.dimensionless

    def test_dimension_mismatch_raises(self):
        f = parse_formula("N = x + y")
        with pytest.raises(UnitError):
            eval_units(f.expr, {"x": parse_unit("m"), "y": parse_unit("s")})

    def test_sqrt_of_area(self):
        f = parse_formula("d = sqrt(S)")
        q = eval_units(f.expr, {"S": parse_unit("m^2")})
        assert q.units == parse_unit("m")


class TestFormatUnit:
    def test_pretty(self):
        assert format_unit(parse_unit("m/s^2")) == "m/s²"
        assert format_unit(parse_unit("kg*m/s^2")) == "kg·m/s²"

    def test_dimensionless_empty(self):
        assert format_unit(parse_unit("")) == ""


class TestConvert:
    def test_linear_conversion(self):
        from physics_lab.units import convert

        assert convert(1.0, parse_unit("m"), "cm") == pytest.approx(100.0)
        assert convert(9.8, parse_unit("m/s^2"), "cm/s^2") == pytest.approx(980.0)

    def test_incompatible_conversion_raises(self):
        from physics_lab.units import convert

        with pytest.raises(UnitError):
            convert(1.0, parse_unit("m"), "s")
