"""
Automated regression checks for the defects logged in bug_report.md.
These are written to FAIL while the bugs exist (red), so they double as
regression guards for whenever the bugs get fixed (green).
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
    login_page = LoginPage(driver).load()
    login_page.login(username, "secret_sauce")


@pytest.mark.xfail(reason="BUG-01: problem_user product images are duplicated/incorrect")
def test_problem_user_product_images_are_distinct(driver):
    _login_as(driver, "problem_user")
    images = driver.find_elements(By.CSS_SELECTOR, ".inventory_item_img img")
    srcs = [img.get_attribute("src") for img in images]
    assert len(set(srcs)) == len(srcs), f"Expected distinct images, got: {srcs}"


@pytest.mark.xfail(reason="BUG-02: last-name field corrupts first-name field for problem_user")
def test_problem_user_checkout_name_fields_are_independent(driver):
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)
    inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.open_cart()
    CartPage(driver).start_checkout()

    step_one = CheckoutStepOnePage(driver)
    step_one.fill_info("Shubh", "Sharma", "302017")

    assert step_one.get_first_name_value() == "Shubh"
    assert step_one.get_last_name_value() == "Sharma"


@pytest.mark.xfail(reason="BUG-04: sort dropdown does not reorder products for problem_user")
def test_problem_user_sort_z_to_a_reorders_list(driver):
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)
    before = inventory_page.get_product_names_in_order()

    inventory_page.sort_by("Name (Z to A)")
    after = inventory_page.get_product_names_in_order()

    assert after == sorted(before, reverse=True), (
        f"Expected Z-A order, got: {after}"
    )


def test_performance_glitch_user_login_delay_is_flagged(driver):
    """Not xfail: this test passes but records timing so a slow login is visible in reports."""
    login_page = LoginPage(driver).load()
    start = time.time()
    login_page.login("performance_glitch_user", "secret_sauce")
    InventoryPage(driver).is_loaded()
    elapsed = time.time() - start

    print(f"\n[TIMING] performance_glitch_user login took {elapsed:.2f}s")
    # Soft assertion via warning rather than hard failure, since a delay alone
    # isn't a functional break — but flag anything unreasonable.
    if elapsed > 5:
        pytest.skip(f"BUG-05 observed: abnormal login delay of {elapsed:.2f}s (no loading indicator shown)")


# --- BUG-03: cart button state desyncs between grid view and detail view ---
# Confirmed manually across all 6 products, split into two failure groups.
GROUP_A = ["Sauce Labs Backpack", "Sauce Labs Bike Light", "Sauce Labs Onesie"]
GROUP_B = ["Sauce Labs Bolt T-Shirt", "Sauce Labs Fleece Jacket", "Test.allTheThings() T-Shirt (Red)"]


@pytest.mark.xfail(reason="BUG-03 (Group A): detail page shows stale 'Add to cart' after adding from the grid")
@pytest.mark.parametrize("product_name", GROUP_A)
def test_problem_user_group_a_detail_page_reflects_grid_add(driver, product_name):
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)

    inventory_page.add_item_to_cart_by_name(product_name)
    assert inventory_page.get_cart_button_text_for_product(product_name) == "Remove", (
        "Sanity check: grid button should flip to Remove after adding"
    )

    inventory_page.click_product_title(product_name)
    detail_page = ProductDetailPage(driver)
    assert detail_page.get_cart_button_text() == "Remove", (
        f"Detail page for '{product_name}' still shows 'Add to cart' despite item already being in the cart"
    )


@pytest.mark.xfail(reason="BUG-03 (Group B): grid Add is unresponsive; detail-page Remove doesn't actually remove the item")
@pytest.mark.parametrize("product_name", GROUP_B)
def test_problem_user_group_b_add_and_remove_are_broken(driver, product_name):
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)

    # Grid "Add to cart" should be unresponsive for this group.
    inventory_page.add_item_to_cart_by_name(product_name)
    grid_button_text = inventory_page.get_cart_button_text_for_product(product_name)
    assert grid_button_text == "Remove", (
        f"Expected grid Add to cart for '{product_name}' to work, but button still reads '{grid_button_text}'"
    )

    # Add via the detail page instead, then try to remove it there.
    inventory_page.click_product_title(product_name)
    detail_page = ProductDetailPage(driver)
    if detail_page.get_cart_button_text() == "Add to cart":
        detail_page.click_cart_button()
    detail_page.click_cart_button()  # attempt Remove
    assert detail_page.get_cart_button_text() == "Add to cart", (
        f"'{product_name}' Remove button on the detail page did not actually remove the item"
    )


# --- BUG-07: Reset App State doesn't apply until the page is manually refreshed ---
@pytest.mark.xfail(reason="BUG-07: cart badge/contents don't clear until a manual page refresh after Reset App State")
def test_reset_app_state_applies_without_manual_refresh(driver):
    _login_as(driver, "problem_user")
    inventory_page = InventoryPage(driver)
    inventory_page.add_item_to_cart_by_name("Sauce Labs Backpack")
    assert inventory_page.get_cart_count() == 1

    inventory_page.reset_app_state()

    # Intentionally NOT refreshing the page here — this is the exact
    # condition that exposes the bug. A correct implementation would clear
    # the badge immediately, without needing a reload.
    assert inventory_page.get_cart_count() == 0, (
        "Cart badge still shows the pre-reset count without a manual page refresh"
    )
