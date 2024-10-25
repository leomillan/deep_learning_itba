"""File to train and save the model"""

import logging

import pandas as pd
import yaml
from core.services.configuration import ConfigurationManager
from core.services.database import DatabaseService, Rating
from model.train import do_train, save_embeddings
from sqlalchemy import select

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],  # Ensures logs are sent to stdout
)

logger = logging.getLogger(__name__)


def get_data() -> tuple[pd.DataFrame, dict, dict]:

    config = ConfigurationManager.init_config()
    client = DatabaseService(config["sql"])

    # Make query statement
    logger.info("Getting ratings from Database")
    stmt = select(Rating.id, Rating.movie_id, Rating.user_id, Rating.rating)
    ratings = pd.read_sql(sql=stmt, con=client.engine)
    logger.info(f"Total rows fetched: {ratings.shape[0]}")

    # Create a dictionary of indexes for the users and movies mapping every ID to a given index.
    logger.info("Building user and movie indexes")
    u_unique = ratings.user_id.unique()
    user_index = {o: i + 1 for i, o in enumerate(u_unique)}

    m_unique = ratings.movie_id.unique()
    movie_index = {o: i + 1 for i, o in enumerate(m_unique)}

    # Replace the users and movies ids with the new index value.
    ratings.user_id = ratings.user_id.apply(lambda x: user_index[x])
    ratings.movie_id = ratings.movie_id.apply(lambda x: movie_index[x])

    return ratings, user_index, movie_index


def run(model_name: str = "base_model"):
    logger.info("Loading configs...")
    with open("model_config.yaml", "r") as file:
        conf = yaml.safe_load(file).get(
            model_name, None
        )  # Use safe_load() to avoid arbitrary code execution

    if not conf:
        raise Exception(f"No configs for model {model_name}")

    # Get training data from DB.
    ratings, user_idx, movie_idx = get_data()
    n_users = int(ratings.user_id.nunique())
    n_movies = int(ratings.movie_id.nunique())

    # Train model
    layers = do_train(
        ratings,
        n_users=n_users,
        n_movies=n_movies,
        latent_factor=conf["latent_factors"],
        epochs=conf["epochs"],
        eval_size=conf["eval_size"],
        add_bias=conf["add_bias"],
        metrics=conf["metrics"],
    )

    if conf["save_embeddings"]:
        save_embeddings(layers, user_idx, movie_idx, dir_path="../data")


if __name__ == "__main__":
    run(model_name="base_model")
