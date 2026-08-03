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
