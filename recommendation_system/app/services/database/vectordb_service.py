import os

from flask import current_app
from opensearchpy import OpenSearch


class VectorDBService:

    def __init__(self, config):

        user = config.get("user")
        password = os.environ[config.get("pass")]
        hosts = config.get("hosts")
        port = config.get("port")
        current_app.logger.info(f"{user}, {password}, {hosts}, {port}")
        self.client = OpenSearch(
            hosts=[{"host": host, "port": port} for host in hosts],
            http_auth=(user, password),
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False,
        )

        current_app.logger.info(self.client.cluster.health())
