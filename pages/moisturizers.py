from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class MoisturizersPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def add_two_cheapest(self, targets):
        """Ajoute les deux produits les moins chers contenant les mots-clés spécifiés"""
        print(f"Recherche des produits contenant : {targets}")
        
        try:
            # Attendre que les produits se chargent
            products = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".col-4"))
            )
            print(f"Nombre de produits trouvés : {len(products)}")
        except TimeoutException:
            print("Timeout : impossible de charger les produits")
            return []
        
        matching_products = []
        
        for product in products:
            try:
                # Récupérer le nom du produit
                name_elem = product.find_element(By.TAG_NAME, "p")
                name = name_elem.text.strip()
                
                # Récupérer le prix
                price_elem = product.find_element(By.XPATH, ".//p[contains(text(), 'Price:')]")
                price_text = price_elem.text
                # Extraire le prix numérique (ex: "Price: Rs. 128" -> 128)
                price = int(price_text.split('Rs. ')[1])
                
                # Vérifier si le produit correspond aux critères
                for target in targets:
                    if target.lower() in name.lower():
                        matching_products.append({
                            'element': product,
                            'name': name,
                            'price': price,
                            'target': target
                        })
                        print(f"Produit trouvé : {name} - {price} Rs (correspond à {target})")
                        break
                        
            except (NoSuchElementException, ValueError, IndexError) as e:
                print(f"Erreur lors du traitement d'un produit : {e}")
                continue
        
        if len(matching_products) < 2:
            print(f"Pas assez de produits trouvés. Trouvés : {len(matching_products)}")
            # Si on n'a pas assez de produits correspondants, prendre les moins chers disponibles
            if len(matching_products) == 0:
                return []
        
        # Trier par prix (du moins cher au plus cher)
        matching_products.sort(key=lambda x: x['price'])
        
        # Prendre les 2 moins chers
        selected = matching_products[:2]
        
        prices = []
        for i, product in enumerate(selected):
            try:
                print(f"Tentative d'ajout {i+1}/2 : {product['name']} - {product['price']} Rs")
                
                # Trouver le bouton "Add"
                add_button = product['element'].find_element(By.XPATH, ".//button[contains(text(), 'Add')]")
                
                # Scroll vers l'élément pour s'assurer qu'il est visible
                self.driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                time.sleep(0.5)
                
                # Vérifier que le bouton est cliquable
                self.wait.until(EC.element_to_be_clickable(add_button))
                
                # Cliquer sur le bouton
                add_button.click()
                print(f"✅ Produit ajouté : {product['name']}")
                
                prices.append(product['price'])
                
                # Attendre un peu entre les ajouts pour éviter les problèmes de timing
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Erreur lors de l'ajout de {product['name']} : {e}")
                # Essayer une méthode alternative de clic
                try:
                    self.driver.execute_script("arguments[0].click();", add_button)
                    print(f"✅ Produit ajouté via JavaScript : {product['name']}")
                    prices.append(product['price'])
                except Exception as e2:
                    print(f"❌ Échec même avec JavaScript : {e2}")
        
        print(f"Prix des produits ajoutés : {prices}")
        return prices
    
    def get_available_products(self):
        """Méthode de debug pour voir tous les produits disponibles"""
        try:
            products = self.driver.find_elements(By.CSS_SELECTOR, ".col-4")
            product_info = []
            for product in products:
                try:
                    name = product.find_element(By.TAG_NAME, "p").text
                    price_elem = product.find_element(By.XPATH, ".//p[contains(text(), 'Price:')]")
                    price = price_elem.text
                    product_info.append(f"{name}: {price}")
                except:
                    product_info.append("Produit non lisible")
            return product_info
        except Exception as e:
            return [f"Erreur: {str(e)}"]
    
    def get_cart_count(self):
        """Récupère le nombre d'articles dans le panier"""
        try:
            # Le compteur du panier est généralement dans un span ou badge
            cart_count = self.driver.find_element(By.CSS_SELECTOR, "#cart .badge, .cart-count, .badge")
            return int(cart_count.text) if cart_count.text.isdigit() else 0
        except:
            # Si pas de badge visible, essayer de compter les éléments du panier directement
            try:
                cart_items = self.driver.find_elements(By.CSS_SELECTOR, ".cart-item, .item")
                return len(cart_items)
            except:
                return 0