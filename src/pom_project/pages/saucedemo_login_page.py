from playwright.sync_api import Locator, Page, expect

from .base_page import BasePage


class SauceDemoLoginPage(BasePage):
    """Page object for SauceDemo login page interactions."""

    USERNAME_INPUT_SELECTOR = "#user-name"
    PASSWORD_INPUT_SELECTOR = "#password"
    LOGIN_BUTTON_SELECTOR = "#login-button"
    ERROR_MESSAGE_SELECTOR = "h3[data-test='error']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input: Locator = self.locator(self.USERNAME_INPUT_SELECTOR)
        self.password_input: Locator = self.locator(self.PASSWORD_INPUT_SELECTOR)
        self.login_button: Locator = self.locator(self.LOGIN_BUTTON_SELECTOR)
        self.error_message: Locator = self.locator(self.ERROR_MESSAGE_SELECTOR)

    def open(self, base_url: str) -> None:
        self.goto(base_url)

    def expect_loaded(self) -> None:
        self.wait_for_visible(self.USERNAME_INPUT_SELECTOR)
        self.wait_for_visible(self.PASSWORD_INPUT_SELECTOR)
        self.wait_for_visible(self.LOGIN_BUTTON_SELECTOR)

    def login(self, username: str, password: str) -> None:
        self.fill_text(self.USERNAME_INPUT_SELECTOR, username)
        self.fill_text(self.PASSWORD_INPUT_SELECTOR, password)
        self.click_element(self.LOGIN_BUTTON_SELECTOR)

    def expect_invalid_login_error(self) -> None:
        expect(self.error_message).to_contain_text(
            "Username and password do not match any user in this service"
        )
