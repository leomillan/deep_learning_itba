"""File to load Embeddings into vector DB"""

import logging
import pickle
from datetime import datetime

import numpy as np
import pandas as pd
from core.services.configuration import ConfigurationManager
from core.services.database import (
    DatabaseService,
    Movie,
    User,
    VectorDBService,
    VMovie,
    VUser,
)
from sqlalchemy import select
from tqdm import tqdm

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],  # Ensures logs are sent to stdout
)

logger = logging.getLogger(__name__)


def load_embeddings():

    config = ConfigurationManager.init_config()
    elastic_client = VectorDBService(config["elastic"])
    sql_client = DatabaseService(config["sql"])

    logger.info("Loading embeddings and indexes")
    movie_embeddings_matrix = np.load("movie_embeddings_matrix.npy")
    user_embeddings_matrix = np.load("user_embeddings_matrix.npy")

    with open("movie2Idx.pkl", "rb") as file:
        movie_idx = pickle.load(file)

    with open("user2Idx.pkl", "rb") as file:
        user_idx = pickle.load(file)

    # Make query statement
    logger.info("Getting movies from SQL Database")
    stmt = select(Movie.id, Movie.url, Movie.name)
    movies = pd.read_sql(sql=stmt, con=sql_client.engine)
    logger.info(f"Total rows fetched: {movies.shape[0]}")

    logger.info("Getting users from SQL Database")
    stmt = select(User.id, User.name)
    users = pd.read_sql(sql=stmt, con=sql_client.engine)
    logger.info(f"Total rows fetched: {users.shape[0]}")

    logger.info("Adding user and movies Index")
    movies["movieIdx"] = movies["id"].apply(lambda x: movie_idx[x])
    users["userIdx"] = users["id"].apply(lambda x: user_idx[x])

    if not elastic_client.client.indices.exists(VUser.Index.name):
        VUser.init(using=elastic_client.client)
    else:
        logger.info("Deleting all user documents from Vector DB")
        response = elastic_client.client.delete_by_query(
            index=VUser.Index.name, body={"query": {"match_all": {}}}
        )
        elastic_client.client.indices.delete(index=VUser.Index.name)
        VUser.init(using=elastic_client.client)

        logger.info(f"Total user documents deleted: {response['total']}")

    logger.info("Loading new User Embeddings to Vector DB")
    for i, row in tqdm(users.iterrows(), total=users.shape[0]):
        vu = VUser(
            user_id=row["id"],
            name=row["name"],
            vector=list(user_embeddings_matrix[row["userIdx"]]),
            created_at=datetime.now(),
        )
        vu.save(using=elastic_client.client, index=VUser.Index.name)

    if not elastic_client.client.indices.exists(VMovie.Index.name):
        VMovie.init(using=elastic_client.client)
    else:
        logger.info("Deleting all movie documents from Vector DB")
        response = elastic_client.client.delete_by_query(
            index=VMovie.Index.name, body={"query": {"match_all": {}}}
        )
        elastic_client.client.indices.delete(index=VMovie.Index.name)
        VMovie.init(using=elastic_client.client)
        logger.info(f"Total movie documents deleted: {response['total']}")

    logger.info("Loading new Movie Embeddings to Vector DB")
    for i, row in tqdm(movies.iterrows(), total=movies.shape[0]):
        vm = VMovie(
            movie_id=row["id"],
            url=row["url"],
            name=row["name"],
            vector=list(movie_embeddings_matrix[row["movieIdx"]]),
            created_at=datetime.now(),
        )
        vm.save(using=elastic_client.client, index=VMovie.Index.name)

    logger.info("Updating movies embeddings in the SQL Database")
    for movie_id, idx in tqdm(movie_idx.items()):
        sql_client.db_session.query(Movie).filter(Movie.id == movie_id.item()).update(
            {"embedding": movie_embeddings_matrix[idx].tolist()}
        )

    sql_client.db_session.commit()
    logger.info("Movie Embeddings successfully updated")

    logger.info("Updating user embeddings in the SQL Database")
    for user_id, idx in tqdm(user_idx.items()):
        sql_client.db_session.query(User).filter(User.id == user_id.item()).update(
            {"embedding": user_embeddings_matrix[idx].tolist()}
        )

    sql_client.db_session.commit()
    logger.info("User Embeddings successfully updated")


if __name__ == "__main__":
    load_embeddings()
