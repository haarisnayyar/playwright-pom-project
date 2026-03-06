# Playwright POM Example

A clean starter scaffold for Python Page Object Model (POM) tests with Playwright and pytest.

## Setup

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium firefox webkit
```

## Configuration and Secrets

Create a local env file from the template:

```bash
cp .env.example .env
```

Set values in `.env`:

- `APP_URL`
- `BROWSER` (`chromium`, `firefox`, `webkit`)
- `BROWSERS` (optional comma-separated loop, for example `chromium,firefox,webkit`)
- `ATS_LOGIN_USERNAME`
- `ATS_LOGIN_PASSWORD`
- `SAUCEDEMO_URL`
- `SAUCEDEMO_USERNAME`
- `SAUCEDEMO_PASSWORD`
- `SAUCEDEMO_INVALID_PASSWORD`

Framework config file:

- `config/test_config.toml` controls `browser`, `base_url`, `credential_key`, and `db_path`.
- Env vars override config file values.
- Optional custom config path:

```bash
pytest --framework-config path/to/your_config.toml
```

## Database Connectivity

- Local SQLite store is used for credential retrieval during test execution.
- DB file path is config-driven (`db_path` in `config/test_config.toml`).
- Test setup seeds credentials into DB from env vars, then tests fetch credentials from DB.

## Run checks

```bash
ruff check .
mypy src
pytest -q
```

## Task 3 Scenario 1

Run SauceDemo invalid-login scenario:

```bash
pytest -q tests/task3/test_scenario_1_invalid_login.py
```

Run the same scenario in a Safari-inclusive loop (Playwright Safari = `webkit`):

```bash
pytest -q tests/task3/test_scenario_1_invalid_login.py --browser chromium --browser firefox --browser webkit
```

Headed version:

```bash
pytest -q tests/task3/test_scenario_1_invalid_login.py --browser chromium --browser firefox --browser webkit --headed --slowmo 250
```

## Generate reports (Allure + HTML)

```bash
pytest -q --html=reports/pytest-report.html --self-contained-html --alluredir=reports/allure-results
```

To view Allure report locally, install the Allure CLI once and then run:

```bash
allure serve reports/allure-results
```

## Hooks

- `pytest_runtest_makereport` hook captures screenshot on test failure.
- Screenshots are saved under `reports/screenshots/` and attached to Allure (when available).

## Project layout

- `src/pom_project/pages/` - page object models
- `src/pom_project/db/` - database connectivity and credential store
- `src/pom_project/framework_config.py` - config loader
- `config/test_config.toml` - framework configuration
- `tests/conftest.py` - shared pytest fixtures
- `tests/` - test suite
- `.github/workflows/ci.yml` - CI pipeline (lint + type-check + tests)

## Notes

- Example cross-browser run from env:
  - `BROWSER=firefox pytest -q`
- Example Safari run:
  - `BROWSER=webkit pytest -q`
- Example browser loop from env:
  - `BROWSERS=chromium,firefox,webkit pytest -q tests/task3/test_scenario_1_invalid_login.py`
- Example full override run:
  - `APP_URL=https://staging.your-app.com BROWSER=webkit ATS_LOGIN_USERNAME=user ATS_LOGIN_PASSWORD=pass pytest -q`
