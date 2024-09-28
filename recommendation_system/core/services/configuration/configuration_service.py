import json
import logging
import os

logger = logging.getLogger(__name__)


class ConfigurationManager:

    @staticmethod
    def init_config():
        config_path = os.getenv("CONFIG_PATH", "conf/configurations.json")
        with open(config_path, "rb") as conf:
            return json.load(conf)
