from selenium.webdriver.common.by import By


class ProductPage:
    product_name = (By.XPATH, "//span[@class='B_NuCI']")
    product_price = (By.XPATH, "//div[@class='_30jeq3 _16Jk6d']")

    def __init__(self, driver):
        self.driver = driver

    def getProductName(self):
        return self.driver.find_element(*self.product_name).text

    def getProductPrice(self):
        return self.driver.find_element(*self.product_price).text
