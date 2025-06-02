import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class PaymentPage:
    STRIPE_IFRAME = (By.XPATH, "//iframe[contains(@name,'stripe_checkout_app')]")

    EMAIL_INPUT = (By.ID, "email")
    CARD_INPUT  = (By.ID, "card_number")
    EXP_INPUT   = (By.ID, "cc-exp")
    CVC_INPUT   = (By.ID, "cc-csc")
    ZIP_INPUT   = (By.ID, "billing-zip")
    SUBMIT_BTN  = (By.ID, "submitButton")

    SUCCESS_HDR = (By.XPATH, "//h2[contains(translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'PAYMENT SUCCESS')]")

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _switch_to_iframe(self):
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(self.STRIPE_IFRAME))

    def _switch_to_default(self):
        self.driver.switch_to.default_content()

    def _type(self, locator, value):
        field = self.wait.until(EC.visibility_of_element_located(locator))
        field.clear()
        field.send_keys(value)

    def _slow_type(self, locator, value, delay=0.15):
        """Saisie lente caractère par caractère."""
        field = self.wait.until(EC.visibility_of_element_located(locator))
        field.clear()
        for char in value:
            field.send_keys(char)
            time.sleep(delay)

    def _click(self, locator):
        try:
            self.wait.until(EC.element_to_be_clickable(locator)).click()
        except Exception:
            print("⚠️ Clic normal échoué, tentative JavaScript click()")
            self._js_click(locator)

    def _js_click(self, locator):
        el = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].click();", el)

    def pay(self, email, card, exp, cvc, zip_code):
        """Remplit tous les champs Stripe et clique sur Payer."""
        self._switch_to_iframe()

        self._type(self.EMAIL_INPUT, email)
        time.sleep(0.5)

        self._slow_type(self.CARD_INPUT, card)
        time.sleep(0.5)

        self._slow_type(self.EXP_INPUT, exp)  # exp = "1234" pour 12/34
        time.sleep(0.5)

        self._type(self.CVC_INPUT, cvc)
        time.sleep(0.5)

        self._type(self.ZIP_INPUT, zip_code)
        time.sleep(0.5)

        self._click(self.SUBMIT_BTN)

        self._switch_to_default()
        time.sleep(2)
        self.driver.save_screenshot("stripe_submit.png")
        print("📸 Screenshot pris après la tentative de paiement.")

    def payment_successful(self, timeout=20):
        """Vérifie si un message de succès s'affiche après paiement."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.SUCCESS_HDR)
            )
            print("✅ Message de confirmation trouvé.")
            return True
        except TimeoutException:
            print("❌ Aucun message de confirmation détecté.")
            try:
                print("📍 URL actuelle :", self.driver.current_url)
                print("📍 Titre :", self.driver.title)
                body = self.driver.find_element(By.TAG_NAME, "body").text
                print("📍 Contenu visible :\n", body[:1000])  # Limite à 1000 caractères
            except:
                print("❌ Impossible de récupérer le contenu de la page.")
            return False
