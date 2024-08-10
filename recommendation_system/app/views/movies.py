"""Module with movies endpoints"""

from flask import Blueprint, current_app, request
from flask_restx import Api, Resource

movies = Blueprint("movies", __name__)

api = Api(
    movies,
    title="Movies Endpoints",
    description="Endpoints to get Movies recommendations",
)


@api.route("/movie", methods=["POST", "GET"])
class GetUserService(Resource):

    @staticmethod
    def post():
        vdb = current_app.container.vector_db()
        query = request.json["query"]
        response = vdb.client.search(index="movie", body=query)
        if hits := response.get("hits", {}).get("hits", {}):
            result = [
                {
                    "movie_id": hit["_source"]["movie_id"],
                    "name": hit["_source"]["name"],
                    "url": hit["_source"]["url"],
                }
                for hit in hits
            ]
            return result, 200
        else:
            return {"msg": "No movies found"}, 204
