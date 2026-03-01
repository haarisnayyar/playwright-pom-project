# Playwright POM Example

A clean starter scaffold for Python Page Object Model (POM) tests with Playwright and pytest.

## Setup

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
```

## Run checks

```bash
ruff check .
mypy src
pytest -q
```

## Project layout

- `src/pom_project/pages/` - page object models
- `tests/conftest.py` - shared pytest fixtures
- `tests/` - test suite
- `.github/workflows/ci.yml` - CI pipeline (lint + type-check + tests)

## Notes

- Default test target URL is `https://example.com`.
- Set `APP_URL` to run the same tests against your own environment.
  - Example: `APP_URL=https://staging.your-app.com pytest -q`
