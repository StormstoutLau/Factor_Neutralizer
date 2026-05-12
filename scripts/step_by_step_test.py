"""
FactorNeutralizer 逐步测试和验证脚本

功能：
1. 创建少量测试数据（10只股票，5个交易日）
2. 逐步运行程序，验证每一步中间结果
3. 可视化排查错误
4. 确保每一步可追溯

作者：StormstoutLau
日期：2026-05-11
"""

import os
import sys
import tempfile
import shutil
import pandas as pd
import numpy as np
import warnings
import pickle
import matplotlib.pyplot as plt

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from factor_neutralizer.core.FactorNeutralizer import FactorNeutralizer

# ==========================================
# 步骤 0: 初始化和配置
# ==========================================
print("=" * 80)
print("步骤 0: 初始化和配置")
print("=" * 80)

# 创建临时工作目录
work_dir = tempfile.mkdtemp(prefix="factor_neutralizer_test_")
print(f"工作目录: {work_dir}")

# 创建子目录
factor_dir = os.path.join(work_dir, "factors")
price_dir = os.path.join(work_dir, "price")
output_dir = os.path.join(work_dir, "output")

os.makedirs(factor_dir, exist_ok=True)
os.makedirs(price_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

print(f"因子目录: {factor_dir}")
print(f"价格目录: {price_dir}")
print(f"输出目录: {output_dir}")

# ==========================================
# 步骤 1: 创建少量测试数据
# ==========================================
print("\n" + "=" * 80)
print("步骤 1: 创建少量测试数据")
print("=" * 80)

print("\n创建参数:")
print("  股票数量: 10")
print("  交易日: 5 (2023-01-02 至 2023-01-06)")
print("  行业分类: 3个 (银行, 房地产, 计算机)")

# 创建日期
dates = pd.date_range("2023-01-02", periods=5, freq="D")

# 创建股票代码（10只）
symbols = [
    "600000.SH", "600001.SH", "600002.SH", "000001.SZ", "000002.SZ",
    "000003.SZ", "300001.SZ", "300002.SZ", "300003.SZ", "688001.SH"
]

print("\n股票列表:")
for sym in symbols:
    print(f"  - {sym}")

# ------------------------------
# 1.1 价格数据
# ------------------------------
print("\n1.1 创建价格数据...")
np.random.seed(42)  # 固定随机种子确保可复现
price_data = pd.DataFrame(
    np.random.randn(len(dates), len(symbols)) * 0.02 + 1,
    index=dates,
    columns=symbols
)

# 保存价格数据
price_file = os.path.join(price_dir, "stock_close.pkl")
price_data.to_pickle(price_file)

print(f"  价格数据形状: {price_data.shape}")
print(f"  保存路径: {price_file}")
print("\n价格数据前3行:")
print(price_data.head(3))

# ------------------------------
# 1.2 因子数据 (动量因子)
# ------------------------------
print("\n1.2 创建因子数据 (动量因子)...")
np.random.seed(43)
factor_data = pd.DataFrame(
    np.random.randn(len(dates), len(symbols)),
    index=dates,
    columns=symbols
)

# 保存因子数据
factor_file = os.path.join(factor_dir, "momentum.pkl")
factor_data.to_pickle(factor_file)

print(f"  因子数据形状: {factor_data.shape}")
print(f"  保存路径: {factor_file}")
print("\n因子数据前3行:")
print(factor_data.head(3))

# ------------------------------
# 1.3 行业数据
# ------------------------------
print("\n1.3 创建行业数据...")
industry_mapping = pd.DataFrame({
    "code": symbols,
    "industry": [
        "银行", "银行", "银行", "房地产", "房地产",
        "房地产", "计算机", "计算机", "计算机", "计算机"
    ]
})

industry_file = os.path.join(work_dir, "industry.pkl")
industry_mapping.to_pickle(industry_file)

print(f"  行业数据形状: {industry_mapping.shape}")
print(f"  保存路径: {industry_file}")
print("\n行业数据:")
print(industry_mapping)

# ------------------------------
# 1.4 指数数据
# ------------------------------
print("\n1.4 创建指数数据...")
index_data = pd.DataFrame({
    "index_code": ["000001.SH"] * len(symbols),
    "trade_date": ["20230101"] * len(symbols),
    "con_code": symbols
})

index_file = os.path.join(work_dir, "index.pkl")
index_data.to_pickle(index_file)

print(f"  指数数据形状: {index_data.shape}")
print(f"  保存路径: {index_file}")
print("\n指数数据:")
print(index_data)

# ------------------------------
# 1.5 市值数据
# ------------------------------
print("\n1.5 创建市值数据...")
np.random.seed(44)
market_cap_data = pd.DataFrame(
    np.random.uniform(1e9, 1e11, (len(dates), len(symbols))),
    index=dates,
    columns=symbols
)

market_cap_file = os.path.join(work_dir, "market_value.pkl")
market_cap_data.to_pickle(market_cap_file)

print(f"  市值数据形状: {market_cap_data.shape}")
print(f"  保存路径: {market_cap_file}")
print("\n市值数据前3行:")
print(market_cap_data.head(3))

print("\n✅ 测试数据创建完成！")

# ==========================================
# 步骤 2: 初始化 FactorNeutralizer
# ==========================================
print("\n" + "=" * 80)
print("步骤 2: 初始化 FactorNeutralizer")
print("=" * 80)

neutralizer = FactorNeutralizer(
    factor_dir=factor_dir,
    price_dir=price_dir,
    industry_file=industry_file,
    index_file=index_file,
    market_value_file=market_cap_file,
    output_dir=output_dir,
    enable_cache=False,
    industry_file_type="pkl",
    index_file_type="pkl",
    market_value_file_type="pkl"
)

print("\n✅ 初始化完成！")

# ==========================================
# 步骤 3: 加载数据（逐步检查）
# ==========================================
print("\n" + "=" * 80)
print("步骤 3: 加载数据")
print("=" * 80)

neutralizer.load_data()

print("\n✅ 数据加载完成！")

# ==========================================
# 步骤 4: 验证加载的数据
# ==========================================
print("\n" + "=" * 80)
print("步骤 4: 验证加载的数据")
print("=" * 80)

print("\n因子数量:", len(neutralizer.factors))
for name in neutralizer.factors:
    print(f"  - {name}: {neutralizer.factors[name].shape}")

print("\n价格数据形状:", neutralizer.price_data.shape)

print("\n行业数据前5行:")
print(neutralizer.industry_data.head())

print("\n指数数据前5行:")
print(neutralizer.index_data.head())

print("\n市值数据前3行:")
print(neutralizer.market_value_data.head(3))

# ==========================================
# 步骤 5: 行业中性化（回归法）
# ==========================================
print("\n" + "=" * 80)
print("步骤 5: 行业中性化（回归法）")
print("=" * 80)

factor_before = neutralizer.factors["momentum"].copy()
neutralized_factor = neutralizer.industry_neutralization(
    factor_before,
    method="regression"
)

print("\n因子数据形状:", factor_before.shape)
print("中性化后形状:", neutralized_factor.shape)

# 检查中性化后的因子行业分布
print("\n验证行业中性化效果...")
industry_series = neutralizer.industry_data
date_idx = 0  # 检查第一个交易日

# 获取该日的因子和行业
daily_factor = factor_before.iloc[date_idx]
daily_neutral = neutralized_factor.iloc[date_idx]
daily_industry = industry_series

# 计算中性化前的行业均值
print("\n中性化前 - 行业均值:")
for industry in daily_industry.unique():
    mask = daily_industry == industry
    mean_val = daily_factor[mask].mean()
    print(f"  {industry:<10} : {mean_val:>8.4f}")

# 计算中性化后的行业均值
print("\n中性化后 - 行业均值:")
for industry in daily_industry.unique():
    mask = daily_industry == industry
    mean_val = daily_neutral[mask].mean()
    print(f"  {industry:<10} : {mean_val:>8.4f}")

print("\n✅ 行业中性化验证完成！")

# ==========================================
# 步骤 6: 可视化
# ==========================================
print("\n" + "=" * 80)
print("步骤 6: 可视化")
print("=" * 80)

# 创建可视化目录
visualization_dir = os.path.join(output_dir, "visualizations")
os.makedirs(visualization_dir, exist_ok=True)

# 6.1 因子中性化前后对比
print("\n6.1 因子中性化前后对比...")
fig, axes = plt.subplots(2, 1, figsize=(12, 10))

# 中性化前
axes[0].plot(factor_before.iloc[:, 0:3], label=factor_before.columns[0:3])
axes[0].set_title("因子中性化前（前3只股票）", fontsize=14)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 中性化后
axes[1].plot(neutralized_factor.iloc[:, 0:3], label=neutralized_factor.columns[0:3])
axes[1].set_title("因子中性化后（前3只股票）", fontsize=14)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
compare_plot = os.path.join(visualization_dir, "01_factor_compare.png")
plt.savefig(compare_plot, dpi=150)
plt.close()
print(f"  保存路径: {compare_plot}")

# 6.2 行业分布
print("\n6.2 行业分布可视化...")
fig, ax = plt.subplots(figsize=(10, 6))
industry_counts = industry_mapping["industry"].value_counts()
industry_counts.plot(kind="bar", ax=ax)
ax.set_title("股票行业分布", fontsize=14)
ax.set_xlabel("行业", fontsize=12)
ax.set_ylabel("数量", fontsize=12)
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()

industry_plot = os.path.join(visualization_dir, "02_industry_distribution.png")
plt.savefig(industry_plot, dpi=150)
plt.close()
print(f"  保存路径: {industry_plot}")

# 6.3 因子中性化前后散点图
print("\n6.3 因子中性化前后散点图...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].scatter(range(len(daily_factor)), daily_factor.values, alpha=0.7)
axes[0].set_title("中性化前因子值", fontsize=14)
axes[0].set_xlabel("股票索引", fontsize=12)
axes[0].set_ylabel("因子值", fontsize=12)
axes[0].grid(True, alpha=0.3)

axes[1].scatter(range(len(daily_neutral)), daily_neutral.values, alpha=0.7)
axes[1].set_title("中性化后因子值", fontsize=14)
axes[1].set_xlabel("股票索引", fontsize=12)
axes[1].set_ylabel("因子值", fontsize=12)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
scatter_plot = os.path.join(visualization_dir, "03_factor_scatter.png")
plt.savefig(scatter_plot, dpi=150)
plt.close()
print(f"  保存路径: {scatter_plot}")

# 6.4 因子值箱线图
print("\n6.4 因子值箱线图...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].boxplot(factor_before.values.flatten())
axes[0].set_title("中性化前因子值分布", fontsize=14)
axes[0].set_ylabel("因子值", fontsize=12)
axes[0].grid(True, alpha=0.3)

axes[1].boxplot(neutralized_factor.values.flatten())
axes[1].set_title("中性化后因子值分布", fontsize=14)
axes[1].set_ylabel("因子值", fontsize=12)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
box_plot = os.path.join(visualization_dir, "04_factor_boxplot.png")
plt.savefig(box_plot, dpi=150)
plt.close()
print(f"  保存路径: {box_plot}")

print("\n✅ 可视化完成！")

# ==========================================
# 步骤 7: 保存中间结果
# ==========================================
print("\n" + "=" * 80)
print("步骤 7: 保存中间结果（可追溯）")
print("=" * 80)

results_dir = os.path.join(output_dir, "results")
os.makedirs(results_dir, exist_ok=True)

# 保存中性化前因子
before_file = os.path.join(results_dir, "factor_before.pkl")
factor_before.to_pickle(before_file)
print(f"  中性化前因子: {before_file}")

# 保存中性化后因子
after_file = os.path.join(results_dir, "factor_after.pkl")
neutralized_factor.to_pickle(after_file)
print(f"  中性化后因子: {after_file}")

# 保存行业数据
industry_save_file = os.path.join(results_dir, "industry_data.pkl")
neutralizer.industry_data.to_pickle(industry_save_file)
print(f"  行业数据: {industry_save_file}")

# 保存分析日志
summary = {
    "work_dir": work_dir,
    "dates": dates,
    "symbols": symbols,
    "factor_shape": factor_before.shape,
    "neutralized_shape": neutralized_factor.shape,
    "industry_distribution": industry_mapping.to_dict("records"),
    "visualizations": [
        compare_plot,
        industry_plot,
        scatter_plot,
        box_plot
    ]
}

summary_file = os.path.join(results_dir, "summary.pkl")
with open(summary_file, "wb") as f:
    pickle.dump(summary, f)
print(f"  分析摘要: {summary_file}")

print("\n✅ 结果保存完成！")

# ==========================================
# 步骤 8: 最终验证和总结
# ==========================================
print("\n" + "=" * 80)
print("步骤 8: 最终验证和总结")
print("=" * 80)

print("\n📊 测试总结:")
print("  股票数量: 10")
print("  交易日: 5")
print("  行业分类: 3个")
print("  中性化方法: 回归法")
print("\n📁 输出目录:")
print(f"  可视化: {visualization_dir}")
print(f"  结果: {results_dir}")
print("\n✅ 全部步骤验证完成！")

# 检查所有输出文件是否存在
print("\n📂 输出文件检查:")
all_files = [
    compare_plot,
    industry_plot,
    scatter_plot,
    box_plot,
    before_file,
    after_file,
    industry_save_file,
    summary_file
]

all_exists = True
for file_path in all_files:
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        print(f"  ✅ {os.path.basename(file_path)} ({file_size:,} bytes)")
    else:
        print(f"  ❌ {os.path.basename(file_path)}")
        all_exists = False

print("\n" + "=" * 80)
if all_exists:
    print("✅ 测试完成！所有输出文件已生成，可追溯！")
else:
    print("❌ 部分文件未生成！")

# ==========================================
# 完成
# ==========================================
print("\n提示：运行以下命令查看工作目录:")
print(f"  explorer \"{work_dir}\"")
