# Factor Neutralizer v2.2

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-29%2F29%20Passing-brightgreen)]()
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-black)]()

**[中文](README.md)** | **English**

A quantitative factor neutralization toolkit supporting industry, market-value, and index neutralization with vectorized computation, parallel loading, and intelligent caching.

## Features

- **Industry Neutralization**: OLS regression and Z-Score standardization methods
- **Market-Value Neutralization**: Multiple grouping strategies
- **Index Neutralization**: Based on index constituents
- **Parallel Loading**: Multi-threaded data loading for 5 data sources
- **Caching**: Joblib + zlib compression with 24-hour expiry
- **Memory Optimization**: Automatic dtype downcasting (float64→float32, int64→int32)
- **Visualization**: Industry rotation heatmaps, market-value rotation charts
- **Logging**: Comprehensive operation logging with structured levels

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

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

# Batch process all factors
neutralizer.process_all_factors(
    neutralization_type='industry',
    industry_method='regression'
)
```

## Project Structure

```
factor_neutralizer/
├── core/               # Core processing module
│   └── FactorNeutralizer.py
├── utils/              # Utility modules
│   ├── config_manager.py
│   ├── logger_config.py
│   └── error_handling.py
└── visualization/      # Visualization module
    └── visualization_module.py

tests/
├── unit/               # Unit tests
└── integration/        # Integration tests

docs/                   # Documentation
examples/               # Example code
scripts/                # Helper scripts
```

## Technical Implementation

### Core Algorithms

#### Industry Neutralization - Regression Method

Uses OLS regression to extract residuals as the neutralized factor:

```python
# 1. Create industry dummy variable matrix
industry_dummies = pd.get_dummies(industry_series, drop_first=True)
industry_dummies = sm.add_constant(industry_dummies)

# 2. Pseudo-inverse matrix solving (vectorized for all dates)
X_pinv = np.linalg.pinv(X_clean.values)
beta = X_pinv @ y_clean
residuals = y_clean - X_clean.values @ beta  # Residuals = neutralized factor
```

**Mathematical Principle**:
- Original Factor = Industry Exposure + Pure Alpha
- Regression removes systematic industry exposure
- Residuals represent the pure factor after removing industry effects

#### Industry Neutralization - Standardization Method

Z-Score standardization grouped by industry:

```python
Factor_neutralized = (Factor_original - Industry_mean) / Industry_std
```

### Performance Optimization

| Strategy | Implementation | Effect |
|----------|---------------|--------|
| **Vectorized Computation** | NumPy matrix operations replace row-wise loops | 10-100x speedup |
| **Parallel Loading** | ThreadPoolExecutor loads 5 data types | 60%+ loading time reduction |
| **Smart Caching** | joblib + zlib compression, 24-hour expiry | Avoids redundant computation |
| **Memory Optimization** | float64→float32, int64→int32, category dtype | 30-50% memory savings |
| **Batch I/O** | Batch read/write replaces single-file operations | 20-40% I/O performance boost |

### Caching Mechanism

```python
# Cache key generation (based on data hash)
cache_key = hashlib.sha256(
    f"{data_type}_{factor_dir}_{industry_file}_{kwargs}"
).hexdigest()

# Save (joblib + zlib compression)
joblib.dump(cached_data, cache_path, protocol=4, compress=('zlib', 3))

# Load (24-hour expiry check)
if time.time() - cached_data['timestamp'] < 86400:
    return cached_data['data']
```

### Data Alignment Logic

1. **Time Alignment**: Intersect factor dates with price dates
2. **Stock Alignment**: Keep only stock codes present in price data
3. **Code Format Unification**: Auto-detect and append exchange suffix (`.SH` / `.SZ` / `.BJ`)
4. **Industry Alignment**: Intersect factor stocks with industry mapping

### Error Handling Hierarchy

```
FactorNeutralizerError (base class)
├── DataLoadError          # Data loading error (HIGH)
├── ProcessingError       # Processing error (MEDIUM)
├── CacheError            # Cache error (LOW)
├── VisualizationError    # Visualization error (LOW)
└── ConfigurationError    # Configuration error (HIGH)
```

## API Reference

### FactorNeutralizer Class

#### Initialization Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `factor_dir` | str | required | Factor data directory path |
| `price_dir` | str | required | Price data directory or PKL file path |
| `industry_file` | str | required | Industry mapping file path |
| `index_file` | str | required | Index constituent file path |
| `market_value_file` | str | required | Market value data file path |
| `output_dir` | str | `'neutralized_factors'` | Output directory |
| `index_code` | str | `'000001.SH'` | Index code |
| `enable_cache` | bool | `True` | Enable caching |
| `industry_file_type` | str | `'auto'` | Industry file type: 'auto', 'csv', 'pkl' |

#### Main Methods

| Method | Description |
|--------|-------------|
| `load_data()` | Parallel load all data (price, factor, industry, index, market value) |
| `industry_neutralization(factor_data, method='regression')` | Industry neutralization entry |
| `process_all_factors(neutralization_type, industry_method)` | Batch process all factors |
| `rotation_analysis()` | Execute full rotation analysis |
| `_optimize_memory_usage(df)` | DataFrame memory optimization |

### Input Data Formats

**Factor Data** (`factors_input/*.pkl`)
```python
# DataFrame format
# Index: datetime64[ns] (trading days)
# Columns: stock codes (e.g., '600000.SH', '000001.SZ')
# Values: float (factor values)

Example:
            600000.SH  600036.SH  000001.SZ
2023-01-01    1.23       0.87      -0.45
2023-01-02    1.25       0.90      -0.42
```

**Price Data** (`price_data/`)
- CSV format: `index=trade_date, columns=stock_codes`
- PKL format: DataFrame, same structure as above

**Industry Mapping** (`industry_mapping`)
- CSV: columns `'证券代码'` (stock code) and `'所属申万行业'` (industry)
- PKL DataFrame: columns `'code'` and `'industry'`
- PKL Series: index=stock code, value=industry name

**Index Constituents** (`index_constituents`)
```python
# DataFrame format
# Columns: 'index_code', 'trade_date', 'con_code'
```

**Market Value Data** (`stock_market_value`)
```python
# DataFrame format
# Index: datetime64[ns] (trading days)
# Columns: stock codes
# Values: float (market value)
```

### Output Results

**Neutralized Factors** (`neutralized_results/factors/`)
```
{factor_name}_neutralized.pkl
# DataFrame format, same structure as input factor
# Values have industry/market-value/index exposure removed
```

**Visualization Charts** (`neutralized_results/visualizations/`)
```
{factor_name}_industry_rotation.png    # Industry rotation heatmap
{factor_name}_neutralization.png       # Neutralization effect comparison
market_value_rotation.png              # Market-value rotation line chart
```

**Analysis Results** (`neutralized_results/analysis/`)
```json
// industry_rotation.json
{
  "factor_name": {
    "2023-03-31": {
      "Banking": 0.523,
      "Real Estate": -0.312,
      "Computing": 1.245
    }
  }
}
```

## Documentation Index

| Document | Description |
|----------|-------------|
| [docs/TECHNICAL_DOCUMENTATION_EN.md](docs/TECHNICAL_DOCUMENTATION_EN.md) | Comprehensive technical documentation (Architecture + Bug analysis + Test report) |
| [docs/DEEP_BUG_ANALYSIS.md](docs/DEEP_BUG_ANALYSIS.md) | Deep bug analysis report |
| [CHANGELOG.md](CHANGELOG.md) | Version changelog |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |

## Testing

```bash
python -m pytest tests/ -v
```

**Current Test Status**: ✅ 29/29 All Passing

- Unit Tests: 26/26 passed
- Integration Tests: 3/3 passed

### Core Verification Results

**Industry Neutralization Effect Verification** (10 stocks × 5 trading days):

| Industry | Pre-Neutralization Mean | Post-Neutralization Mean |
|----------|------------------------|--------------------------|
| Banking | -0.3432 | 0.0000 |
| Real Estate | -0.0300 | 0.0000 |
| Computing | 0.8330 | 0.0000 |

## Project Status

| Metric | Value |
|--------|-------|
| Version | v2.2.0 |
| Bugs Fixed | 16 |
| Tests | 29/29 passing |
| Code Style | Black + flake8 |
| CI/CD | GitHub Actions |

## Contributors

Thanks to all developers who contributed to this project.

- **Author**: StormstoutLau
- **GitHub**: [https://github.com/StormstoutLau/Factor_Neutralizer](https://github.com/StormstoutLau/Factor_Neutralizer)

## License

MIT License
