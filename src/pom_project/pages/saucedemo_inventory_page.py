import re

from playwright.sync_api import Locator, Page, expect

from .base_page import BasePage


class SauceDemoInventoryPage(BasePage):
    """Page object for SauceDemo inventory dashboard."""

    INVENTORY_URL_PATTERN = re.compile(r".*/inventory\.html$")
    PAGE_TITLE_SELECTOR = "span[data-test='title']"
    INVENTORY_CONTAINER_SELECTOR = "[data-test='inventory-container']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page_title: Locator = self.locator(self.PAGE_TITLE_SELECTOR)
        self.inventory_container: Locator = self.locator(self.INVENTORY_CONTAINER_SELECTOR)

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(self.INVENTORY_URL_PATTERN)
        expect(self.page_title).to_have_text("Products")
        expect(self.inventory_container).to_be_visible()
