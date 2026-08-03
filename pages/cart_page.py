from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CartPage(BasePage):
    CHECKOUT_BUTTON = (By.ID, "checkout")
    CART_ITEM = (By.CLASS_NAME, "cart_item")

    def is_loaded(self) -> bool:
        self.wait_for_url_contains("cart.html")
        return True

    def get_item_count(self) -> int:
        return len(self.driver.find_elements(*self.CART_ITEM))

    def start_checkout(self):
        self.click(self.CHECKOUT_BUTTON)
