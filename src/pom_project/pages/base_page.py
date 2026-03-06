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

    def click_element(self, selector: str) -> None:
        self.locator(selector).click()

    def fill_text(self, selector: str, value: str) -> None:
        self.locator(selector).fill(value)

    def select_dropdown(
        self,
        selector: str,
        *,
        value: str | None = None,
        label: str | None = None,
        index: int | None = None,
    ) -> None:
        if sum(option is not None for option in (value, label, index)) != 1:
            raise ValueError("Provide exactly one selection argument: value, label, or index.")

        locator = self.locator(selector)
        if value is not None:
            locator.select_option(value=value)
        elif label is not None:
            locator.select_option(label=label)
        else:
            assert index is not None
            locator.select_option(index=index)

    def wait_for_visible(self, selector: str, timeout_ms: float = 5000) -> None:
        expect(self.locator(selector)).to_be_visible(timeout=timeout_ms)

    def element_text(self, selector: str) -> str:
        return self.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.locator(selector).is_visible()

    def title(self) -> str:
        return self.page.title()

    def expect_title(self, title: str | Pattern[str]) -> None:
        expect(self.page).to_have_title(title)
