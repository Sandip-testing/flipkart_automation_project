import configparser
import os

config = configparser.ConfigParser()

config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "test_data",
    "config.ini"
)

if not os.path.exists(config_path):
    raise FileNotFoundError(f"config.ini not found at: {config_path}")

config.read(config_path)


class ReadConfig:

    @staticmethod
    def getApplicationURL():
        return config["DEFAULT"]["baseURL"]

    @staticmethod
    def getProductName():
        return config["DEFAULT"]["productName"]
