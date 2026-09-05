import pytest

from physics_lab.formula import (
    FormulaError,
    detect_monomial,
    expr_text,
    parse_formula,
    partial_derivatives,
)


class TestParseFormula:
    def test_basic_with_label(self):
        f = parse_formula("g = 4*pi^2*L/T^2")
        assert f.label == "g"
        assert f.vars == ["L", "T"]
        assert [c.symbol for c in f.constants] == ["pi"]

    def test_without_label(self):
        f = parse_formula("x + y")
        assert f.label == ""
        assert f.vars == ["x", "y"]
        assert f.constants == []

    def test_power_notation_and_implicit_multiplication(self):
        f = parse_formula("4pi^2*L/T^2")
        assert f.vars == ["L", "T"]

    def test_functions(self):
        f = parse_formula("a*sin(b) + sqrt(d)")
        assert set(f.vars) == {"a", "b", "d"}

    def test_greek_label_and_variable(self):
        f = parse_formula("ρ = 4m/(pi*d*d)")
        assert f.label == "ρ"
        assert f.vars == ["m", "d"]

    def test_fullwidth_and_unicode_operators(self):
        f = parse_formula("g ＝ 4×pi^2×L÷（T^2）")
        assert f.vars == ["L", "T"]

    def test_constants_not_variables(self):
        f = parse_formula("t = sqrt(2*h_2/g_n)")
        assert "g_n" not in f.vars
        assert [c.symbol for c in f.constants] == ["g_n"]

    def test_constant_collision_notice(self):
        f = parse_formula("E = m*g_n*h")
        assert f.vars == ["m"]
        assert {c.symbol for c in f.constants} == {"g_n", "h"}

    def test_empty_formula(self):
        with pytest.raises(FormulaError):
            parse_formula("")

    def test_syntax_error(self):
        with pytest.raises(FormulaError):
            parse_formula("g = sin(L")

    def test_no_variables(self):
        with pytest.raises(FormulaError):
            parse_formula("4*pi^2/2")

    def test_label_collides_with_constant(self):
        with pytest.raises(FormulaError):
            parse_formula("pi = x + y")

    def test_unsupported_function(self):
        with pytest.raises(FormulaError):
            parse_formula("N = gamma(x)")


class TestDerivativesAndMonomial:
    def test_partial_derivatives_text(self):
        f = parse_formula("g = 4*pi^2*L/T^2")
        derivs = partial_derivatives(f.expr, f.vars)
        assert expr_text(derivs["L"]) == "4*pi^2/T^2"
        assert expr_text(derivs["T"]) == "-8*pi^2*L/T^3"

    def test_monomial_detected(self):
        f = parse_formula("g = 4*pi^2*L/T^2")
        assert detect_monomial(f.expr, f.vars) == {"L": 1.0, "T": -2.0}

    def test_monomial_with_fractional_power(self):
        f = parse_formula("T = 2*pi*sqrt(L/g_n)")
        assert detect_monomial(f.expr, f.vars) == {"L": 0.5}

    def test_non_monomial_sum(self):
        f = parse_formula("N = x + y")
        assert detect_monomial(f.expr, f.vars) is None

    def test_non_monomial_function(self):
        f = parse_formula("N = x*sin(y)")
        assert detect_monomial(f.expr, f.vars) is None

    def test_non_monomial_variable_exponent(self):
        f = parse_formula("N = 2^x")
        assert detect_monomial(f.expr, f.vars) is None
