from playwright.sync_api import Locator, Page, expect

from .base_page import BasePage


class LoginPage(BasePage):
    """Page object for login interactions."""

    LOGIN_PATH = "index.php?rt=account/login"
    USER_INPUT_SELECTOR = "#loginFrm_loginname"
    PASS_INPUT_SELECTOR = "#loginFrm_password"
    SUBMIT_BUTTON_SELECTOR = "button[title='Login']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input: Locator = self.locator(self.USER_INPUT_SELECTOR)
        self.password_input: Locator = self.locator(self.PASS_INPUT_SELECTOR)
        self.submit_button: Locator = self.locator(self.SUBMIT_BUTTON_SELECTOR)
        self.returning_customer_heading: Locator = page.get_by_role(
            "heading", name="Returning Customer", exact=True
        )

    def open(self, base_url: str) -> None:
        self.goto_path(base_url, self.LOGIN_PATH)

    def expect_loaded(self) -> None:
        expect(self.returning_customer_heading).to_be_visible()
        expect(self.username_input).to_be_visible()

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()
