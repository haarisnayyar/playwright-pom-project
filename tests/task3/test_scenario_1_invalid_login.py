import allure
import pytest

from pom_project.db import LoginCredentials
from pom_project.pages import SauceDemoLoginPage


@pytest.mark.e2e
@allure.title("Scenario 1: SauceDemo invalid login shows error")
def test_saucedemo_invalid_login_shows_error(
    page,
    saucedemo_url: str,
    saucedemo_invalid_credentials: LoginCredentials,
) -> None:
    login_page = SauceDemoLoginPage(page)

    with allure.step("Go to URL"):
        login_page.open(saucedemo_url)
        login_page.expect_loaded()

    with allure.step("Enter valid username and invalid password"):
        login_page.login(
            saucedemo_invalid_credentials.username,
            saucedemo_invalid_credentials.password,
        )

    with allure.step("Assert error message"):
        login_page.expect_invalid_login_error()
