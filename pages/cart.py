from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

class CartPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def open(self):
        """Ouvre la page du panier."""
        cart_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Cart')]"))
        )
        cart_button.click()
        self.wait.until(EC.url_contains("/cart"))

    def count_items(self):
        """Compte le nombre d'articles dans le panier."""
        time.sleep(2)
        selectors = [
            "tbody tr", ".cart-item", ".item", "tr[data-item]", "div[data-product]", ".product-row"
        ]
        for selector in selectors:
            items = self.driver.find_elements(By.CSS_SELECTOR, selector)
            valid_items = [item for item in items if item.text.strip() and 'Total' not in item.text]
            if valid_items:
                return len(valid_items)
        return 0

    def total_amount(self):
        """Récupère le montant total du panier."""
        xpath_selectors = [
            "//td[contains(text(), 'Total:')]",
            "//span[contains(text(), 'Total:')]",
            "//div[contains(text(), 'Total:')]",
            "//p[contains(text(), 'Total:')]",
        ]
        for xp in xpath_selectors:
            try:
                elem = self.driver.find_element(By.XPATH, xp)
                txt = elem.text
                if 'Rupees' in txt:
                    return int(txt.split('Rupees ')[1].replace(',', ''))
                if 'Rs.' in txt:
                    return int(txt.split('Rs. ')[1].replace(',', ''))
            except:
                continue
        body = self.driver.find_element(By.TAG_NAME, 'body').text
        match = re.search(r'Total:\s*(?:Rupees\s*)?(\d+)', body)
        if match:
            return int(match.group(1))
        return 0

    def _open_stripe_modal(self):
        """Ouvre la modal de paiement Stripe."""
        stripe_button_xpaths = [
            "//button[@class='stripe-button-el']",
            "//button[@type='submit']"
        ]
        for xpath in stripe_button_xpaths:
            try:
                btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView();", btn)
                time.sleep(0.5)
                btn.click()
                print("✅ Stripe modal ouverte.")
                return
            except:
                continue
        raise RuntimeError("❌ Aucun bouton Stripe trouvé pour ouvrir la modale.")
