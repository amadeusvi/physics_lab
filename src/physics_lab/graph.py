from pathlib import Path

from .io import (
    input_choice,
    input_confirm,
    input_data,
    input_optional_text,
    print_fit_report,
    save_report,
)
from .plotting import configure_cjk_font, plot_linear_fit
from .regression import (
    GraphicalResult,
    format_slope_unit,
    graphical_result,
    least_squares,
)


def run_graph() -> None:
    print()
    print("作图与线性拟合（最小二乘法作图）")

    x = input_data("请输入横轴 x 的实验数据（空格或逗号分隔）: ")
    while True:
        y = input_data("请输入纵轴 y 的实验数据（空格或逗号分隔）: ")
        if y.size == x.size:
            break
        print(f"y 的数据个数（{y.size}）与 x（{x.size}）不一致，请重新输入。")
    if x.size < 3:
        print("作图拟合至少需要 3 组数据，返回主菜单。")
        return

    x_label = input_optional_text("请输入横轴物理量名称（回车使用 x）: ")
    x_unit = input_optional_text("请输入横轴单位（无量纲可直接回车）: ")
    y_label = input_optional_text("请输入纵轴物理量名称（回车使用 y）: ")
    y_unit = input_optional_text("请输入纵轴单位（无量纲可直接回车）: ")
    title = input_optional_text("请输入图名（回车使用默认名）: ")

    try:
        fit = least_squares(x, y)
    except ValueError as exc:
        print(f"拟合失败: {exc}")
        return

    print()
    print(f"最小二乘拟合结果: 斜率 a = {fit.a:.6g}，截距 b = {fit.b:.6g}，"
          f"相关系数 R = {fit.R:.6g}")

    if not configure_cjk_font():
        print("提示: 未检测到中文字体，图名与中文标签可能显示为方框，"
              "建议改用英文。")

    try:
        figure_path = plot_linear_fit(
            x, y, fit,
            x_label=x_label, y_label=y_label,
            x_unit=x_unit, y_unit=y_unit,
            title=title,
        )
    except OSError as exc:
        print(f"绘图保存失败: {exc}")
        return
    print(f"拟合图已保存至: {figure_path}")

    choice = input_choice(
        "请选择求斜率与截距的方法: ",
        ["图解法（两点式，自动在拟合直线两端取点）",
         "线性回归法（最小二乘结果）"],
    )

    graphical: GraphicalResult | None = None
    marked_path: Path | None = None
    if choice == 1:
        graphical = graphical_result(fit, float(x.min()), float(x.max()))
        print("图解法在拟合直线上选取:")
        print(f"  端点 A{graphical.point_a}，端点 B{graphical.point_b}，"
              f"取点 C{graphical.point_c}")
        filename = input_optional_text(
            "请输入标记取点图文件名（回车使用默认名）: "
        )
        try:
            marked_path = plot_linear_fit(
                x, y, fit,
                x_label=x_label, y_label=y_label,
                x_unit=x_unit, y_unit=y_unit,
                title=title,
                marked=graphical,
                filename=filename,
            )
        except OSError as exc:
            print(f"标记取点图保存失败: {exc}")
        if marked_path is not None:
            print(f"标记取点图已保存至: {marked_path}")

    slope_unit = format_slope_unit(y_unit, x_unit)
    report_text = print_fit_report(
        x=x,
        y=y,
        fit=fit,
        x_label=x_label,
        y_label=y_label,
        x_unit=x_unit,
        y_unit=y_unit,
        title=title,
        slope_unit=slope_unit,
        figure_path=figure_path,
        marked_path=marked_path,
        method="graphical" if choice == 1 else "regression",
        graphical=graphical,
    )

    if input_confirm("是否保存本次报告？(y/n): "):
        filename = input_optional_text("请输入文件名（回车使用默认名）: ")
        path = save_report(report_text, filename)
        print(f"报告已保存至: {path}")
