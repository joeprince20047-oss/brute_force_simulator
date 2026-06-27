# Contributing Guide

Thank you for contributing to the Brute Force Simulator project!

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, protected — only merged via PR |
| `develop` | Integration branch |
| `feature/your-feature` | New feature development |
| `fix/bug-name` | Bug fixes |

## Workflow

1. Fork the repository
2. Create a feature branch from `develop`:
   ```bash
   git checkout develop
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and write/update tests
4. Run tests locally:
   ```bash
   pytest tests/ -v
   ```
5. Commit using conventional commits:
   ```
   feat: add GUI dashboard
   fix:  handle HTTP 429 correctly
   docs: update README setup steps
   test: add attacker engine tests
   ```
6. Push your branch and open a Pull Request against `develop`

## Code Standards

- Python 3.10+ compatible
- All new functions must have docstrings
- All new modules must have corresponding tests in `tests/`
- Never hardcode credentials or target URLs

## Ethical Rules

- This tool is for **educational use only**
- All test targets must be localhost or systems you own
- Do not add real leaked credential databases to the repo
