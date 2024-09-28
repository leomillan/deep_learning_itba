import datetime

from core.services.database.database_service import Base
from opensearchpy import Date, Document, Field, Keyword, Text
from sqlalchemy import ARRAY, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    year_of_birth = Column(Integer, nullable=False)
    gender = Column(String(2), nullable=False)
    zipcode = Column(String(40), nullable=False)
    occupation = Column(String(255), nullable=False)
    active_since = Column(DateTime, nullable=False)
    embedding = Column(ARRAY(Float), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    rating = relationship("Rating")


class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    release_date = Column(DateTime, nullable=False)
    embedding = Column(ARRAY(String(255)), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    rating = relationship("Rating")


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())


class KNNVector(Field):
    name = "knn_vector"

    def __init__(self, dimension, method, **kwargs):
        super(KNNVector, self).__init__(dimension=dimension, method=method, **kwargs)


class VMovie(Document):

    method = {"name": "hnsw", "space_type": "cosinesimil", "engine": "nmslib"}

    movie_id = Keyword()
    url = Text()
    name = Text()
    created_at = Date()

    # Update the vector field to be initialized in the __init__ method
    vector = None

    class Index:
        name = "movie"
        settings = {"index": {"knn": True}}

    def __init__(self, dimension, **kwargs):
        super().__init__(**kwargs)  # Call the parent constructor
        # Initialize vector with the passed dimension
        self.vector = KNNVector(dimension=dimension, method=self.method)

    # Redefine the save method to assign the movie_id as index instead of a custom index
    # This approach will prevent having duplicated movies
    def save(self, **kwargs):
        self.meta.id = self.movie_id
        return super(VMovie, self).save(**kwargs)
