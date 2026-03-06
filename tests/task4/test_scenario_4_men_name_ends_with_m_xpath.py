import allure
import pytest

from pom_project.db import LoginCredentials
from pom_project.pages import AutomationStoreXpathPage


@pytest.mark.e2e
@allure.title("Task 4 Scenario 4: Add Men product whose name ends with M (XPath)")
def test_add_men_product_name_ends_with_m_xpath(
    page,
    app_url: str,
    login_credentials: LoginCredentials,
) -> None:
    store_page = AutomationStoreXpathPage(page)

    with allure.step("Login to website"):
        store_page.open_login(app_url)
        store_page.login(login_credentials.username, login_credentials.password)

    with allure.step("Start with empty cart"):
        store_page.clear_cart_if_needed(app_url)

    with allure.step("Go to Men section"):
        store_page.open_men_section(app_url)

    with allure.step("Add product whose name ends with M"):
        selected_product_name = store_page.add_men_product_ending_with_m_and_get_name(app_url)

    with allure.step("Assert cart item name ends with M"):
        cart_item_name = store_page.get_first_cart_item_name()
        assert selected_product_name.casefold().endswith("m")
        assert cart_item_name.casefold().endswith("m")
