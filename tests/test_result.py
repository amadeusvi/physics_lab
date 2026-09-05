import pytest

from physics_lab.result import format_result, round_result, round_uncertainty


class TestDocExamples:
    """《实验数据处理流程总结》'标准常见错误示例'逐条回归。"""

    def test_example1(self):
        assert format_result(12.0012, 0.000625, "cm") == "(12.0012 ± 0.0007) cm"

    def test_example2(self):
        assert format_result(0.576361, 0.0005, "mm") == "(0.5764 ± 0.0005) mm"

    def test_example3(self):
        assert format_result(9.75, 0.0626, "mA") == "(9.75 ± 0.07) mA"

    def test_example4(self):
        assert format_result(96500, 500, "g") == "(9.65 ± 0.05)×10⁴ g"

    def test_example5(self):
        assert format_result(22, 0.5, "℃") == "(22.0 ± 0.5) ℃"


class TestRoundUncertainty:
    def test_ceiling_only(self):
        assert round_uncertainty(0.0431) == 0.05
        assert round_uncertainty(0.021) == 0.03
        assert round_uncertainty(0.48) == 0.5
        assert round_uncertainty(1.2) == 2
        assert round_uncertainty(0.0626) == 0.07

    def test_requires_positive(self):
        with pytest.raises(ValueError):
            round_uncertainty(0)
        with pytest.raises(ValueError):
            round_uncertainty(-0.1)


class TestScientificNotation:
    def test_large_mean_with_ambiguous_uncertainty(self):
        assert format_result(96500, 500) == "(9.65 ± 0.05)×10⁴"

    def test_very_large_mean(self):
        assert format_result(1.6e19, 6e18) == "(1.6 ± 0.6)×10¹⁹"

    def test_very_small_values(self):
        assert format_result(1.60e-19, 7e-22) == "(1.600 ± 0.007)×10⁻¹⁹"

    def test_plain_when_reasonable(self):
        assert format_result(9.75, 0.07) == "9.75 ± 0.07"
        assert format_result(22, 3) == "22 ± 3"


class TestRoundResult:
    def test_aligns_measurement_to_uncertainty(self):
        assert round_result(12.0012, 0.000625) == (12.0012, 0.0007)
        assert round_result(0.576361, 0.0005) == (0.5764, 0.0005)
