import allure
import pytest

from pom_project.db import LoginCredentials
from pom_project.pages import AutomationStoreCssPage


@pytest.mark.e2e
@allure.title(
    "Task 4 Scenario 2: Add 3 low-price medium T-shirts and 1 high-price shoe with qty 2 (CSS)"
)
def test_add_tshirts_and_shoes_to_cart_with_css_selectors(
    page,
    app_url: str,
    login_credentials: LoginCredentials,
) -> None:
    store_page = AutomationStoreCssPage(page)

    with allure.step("Login to website"):
        store_page.open_login(app_url)
        store_page.login(login_credentials.username, login_credentials.password)

    with allure.step("Clear cart before scenario execution"):
        store_page.clear_cart_if_needed(app_url)

    with allure.step("Go to Apparel & Accessories > T-shirts and sort by low to high"):
        store_page.open_tshirts_via_apparel(app_url)
        store_page.sort_low_to_high()

    with allure.step("Add top 3 low-price T-shirts with Medium size"):
        added_tshirts = store_page.add_top_three_tshirts_with_medium_size()

    with allure.step("Go to Apparel & Accessories > Shoes and sort by high to low"):
        store_page.open_shoes_via_apparel(app_url)
        store_page.sort_high_to_low()

    with allure.step("Add highest-value shoe product to cart"):
        added_shoe = store_page.add_highest_value_shoe()

    with allure.step("Set shoe quantity to 2 in cart"):
        store_page.set_cart_quantity(added_shoe, quantity=2)

    with allure.step("Assert selected items in cart"):
        store_page.assert_tshirts_in_cart_with_medium(added_tshirts)
        store_page.assert_cart_quantity(added_shoe, expected_quantity=2)
