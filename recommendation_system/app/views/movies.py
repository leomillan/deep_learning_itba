"""Module with movies endpoints"""

from core.services.database import Movie, VMovie
from flask import Blueprint, current_app, request
from flask_restx import Api, Resource

movies = Blueprint("movies", __name__)

api = Api(
    movies,
    title="Movies Endpoints",
    description="Endpoints to get Movies recommendations",
)


@api.route("/movie/<movie_id>", methods=["GET"])
class GetUserService(Resource):

    @staticmethod
    def get(movie_id):
        vdb = current_app.container.vector_db()
        sqldb = current_app.container.sql_db()

        neighbors = request.args.get("neighbors", 20)

        movie = sqldb.db_session.query(Movie).filter(Movie.id == movie_id).first()
        current_app.logger.info(movie.name)

        query = {
            "size": len(movie.embedding),
            "query": {
                "knn": {
                    "vector": {
                        "vector": [float(val) for val in movie.embedding],
                        "k": neighbors,
                    }
                }
            },
        }

        current_app.logger.info(query)
        response = vdb.client.search(index=VMovie.Index.name, body=query)
        current_app.logger.info(response)
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
            return {"msg": f"No recommendations found for {movie.name}"}, 200
