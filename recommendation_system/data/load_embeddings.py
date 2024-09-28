"""File to load Embeddings into vector DB"""

import logging
import pickle
from datetime import datetime

import numpy as np
import pandas as pd
from core.services.configuration import ConfigurationManager
from core.services.database import DatabaseService, Movie, VectorDBService, VMovie
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

    with open("movie2Idx.pkl", "rb") as file:
        movie_idx = pickle.load(file)

    # Make query statement
    logger.info("Getting movies from SQL Database")
    stmt = select(Movie.id, Movie.url, Movie.name)
    movies = pd.read_sql(sql=stmt, con=sql_client.engine)
    logger.info(f"Total rows fetched: {movies.shape[0]}")

    logger.info("Adding movies Index")
    movies["movieIdx"] = movies["id"].apply(lambda x: movie_idx[x])

    logger.info("Deleting all documents from Vector DB")
    response = elastic_client.client.delete_by_query(
        index=VMovie.Index.name, body={"query": {"match_all": {}}}
    )
    logger.info(f"Total documents deleted: {response['total']}")

    logger.info("Loading new Movie Embeddings to Vector DB")
    dimension = movie_embeddings_matrix.shape[1]
    if not elastic_client.client.indices.exists(VMovie.Index.name):
        VMovie.init(using=elastic_client.client)

    for i, row in tqdm(movies.iterrows(), total=movies.shape[0]):
        mv = VMovie(dimension=dimension)
        mv.movie_id = row.id
        mv.url = row.url
        mv.name = row.name
        mv.vector = list(movie_embeddings_matrix[row.movieIdx])
        mv.created_at = datetime.now()

        mv.save(using=elastic_client.client)

    logger.info("Updating movies embeddings in the SQL Database")
    for movie_id, idx in tqdm(movie_idx.items()):
        sql_client.db_session.query(Movie).filter(Movie.id == movie_id.item()).update(
            {"embedding": [str(val) for val in movie_embeddings_matrix[idx].tolist()]}
        )

    sql_client.db_session.commit()
    logger.info("Movie Embeddings successfully updated")


if __name__ == "__main__":
    load_embeddings()
