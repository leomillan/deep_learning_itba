import json
import os


class ConfigurationManager:

    @staticmethod
    def init_config():
        print(os.getcwd())
        with open("services/configuration/configurations.json", "rb") as conf:
            return json.load(conf)
