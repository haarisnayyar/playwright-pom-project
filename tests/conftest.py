from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
from dotenv import load_dotenv

from pom_project.db import CredentialStore, LoginCredentials
from pom_project.framework_config import FrameworkConfig, load_framework_config

try:
    import allure
except ImportError:  # pragma: no cover - optional in some local environments
    allure = None

load_dotenv()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise pytest.UsageError(
        f"Missing required environment variable: {name}. "
        "Set it in a local .env file or export it before running tests."
    )


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--framework-config",
        action="store",
        default=None,
        help="Path to framework config file (default: config/test_config.toml).",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "e2e: marks end-to-end tests.")
    if not config.option.browser:
        config_path = config.getoption("--framework-config")
        framework_cfg = load_framework_config(config_path=config_path)
        config.option.browser = framework_cfg.browsers


@pytest.fixture(scope="session")
def framework_config(pytestconfig: pytest.Config) -> FrameworkConfig:
    config_path = pytestconfig.getoption("--framework-config")
    return load_framework_config(config_path=config_path)


@pytest.fixture(scope="session")
def app_url(framework_config: FrameworkConfig) -> str:
    return framework_config.base_url


@pytest.fixture(scope="session")
def saucedemo_url() -> str:
    return os.getenv("SAUCEDEMO_URL", "https://www.saucedemo.com/")


@pytest.fixture(scope="session")
def saucedemo_credential_key(framework_config: FrameworkConfig) -> str:
    return framework_config.saucedemo_credential_key


@pytest.fixture(scope="session")
def saucedemo_invalid_credential_key(framework_config: FrameworkConfig) -> str:
    return framework_config.saucedemo_invalid_credential_key


@pytest.fixture(scope="session")
def saucedemo_credentials(
    credential_store: CredentialStore,
    saucedemo_credential_key: str,
) -> LoginCredentials:
    return credential_store.get_credentials(credential_key=saucedemo_credential_key)


@pytest.fixture(scope="session")
def saucedemo_invalid_credentials(
    credential_store: CredentialStore,
    saucedemo_invalid_credential_key: str,
) -> LoginCredentials:
    return credential_store.get_credentials(credential_key=saucedemo_invalid_credential_key)


@pytest.fixture(scope="session")
def saucedemo_valid_username(saucedemo_credentials: LoginCredentials) -> str:
    return saucedemo_credentials.username


@pytest.fixture(scope="session")
def saucedemo_valid_password(saucedemo_credentials: LoginCredentials) -> str:
    return saucedemo_credentials.password


@pytest.fixture(scope="session")
def credential_key(framework_config: FrameworkConfig) -> str:
    return framework_config.credential_key


@pytest.fixture(scope="session")
def credential_store(
    framework_config: FrameworkConfig,
    credential_key: str,
    saucedemo_credential_key: str,
    saucedemo_invalid_credential_key: str,
) -> CredentialStore:
    username = _required_env("ATS_LOGIN_USERNAME")
    password = _required_env("ATS_LOGIN_PASSWORD")
    saucedemo_username = os.getenv("SAUCEDEMO_USERNAME", "standard_user")
    saucedemo_password = os.getenv("SAUCEDEMO_PASSWORD", "secret_sauce")
    saucedemo_invalid_username = os.getenv("SAUCEDEMO_INVALID_USERNAME", saucedemo_username)
    saucedemo_invalid_password = os.getenv(
        "SAUCEDEMO_INVALID_PASSWORD",
        f"{saucedemo_password}_invalid",
    )

    store = CredentialStore(db_path=framework_config.db_path)
    store.init_schema()
    store.upsert_credentials(
        credential_key=credential_key,
        credentials=LoginCredentials(username=username, password=password),
    )
    store.upsert_credentials(
        credential_key=saucedemo_credential_key,
        credentials=LoginCredentials(username=saucedemo_username, password=saucedemo_password),
    )
    store.upsert_credentials(
        credential_key=saucedemo_invalid_credential_key,
        credentials=LoginCredentials(
            username=saucedemo_invalid_username,
            password=saucedemo_invalid_password,
        ),
    )
    return store


@pytest.fixture(scope="session")
def login_credentials(
    credential_store: CredentialStore,
    credential_key: str,
) -> LoginCredentials:
    return credential_store.get_credentials(credential_key=credential_key)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> None:
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or report.passed:
        return

    page = item.funcargs.get("page")
    if page is None:
        return

    screenshot_dir = Path("reports/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    safe_node_id = re.sub(r"[^a-zA-Z0-9_.-]+", "_", item.nodeid)
    screenshot_path = screenshot_dir / f"{safe_node_id}.png"

    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
    except Exception:
        return

    if allure is not None:
        allure.attach.file(
            str(screenshot_path),
            name=f"failure-{safe_node_id}",
            attachment_type=allure.attachment_type.PNG,
        )
