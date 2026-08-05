"""
Automated tests for the login functionality of the Swag Labs application.

This suite covers:
1. Positive authentication flow for standard users (verify successful navigation).
2. Blocked login flow for locked-out users (verify error message matches expectations).
3. Negative input checks (empty inputs, invalid credentials) to ensure validation rules work.
"""
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


def test_login_with_valid_standard_user(driver):
    """Verifies that a standard user with valid credentials successfully redirects to the product catalog."""
    login_page = LoginPage(driver).load()
    login_page.login("standard_user", "secret_sauce")

    inventory_page = InventoryPage(driver)
    # Check that the user is navigated to the correct catalog screen
    assert "inventory.html" in driver.current_url
    assert inventory_page.is_loaded(), "Verification failed: Inventory catalog page failed to load after login."


def test_login_with_locked_out_user_shows_error(driver):
    """Ensures that locked-out users are denied entry and see a corresponding error banner."""
    login_page = LoginPage(driver).load()
    login_page.login("locked_out_user", "secret_sauce")

    # The error banner must show up and mention 'locked out'
    assert login_page.is_error_displayed(), "Verification failed: Locked out user did not see an error banner."
    error_text = login_page.get_error_text()
    assert "locked out" in error_text.lower(), f"Verification failed: Incorrect error text displayed: {error_text}"
    
    # Crucial security check: Ensure the user stayed on the login screen
    assert "inventory.html" not in driver.current_url, "Verification failed: Locked out user bypassed login barrier."


@pytest.mark.parametrize(
    "username,password,expected_error_snippet",
    [
        ("", "secret_sauce", "username is required"),
        ("standard_user", "", "password is required"),
        ("invalid_user", "wrong_pass", "do not match"),
    ],
)
def test_login_negative_cases(driver, username, password, expected_error_snippet):
    """Validates boundary inputs and incorrect credentials, checking that the correct validation errors trigger."""
    login_page = LoginPage(driver).load()
    login_page.login(username, password)

    assert login_page.is_error_displayed(), f"Verification failed: Error banner not shown for input: user='{username}', pass='{password}'"
    assert expected_error_snippet in login_page.get_error_text().lower(), (
        f"Verification failed: Expected snippet '{expected_error_snippet}' in error text: {login_page.get_error_text()}"
    )

