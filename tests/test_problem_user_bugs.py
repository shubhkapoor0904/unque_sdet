"""
Automated regression tests targeting identified defects in the problem_user and performance_glitch_user accounts.

These tests are configured to:
- Use @pytest.mark.xfail for known, persistent application bugs (they act as regression guards).
- Fail/Skip to document the issues clearly in test execution logs.
- Flip to passing (or unexpected pass) if development ever resolves the underlying application bugs.
"""
import time
import pytest
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutStepOnePage
from pages.product_detail_page import ProductDetailPage


def _login_as(driver, username):
    """Helper method to log in a specified user role."""
    login_page = LoginPage(driver).load()
    login_page.login(username, "secret_sauce")


@pytest.mark.xfail(reason="BUG-01: problem_user catalog images are duplicated/broken (dog with tennis ball image)")
def test_problem_user_product_images_are_distinct(driver):
    """Verifies that all catalog item images are distinct and match their corresponding product (fails due to BUG-01)."""
    _login_as(driver, "problem_user")
    images = driver.find_elements(By.CSS_SELECTOR, ".inventory_item_img img")
    srcs = [img.get_attribute("src") for img in images]
    
    # Assert that all image URLs are unique; duplicates indicate catalog image corruption
    assert len(set(srcs)) == len(srcs), f"Verification failed: Duplicate product images found: {srcs}"


@pytest.mark.xfail(reason="BUG-02: Typing into the Last Name field corrupts the First Name field for problem_user")
def test_problem_user_checkout_name_fields_are_independent(driver):
    """Checks whether text inputs for First Name and Last Name act independently (fails due to BUG-02)."""
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)
    inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.open_cart()
    CartPage(driver).start_checkout()

    step_one = CheckoutStepOnePage(driver)
    step_one.fill_info("Shubh", "Sharma", "302017")

    # The inputs should independently store what was entered
    assert step_one.get_first_name_value() == "Shubh", (
        f"Verification failed: First Name field was corrupted. Expected 'Shubh', got '{step_one.get_first_name_value()}'"
    )
    assert step_one.get_last_name_value() == "Sharma", (
        f"Verification failed: Last Name field was corrupted. Expected 'Sharma', got '{step_one.get_last_name_value()}'"
    )


@pytest.mark.xfail(reason="BUG-02 (Checkout block): Checkout step one cannot be completed by problem_user due to input state corruption")
def test_problem_user_checkout_is_blocked(driver):
    """Verifies that problem_user is unable to proceed past Checkout Step One because their last name input is corrupted,
    triggering a validation error or blocking navigation to the overview page."""
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)
    inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.open_cart()
    CartPage(driver).start_checkout()

    step_one = CheckoutStepOnePage(driver)
    step_one.fill_info("Shubh", "Sharma", "302017")
    step_one.click_continue()

    # The user should be blocked from reaching step two due to name corruption
    assert "checkout-step-two.html" not in driver.current_url, (
        "Verification failed: User was able to navigate to checkout step two despite corrupted checkout details."
    )


@pytest.mark.xfail(reason="BUG-04: sort dropdown does not successfully reorder the catalog items for problem_user")
def test_problem_user_sort_z_to_a_reorders_list(driver):
    """Verifies that selecting 'Name (Z to A)' actually re-sorts catalog items alphabetically (fails due to BUG-04)."""
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)
    before = inventory_page.get_product_names_in_order()

    inventory_page.sort_by("Name (Z to A)")
    after = inventory_page.get_product_names_in_order()

    # The on-screen list must match a reverse-sorted copy of the original names
    assert after == sorted(before, reverse=True), (
        f"Verification failed: Sort dropdown did not reorder catalog items. Expected: {sorted(before, reverse=True)}, got: {after}"
    )


def test_performance_glitch_user_login_delay_is_flagged(driver):
    """Measures the authentication delay for performance_glitch_user and skips/warns if it exceeds acceptable thresholds."""
    login_page = LoginPage(driver).load()
    start = time.time()
    login_page.login("performance_glitch_user", "secret_sauce")
    InventoryPage(driver).is_loaded()
    elapsed = time.time() - start

    print(f"\n[TIMING] performance_glitch_user login took {elapsed:.2f}s")
    
    # Soft assertion: we skip the test if it exhibits the abnormal 5+ second delay (BUG-05)
    if elapsed > 5:
        pytest.skip(f"BUG-05 observed: abnormal login delay of {elapsed:.2f}s (no loading indicator shown)")


# --- BUG-03: Cart button state desynced between catalog view and item detail view ---
# Confirmed manually across all 6 products, which split into two failure groups:
GROUP_A = ["Sauce Labs Backpack", "Sauce Labs Bike Light", "Sauce Labs Onesie"]
GROUP_B = ["Sauce Labs Bolt T-Shirt", "Sauce Labs Fleece Jacket", "Test.allTheThings() T-Shirt (Red)"]


@pytest.mark.xfail(reason="BUG-03 (Group A): item detail page shows stale 'Add to cart' after item was added from the catalog grid")
@pytest.mark.parametrize("product_name", GROUP_A)
def test_problem_user_group_a_detail_page_reflects_grid_add(driver, product_name):
    """Verifies detail page button reflects the cart state of Group A products added from grid (fails due to BUG-03)."""
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)

    inventory_page.add_item_to_cart_by_name(product_name)
    assert inventory_page.get_cart_button_text_for_product(product_name) == "Remove", (
        "Sanity check failed: Catalog grid button should flip to 'Remove' after adding item."
    )

    # Click the product name to go to the detail view and check state sync
    inventory_page.click_product_title(product_name)
    detail_page = ProductDetailPage(driver)
    assert detail_page.get_cart_button_text() == "Remove", (
        f"Verification failed: Detail page for '{product_name}' still shows 'Add to cart' despite product already being in the cart."
    )


@pytest.mark.xfail(reason="BUG-03 (Group B): grid Add is unresponsive; detail page Remove button fails to remove product from cart")
@pytest.mark.parametrize("product_name", GROUP_B)
def test_problem_user_group_b_add_and_remove_are_broken(driver, product_name):
    """Checks button interaction bugs (unresponsive add on grid, unresponsive remove on detail page) for Group B (fails due to BUG-03)."""
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)

    # 1. Try to add from catalog grid (should fail / button stays 'Add to cart')
    inventory_page.add_item_to_cart_by_name(product_name)
    grid_button_text = inventory_page.get_cart_button_text_for_product(product_name)
    assert grid_button_text == "Remove", (
        f"Verification failed: Expected catalog grid button for '{product_name}' to flip to 'Remove', but it reads '{grid_button_text}'."
    )

    # 2. Try to add via detail page (this works), then verify removing it from detail page fails
    inventory_page.click_product_title(product_name)
    detail_page = ProductDetailPage(driver)
    if detail_page.get_cart_button_text() == "Add to cart":
        detail_page.click_cart_button()
    
    # Attempt to remove from cart
    detail_page.click_cart_button()
    assert detail_page.get_cart_button_text() == "Add to cart", (
        f"Verification failed: '{product_name}' Remove button on detail page failed to remove the item (button stuck on 'Remove')."
    )


# --- BUG-07: Reset App State doesn't apply until the page is manually refreshed ---
@pytest.mark.xfail(reason="BUG-07: cart badge does not reset until manual page refresh after clicking 'Reset App State'")
def test_reset_app_state_applies_without_manual_refresh(driver):
    """Ensures that resetting the app state immediately updates and clears the UI cart badge without a refresh (fails due to BUG-07)."""
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)
    inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
    assert inventory_page.get_cart_count() == 1

    # Trigger Reset App State from the sidebar menu
    inventory_page.reset_app_state()

    # A proper real-time state sync should clear the badge count instantly without a page reload
    assert inventory_page.get_cart_count() == 0, (
        "Verification failed: Cart badge counter still shows pre-reset state without a manual page reload."
    )
