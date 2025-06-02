from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

class HomePage:
    URL = "https://weathershopper.pythonanywhere.com"

    _moisturizers_btn = (By.XPATH, "//button[contains(., 'Buy moisturizers')]")
    _sunscreens_btn   = (By.XPATH, "//button[contains(., 'Buy sunscreens')]")
    _temp_locator     = (By.ID, "temperature")

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.URL)

    def get_temperature(self) -> float:
        text = self.driver.find_element(*self._temp_locator).text
        m = re.search(r"(-?\d+)", text)
        if not m:
            raise ValueError(f"Impossible de parser la température depuis '{text}'")
        return float(m.group(1))

    def click_moisturizers(self):
        self.driver.find_element(*self._moisturizers_btn).click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("moisturizer"))

    def click_sunscreens(self):
        self.driver.find_element(*self._sunscreens_btn).click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("sunscreen"))
