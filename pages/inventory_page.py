from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class InventoryPage(BasePage):
    INVENTORY_LIST = (By.CLASS_NAME, "inventory_list")
    INVENTORY_ITEM = (By.CLASS_NAME, "inventory_item")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    RESET_APP_STATE_LINK = (By.ID, "reset_sidebar_link")
    MENU_CLOSE_BUTTON = (By.ID, "react-burger-cross-btn")

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

    def get_cart_button_text_for_product(self, product_name: str) -> str:
        """Returns the current label ('Add to cart' / 'Remove') of the button
        inside the grid tile for the given product, found by matching its
        visible title text rather than a hardcoded id (which changes between
        add/remove states)."""
        item = self.driver.find_element(
            By.XPATH,
            f"//div[contains(@class,'inventory_item_name') and text()='{product_name}']"
            "/ancestor::div[contains(@class,'inventory_item')]",
        )
        return item.find_element(By.TAG_NAME, "button").text

    def click_product_title(self, product_name: str):
        """Navigates to a product's detail page by clicking its title text."""
        elements = self.driver.find_elements(*self.ITEM_NAMES)
        for el in elements:
            if el.text == product_name:
                el.click()
                return
        raise ValueError(f"Product '{product_name}' not found on inventory page")

    def reset_app_state(self):
        self.click(self.MENU_BUTTON)
        self.click(self.RESET_APP_STATE_LINK)
        self.click(self.MENU_CLOSE_BUTTON)
