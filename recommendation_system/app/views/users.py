"""Module with movies endpoints"""

from app.services.database.models import User
from flask import Blueprint, current_app, request
from flask_restx import Api, Resource

users = Blueprint("users", __name__)

api = Api(
    users, title="Users Endpoints", description="Endpoints to get Users recommendations"
)


@api.route("<user_name>/user", methods=["GET"])
class GetUserService(Resource):

    @staticmethod
    def get(user_name):
        db = current_app.container.sql_db()
        row = db.db_session.query(User).filter(User.name == user_name).first()
        if row:
            return {"User name": row.name, "User age": row.age}, 200
        else:
            return {"msg": f"user {user_name} not found in the database"}, 200


@api.route("/user", methods=["POST"])
class AddUserService(Resource):
    @staticmethod
    def post():
        body = request.json
        db = current_app.container.sql_db()
        user = User(**body)
        db.db_session.add(user)
        db.db_session.commit()
        return {"msg": "user successfully added"}
