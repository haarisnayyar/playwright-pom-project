from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

load_dotenv()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise pytest.UsageError(
        f"Missing required environment variable: {name}. "
        "Set it in a local .env file or export it before running tests."
    )


@pytest.fixture(scope="session")
def app_url() -> str:
    return os.getenv("APP_URL", "https://automationteststore.com/")


@pytest.fixture(scope="session")
def login_username() -> str:
    return _required_env("ATS_LOGIN_USERNAME")


@pytest.fixture(scope="session")
def login_password() -> str:
    return _required_env("ATS_LOGIN_PASSWORD")
