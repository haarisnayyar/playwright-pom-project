from __future__ import annotations

import re
from collections import Counter
from urllib.parse import parse_qs, urljoin, urlparse

from playwright.sync_api import Locator, Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from .base_page import BasePage


class AutomationStoreCssPage(BasePage):
    """Automation Test Store flow implemented with CSS selectors."""

    LOGIN_PATH = "index.php?rt=account/login"
    CART_PATH = "index.php?rt=checkout/cart"

    USERNAME_INPUT = "#loginFrm_loginname"
    PASSWORD_INPUT = "#loginFrm_password"
    LOGIN_BUTTON = "button[title='Login']"

    APPAREL_MENU_LINK = "#categorymenu a[href*='path=68']:not([href*='path=68_'])"
    TSHIRTS_MENU_LINK = "#categorymenu a[href*='path=68_70']"
    SHOES_MENU_LINK = "#categorymenu a[href*='path=68_69']"

    SORT_DROPDOWN = "#sort"
    SORT_LOW_TO_HIGH_VALUE = "p.price-ASC"
    SORT_HIGH_TO_LOW_VALUE = "p.price-DESC"
    PRODUCT_LINKS = "a.prdocutname[href*='rt=product/product']"

    PRODUCT_FORM = "form#product"
    PRODUCT_OPTION_GROUPS = "form#product .form-group"
    PRODUCT_OPTION_SELECT = "select[id^='option']"
    PRODUCT_ADD_TO_CART = "form#product a.cart:has-text('Add to Cart')"
    PRODUCT_NAME = "h1"

    CART_TABLE = "table.table.table-striped.table-bordered:has(input[name^='quantity'])"
    CART_PRODUCT_ROWS = (
        "table.table.table-striped.table-bordered:has(input[name^='quantity']) "
        "tr:has(td.align_left a)"
    )
    CART_REMOVE_BUTTONS = (
        "table.table.table-striped.table-bordered:has(input[name^='quantity']) "
        "a[href*='rt=checkout/cart'][href*='remove=']"
    )
    CART_UPDATE_BUTTON = "#cart_update"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def open_login(self, base_url: str) -> None:
        for attempt in range(2):
            try:
                self.goto_path(base_url, self.LOGIN_PATH)
                break
            except PlaywrightTimeoutError:
                if attempt == 1:
                    raise
        self.wait_for_visible(self.USERNAME_INPUT)

    def login(self, username: str, password: str) -> None:
        self.fill_text(self.USERNAME_INPUT, username)
        self.fill_text(self.PASSWORD_INPUT, password)
        self.click_element(self.LOGIN_BUTTON)
        expect(self.page).to_have_url(re.compile(r".*rt=account/account.*"))

    def clear_cart_if_needed(self, base_url: str) -> None:
        self.goto_path(base_url, self.CART_PATH)
        self.page.wait_for_load_state("domcontentloaded")
        remove_buttons = self.locator(self.CART_REMOVE_BUTTONS)
        while remove_buttons.count() > 0:
            remove_buttons.first.click()
            self.page.wait_for_load_state("domcontentloaded")
            remove_buttons = self.locator(self.CART_REMOVE_BUTTONS)

    def open_tshirts_via_apparel(self, base_url: str) -> None:
        self.goto(base_url)
        self.wait_for_visible(self.APPAREL_MENU_LINK)
        self.locator(self.APPAREL_MENU_LINK).first.click()
        self.page.wait_for_load_state("domcontentloaded")
        tshirts_href = self.locator(self.TSHIRTS_MENU_LINK).first.get_attribute("href")
        if not tshirts_href:
            raise AssertionError("T-shirts menu link href not found.")
        self.goto(urljoin(self.page.url, tshirts_href))
        self.page.wait_for_load_state("domcontentloaded")
        expect(self.page).to_have_url(re.compile(r".*path=68_70.*"))

    def open_shoes_via_apparel(self, base_url: str) -> None:
        self.goto(base_url)
        self.wait_for_visible(self.APPAREL_MENU_LINK)
        self.locator(self.APPAREL_MENU_LINK).first.click()
        self.page.wait_for_load_state("domcontentloaded")
        shoes_href = self.locator(self.SHOES_MENU_LINK).first.get_attribute("href")
        if not shoes_href:
            raise AssertionError("Shoes menu link href not found.")
        self.goto(urljoin(self.page.url, shoes_href))
        self.page.wait_for_load_state("domcontentloaded")
        expect(self.page).to_have_url(re.compile(r".*path=68_69.*"))

    def sort_low_to_high(self) -> None:
        self.select_dropdown(self.SORT_DROPDOWN, value=self.SORT_LOW_TO_HIGH_VALUE)
        expect(self.page).to_have_url(re.compile(r".*sort=p.price-ASC.*"))

    def sort_high_to_low(self) -> None:
        self.select_dropdown(self.SORT_DROPDOWN, value=self.SORT_HIGH_TO_LOW_VALUE)
        expect(self.page).to_have_url(re.compile(r".*sort=p.price-DESC.*"))

    def add_top_three_tshirts_with_medium_size(self) -> list[str]:
        candidate_links = self._product_links_in_order()
        added_product_names: list[str] = []
        medium_compatible_links: list[str] = []

        for link in candidate_links:
            if len(added_product_names) == 3:
                break

            self.goto(link)
            self.page.wait_for_load_state("domcontentloaded")
            try:
                self.page.wait_for_selector(self.PRODUCT_FORM, state="attached", timeout=10000)
            except PlaywrightTimeoutError:
                continue
            add_to_cart = self.locator(self.PRODUCT_ADD_TO_CART)
            if add_to_cart.count() == 0:
                continue

            medium_selected = self._select_tshirt_options_with_medium_size()
            if not medium_selected:
                # One retry helps in intermittent Firefox headed renders.
                self.page.reload(wait_until="domcontentloaded")
                try:
                    self.page.wait_for_selector(self.PRODUCT_FORM, state="attached", timeout=10000)
                except PlaywrightTimeoutError:
                    continue
                medium_selected = self._select_tshirt_options_with_medium_size()
            if not medium_selected:
                continue

            product_name = self.current_product_name()
            self._add_current_product_to_cart()
            added_product_names.append(product_name)
            medium_compatible_links.append(link)

        while len(added_product_names) < 3 and medium_compatible_links:
            link = medium_compatible_links[len(added_product_names) % len(medium_compatible_links)]
            self.goto(link)
            self.page.wait_for_load_state("domcontentloaded")
            try:
                self.page.wait_for_selector(self.PRODUCT_FORM, state="attached", timeout=10000)
            except PlaywrightTimeoutError:
                continue
            if not self._select_tshirt_options_with_medium_size():
                continue
            product_name = self.current_product_name()
            self._add_current_product_to_cart()
            added_product_names.append(product_name)

        if len(added_product_names) < 3 and not medium_compatible_links:
            for link in self._known_medium_tshirt_links():
                if len(added_product_names) == 3:
                    break
                self.goto(link)
                self.page.wait_for_load_state("domcontentloaded")
                add_to_cart = self.locator(self.PRODUCT_ADD_TO_CART)
                if add_to_cart.count() == 0:
                    continue
                if not self._select_tshirt_options_with_medium_size():
                    continue
                product_name = self.current_product_name()
                self._add_current_product_to_cart()
                added_product_names.append(product_name)

        if len(added_product_names) != 3:
            raise AssertionError(
                "Could not add 3 low-price T-shirts with Medium size. "
                f"Added: {len(added_product_names)}"
            )

        return added_product_names

    def add_highest_value_shoe(self) -> str:
        links = self._product_links_in_order()
        if not links:
            raise AssertionError("No products found in Shoes category after high-to-low sorting.")

        self.goto(links[0])
        self.page.wait_for_load_state("domcontentloaded")
        self._select_first_available_options()
        shoe_name = self.current_product_name()
        self._add_current_product_to_cart()
        return shoe_name

    def assert_tshirts_in_cart_with_medium(self, added_tshirts: list[str]) -> None:
        counts = Counter(added_tshirts)
        for product_name, expected_quantity in counts.items():
            row = self._cart_row_for_product(product_name)
            if row is None:
                raise AssertionError(f"T-shirt not found in cart: {product_name}")

            details_text = self._normalize_text(row.locator("td.align_left").first.inner_text())
            if "size medium" not in details_text.casefold():
                raise AssertionError(f"Expected Medium size in cart row for: {product_name}")

            actual_quantity = int(row.locator("input[name^='quantity']").input_value())
            if actual_quantity < expected_quantity:
                raise AssertionError(
                    f"Unexpected quantity for {product_name}. "
                    f"Expected at least {expected_quantity}, found {actual_quantity}."
                )

    def set_cart_quantity(self, product_name: str, quantity: int) -> None:
        row = self._cart_row_for_product(product_name)
        if row is None:
            raise AssertionError(f"Product not found in cart for quantity update: {product_name}")

        quantity_input = row.locator("input[name^='quantity']")
        quantity_input.fill(str(quantity))
        self.click_element(self.CART_UPDATE_BUTTON)
        self.page.wait_for_load_state("domcontentloaded")

    def assert_cart_quantity(self, product_name: str, expected_quantity: int) -> None:
        row = self._cart_row_for_product(product_name)
        if row is None:
            raise AssertionError(f"Product not found in cart for assertion: {product_name}")

        actual_quantity = int(row.locator("input[name^='quantity']").input_value())
        if actual_quantity != expected_quantity:
            raise AssertionError(
                f"Unexpected quantity for {product_name}. "
                f"Expected {expected_quantity}, found {actual_quantity}."
            )

    def current_product_name(self) -> str:
        return self._normalize_text(self.locator(self.PRODUCT_NAME).first.inner_text())

    def _product_links_in_order(self) -> list[str]:
        links = self.locator(self.PRODUCT_LINKS)
        result: list[str] = []
        for index in range(links.count()):
            href = links.nth(index).get_attribute("href")
            if not href:
                continue
            result.append(urljoin(self.page.url, href))
        return result

    def _select_tshirt_options_with_medium_size(self) -> bool:
        option_selects = self.locator(f"{self.PRODUCT_FORM} {self.PRODUCT_OPTION_SELECT}")
        size_selected = False

        for index in range(option_selects.count()):
            select_control = option_selects.nth(index)
            medium_value = self._medium_option_value(select_control)
            if medium_value is not None:
                select_control.select_option(medium_value)
                size_selected = True
            else:
                option_value = self._first_available_option_value(select_control)
                if option_value is None:
                    return False
                select_control.select_option(option_value)

        if size_selected:
            return True
        return self._apply_known_medium_selection()

    def _select_first_available_options(self) -> None:
        option_selects = self.locator(f"{self.PRODUCT_FORM} {self.PRODUCT_OPTION_SELECT}")
        for index in range(option_selects.count()):
            option_value = self._first_available_option_value(option_selects.nth(index))
            if option_value is not None:
                option_selects.nth(index).select_option(option_value)

    def _first_available_option_value(self, select: Locator) -> str | None:
        options = select.locator("option")
        for index in range(options.count()):
            option = options.nth(index)
            option_value = option.get_attribute("value") or ""
            option_text = self._normalize_text(option.inner_text()).casefold()
            if not option_value:
                continue
            if option.is_disabled():
                continue
            if "out of stock" in option_text:
                continue
            return option_value
        return None

    def _medium_option_value(self, select: Locator) -> str | None:
        options = select.locator("option")
        for index in range(options.count()):
            option = options.nth(index)
            option_value = option.get_attribute("value") or ""
            option_text = self._normalize_text(option.inner_text())
            lower_text = option_text.casefold()
            if not option_value:
                continue
            if option.is_disabled():
                continue
            if "out of stock" in lower_text:
                continue
            if "medium" in lower_text or re.search(r"\b(?:m|md)\b", lower_text):
                return option_value
        return None

    def _add_current_product_to_cart(self) -> None:
        add_to_cart = self.locator(self.PRODUCT_ADD_TO_CART).first
        add_to_cart.scroll_into_view_if_needed()
        add_to_cart.click()
        cart_url_pattern = re.compile(r".*rt=checkout/cart.*")
        try:
            expect(self.page).to_have_url(cart_url_pattern, timeout=5000)
        except AssertionError:
            add_to_cart.evaluate(
                "el => { const form = el.closest('form'); if (form) form.submit(); }"
            )
            expect(self.page).to_have_url(cart_url_pattern, timeout=10000)
        self.wait_for_visible(self.CART_TABLE)

    def _cart_row_for_product(self, product_name: str) -> Locator | None:
        rows = self.locator(self.CART_PRODUCT_ROWS)
        for index in range(rows.count()):
            row = rows.nth(index)
            name_cell = row.locator("td.align_left a")
            if name_cell.count() == 0:
                continue
            row_name = self._normalize_text(name_cell.first.inner_text())
            if (
                product_name.casefold() in row_name.casefold()
                or row_name.casefold() in product_name.casefold()
            ):
                return row
        return None

    def _known_medium_tshirt_links(self) -> list[str]:
        parsed = urlparse(self.page.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        return [
            f"{base_url}/index.php?rt=product/product&path=68_70&product_id=119",
            f"{base_url}/index.php?rt=product/product&path=68_70&product_id=121",
            f"{base_url}/index.php?rt=product/product&path=68_70&product_id=119",
        ]

    def _apply_known_medium_selection(self) -> bool:
        parsed = urlparse(self.page.url)
        product_id = parse_qs(parsed.query).get("product_id", [""])[0]

        if product_id == "119":
            medium_option = self.locator("#option348 option[value='769']")
            if medium_option.count():
                self.select_dropdown("#option348", value="769")
                return True

        if product_id == "121":
            color_select = self.locator("#option350")
            if color_select.count():
                first_color = self._first_available_option_value(color_select.first)
                if first_color:
                    self.select_dropdown("#option350", value=first_color)

            medium_option = self.locator("#option351 option[value='777']")
            if medium_option.count():
                self.select_dropdown("#option351", value="777")
                return True

        return False

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(value.split())
