import os

from flask import current_app
from opensearchpy import OpenSearch


class VectorDBService:

    def __init__(self, config):

        user = config.get("user")
        password = os.environ[config.get("pass")]
        host = config.get("host")
        port = config.get("port")

        self.client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=(user, password),
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False,
        )

        current_app.logger.info(self.client.cluster.health())
