# Factor Neutralizer

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-29%2F29%20Passing-brightgreen)]()
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-black)]()

量化因子中性化处理工具，支持行业中性化、市值中性化等多种中性化方法。

## 功能特性

- **行业中性化**：回归法、标准化法
- **市值中性化**：支持多种市值分组
- **指数中性化**：基于指数成分股
- **并行加载**：多线程加速数据加载
- **缓存机制**：自动缓存中间结果
- **内存优化**：自动类型降级减少内存占用
- **可视化**：行业轮动分析图表
- **日志系统**：完整的操作日志记录

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```python
from factor_neutralizer import FactorNeutralizer

neutralizer = FactorNeutralizer(
    factor_dir="path/to/factors",
    price_dir="path/to/prices",
    industry_file="path/to/industry.pkl",
    index_file="path/to/index.pkl",
    market_value_file="path/to/market_value.pkl",
    output_dir="output"
)

# 批量处理所有因子
neutralizer.process_all_factors(
    neutralization_type='industry',
    industry_method='regression'
)
```

## 项目结构

```
factor_neutralizer/
├── core/               # 核心处理模块
│   └── FactorNeutralizer.py
├── utils/              # 工具模块
│   ├── config_manager.py
│   ├── logger_config.py
│   └── error_handling.py
└── visualization/      # 可视化模块
    └── visualization_module.py

tests/
├── unit/               # 单元测试
└── integration/        # 集成测试

docs/                   # 文档
examples/               # 示例代码
scripts/                # 辅助脚本
```

## 技术实现细节

### 核心算法

#### 行业中性化 - 回归法

使用 OLS 回归提取残差作为中性化因子：

```python
# 1. 创建行业哑变量矩阵
industry_dummies = pd.get_dummies(industry_series, drop_first=True)
industry_dummies = sm.add_constant(industry_dummies)

# 2. 伪逆矩阵求解（向量化处理所有日期）
X_pinv = np.linalg.pinv(X_clean.values)
beta = X_pinv @ y_clean
residuals = y_clean - X_clean.values @ beta  # 残差 = 中性化因子
```

**数学原理**：
- 原始因子 = 行业暴露 + 纯Alpha
- 通过回归去除行业系统性暴露
- 残差即为去除行业影响后的纯净因子

#### 行业中性化 - 标准化法

按行业分组进行 Z-Score 标准化：

```python
Factor_neutralized = (Factor_original - Industry_mean) / Industry_std
```

### 性能优化

| 优化策略 | 实现方式 | 效果 |
|---------|---------|------|
| **向量化计算** | NumPy 矩阵运算替代逐行循环 | 10-100x 加速 |
| **并行加载** | ThreadPoolExecutor 加载5类数据 | 减少 60%+ 加载时间 |
| **智能缓存** | joblib + zlib 压缩，24小时过期 | 避免重复计算 |
| **内存优化** | float64→float32, int64→int32, category 类型 | 节省 30-50% 内存 |
| **批量 I/O** | 批量读写替代单文件操作 | 提升 20-40% I/O 性能 |

### 缓存机制

```python
# 缓存键生成（基于数据哈希）
cache_key = hashlib.sha256(
    f"{data_type}_{factor_dir}_{industry_file}_{kwargs}"
).hexdigest()

# 保存（joblib + zlib压缩）
joblib.dump(cached_data, cache_path, protocol=4, compress=('zlib', 3))

# 加载（24小时过期检查）
if time.time() - cached_data['timestamp'] < 86400:
    return cached_data['data']
```

### 数据对齐逻辑

1. **时间对齐**：因子数据与价格数据取日期交集
2. **股票对齐**：只保留价格数据中存在的股票代码
3. **代码格式统一**：自动识别并添加交易所后缀（`.SH` / `.SZ` / `.BJ`）
4. **行业对齐**：因子股票与行业映射取交集

### 错误处理体系

```
FactorNeutralizerError (基类)
├── DataLoadError          # 数据加载错误 (HIGH)
├── ProcessingError         # 处理错误 (MEDIUM)
├── CacheError              # 缓存错误 (LOW)
├── VisualizationError      # 可视化错误 (LOW)
└── ConfigurationError      # 配置错误 (HIGH)
```

## API 参考

### FactorNeutralizer 类

#### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `factor_dir` | str | 必填 | 因子数据目录路径 |
| `price_dir` | str | 必填 | 价格数据目录或 PKL 文件路径 |
| `industry_file` | str | 必填 | 行业映射文件路径 |
| `index_file` | str | 必填 | 指数成分股文件路径 |
| `market_value_file` | str | 必填 | 市值数据文件路径 |
| `output_dir` | str | `'neutralized_factors'` | 输出目录 |
| `index_code` | str | `'000001.SH'` | 指数代码 |
| `enable_cache` | bool | `True` | 是否启用缓存 |
| `industry_file_type` | str | `'auto'` | 行业文件类型：'auto','csv','pkl' |

#### 主要方法

| 方法 | 说明 |
|-----|------|
| `load_data()` | 并行加载所有数据（价格、因子、行业、指数、市值） |
| `industry_neutralization(factor_data, method='regression')` | 行业中性化入口 |
| `process_all_factors(neutralization_type, industry_method)` | 批量处理所有因子 |
| `rotation_analysis()` | 执行完整的轮动分析 |
| `_optimize_memory_usage(df)` | DataFrame 内存优化 |

### 输入数据格式

**因子数据** (`factors_input/*.pkl`)
```python
# DataFrame 格式
# 索引: datetime64[ns] (交易日)
# 列: 股票代码 (如 '600000.SH', '000001.SZ')
# 值: float (因子值)

示例:
            600000.SH  600036.SH  000001.SZ
2023-01-01    1.23       0.87      -0.45
2023-01-02    1.25       0.90      -0.42
```

**价格数据** (`price_data/`)
- CSV 格式: `index=trade_date, columns=stock_codes`
- PKL 格式: DataFrame，同上结构

**行业映射** (`industry_mapping`)
- CSV: 列名 `'证券代码'` 和 `'所属申万行业'`
- PKL DataFrame: 列名 `'code'` 和 `'industry'`
- PKL Series: index=股票代码, value=行业名称

**指数成分股** (`index_constituents`)
```python
# DataFrame 格式
# 列: 'index_code', 'trade_date', 'con_code'
```

**市值数据** (`stock_market_value`)
```python
# DataFrame 格式
# 索引: datetime64[ns] (交易日)
# 列: 股票代码
# 值: float (市值)
```

### 输出结果

**中性化因子** (`neutralized_results/factors/`)
```
{factor_name}_neutralized.pkl
# DataFrame 格式，与输入因子同结构
# 值已去除行业/市值/指数暴露
```

**可视化图表** (`neutralized_results/visualizations/`)
```
{factor_name}_industry_rotation.png    # 行业轮动热力图
{factor_name}_neutralization.png       # 中性化效果对比
market_value_rotation.png              # 市值轮动折线图
```

**分析结果** (`neutralized_results/analysis/`)
```json
// industry_rotation.json
{
  "factor_name": {
    "2023-03-31": {
      "银行": 0.523,
      "房地产": -0.312,
      "计算机": 1.245
    }
  }
}
```

## 文档索引

| 文档 | 说明 |
|------|------|
| [docs/TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md) | 综合技术文档（架构 + Bug分析 + 测试报告） |
| [docs/FactorNeutralizer_详细说明文档.md](docs/FactorNeutralizer_详细说明文档.md) | 详细算法说明与使用指南 |
| [docs/DEEP_BUG_ANALYSIS.md](docs/DEEP_BUG_ANALYSIS.md) | 深度Bug分析报告 |
| [CHANGELOG.md](CHANGELOG.md) | 版本变更日志 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |

## 测试

```bash
python -m pytest tests/ -v
```

**当前测试状态**: ✅ 29/29 全部通过

- 单元测试: 26/26 通过
- 集成测试: 3/3 通过

### 核心验证结果

**行业中性化效果验证**（10只股票 × 5个交易日）：

| 行业 | 中性化前均值 | 中性化后均值 |
|------|------------|------------|
| 银行 | -0.3432 | 0.0000 |
| 房地产 | -0.0300 | 0.0000 |
| 计算机 | 0.8330 | 0.0000 |

## 项目状态

| 指标 | 数值 |
|------|------|
| 版本 | v2.1.0 |
| Bug修复 | 17个 |
| 测试覆盖率 | 29/29 |
| 代码规范 | Black + flake8 |
| CI/CD | GitHub Actions |

## 贡献者

感谢所有为这个项目做出贡献的开发者。

- **作者**: StormstoutLau
- **GitHub**: [https://github.com/StormstoutLau/Factor_Neutralizer](https://github.com/StormstoutLau/Factor_Neutralizer)

## 许可证

MIT License
