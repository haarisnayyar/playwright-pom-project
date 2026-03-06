from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SUPPORTED_BROWSERS = {"chromium", "firefox", "webkit"}


@dataclass(frozen=True)
class FrameworkConfig:
    browsers: list[str]
    base_url: str
    credential_key: str
    saucedemo_credential_key: str
    saucedemo_invalid_credential_key: str
    db_path: str


def _default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "test_config.toml"


def _unique_in_order(values: list[str]) -> list[str]:
    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique


def _resolve_browsers(framework_cfg: dict[str, Any]) -> list[str]:
    browsers_env = os.getenv("BROWSERS")
    browser_env = os.getenv("BROWSER")

    if browsers_env:
        browsers = [item.strip() for item in browsers_env.split(",") if item.strip()]
    elif browser_env:
        browsers = [browser_env]
    else:
        configured_browsers = framework_cfg.get("browsers")
        configured_browser = framework_cfg.get("browser")
        if isinstance(configured_browsers, list) and configured_browsers:
            browsers = [str(item).strip() for item in configured_browsers if str(item).strip()]
        elif configured_browser:
            browsers = [str(configured_browser).strip()]
        else:
            browsers = ["chromium"]

    browsers = _unique_in_order(browsers)
    invalid = [browser for browser in browsers if browser not in SUPPORTED_BROWSERS]
    if invalid:
        supported = ", ".join(sorted(SUPPORTED_BROWSERS))
        invalid_list = ", ".join(invalid)
        raise ValueError(f"Unsupported browser(s): {invalid_list}. Use only: {supported}")

    return browsers


def load_framework_config(config_path: str | None = None) -> FrameworkConfig:
    path = Path(config_path) if config_path else _default_config_path()
    with path.open("rb") as file_obj:
        parsed = tomllib.load(file_obj)

    framework_cfg = parsed.get("framework", {})
    browsers = _resolve_browsers(framework_cfg)
    base_url = os.getenv("APP_URL", framework_cfg.get("base_url", "https://automationteststore.com/"))
    credential_key = os.getenv(
        "CREDENTIAL_KEY", framework_cfg.get("credential_key", "automationteststore_user")
    )
    saucedemo_credential_key = os.getenv(
        "SAUCEDEMO_CREDENTIAL_KEY", framework_cfg.get("saucedemo_credential_key", "saucedemo_user")
    )
    saucedemo_invalid_credential_key = os.getenv(
        "SAUCEDEMO_INVALID_CREDENTIAL_KEY",
        framework_cfg.get("saucedemo_invalid_credential_key", "saucedemo_user_invalid"),
    )
    db_path = os.getenv("TEST_DB_PATH", framework_cfg.get("db_path", "data/test_data.sqlite3"))

    return FrameworkConfig(
        browsers=browsers,
        base_url=base_url,
        credential_key=credential_key,
        saucedemo_credential_key=saucedemo_credential_key,
        saucedemo_invalid_credential_key=saucedemo_invalid_credential_key,
        db_path=db_path,
    )
