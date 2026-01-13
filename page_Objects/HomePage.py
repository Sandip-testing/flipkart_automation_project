from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HomePage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    CLOSE_POPUP = (By.XPATH, "//button[contains(text(),'✕')]")
    SEARCH_BOX = (By.NAME, "q")
    SEARCH_BUTTON = (By.XPATH, "//button[@type='submit']")

    def closePopup(self):
        try:
            self.wait.until(EC.element_to_be_clickable(self.CLOSE_POPUP)).click()
        except:
            pass

    def searchProduct(self, product_name):
        search = self.wait.until(EC.presence_of_element_located(self.SEARCH_BOX))
        search.clear()
        search.send_keys(product_name)
        self.driver.find_element(*self.SEARCH_BUTTON).click()
