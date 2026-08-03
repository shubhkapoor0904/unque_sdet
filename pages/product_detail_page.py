from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class ProductDetailPage(BasePage):
    """The single-product page reached by clicking a product's title/image
    from the inventory grid (URL pattern: /inventory-item.html?id=N)."""

    CART_BUTTON = (By.CSS_SELECTOR, ".btn_inventory")

    def get_cart_button_text(self) -> str:
        return self.get_text(self.CART_BUTTON)

    def click_cart_button(self):
        self.click(self.CART_BUTTON)
