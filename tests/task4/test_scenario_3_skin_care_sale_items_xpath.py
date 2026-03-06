import allure
import pytest

from pom_project.pages import AutomationStoreXpathPage


@pytest.mark.e2e
@allure.title("Task 4 Scenario 3: Skin Care sale items cart validation with XPath")
def test_skin_care_sale_items_cart_validation_with_xpath(
    page,
    app_url: str,
) -> None:
    store_page = AutomationStoreXpathPage(page)

    with allure.step("Go back to home URL"):
        store_page.open_home(app_url)

    with allure.step("Start with empty cart"):
        store_page.clear_cart_if_needed(app_url)

    with allure.step("Go to Skin Care section"):
        store_page.open_skin_care_section(app_url)

    with allure.step("Log sale counts and add sale items to cart"):
        sale_summary = store_page.add_skin_care_sale_items_and_get_summary()
        log_text = (
            f"Sale items: {sale_summary.sale_count}\\n"
            f"Sale and out-of-stock items: {sale_summary.sale_and_out_of_stock_count}\\n"
            f"Added sale items: {sale_summary.added_sale_count}\\n"
            f"Expected sale amount: {sale_summary.added_sale_amount:.2f}"
        )
        allure.attach(
            log_text,
            name="skin-care-sale-summary",
            attachment_type=allure.attachment_type.TEXT,
        )
        print(log_text)

    with allure.step("Assert total item count and amount of sale items in cart"):
        cart_summary = store_page.get_cart_summary(app_url)
        assert sale_summary.added_sale_count > 0
        assert cart_summary.line_item_count == sale_summary.added_sale_count
        assert cart_summary.total_quantity == sale_summary.added_sale_count
        assert cart_summary.total_amount == pytest.approx(sale_summary.added_sale_amount, abs=0.01)
