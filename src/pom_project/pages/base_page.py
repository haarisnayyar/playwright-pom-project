from __future__ import annotations

from re import Pattern
from urllib.parse import urljoin

from playwright.sync_api import Locator, Page, expect


class BasePage:
    """Base class shared across all page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    def goto_path(self, base_url: str, path: str) -> None:
        self.goto(urljoin(base_url, path))

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def title(self) -> str:
        return self.page.title()

    def expect_title(self, title: str | Pattern[str]) -> None:
        expect(self.page).to_have_title(title)
