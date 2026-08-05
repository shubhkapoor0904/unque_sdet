from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CartPage(BasePage):
    CHECKOUT_BUTTON = (By.ID, "checkout")
    CONTINUE_SHOPPING_BUTTON = (By.ID, "continue-shopping")
    CART_ITEM = (By.CLASS_NAME, "cart_item")

    def is_loaded(self) -> bool:
        self.wait_for_url_contains("cart.html")
        return True

    def get_item_count(self) -> int:
        return len(self.driver.find_elements(*self.CART_ITEM))

    def start_checkout(self):
        self.click(self.CHECKOUT_BUTTON)

    def remove_item_by_name(self, product_name: str):
        """Clicks the 'Remove' button for the given product name in the cart."""
        button_id = "remove-" + product_name.lower().replace(" ", "-")
        locator = (By.ID, button_id)
        self.click(locator)

    def continue_shopping(self):
        """Navigates back to the inventory page from the cart."""
        self.click(self.CONTINUE_SHOPPING_BUTTON)

