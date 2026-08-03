from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class InventoryPage(BasePage):
    INVENTORY_LIST = (By.CLASS_NAME, "inventory_list")
    INVENTORY_ITEM = (By.CLASS_NAME, "inventory_item")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")

    def is_loaded(self) -> bool:
        return self.is_visible(self.INVENTORY_LIST, timeout=10)

    def add_item_to_cart_by_name(self, product_name: str):
        """Adds the item matching product_name via its 'Add to cart' button."""
        button_id = "add-to-cart-" + product_name.lower().replace(" ", "-")
        locator = (By.ID, button_id)
        self.click(locator)

    def get_cart_count(self) -> int:
        if not self.is_visible(self.CART_BADGE, timeout=3):
            return 0
        return int(self.get_text(self.CART_BADGE))

    def open_cart(self):
        self.click(self.CART_LINK)

    def get_product_names_in_order(self):
        elements = self.driver.find_elements(*self.ITEM_NAMES)
        return [el.text for el in elements]

    def sort_by(self, visible_text: str):
        from selenium.webdriver.support.ui import Select

        select = Select(self.find(self.SORT_DROPDOWN))
        select.select_by_visible_text(visible_text)
