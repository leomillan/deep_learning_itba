from app.container import Container
from app.views import movies, users
from flask import Flask
from flask.logging import default_handler

ACTIVE_ENDPOINTS = (("/", users), ("/", movies))


def create_app():
    app = Flask(__name__)
    app.container = Container()
    app.logger.addHandler(default_handler)

    for url, blueprint in ACTIVE_ENDPOINTS:
        app.register_blueprint(blueprint, url_prefix=url)

    return app
