import allure
import pytest

from pom_project.db import LoginCredentials
from pom_project.pages import SauceDemoInventoryPage, SauceDemoLoginPage


@pytest.mark.e2e
@allure.title("Scenario 2: SauceDemo valid login lands on dashboard")
def test_saucedemo_valid_login_lands_on_dashboard(
    page,
    saucedemo_url: str,
    saucedemo_credentials: LoginCredentials,
) -> None:
    login_page = SauceDemoLoginPage(page)
    inventory_page = SauceDemoInventoryPage(page)

    with allure.step("Go to URL"):
        login_page.open(saucedemo_url)
        login_page.expect_loaded()

    with allure.step("Enter valid username and valid password"):
        login_page.login(saucedemo_credentials.username, saucedemo_credentials.password)

    with allure.step("Assert user lands on dashboard"):
        inventory_page.expect_loaded()

    with allure.step("Hold dashboard view for visual confirmation"):
        page.wait_for_timeout(1000)
