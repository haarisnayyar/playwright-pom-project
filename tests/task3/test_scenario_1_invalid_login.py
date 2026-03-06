import allure
import pytest

from pom_project.pages import SauceDemoLoginPage


@pytest.mark.e2e
@allure.title("Scenario 1: SauceDemo invalid login shows error")
def test_saucedemo_invalid_login_shows_error(
    page,
    saucedemo_url: str,
    saucedemo_valid_username: str,
    saucedemo_invalid_password: str,
) -> None:
    login_page = SauceDemoLoginPage(page)

    with allure.step("Go to URL"):
        login_page.open(saucedemo_url)
        login_page.expect_loaded()

    with allure.step("Enter valid username and invalid password"):
        login_page.login(saucedemo_valid_username, saucedemo_invalid_password)

    with allure.step("Assert error message"):
        login_page.expect_invalid_login_error()
