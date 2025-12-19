# Contributing to EventStreamMonitor

Thank you for your interest in contributing to EventStreamMonitor! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists
2. Use the issue template to report bugs
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Docker version, etc.)

### Suggesting Features

1. Check existing issues for similar suggestions
2. Open an issue with the "enhancement" label
3. Describe the feature and its use case
4. Discuss before implementing

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## Development Setup

1. Fork and clone the repository
2. Set up development environment:
   ```bash
   docker-compose up -d
   ```
3. Make your changes
4. Run tests: `python3 scripts/dry_run_tests.py`
5. Ensure all services work correctly

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small

## Commit Messages

- Use clear, descriptive messages
- Reference issue numbers if applicable
- Format: `Type: Brief description`

Examples:
- `Fix: Correct database connection error`
- `Feature: Add health check endpoint`
- `Docs: Update README with new setup steps`

## Testing

- Test your changes locally
- Ensure existing tests still pass
- Add tests for new features when possible

## Questions?

Feel free to open an issue with questions or reach out to the maintainers.

Thank you for contributing! 🎉

