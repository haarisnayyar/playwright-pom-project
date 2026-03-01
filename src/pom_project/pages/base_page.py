from __future__ import annotations

from re import Pattern

from playwright.sync_api import Locator, Page, expect


class BasePage:
    """Base class shared across all page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def title(self) -> str:
        return self.page.title()

    def expect_title(self, title: str | Pattern[str]) -> None:
        expect(self.page).to_have_title(title)
