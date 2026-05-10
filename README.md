# Playwright POM Example

A clean starter scaffold for Python Page Object Model (POM) tests with Playwright and pytest.

## Setup

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium firefox webkit
```

## Configuration

Optional runtime overrides can be set in the shell or copied into a local `.env` file from the
template:

```bash
cp .env.example .env
```

Supported non-secret overrides:

- `APP_URL`
- `BROWSER` (`chromium`, `firefox`, `webkit`)
- `BROWSERS` (optional comma-separated loop, for example `chromium,firefox,webkit`)
- `SAUCEDEMO_URL`
- `SAUCEDEMO_CREDENTIAL_KEY`
- `SAUCEDEMO_INVALID_CREDENTIAL_KEY`

Framework config file:

- `config/test_config.toml` controls `browser(s)`, URLs, credential keys, and `db_path`.
- Env vars override config file values when set in the runtime environment.
- Optional custom config path:

```bash
venv/bin/pytest --framework-config path/to/your_config.toml
```

## Database Connectivity

- Local SQLite store is used for credential retrieval during test execution.
- DB file path is `data/test_data.sqlite3` by default.
- DB table is `login_credentials`.
- `data/test_data.sqlite3` is local-only and must not be committed.
- Credentials must not be stored in `.env`, `.env.example`, README, or source files.
- Tests fetch credentials from SQLite using `CredentialStore` and configured credential keys.

## Run checks

```bash
venv/bin/ruff check .
venv/bin/mypy src
venv/bin/pytest
venv/bin/pytest --browser chromium --browser firefox --browser webkit
```

## Task 3 Scenario 1

Run SauceDemo invalid-login scenario:

```bash
venv/bin/pytest -q tests/task3/test_scenario_1_invalid_login.py
```

Run the same scenario in a Safari-inclusive loop (Playwright Safari = `webkit`):

```bash
venv/bin/pytest -q tests/task3/test_scenario_1_invalid_login.py --browser chromium --browser firefox --browser webkit
```

Headed version:

```bash
venv/bin/pytest -q tests/task3/test_scenario_1_invalid_login.py --browser chromium --browser firefox --browser webkit --headed --slowmo 250
```

## Task 3 Scenario 2

Run SauceDemo valid-login scenario:

```bash
venv/bin/pytest -q tests/task3/test_scenario_2_valid_login.py
```

Run the same scenario across all browsers:

```bash
venv/bin/pytest -q tests/task3/test_scenario_2_valid_login.py --browser chromium --browser firefox --browser webkit
```

## Task 4 Scenario 1

Run Automation Test Store Dove newest-item cart scenario (XPath selectors):

```bash
venv/bin/pytest -q tests/task4/test_scenario_1_dove_newest_item_cart.py
```

Run across all browsers:

```bash
venv/bin/pytest -q tests/task4/test_scenario_1_dove_newest_item_cart.py --browser chromium --browser firefox --browser webkit
```

## Task 4 Scenario 2

Run Apparel/T-shirts/Shoes cart scenario (CSS selectors):

```bash
venv/bin/pytest -q tests/task4/test_scenario_2_apparel_shoes_css_cart.py
```

Run across all browsers:

```bash
venv/bin/pytest -q tests/task4/test_scenario_2_apparel_shoes_css_cart.py --browser chromium --browser firefox --browser webkit
```

## Task 4 Scenario 3

Run Skin Care sale-items cart scenario (XPath selectors):

```bash
venv/bin/pytest -q tests/task4/test_scenario_3_skin_care_sale_items_xpath.py
```

Run across all browsers:

```bash
venv/bin/pytest -q tests/task4/test_scenario_3_skin_care_sale_items_xpath.py --browser chromium --browser firefox --browser webkit
```

## Task 4 Scenario 4

Run Men product-name-ends-with-M scenario (XPath selectors):

```bash
venv/bin/pytest -q tests/task4/test_scenario_4_men_name_ends_with_m_xpath.py
```

Run across all browsers:

```bash
venv/bin/pytest -q tests/task4/test_scenario_4_men_name_ends_with_m_xpath.py --browser chromium --browser firefox --browser webkit
```

## Generate reports (Allure + HTML)

```bash
venv/bin/pytest -q --html=reports/pytest-report.html --self-contained-html --alluredir=reports/allure-results
```

To view Allure report locally, install the Allure CLI once and then run:

```bash
allure serve reports/allure-results
```

## One-command all-scenarios run across all browsers

Run entire pytest suite on Chromium, Firefox, and WebKit and generate a combined Allure report:

```bash
./scripts/run_all_pytest.sh
```

Alternative:

```bash
make pytest-all
```

Optional environment overrides:

- `HEADED=true` to run browsers in headed mode
- `SLOWMO_MS=150` to slow interactions
- `MAX_ATTEMPTS=2` retry count per browser if transient failures occur

Outputs:

- Per-browser pytest HTML reports:
  - `reports/pytest-report-chromium.html`
  - `reports/pytest-report-firefox.html`
  - `reports/pytest-report-webkit.html`
- Per-browser Allure raw results:
  - `reports/allure-results-chromium`
  - `reports/allure-results-firefox`
  - `reports/allure-results-webkit`
- Combined Allure:
  - `reports/allure-results`
  - `reports/allure-html/index.html`

Open the generated combined Allure HTML report:

```bash
allure open reports/allure-html
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

- Example Firefox run:
  - `venv/bin/pytest --browser firefox`
- Example WebKit run:
  - `venv/bin/pytest --browser webkit`
- Example cross-browser run:
  - `venv/bin/pytest --browser chromium --browser firefox --browser webkit`
- Example app URL override:
  - `APP_URL=https://staging.your-app.com venv/bin/pytest --browser webkit`
