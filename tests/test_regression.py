import numpy as np
import pytest

from physics_lab.regression import (
    format_slope_unit,
    graphical_result,
    least_squares,
)

TEXTBOOK_X = np.array([15.0, 25.8, 30.0, 36.6, 44.4])
TEXTBOOK_Y = np.array([39.4, 42.9, 44.4, 46.6, 49.2])


class TestLeastSquares:
    def test_textbook_example(self):
        fit = least_squares(TEXTBOOK_X, TEXTBOOK_Y)
        x, y = TEXTBOOK_X, TEXTBOOK_Y
        n = x.size
        x_mean, y_mean = x.mean(), y.mean()
        a = (np.sum(x * y) / n - x_mean * y_mean) / (
            np.sum(x * x) / n - x_mean * x_mean
        )
        b = y_mean - a * x_mean
        assert fit.n == 5
        assert fit.a == pytest.approx(a, abs=1e-9)
        assert fit.b == pytest.approx(b, abs=1e-9)
        assert fit.Lxy == pytest.approx(np.sum(x * y) / n - x_mean * y_mean)
        assert fit.Lxx == pytest.approx(np.sum(x * x) / n - x_mean * x_mean)
        assert fit.Lyy == pytest.approx(np.sum(y * y) / n - y_mean * y_mean)
        assert fit.R == pytest.approx(fit.Lxy / np.sqrt(fit.Lxx * fit.Lyy))
        polyfit_a, polyfit_b = np.polyfit(x, y, 1)
        assert fit.a == pytest.approx(polyfit_a)
        assert fit.b == pytest.approx(polyfit_b)
        # 教材 0.32/34.8/0.95 源于中间量取 3 位有效数字的舍入，数值应接近
        assert fit.a == pytest.approx(0.32, abs=0.02)
        assert fit.b == pytest.approx(34.8, abs=0.5)
        assert fit.R == pytest.approx(0.95, abs=0.06)

    def test_perfect_line(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = 2.0 * x + 3.0
        fit = least_squares(x, y)
        assert fit.a == pytest.approx(2.0)
        assert fit.b == pytest.approx(3.0)
        assert fit.R == pytest.approx(1.0)

    def test_negative_correlation(self):
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([3.0, 2.0, 1.0])
        fit = least_squares(x, y)
        assert fit.a == pytest.approx(-1.0)
        assert fit.R == pytest.approx(-1.0)

    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            least_squares(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0]))

    def test_too_few_points(self):
        with pytest.raises(ValueError):
            least_squares(np.array([1.0, 2.0]), np.array([1.0, 2.0]))

    def test_constant_x(self):
        with pytest.raises(ValueError):
            least_squares(np.array([2.0, 2.0, 2.0]), np.array([1.0, 2.0, 3.0]))


class TestGraphicalResult:
    def test_two_point_slope_matches_fit(self):
        fit = least_squares(TEXTBOOK_X, TEXTBOOK_Y)
        result = graphical_result(fit, 15.0, 44.4)
        assert result.slope == pytest.approx(fit.a, abs=1e-9)
        assert result.intercept == pytest.approx(fit.b, abs=1e-9)
        assert result.point_a.x == 15.0
        assert result.point_b.x == 44.4
        assert result.point_a.y == pytest.approx(fit.a * 15.0 + fit.b)
        assert result.point_c.x == pytest.approx((15.0 + 44.4) / 2)

    def test_constant_range_rejected(self):
        fit = least_squares(TEXTBOOK_X, TEXTBOOK_Y)
        with pytest.raises(ValueError):
            graphical_result(fit, 15.0, 15.0)


class TestFormatSlopeUnit:
    def test_both_units(self):
        assert format_slope_unit("mV", "mA") == "mV/mA"

    def test_only_y_unit(self):
        assert format_slope_unit("m", "") == "m"

    def test_only_x_unit(self):
        assert format_slope_unit("", "s") == "1/s"

    def test_no_units(self):
        assert format_slope_unit("", "") == ""
