"""Page object models for the application under test."""

from .account_page import AccountPage
from .automation_store_css_page import AutomationStoreCssPage
from .automation_store_xpath_page import (
    AutomationStoreXpathPage,
    CartItemDetails,
    CartSummary,
    SkinCareSaleSummary,
)
from .base_page import BasePage
from .home_page import HomePage
from .login_page import LoginPage
from .saucedemo_inventory_page import SauceDemoInventoryPage
from .saucedemo_login_page import SauceDemoLoginPage

__all__ = [
    "AccountPage",
    "AutomationStoreCssPage",
    "AutomationStoreXpathPage",
    "CartSummary",
    "CartItemDetails",
    "BasePage",
    "HomePage",
    "LoginPage",
    "SkinCareSaleSummary",
    "SauceDemoInventoryPage",
    "SauceDemoLoginPage",
]
