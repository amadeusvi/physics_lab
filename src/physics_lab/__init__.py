__version__ = "0.1.0"

from .method import get_mean, get_std
from .outlier import grubbs_test
from .result import format_result, round_result, round_uncertainty
from .uncertainty import get_uncertainty, type_a, type_b

__all__ = [
    "__version__",
    "get_mean",
    "get_std",
    "grubbs_test",
    "type_a",
    "type_b",
    "get_uncertainty",
    "round_uncertainty",
    "round_result",
    "format_result",
]
