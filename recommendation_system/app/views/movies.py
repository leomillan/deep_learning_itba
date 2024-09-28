"""Module with movies endpoints"""

from core.services.database import Movie, VMovie
from flask import Blueprint, current_app, request
from flask_caching import Cache
from flask_restx import Api, Resource

movies = Blueprint("movies", __name__)

api = Api(
    movies,
    title="Movies Endpoints",
    description="Endpoints to get Movies recommendations",
)

cache = Cache()


@cache.cached(timeout=60)
@api.route("/movie/<movie_id>", methods=["GET"])
class GetUserService(Resource):

    def get(self, movie_id):
        vdb = current_app.container.vector_db()
        sqldb = current_app.container.sql_db()

        neighbors = int(request.args.get("neighbors", 20))

        movie = sqldb.db_session.query(Movie).filter(Movie.id == movie_id).first()

        if not movie:
            return {"msg": f"There is no movie with ID {movie_id}"}, 200

        current_app.logger.info(movie.name)
        query = {
            "size": neighbors + 1,
            "query": {
                "knn": {
                    "vector": {
                        "vector": movie.embedding,
                        "k": len(movie.embedding),
                    }
                }
            },
        }

        current_app.logger.info(query)
        response = vdb.client.search(index=VMovie.Index.name, body=query)
        current_app.logger.info(response)
        result = {
            "movie_id": movie.id,
            "name": movie.name,
            "year": movie.release_date.year,
            "genres": movie.genres,
        }
        if hits := response.get("hits", {}).get("hits", {}):
            recommendations = [
                {
                    "movie_id": hit["_source"]["movie_id"],
                    "name": hit["_source"]["name"],
                    "url": hit["_source"]["url"],
                    "score": hit["_score"],
                }
                for hit in hits
                if hit["_source"]["movie_id"] != movie.id
            ]
            recommendations = self.get_genres(sqldb, recommendations)
            current_app.logger.info(recommendations)
            result["recommendations"] = recommendations
            return result, 200

    @staticmethod
    def get_genres(sqldb, recommendations):
        ids = [i["movie_id"] for i in recommendations]
        response = (
            sqldb.db_session.query(Movie.id, Movie.release_date, Movie.genres)
            .filter(Movie.id.in_(ids))
            .all()
        )
        response = {key: {"release_date": rd, "genres": g} for key, rd, g in response}
        for r in recommendations:
            r["year"] = response[r["movie_id"]]["release_date"].year
            r["genres"] = response[r["movie_id"]]["genres"]
        current_app.logger.info(recommendations)
        return recommendations
