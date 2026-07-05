# Contributing Guidelines

**中文** | **[English](CONTRIBUTING_EN.md)**

## 开发环境设置

```bash
git clone https://github.com/StormstoutLau/Factor_Neutralizer.git
cd factor-neutralizer
pip install -r requirements.txt
pip install -e ".[dev]"
```

## 代码规范

- 使用 Black 进行代码格式化
- 使用 flake8 进行代码检查
- 类型注解是可选但推荐的

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复
- `docs:` 文档
- `style:` 格式（不影响代码含义）
- `refactor:` 重构
- `test:` 测试
- `chore:` 构建过程或辅助工具的变动

## 测试

确保所有测试通过：

```bash
pytest tests/ -v
```

## Pull Request 流程

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request
