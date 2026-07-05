# Changelog

**中文** | **[English](CHANGELOG_EN.md)**

## [2.2.0] - 2026-05-17

### Fixed
- Bug-018: 修复 `_async_save_figure` NameError，改为调用 `_save_figure_sync()`
- Bug-019: 修复 Pandas 3.0+ `select_dtypes` 警告，扩展为 `['object', 'str']`
- Bug-020: 修复 Matplotlib `plt.subplots` 资源泄漏，5处改用 `try/finally`（FactorNeutralizer.py 3处 + visualization_module.py 2处）
- Bug-022: 移除重复的 `import matplotlib.font_manager as fm` 语句
- Bug-021: 7处裸 `raise Exception(...)` 替换为 `ValueError` / `RuntimeError`

### Changed
- 100+ 处 `print()` 替换为 `logger` 调用
- 标准化 PEP 8 导入顺序（标准库→第三方→本地模块）
- 31个方法添加类型注解
- 5个魔法数字定义为模块常量：
  - `CACHE_EXPIRY_SECONDS = 24 * 60 * 60`
  - `JOBLIB_PROTOCOL = 4`
  - `JOBLIB_COMPRESS_LEVEL = 3`
  - `FILLNA_VALUE = 0`
  - `DUMMY_DROP_FIRST = True`

### Added
- 中英文双语文档
- GitHub 规范符合性分析报告
- 工程规范报告

## [2.1.0] - 2026-05-11

### Fixed
- Bug-001: 替换已弃用的 `fillna(method=...)` 为 `ffill()/bfill()`
- Bug-002: 修复可视化模块字典值引用错误
- Bug-003: 行业数据加载失败时不再生成随机数据，改为抛出异常
- Bug-004: 修复股票代码格式转换硬编码 `.SH` 问题
- Bug-006: 缓存键生成使用 SHA256 + JSON 序列化避免冲突
- Bug-007: 修复 `force_reprocess` 副作用问题
- Bug-008: 修复行业哑变量索引不匹配问题

### Added
- 集成日志系统到主类
- Numba 加速支持（可选）
- 完整的单元测试和集成测试
- 标准 Python 项目结构

### Changed
- 重构项目结构为包格式
- 优化内存使用

## [2.0.0] - 2026-05-10

### Added
- 初始版本发布
- 行业中性化（回归法、标准化法）
- 市值中性化
- 并行数据加载
- 缓存机制
