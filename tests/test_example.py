import allure
import pytest

from pom_project.db import LoginCredentials
from pom_project.pages.account_page import AccountPage
from pom_project.pages.login_page import LoginPage


@pytest.mark.e2e
@allure.title("Returning customer can log in to Automation Test Store")
def test_user_can_login_to_automation_test_store(
    page,
    app_url: str,
    login_credentials: LoginCredentials,
) -> None:
    login_page = LoginPage(page)
    account_page = AccountPage(page)

    with allure.step("Open login page"):
        login_page.open(app_url)
        login_page.expect_loaded()

    with allure.step("Submit valid credentials"):
        login_page.login(login_credentials.username, login_credentials.password)

    with allure.step("Verify account page is displayed"):
        account_page.expect_loaded()
