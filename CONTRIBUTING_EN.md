# Contributing Guidelines

**[中文](CONTRIBUTING.md)** | **English**

Thanks for your interest in contributing to Factor Neutralizer! This guide will help you get started.

## Development Environment Setup

```bash
git clone https://github.com/StormstoutLau/Factor_Neutralizer.git
cd factor-neutralizer
pip install -r requirements.txt
pip install -e ".[dev]"
```

## Code Style

- Use [Black](https://github.com/psf/black) for code formatting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Type annotations are optional but recommended
- Follow PEP 8 import order: standard library → third-party → local modules
- Replace `print()` with proper `logger` calls
- Use specific exception types (`ValueError`, `RuntimeError`) instead of bare `Exception`

## Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `style:` formatting changes (no code logic impact)
- `refactor:` code refactoring
- `test:` test additions or modifications
- `chore:` build process or auxiliary tool changes

### Example

```bash
git commit -m "fix(core): resolve matplotlib resource leak in rotation visualization"
```

## Testing

Ensure all tests pass before submitting a PR:

```bash
pytest tests/ -v
```

Current test coverage: 29/29 passing (26 unit tests + 3 integration tests).

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to your branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request against `master`

### PR Checklist

- [ ] All tests pass locally
- [ ] No new `print()` statements introduced
- [ ] No new bare `Exception` raises introduced
- [ ] Type annotations added to new public methods
- [ ] Documentation updated if needed
- [ ] Commit message follows Conventional Commits format

## Reporting Bugs

Please use [GitHub Issues](https://github.com/StormstoutLau/Factor_Neutralizer/issues) to report bugs. Include:

- Python version and OS
- Minimal reproducible example
- Expected vs actual behavior
- Relevant log output

## Code of Conduct

Be respectful and constructive in all interactions.
