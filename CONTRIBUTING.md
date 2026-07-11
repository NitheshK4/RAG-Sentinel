# Contributing to RAG Sentinel

Thank you for your interest in contributing to RAG Sentinel! This guide will help you get started.

---

## 🛠️ Development Environment Setup

### Prerequisites

- **Python 3.11+**
- **Git**
- A [Google AI API key](https://aistudio.google.com/apikey) (optional — demo mode works without it)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/NitheshK4/RAG-Sentinel.git
cd RAG-Sentinel

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install dev dependencies
pip install pytest ruff

# 5. Run the server
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📐 Code Style

- **Python**: Follow PEP 8. We use [Ruff](https://docs.astral.sh/ruff/) for linting.
- **JavaScript**: Use consistent `camelCase` for variables and functions.
- **CSS**: Use BEM-inspired naming with `kebab-case`.

### Linting

```bash
# Run linter
ruff check backend/ tests/

# Auto-fix
ruff check --fix backend/ tests/
```

---

## 📝 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

Types:
  feat     — new feature
  fix      — bug fix
  test     — adding or updating tests
  docs     — documentation changes
  refactor — code change that neither fixes a bug nor adds a feature
  style    — formatting, missing semicolons, etc.
  chore    — build process, auxiliary tools, etc.
```

**Examples:**
```
feat: add rate-limit middleware with per-IP tracking
fix: correct JSON parsing for nested LLM responses
test: add unit tests for incident export endpoint
docs: update README with Docker quickstart
```

---

## 🧪 Testing

All new features and bug fixes should include tests.

```bash
# Run the full test suite
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_api.py -v

# Run with coverage (if installed)
python -m pytest tests/ --cov=backend --cov-report=term-missing
```

### Test Guidelines

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use `pytest` fixtures for shared setup
- Mock external API calls — never hit real APIs in tests

---

## 🔄 Pull Request Process

1. **Fork** the repository and create a feature branch from `main`
2. **Make your changes** following the code style and commit conventions above
3. **Add tests** for any new functionality
4. **Run the test suite** and ensure all tests pass
5. **Update documentation** if your change affects the public API or user-facing behavior
6. **Submit a PR** with a clear description of what changed and why

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] Tests added/updated and passing
- [ ] Commit messages follow conventional commit format
- [ ] Documentation updated (if applicable)
- [ ] No new linting warnings

---

## 🏗️ Project Structure Reference

```
backend/
  core/         → Config, LLM client, rate limiter, middleware
  models/       → Pydantic v2 I/O schemas
  routes/       → FastAPI route modules (ingestion, detection, etc.)
  main.py       → App entrypoint

frontend/       → SPA (HTML, CSS, JS)
schemas/        → JSON Schema definitions
examples/       → Sample data bundles
tests/          → pytest test suite
```

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
