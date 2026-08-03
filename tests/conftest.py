import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def driver():
    """Yields a fresh Chrome WebDriver instance for each test, quitting it afterward."""
    options = webdriver.ChromeOptions()
    # Run headless in CI; comment out the next 3 lines to watch tests run visually.
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(0)  # we rely on explicit waits in page objects
    yield drv
    drv.quit()
