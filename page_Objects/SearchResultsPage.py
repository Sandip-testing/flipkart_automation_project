from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SearchResultsPage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 25)

    # Product card container (very stable)
    PRODUCT_CARDS = (By.XPATH, "//div[@data-id]")

    def getAllProductTitles(self):
        try:
            self.wait.until(
                EC.presence_of_all_elements_located(self.PRODUCT_CARDS)
            )

            products = self.driver.find_elements(*self.PRODUCT_CARDS)
            print(f"Products found by Selenium: {len(products)}")
            return products

        except Exception as e:
            print("Error:", e)
            return []
