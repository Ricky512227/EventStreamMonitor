# Contributing to Open Source

This document tracks open source contributions made from this project.

## Contribution Opportunities Found

### 1. **redis-py** - Issue #1744
- **Title**: We need examples!
- **URL**: https://github.com/redis/redis-py/issues/1744
- **Type**: Documentation/Examples
- **Status**: Open
- **Labels**: help-wanted, good first issue, maintenance

**Contribution Plan**:
- Create example files showing common redis-py usage patterns
- Examples include: basic operations, connection pooling, pipelines, pub/sub, transactions
- See `scripts/contribute_redis_examples.py` for reference implementation

### 2. **gunicorn** - Issue #2279
- **Title**: sendfile example does not use sendfile
- **URL**: https://github.com/benoitc/gunicorn/issues/2279
- **Type**: Bug fix/Example
- **Status**: Open
- **Labels**: good first issue

### 3. **gunicorn** - Issue #1643
- **Title**: `reload_extra_files` should accept wildcards
- **URL**: https://github.com/benoitc/gunicorn/issues/1643
- **Type**: Feature
- **Status**: Open
- **Labels**: good first issue

## Tools Created

### `scripts/find_contribution_opportunities.py`
A utility script that searches for "good first issue" labels in popular open source projects you use.

**Usage**:
```bash
python3 scripts/find_contribution_opportunities.py
```

### `scripts/contribute_redis_examples.py`
Example implementations for redis-py that can be contributed to the project.

**Usage**:
```bash
python3 scripts/contribute_redis_examples.py
```

## How to Contribute

1. **Find an issue** using the find_contribution_opportunities script
2. **Fork the repository** on GitHub
3. **Clone your fork** locally
4. **Create a branch** for your contribution
5. **Make your changes** following the project's guidelines
6. **Test your changes** thoroughly
7. **Commit and push** to your fork
8. **Create a Pull Request** on GitHub

## Resources

- [First Timers Only](https://www.firsttimersonly.com/)
- [GitHub Good First Issues](https://github.com/topics/good-first-issue)
- [Up For Grabs](https://up-for-grabs.net/)
- [GitHub Contributing Guide](https://docs.github.com/en/get-started/quickstart/contributing-to-projects)

## Notes

- Always read the project's CONTRIBUTING.md file
- Follow the project's code style and conventions
- Write clear commit messages
- Be patient and respectful with maintainers

