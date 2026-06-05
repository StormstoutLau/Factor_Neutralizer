"""
验证行业中性化的数学原理

说明：
- 回归中性化的残差与解释变量正交
- 当X包含行业哑变量时，每个行业的残差之和为0
- 这意味着每个行业的均值为0（如果该行业有股票）
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

print("=" * 80)
print("行业中性化数学原理验证")
print("=" * 80)

# 创建简单测试数据
np.random.seed(42)
n_stocks = 10

# 行业标签
industries = ['银行', '银行', '银行', '房地产', '房地产', 
              '房地产', '计算机', '计算机', '计算机', '计算机']

# 原始因子值（故意让不同行业有不同均值）
factor_values = np.array([
    1.0, 1.2, 0.8,   # 银行 (均值≈1.0)
    3.0, 3.2, 2.8,   # 房地产 (均值≈3.0)
    5.0, 5.2, 4.8, 6.0  # 计算机 (均值≈5.25)
])

print("\n原始因子值:")
for i, (ind, val) in enumerate(zip(industries, factor_values)):
    print(f"  股票{i}: {ind:<6} = {val:.2f}")

# 计算各行业均值
print("\n中性化前行业均值:")
for ind in set(industries):
    mask = [x == ind for x in industries]
    mean_val = factor_values[mask].mean()
    print(f"  {ind:<6}: {mean_val:.4f}")

# 创建行业哑变量矩阵
industry_dummies = pd.get_dummies(industries, drop_first=True)
X = sm.add_constant(industry_dummies)  # 添加常数项

# 确保X是数值类型
X = X.astype(float)

print("\n行业哑变量矩阵 X:")
print(X)

# 执行OLS回归
model = sm.OLS(factor_values, X)
results = model.fit()

print("\n回归结果:")
print(f"  R-squared: {results.rsquared:.4f}")
print(f"  系数: {results.params.values}")

# 计算残差
residuals = results.resid

print("\n残差 (中性化后因子值):")
for i, (ind, val, resid) in enumerate(zip(industries, factor_values, residuals)):
    print(f"  股票{i}: {ind:<6} = {resid:.4f}")

# 验证残差性质
print("\n残差性质验证:")
print(f"  残差之和: {residuals.sum():.10f} (应为≈0)")

# 验证每个行业的残差之和
print("\n各行业残差之和:")
for ind in set(industries):
    mask = [x == ind for x in industries]
    sum_resid = residuals[mask].sum()
    mean_resid = residuals[mask].mean()
    print(f"  {ind:<6}: 和={sum_resid:.10f}, 均值={mean_resid:.10f}")

# 验证残差与X正交
print("\n残差与X正交验证 (X^T @ residuals):")
Xt_r = X.T.values @ residuals
for i, col in enumerate(X.columns):
    print(f"  {col:<15}: {Xt_r[i]:.10f} (应为≈0)")

print("\n" + "=" * 80)
print("结论:")
print("=" * 80)
print("""
1. 残差之和为0（因为X包含常数项）
2. 每个行业的残差之和为0（因为X包含该行业哑变量）
3. 因此每个行业的均值为0

这是回归中性化的正确数学性质，不是Bug！

行业中性化的目标就是消除行业间的系统性差异，
使得因子值不再受行业归属的影响。
""")
