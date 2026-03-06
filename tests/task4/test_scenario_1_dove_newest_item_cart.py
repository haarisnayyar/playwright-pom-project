import allure
import pytest

from pom_project.db import LoginCredentials
from pom_project.pages import AutomationStoreXpathPage


@pytest.mark.e2e
@allure.title("Task 4 Scenario 1: Login and add newest Dove item to cart using XPath")
def test_login_and_add_newest_dove_item_to_cart_with_xpath(
    page,
    app_url: str,
    login_credentials: LoginCredentials,
) -> None:
    store_page = AutomationStoreXpathPage(page)

    with allure.step("Login to the website"):
        store_page.open_login(app_url)
        store_page.login(login_credentials.username, login_credentials.password)

    with allure.step("Start with an empty cart for deterministic quantity assertion"):
        store_page.clear_cart_if_needed(app_url)

    with allure.step("Scroll and open Dove brand from brands scrolling list"):
        store_page.open_home(app_url)
        store_page.open_dove_products_from_brand_scrolling_list()

    with allure.step("Select newest item from Dove listing"):
        store_page.sort_by_newest()
        newest_item_name = store_page.open_newest_item_and_get_name()

    with allure.step("Add newest item to cart"):
        store_page.add_item_to_cart()

    with allure.step("Assert item in cart with amount and quantity"):
        cart_item = store_page.get_cart_item_details()
        assert newest_item_name.casefold() in cart_item.name.casefold()
        assert cart_item.quantity == 1
        assert cart_item.unit_price > 0
        assert cart_item.total_price == pytest.approx(
            cart_item.unit_price * cart_item.quantity,
            abs=0.01,
        )
