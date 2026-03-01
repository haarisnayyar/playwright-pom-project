from playwright.sync_api import Locator, Page

from .base_page import BasePage


class LoginPage(BasePage):
    """Page object for login interactions."""

    USER_INPUT_SELECTOR = "input[name='username']"
    PASS_INPUT_SELECTOR = "input[name='password']"
    SUBMIT_BUTTON_SELECTOR = "button[type='submit']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input: Locator = self.locator(self.USER_INPUT_SELECTOR)
        self.password_input: Locator = self.locator(self.PASS_INPUT_SELECTOR)
        self.submit_button: Locator = self.locator(self.SUBMIT_BUTTON_SELECTOR)

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()
