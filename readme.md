# physics_lab

大学物理实验数据处理工具。针对直接测量法，把数据处理过程完整、透明地展示出来，便于华南理工大学（SCUT）的同学快速得到可写进实验报告的结果。

## 功能

- 算术平均值与样本标准差（贝塞尔公式）计算
- Grubbs 准则剔除粗大误差，并展示每一步的 G 统计量与临界值对比
- A 类不确定度（`u_A = S / √n`）与 B 类不确定度（`u_B = Δ / √3`，按均匀分布）及合成标准不确定度
- 有效数字修约：不确定度保留 1 位有效数字、只进不舍，测量值末位对齐
- 处理报告可打印到屏幕，也可保存到 `reports/` 文件夹（可选自定义文件名）

> **注意：项目目前不支持单位换算。请确保输入数据已统一单位后再进行计算。**

## 安装教程

要求 Python >= 3.10。

```bash
# 1. 克隆仓库
git clone <仓库地址>
cd physics_lab

# 2. 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate        # Windows 使用 .venv\Scripts\activate

# 3. 安装依赖与项目本体
pip install -r requirements.txt
pip install -e .
```

不执行`pip install -e .`也可以直接运行（程序会自动找到 `src/` 下的包）

启动程序：
```bash
python main.py
```

## 使用方法

运行后按提示操作：

1. 输入实验数据（空格、逗号、中文逗号、顿号均可分隔），如 `1.0 1.2 1.1 1.0 5.0`
2. 输入仪器误差（B 类不确定度来源），如 `0.01`
3. 程序自动执行 Grubbs 检验（数据少于 3 个时跳过）并展示剔除过程
4. 程序计算均值、样本标准差、A/B 类及合成不确定度，修约后给出最终结果
5. 可选输入单位（仅附加在结果中展示，不做换算）
6. 询问是否保存报告：输入文件名保存到 `reports/`，回车则使用带时间戳的默认名
7. 可循环处理多组数据，按 Ctrl+C 或输入 EOF 优雅退出

示例输出：

```
最终结果: x = (1.08 ± 0.05) m
```

## 项目结构与基本设置

```
physics_lab/
├── main.py                  # 程序入口，流程编排
├── pyproject.toml           # 打包配置（名称、版本、Python 版本要求、依赖）
├── requirements.txt         # 运行依赖
├── readme.md
├── docs/
│   └── fixes_and_design.md  # 错误修复对照与设计说明
└── src/physics_lab/
    ├── __init__.py          # 版本号与公共 API 导出
    ├── method.py            # 均值、样本标准差
    ├── outlier.py           # Grubbs 检验
    ├── uncertainty.py       # A/B 类不确定度与合成
    ├── result.py            # 有效数字修约与结果格式化
    └── io.py                # 输入输出（交互、报告打印与保存）
```

### 常用设置及修改方法

| 设置项 | 位置 | 默认值 | 说明 |
| --- | --- | --- | --- |
| Grubbs 检验显著性水平 | `main.py` 顶部 `ALPHA` | `0.05` | 也可单独调用 `grubbs_test(data, alpha=...)` 指定 |
| 报告保存文件夹 | `src/physics_lab/io.py` 顶部 `REPORT_DIR` | `reports/`（相对运行目录） | 修改为绝对路径可固定保存位置 |
| 不确定度修约规则 | `src/physics_lab/result.py` | `ROUND_CEILING`（1 位有效数字，只进不舍） | 换用其他 `ROUND_*` 常量可改变进位方式 |
| 测量值对齐修约 | `src/physics_lab/result.py` | `ROUND_HALF_EVEN`（四舍六入五成双，GB/T 8170） | 换成 `ROUND_HALF_UP` 即普通四舍五入 |
| B 类不确定度分布假设 | `src/physics_lab/uncertainty.py` | 均匀分布 `Δ / √3` | 若按正态分布可取 `Δ / 3` |
| Python 版本要求 | `pyproject.toml` | `>=3.10` | 按需调整 |

## 常见问题

- **为什么我的某个数据没被 Grubbs 剔除？** Grubbs 准则基于显著性水平与样本量判断，两个相同的可疑极值会产生"掩蔽效应"导致判不出，属统计方法固有局限。
- **报告文件在哪？** 默认保存在运行目录下的 `reports/` 文件夹，保存后程序会打印完整路径。
