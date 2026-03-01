# Playwright POM Example

A clean starter scaffold for Python Page Object Model (POM) tests with Playwright and pytest.

## Setup

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
```

## Test target

Create a local env file from the template:

```bash
cp .env.example .env
```

Then set:

- `APP_URL` (default is fine for this project)
- `ATS_LOGIN_USERNAME`
- `ATS_LOGIN_PASSWORD`

## Run checks

```bash
ruff check .
mypy src
pytest -q
```

## Generate reports (Allure + HTML)

```bash
pytest -q --html=reports/pytest-report.html --self-contained-html --alluredir=reports/allure-results
```

To view Allure report locally, install the Allure CLI once and then run:

```bash
allure serve reports/allure-results
```

## Project layout

- `src/pom_project/pages/` - page object models
- `tests/conftest.py` - shared pytest fixtures
- `tests/` - test suite
- `.github/workflows/ci.yml` - CI pipeline (lint + type-check + tests)

## Notes

- Set `APP_URL` to run tests against another environment.
  - Example: `APP_URL=https://staging.your-app.com ATS_LOGIN_USERNAME=user ATS_LOGIN_PASSWORD=pass pytest -q`
