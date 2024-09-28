"""Module with users endpoints"""

from multiprocessing.pool import ThreadPool

from core.services.database import Movie, Rating, User, VMovie
from flask import Blueprint, current_app, request
from flask_caching import Cache
from flask_restx import Api, Resource
from sqlalchemy import func

users = Blueprint("users", __name__)

api = Api(
    users, title="Users Endpoints", description="Endpoints to get Users recommendations"
)

cache = Cache()


@cache.cached(timeout=60)
@api.route("/user/<user_id>", methods=["GET"])
class GetUserService(Resource):

    def get(self, user_id):
        vdb = current_app.container.vector_db()
        sqldb = current_app.container.sql_db()

        n = int(request.args.get("n", 5))
        if not sqldb.db_session.query(User.id).filter(User.id == user_id).first():
            return {"msg": f"There is no user with ID {user_id}"}, 200

        # Get the top n movies that the user rate with 4 or more.
        user = (
            sqldb.db_session.query(
                User.id.label("user_id"),
                User.name.label("user_name"),
                Rating.rating,
                Movie.id.label("movie_id"),
                Movie.embedding,
            )
            .join(Rating, User.id == Rating.user_id, isouter=True)
            .join(Movie, Rating.movie_id == Movie.id, isouter=True)
            .filter(User.id == user_id, Rating.rating >= 4)
            .order_by(Rating.rating.desc())
            .limit(n)
            .all()
        )
        results = {"user_id": user[0].user_id, "name": user[0].user_name}
        if user:
            movie_ids = [u.movie_id for u in user]
            items = [(vdb, u.embedding, movie_ids) for u in user]
            with ThreadPool() as pool:
                movies = pool.starmap(self.get_recommendation, items)

            movie_ids = [m["movie_id"] for m in movies if m]
            movie_stats = self.get_movie_stats(sqldb, movie_ids)

            results["recommendations"] = movie_stats

        else:
            movies = self.get_fallback(sqldb, n)
            results["recommendations"] = movies

        return results, 200

    @staticmethod
    def get_recommendation(vdb, embedding, movie_ids):
        query = {
            "size": 5,
            "query": {
                "knn": {
                    "vector": {
                        "vector": embedding,
                        "k": len(embedding),
                    }
                }
            },
        }
        response = vdb.client.search(index=VMovie.Index.name, body=query)

        recos = None
        if hits := response.get("hits", {}).get("hits", {}):
            recos = [
                {
                    "movie_id": hit["_source"]["movie_id"],
                    "name": hit["_source"]["name"],
                    "url": hit["_source"]["url"],
                    "score": hit["_score"],
                }
                for hit in hits
                if hit["_source"]["movie_id"] not in movie_ids
            ]
        return recos[0] if len(recos) > 0 else recos

    @staticmethod
    def get_movie_stats(sqldb, movie_ids):
        response = (
            sqldb.db_session.query(
                Movie.id, Movie.name, Movie.url, Movie.release_date, Movie.genres
            )
            .filter(Movie.id.in_(movie_ids))
            .all()
        )

        stats = [
            {
                "movie_id": r.id,
                "name": r.name,
                "url": r.url,
                "year": r.release_date.year,
                "genres": r.genres,
            }
            for r in response
        ]
        return stats

    @staticmethod
    def get_fallback(sqldb, n):

        response = (
            sqldb.db_session.query(
                Rating.movie_id, Movie.name, Movie.url, Movie.genres, Movie.release_date
            )
            .group_by(
                Rating.movie_id, Movie.name, Movie.genres, Movie.release_date, Movie.url
            )
            .join(Movie)
            .having(func.count(Rating.rating) > 10)
            .order_by(func.avg(Rating.rating).desc(), func.count(Rating.rating).desc())
            .limit(n)
        ).all()

        stats = [
            {
                "movie_id": r.movie_id,
                "name": r.name,
                "url": r.url,
                "year": r.release_date.year,
                "genres": r.genres,
            }
            for r in response
        ]
        return stats
