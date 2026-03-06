from __future__ import annotations

import re
from dataclasses import dataclass

from playwright.sync_api import Page, expect

from .base_page import BasePage


@dataclass(frozen=True)
class CartItemDetails:
    name: str
    unit_price: float
    quantity: int
    total_price: float


class AutomationStoreXpathPage(BasePage):
    """Automation Test Store flow implemented with XPath selectors."""

    LOGIN_PATH = "index.php?rt=account/login"
    CART_PATH = "index.php?rt=checkout/cart"

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
        self.goto(base_url)
        self.wait_for_visible(self.DOVE_BRAND_LINK_XPATH)

    def clear_cart_if_needed(self, base_url: str) -> None:
        self.goto_path(base_url, self.CART_PATH)
        self.page.wait_for_load_state("domcontentloaded")
        remove_buttons = self.locator(self.CART_REMOVE_BUTTONS_XPATH)
        while remove_buttons.count() > 0:
            remove_buttons.first.click()
            self.page.wait_for_load_state("domcontentloaded")
            remove_buttons = self.locator(self.CART_REMOVE_BUTTONS_XPATH)

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

    @staticmethod
    def _parse_currency(value: str) -> float:
        digits = re.sub(r"[^0-9.]", "", value)
        return float(digits) if digits else 0.0

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(value.split())
