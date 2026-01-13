from page_Objects.HomePage import HomePage
from page_Objects.SearchResultsPage import SearchResultsPage
from utilities.readConfig import ReadConfig
from utilities.screenshot import take_screenshot


class Test_SearchProduct:

    def test_search_product(self, setup):
        self.driver = setup
        self.driver.get(ReadConfig.getApplicationURL())

        hp = HomePage(self.driver)
        hp.closePopup()

        product_name = ReadConfig.getProductName()
        hp.searchProduct(product_name)

        srp = SearchResultsPage(self.driver)
        products = srp.getAllProductTitles()

        # 📸 Screenshot on EVERY run
        take_screenshot(self.driver, f"search_{product_name}")

        assert len(products) > 0, "No products found"
