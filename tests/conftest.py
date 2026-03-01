from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session")
def app_url() -> str:
    """Default target URL for smoke tests; override with APP_URL."""
    return os.getenv("APP_URL", "https://example.com")
