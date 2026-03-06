from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_BROWSERS = {"chromium", "firefox", "webkit"}


@dataclass(frozen=True)
class FrameworkConfig:
    browser: str
    base_url: str
    credential_key: str
    db_path: str


def _default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "test_config.toml"


def load_framework_config(config_path: str | None = None) -> FrameworkConfig:
    path = Path(config_path) if config_path else _default_config_path()
    with path.open("rb") as file_obj:
        parsed = tomllib.load(file_obj)

    framework_cfg = parsed.get("framework", {})
    browser = os.getenv("BROWSER", framework_cfg.get("browser", "chromium"))
    base_url = os.getenv("APP_URL", framework_cfg.get("base_url", "https://automationteststore.com/"))
    credential_key = os.getenv(
        "CREDENTIAL_KEY", framework_cfg.get("credential_key", "automationteststore_user")
    )
    db_path = os.getenv("TEST_DB_PATH", framework_cfg.get("db_path", "data/test_data.sqlite3"))

    if browser not in SUPPORTED_BROWSERS:
        supported = ", ".join(sorted(SUPPORTED_BROWSERS))
        raise ValueError(f"Unsupported browser '{browser}'. Use one of: {supported}")

    return FrameworkConfig(
        browser=browser,
        base_url=base_url,
        credential_key=credential_key,
        db_path=db_path,
    )
