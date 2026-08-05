"""
End-to-end checkout and shopping cart flow tests.

This suite verifies:
1. Complete e2e shopping flow for a standard user (login -> add item -> cart validation -> checkout info -> overview -> finish).
2. Field-level form validation checks (e.g. blocking checkout if Last Name is omitted).
3. Cart badge behavior when items are removed and the user returns to the catalog (ensuring no badge desync).
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
    """Validates that a standard user can successfully complete a full purchase flow from end to end."""
    # 1. Log in to the application
    login_page = LoginPage(driver).load()
    login_page.login("standard_user", "secret_sauce")

    # 2. Add product to cart and verify inventory page badge updates
    inventory_page = InventoryPage(driver)
    assert inventory_page.is_loaded()
    inventory_page.add_item_to_cart_by_name(PRODUCT_NAME)
    assert inventory_page.get_cart_count() == 1, "Verification failed: Cart badge did not increment to 1 after adding product."

    # 3. Open cart and ensure product is listed
    inventory_page.open_cart()
    cart_page = CartPage(driver)
    assert cart_page.is_loaded()
    assert cart_page.get_item_count() == 1, "Verification failed: Cart item list did not show the added product."

    # 4. Initiate checkout and submit user details
    cart_page.start_checkout()
    step_one = CheckoutStepOnePage(driver)
    step_one.fill_info("Shubh", "Sharma", "302017")
    step_one.click_continue()

    # 5. Verify the order total contains correct formatting before confirming
    step_two = CheckoutStepTwoPage(driver)
    total_text = step_two.get_total_text()
    assert "$" in total_text, f"Verification failed: Summary page total lacks currency sign. Got: {total_text}"
    step_two.click_finish()

    # 6. Confirm the order complete screen is displayed with thank you message
    complete_page = CheckoutCompletePage(driver)
    assert complete_page.is_order_complete(), "Verification failed: Checkout Complete page was not visible."
    assert "thank you" in complete_page.get_complete_header_text().lower(), (
        f"Verification failed: Expected success header text to contain 'Thank you', got: {complete_page.get_complete_header_text()}"
    )


def test_checkout_blocked_when_last_name_missing(driver):
    """Verifies that checkout step one requires the last name and retains entered data on validation failure."""
    login_page = LoginPage(driver).load()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(driver)
    inventory_page.add_item_to_cart_by_name(PRODUCT_NAME)
    inventory_page.open_cart()

    cart_page = CartPage(driver)
    cart_page.start_checkout()

    # Attempt to submit information with the last name left blank
    step_one = CheckoutStepOnePage(driver)
    step_one.fill_info("Shubh", "", "302017")
    step_one.click_continue()

    # Verify appropriate error text is shown
    assert "last name is required" in step_one.get_error_text().lower(), (
        f"Verification failed: Omission error not shown. Got: {step_one.get_error_text()}"
    )
    # Ensure form state retention: First Name should still hold the user's typed value
    assert step_one.get_first_name_value() == "Shubh", "Verification failed: Form cleared fields on validation error."


def test_standard_user_cart_badge_no_desync_on_cart_remove(driver):
    """Confirms that removing an item from the cart correctly decrements the badge,
    and returning to the product grid displays the updated count immediately (BUG-06 scenario)."""
    login_page = LoginPage(driver).load()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(driver)
    assert inventory_page.is_loaded()

    # Add two items to cart
    inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.add_item_to_cart_by_name("Sauce Labs Bike Light")
    assert inventory_page.get_cart_count() == 2, "Verification failed: Catalog cart badge did not show '2' items."

    # Go to cart
    inventory_page.open_cart()
    cart_page = CartPage(driver)
    assert cart_page.is_loaded()
    assert cart_page.get_item_count() == 2

    # Remove one item
    cart_page.remove_item_by_name("Sauce Labs Backpack")
    assert cart_page.get_item_count() == 1, "Verification failed: Item was not removed from cart view."

    # Go back to inventory and ensure badge is synced
    cart_page.continue_shopping()
    assert inventory_page.is_loaded()
    assert inventory_page.get_cart_count() == 1, "Verification failed: Cart badge desynced and did not show '1'."

