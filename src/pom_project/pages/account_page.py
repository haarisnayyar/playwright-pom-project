import re

from playwright.sync_api import Locator, Page, expect

from .base_page import BasePage


class AccountPage(BasePage):
    """Page object for account dashboard assertions after login."""

    ACCOUNT_URL_PATTERN = re.compile(r".*rt=account/account.*")
    ACCOUNT_HEADER_SELECTOR = "span.maintext"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.account_header: Locator = self.locator(self.ACCOUNT_HEADER_SELECTOR)
        self.logoff_link: Locator = page.get_by_role("link", name="Logoff", exact=True).first

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(self.ACCOUNT_URL_PATTERN)
        expect(self.account_header).to_contain_text("My Account")
        expect(self.logoff_link).to_be_visible()
