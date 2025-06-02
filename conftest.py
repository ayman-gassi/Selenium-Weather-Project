import pytest
from selenium import webdriver

@pytest.fixture(scope="session")
def driver():
    driver = webdriver.Edge()
    driver.maximize_window()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()
