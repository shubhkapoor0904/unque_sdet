from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CheckoutStepOnePage(BasePage):
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    ZIP_CODE = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def fill_info(self, first_name: str, last_name: str, zip_code: str):
        self.type_text(self.FIRST_NAME, first_name)
        self.type_text(self.LAST_NAME, last_name)
        self.type_text(self.ZIP_CODE, zip_code)

    def get_first_name_value(self) -> str:
        return self.find(self.FIRST_NAME).get_attribute("value")

    def get_last_name_value(self) -> str:
        return self.find(self.LAST_NAME).get_attribute("value")

    def click_continue(self):
        self.click(self.CONTINUE_BUTTON)

    def get_error_text(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)


class CheckoutStepTwoPage(BasePage):
    FINISH_BUTTON = (By.ID, "finish")
    SUMMARY_TOTAL = (By.CLASS_NAME, "summary_total_label")

    def get_total_text(self) -> str:
        return self.get_text(self.SUMMARY_TOTAL)

    def click_finish(self):
        self.click(self.FINISH_BUTTON)


class CheckoutCompletePage(BasePage):
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")

    def is_order_complete(self) -> bool:
        return self.is_visible(self.COMPLETE_HEADER, timeout=10)

    def get_complete_header_text(self) -> str:
        return self.get_text(self.COMPLETE_HEADER)
