import pytest
import sys
import os
from selenium import webdriver

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture()
def setup():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()
