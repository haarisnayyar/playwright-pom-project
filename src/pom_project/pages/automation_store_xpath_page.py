from __future__ import annotations

import re
from dataclasses import dataclass

from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from .base_page import BasePage


@dataclass(frozen=True)
class CartItemDetails:
    name: str
    unit_price: float
    quantity: int
    total_price: float


@dataclass(frozen=True)
class SkinCareSaleSummary:
    sale_count: int
    sale_and_out_of_stock_count: int
    added_sale_count: int
    added_sale_amount: float


@dataclass(frozen=True)
class CartSummary:
    line_item_count: int
    total_quantity: int
    total_amount: float


class AutomationStoreXpathPage(BasePage):
    """Automation Test Store flow implemented with XPath selectors."""

    LOGIN_PATH = "index.php?rt=account/login"
    CART_PATH = "index.php?rt=checkout/cart"
    SKIN_CARE_PATH = "index.php?rt=product/category&path=43"

    USERNAME_INPUT_XPATH = "xpath=//input[@id='loginFrm_loginname']"
    PASSWORD_INPUT_XPATH = "xpath=//input[@id='loginFrm_password']"
    LOGIN_BUTTON_XPATH = "xpath=//button[@title='Login']"

    DOVE_BRAND_LINK_XPATH = (
        "xpath=(//a[.//img[contains(translate(@alt,'DOVE','dove'),'dove')]])[1]"
    )
    SORT_DROPDOWN_XPATH = "xpath=//select[@id='sort']"
    NEWEST_SORT_VALUE = "date_modified-DESC"
    NEWEST_PRODUCT_LINK_XPATH = "xpath=(//a[contains(@class,'prdocutname')])[1]"

    ADD_TO_CART_BUTTON_XPATH = (
        "xpath=//a[contains(@class,'cart') and contains(normalize-space(.),'Add to Cart')]"
    )

    CART_TABLE_XPATH = "xpath=//table[.//input[contains(@name,'quantity')]]"
    CART_ITEM_NAME_XPATH = (
        "xpath=(//table[.//input[contains(@name,'quantity')]]//tr[position()>1]/td[2]//a)[1]"
    )
    CART_UNIT_PRICE_XPATH = (
        "xpath=(//table[.//input[contains(@name,'quantity')]]//tr[position()>1]/td[4])[1]"
    )
    CART_QUANTITY_INPUT_XPATH = (
        "xpath=(//table[.//input[contains(@name,'quantity')]]//tr[position()>1]/td[5]"
        "//input[contains(@name,'quantity')])[1]"
    )
    CART_TOTAL_PRICE_XPATH = (
        "xpath=(//table[.//input[contains(@name,'quantity')]]//tr[position()>1]/td[6])[1]"
    )
    CART_REMOVE_BUTTONS_XPATH = (
        "xpath=//table[.//input[contains(@name,'quantity')]]//a"
        "[contains(@href,'rt=checkout/cart') and contains(@href,'remove=')]"
    )
    CART_PRODUCT_ROWS_XPATH = (
        "xpath=//table[.//input[contains(@name,'quantity')]]"
        "//tr[td and .//input[contains(@name,'quantity')]]"
    )

    SKIN_CARE_PRODUCT_CARDS_XPATH = (
        "xpath=//div[contains(@class,'fixed_wrapper')]/following-sibling::div[contains(@class,'thumbnail')]"
    )
    CARD_SALE_BADGE_XPATH = "xpath=.//span[contains(@class,'sale')]"
    CARD_OUT_OF_STOCK_XPATH = (
        "xpath=.//*[contains(@class,'nostock') or "
        "contains(translate(normalize-space(.),'OUT OF STOCK','out of stock'),'out of stock')]"
    )
    CARD_ADD_TO_CART_XPATH = (
        "xpath=.//a[contains(@class,'productcart') and contains(@title,'Add to Cart')]"
    )
    CARD_SALE_PRICE_XPATH = (
        "xpath=.//div[contains(@class,'pricenew') or contains(@class,'oneprice')]"
    )

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def open_login(self, base_url: str) -> None:
        self.goto_path(base_url, self.LOGIN_PATH)
        self.wait_for_visible(self.USERNAME_INPUT_XPATH)

    def login(self, username: str, password: str) -> None:
        self.fill_text(self.USERNAME_INPUT_XPATH, username)
        self.fill_text(self.PASSWORD_INPUT_XPATH, password)
        self.click_element(self.LOGIN_BUTTON_XPATH)
        expect(self.page).to_have_url(re.compile(r".*rt=account/account.*"))

    def open_home(self, base_url: str) -> None:
        for attempt in range(2):
            try:
                self.goto(base_url)
                break
            except PlaywrightTimeoutError:
                if attempt == 1:
                    raise
        self.wait_for_visible(self.DOVE_BRAND_LINK_XPATH)

    def clear_cart_if_needed(self, base_url: str) -> None:
        self.goto_path(base_url, self.CART_PATH)
        self.page.wait_for_load_state("domcontentloaded")
        remove_buttons = self.locator(self.CART_REMOVE_BUTTONS_XPATH)
        while remove_buttons.count() > 0:
            remove_buttons.first.click()
            self.page.wait_for_load_state("domcontentloaded")
            remove_buttons = self.locator(self.CART_REMOVE_BUTTONS_XPATH)

    def open_skin_care_section(self, base_url: str) -> None:
        self.goto_path(base_url, self.SKIN_CARE_PATH)
        self.page.wait_for_load_state("domcontentloaded")
        expect(self.locator(self.SKIN_CARE_PRODUCT_CARDS_XPATH).first).to_be_visible()

    def open_dove_products_from_brand_scrolling_list(self) -> None:
        dove_brand_link = self.locator(self.DOVE_BRAND_LINK_XPATH)
        dove_brand_link.scroll_into_view_if_needed()
        dove_brand_link.click()
        expect(self.page).to_have_url(re.compile(r".*manufacturer_id=18.*"))

    def sort_by_newest(self) -> None:
        self.select_dropdown(
            self.SORT_DROPDOWN_XPATH,
            value=self.NEWEST_SORT_VALUE,
        )
        expect(self.page).to_have_url(re.compile(r".*sort=date_modified-DESC.*"))

    def open_newest_item_and_get_name(self) -> str:
        newest_item_link = self.locator(self.NEWEST_PRODUCT_LINK_XPATH)
        expect(newest_item_link).to_be_visible()
        newest_item_name = self._normalize_text(newest_item_link.inner_text())
        newest_item_link.click()
        self.wait_for_visible(self.ADD_TO_CART_BUTTON_XPATH)
        return newest_item_name

    def add_item_to_cart(self) -> None:
        add_to_cart_button = self.locator(self.ADD_TO_CART_BUTTON_XPATH)
        add_to_cart_button.scroll_into_view_if_needed()
        add_to_cart_button.click()
        checkout_cart_url = re.compile(r".*rt=checkout/cart.*")
        try:
            expect(self.page).to_have_url(checkout_cart_url, timeout=5000)
        except AssertionError:
            # Firefox can intermittently miss this anchor click handler.
            # Submit the containing form directly as a fallback.
            add_to_cart_button.evaluate(
                "el => { const form = el.closest('form'); if (form) form.submit(); }"
            )
            expect(self.page).to_have_url(checkout_cart_url, timeout=10000)
        self.wait_for_visible(self.CART_TABLE_XPATH)

    def get_cart_item_details(self) -> CartItemDetails:
        item_name = self._normalize_text(self.element_text(self.CART_ITEM_NAME_XPATH))
        unit_price = self._parse_currency(self.element_text(self.CART_UNIT_PRICE_XPATH))
        quantity = int(self.locator(self.CART_QUANTITY_INPUT_XPATH).input_value())
        total_price = self._parse_currency(self.element_text(self.CART_TOTAL_PRICE_XPATH))
        return CartItemDetails(
            name=item_name,
            unit_price=unit_price,
            quantity=quantity,
            total_price=total_price,
        )

    def add_skin_care_sale_items_and_get_summary(self) -> SkinCareSaleSummary:
        cards = self.locator(self.SKIN_CARE_PRODUCT_CARDS_XPATH)
        sale_count = 0
        sale_and_out_of_stock_count = 0
        added_sale_count = 0
        added_sale_amount = 0.0

        for index in range(cards.count()):
            card = cards.nth(index)
            if card.locator(self.CARD_SALE_BADGE_XPATH).count() == 0:
                continue

            sale_count += 1
            if card.locator(self.CARD_OUT_OF_STOCK_XPATH).count() > 0:
                sale_and_out_of_stock_count += 1
                continue

            add_to_cart = card.locator(self.CARD_ADD_TO_CART_XPATH)
            if add_to_cart.count() == 0:
                continue

            price_locator = card.locator(self.CARD_SALE_PRICE_XPATH)
            if price_locator.count() == 0:
                continue

            sale_price = self._parse_currency(price_locator.first.inner_text())
            add_to_cart.first.scroll_into_view_if_needed()
            add_to_cart.first.click()
            self.page.wait_for_timeout(400)

            added_sale_count += 1
            added_sale_amount += sale_price

        return SkinCareSaleSummary(
            sale_count=sale_count,
            sale_and_out_of_stock_count=sale_and_out_of_stock_count,
            added_sale_count=added_sale_count,
            added_sale_amount=added_sale_amount,
        )

    def get_cart_summary(self, base_url: str) -> CartSummary:
        self.goto_path(base_url, self.CART_PATH)
        self.page.wait_for_load_state("domcontentloaded")

        rows = self.locator(self.CART_PRODUCT_ROWS_XPATH)
        line_item_count = rows.count()
        total_quantity = 0
        total_amount = 0.0

        for index in range(line_item_count):
            row = rows.nth(index)
            quantity_input = row.locator("xpath=.//input[contains(@name,'quantity')]")
            row_total = row.locator("xpath=.//td[6]")
            if quantity_input.count() == 0 or row_total.count() == 0:
                continue
            total_quantity += int(quantity_input.first.input_value())
            total_amount += self._parse_currency(row_total.first.inner_text())

        return CartSummary(
            line_item_count=line_item_count,
            total_quantity=total_quantity,
            total_amount=total_amount,
        )

    @staticmethod
    def _parse_currency(value: str) -> float:
        digits = re.sub(r"[^0-9.]", "", value)
        return float(digits) if digits else 0.0

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(value.split())
