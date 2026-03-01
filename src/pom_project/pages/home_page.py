from playwright.sync_api import Locator, Page, expect

from .base_page import BasePage


class HomePage(BasePage):
    """Page object for the home page."""

    HEADER_SELECTOR = "h1"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header: Locator = self.locator(self.HEADER_SELECTOR)

    def header_text(self) -> str:
        return self.header.inner_text()

    def expect_header_text(self, text: str) -> None:
        expect(self.header).to_have_text(text)
