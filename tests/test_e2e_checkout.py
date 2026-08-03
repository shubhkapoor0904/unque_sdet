"""
Critical flow #2: Add item to cart and complete checkout end to end.
"""
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutStepOnePage,
    CheckoutStepTwoPage,
    CheckoutCompletePage,
)

PRODUCT_NAME = "Sauce Labs Backpack"


def test_add_to_cart_and_complete_checkout(driver):
    # 1. Login
    login_page = LoginPage(driver).load()
    login_page.login("standard_user", "secret_sauce")

    # 2. Add item to cart and verify badge
    inventory_page = InventoryPage(driver)
    assert inventory_page.is_loaded()
    inventory_page.add_item_to_cart_by_name(PRODUCT_NAME)
    assert inventory_page.get_cart_count() == 1, "Cart badge did not update to 1 after adding an item"

    # 3. Go to cart and verify item present
    inventory_page.open_cart()
    cart_page = CartPage(driver)
    assert cart_page.is_loaded()
    assert cart_page.get_item_count() == 1

    # 4. Begin checkout
    cart_page.start_checkout()
    step_one = CheckoutStepOnePage(driver)
    step_one.fill_info("Shubh", "Sharma", "302017")
    step_one.click_continue()

    # 5. Verify order summary total is present, then finish
    step_two = CheckoutStepTwoPage(driver)
    total_text = step_two.get_total_text()
    assert "$" in total_text, f"Expected a dollar total, got: {total_text}"
    step_two.click_finish()

    # 6. Verify order completion
    complete_page = CheckoutCompletePage(driver)
    assert complete_page.is_order_complete()
    assert "thank you" in complete_page.get_complete_header_text().lower()


def test_checkout_blocked_when_last_name_missing(driver):
    login_page = LoginPage(driver).load()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(driver)
    inventory_page.add_item_to_cart_by_name(PRODUCT_NAME)
    inventory_page.open_cart()

    cart_page = CartPage(driver)
    cart_page.start_checkout()

    step_one = CheckoutStepOnePage(driver)
    step_one.fill_info("Shubh", "", "302017")  # last name intentionally blank
    step_one.click_continue()

    assert "last name is required" in step_one.get_error_text().lower()
    # First name value should still be retained on screen after the failed submit
    assert step_one.get_first_name_value() == "Shubh"
