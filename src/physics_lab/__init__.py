__version__ = "0.3.0"

from .constants import CONSTANTS, Constant, format_constants_table
from .formula import FormulaError, detect_monomial, parse_formula, partial_derivatives
from .method import get_mean, get_std
from .outlier import grubbs_test
from .propagation import Propagation, Term, propagate
from .regression import (
    GraphicalResult,
    LinearFit,
    Point,
    format_slope_unit,
    graphical_result,
    least_squares,
)
from .result import format_result, round_result, round_uncertainty
from .uncertainty import get_uncertainty, type_a, type_b
from .units import UnitError, eval_units, parse_unit

__all__ = [
    "__version__",
    "CONSTANTS",
    "Constant",
    "format_constants_table",
    "parse_formula",
    "partial_derivatives",
    "detect_monomial",
    "FormulaError",
    "propagate",
    "Propagation",
    "Term",
    "UnitError",
    "eval_units",
    "parse_unit",
    "get_mean",
    "get_std",
    "grubbs_test",
    "type_a",
    "type_b",
    "get_uncertainty",
    "round_uncertainty",
    "round_result",
    "format_result",
    "least_squares",
    "LinearFit",
    "Point",
    "graphical_result",
    "GraphicalResult",
    "format_slope_unit",
]
