# Changelog

**[中文](CHANGELOG.md)** | **English**

## [2.2.0] - 2026-05-17

### Fixed
- Bug-018: Resolved `_async_save_figure` `NameError` by switching to `_save_figure_sync()`
- Bug-019: Fixed Pandas 3.0+ compatibility warning by extending `select_dtypes(include=['object', 'str'])`
- Bug-020: Eliminated Matplotlib resource leak by wrapping `plt.subplots()` in `try/finally` blocks (3 locations in `FactorNeutralizer.py` + 2 locations in `visualization_module.py`)
- Bug-022: Removed duplicate `import matplotlib.font_manager as fm` statement
- Bug-021: Replaced 7 bare `raise Exception(...)` with specific `ValueError` / `RuntimeError`

### Changed
- Replaced 100+ `print()` statements with proper `logger` calls
- Standardized PEP 8 import order across modules (standard library → third-party → local)
- Added type annotations to 31 methods in `FactorNeutralizer.py`
- Defined 5 module-level constants for magic numbers:
  - `CACHE_EXPIRY_SECONDS = 24 * 60 * 60`
  - `JOBLIB_PROTOCOL = 4`
  - `JOBLIB_COMPRESS_LEVEL = 3`
  - `FILLNA_VALUE = 0`
  - `DUMMY_DROP_FIRST = True`

### Added
- Bilingual documentation (Chinese + English)
- GitHub compliance analysis report
- Code style engineering report

## [2.1.0] - 2026-05-11

### Fixed
- Bug-001: Replaced deprecated `fillna(method=...)` with `ffill()/bfill()`
- Bug-002: Fixed dictionary value reference error in visualization module
- Bug-003: Industry data loading no longer generates random data on failure; raises exception instead
- Bug-004: Fixed hardcoded `.SH` suffix in stock code format conversion
- Bug-006: Cache key generation now uses SHA256 + JSON serialization to avoid collisions
- Bug-007: Fixed `force_reprocess` side-effect issue
- Bug-008: Fixed industry dummy variable index mismatch

### Added
- Integrated logging system into main class
- Optional Numba acceleration support
- Complete unit and integration test suite
- Standard Python package structure

### Changed
- Refactored project structure to package format
- Optimized memory usage

## [2.0.0] - 2026-05-10

### Added
- Initial release
- Industry neutralization (regression, standardization)
- Market-value neutralization
- Parallel data loading
- Caching mechanism
