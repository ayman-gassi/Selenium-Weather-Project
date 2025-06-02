import pytest
from pages.home import HomePage
from pages.moisturizers import MoisturizersPage
from pages.sunscreens import SunscreensPage
from pages.cart import CartPage
from pages.payment_page import PaymentPage

def test_weather_shopper_happy_path(driver):
    home = HomePage(driver)
    home.open()
    temp = home.get_temperature()
    print(f"🌡️ Température détectée : {temp}°C")

    if temp < 19:
        home.click_moisturizers()
        products_page = MoisturizersPage(driver)
        targets = ["Aloe", "Almond"]
    elif temp > 34:
        home.click_sunscreens()
        products_page = SunscreensPage(driver)
        targets = ["SPF-30", "SPF-50"]
    else:
        pytest.skip("Température hors seuil pour le test")

    prices = products_page.add_two_cheapest(targets)
    assert len(prices) == 2

    cart = CartPage(driver)
    cart.open()
    assert cart.count_items() == 2
    assert cart.total_amount() == sum(prices)

    print(f"✅ Panier validé : 2 articles pour un total de {sum(prices)} Rs")

    # Paiement
    cart._open_stripe_modal()

    payment = PaymentPage(driver)
    payment.pay(
        email="test@example.com",
        card="4242424242424242",
        exp="1234",
        cvc="123",
        zip_code="12345"
    )

    assert payment.payment_successful(), "❌ Paiement non confirmé"
    print("✅ Test terminé avec succès ! Paiement effectué.")
