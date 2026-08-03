"""
Critical flow #1: Login with valid credentials
Critical flow #3: Login with locked-out user shows the correct error
"""
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


def test_login_with_valid_standard_user(driver):
    login_page = LoginPage(driver).load()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(driver)
    assert "inventory.html" in driver.current_url
    assert inventory_page.is_loaded(), "Inventory page did not load after valid login"


def test_login_with_locked_out_user_shows_error(driver):
    login_page = LoginPage(driver).load()
    login_page.login("locked_out_user", "secret_sauce")

    assert login_page.is_error_displayed(), "Expected an error message for locked-out user"
    error_text = login_page.get_error_text()
    assert "locked out" in error_text.lower(), f"Unexpected error text: {error_text}"
    # Confirm the user was NOT navigated away from the login page
    assert "inventory.html" not in driver.current_url


@pytest.mark.parametrize(
    "username,password,expected_error_snippet",
    [
        ("", "secret_sauce", "username is required"),
        ("standard_user", "", "password is required"),
        ("invalid_user", "wrong_pass", "do not match"),
    ],
)
def test_login_negative_cases(driver, username, password, expected_error_snippet):
    login_page = LoginPage(driver).load()
    login_page.login(username, password)

    assert login_page.is_error_displayed()
    assert expected_error_snippet in login_page.get_error_text().lower()
