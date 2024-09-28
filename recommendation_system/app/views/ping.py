"""ping view"""

from flask import Blueprint, jsonify
from flask_restx import Api, Resource

ping = Blueprint("ping", __name__)

api = Api(ping, title="Ping Endpoints")


# Ping route for health check
@api.route("/ping", methods=["GET"])
class PingService(Resource):

    @staticmethod
    def get():
        return jsonify({"message": "pong"})
