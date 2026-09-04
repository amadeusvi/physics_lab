import sys
from pathlib import Path

ALPHA = 0.05

try:
    import physics_lab
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    import physics_lab

from physics_lab import (
    format_result,
    get_mean,
    get_std,
    get_uncertainty,
    grubbs_test,
    round_result,
    type_a,
    type_b,
)
from physics_lab.io import (
    input_confirm,
    input_data,
    input_optional_text,
    input_positive_float,
    print_report,
    print_welcome,
)


def run() -> None:
    print_welcome()
    while True:
        data = input_data()
        ins_error = input_positive_float("请输入仪器误差: ")

        if data.size >= 3:
            data_cleaned, removed = grubbs_test(data, alpha=ALPHA)
        else:
            data_cleaned, removed = data, []
            print("数据少于 3 个，跳过 Grubbs 检验。")

        mean = get_mean(data_cleaned)
        std = get_std(data_cleaned)
        ua = type_a(data_cleaned)
        ub = type_b(ins_error)
        u = get_uncertainty(data_cleaned, ins_error)
        mean_r, u_r = round_result(mean, u)
        unit = input_optional_text()
        result = format_result(mean, u, unit)

        print_report(
            data_original=data,
            data_cleaned=data_cleaned,
            removed=removed,
            ins_error=ins_error,
            alpha=ALPHA,
            mean=mean,
            std=std,
            ua=ua,
            ub=ub,
            u=u,
            mean_r=mean_r,
            u_r=u_r,
            result=result,
        )

        if not input_confirm("是否处理下一组数据？(y/n): "):
            break
    print("感谢使用，再见！")


def main() -> None:
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print("\n已退出。")
    except ValueError as exc:
        print(f"错误: {exc}")


if __name__ == "__main__":
    main()
