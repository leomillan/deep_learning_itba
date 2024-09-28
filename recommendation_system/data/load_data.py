"""File to load data into database"""

import logging

import pandas as pd
from core.services.configuration import ConfigurationManager
from core.services.database import DatabaseService, Movie, Rating, User

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],  # Ensures logs are sent to stdout
)

logger = logging.getLogger(__name__)


def load_data():
    config = ConfigurationManager.init_config()
    client = DatabaseService(config["sql"], drop_tables=True)

    logger.info("Loading user data")
    users = pd.read_csv("usuarios.csv")
    user_info = pd.read_csv("personas.csv")

    users = users.merge(user_info, on="id").rename(
        columns={
            "Occupation": "occupation",
            "Active Since": "active_since",
            "Full Name": "name",
            "year of birth": "year_of_birth",
            "Gender": "gender",
            "Zip Code": "zipcode",
        }
    )

    users_to_add = []
    for _, row in users.iterrows():
        users_to_add.append(User(**row))
    client.db_session.add_all(users_to_add)
    client.db_session.commit()
    logger.info(f"Loaded {client.db_session.query(User).count()} users")

    logger.info("Loading Movies data")
    movies = pd.read_csv("peliculas.csv")
    genres_cols = movies.select_dtypes(include=["int64"]).columns.to_list()
    genres_cols.remove("id")  # Remove the id column to keep only genres
    movies["genres"] = movies.apply(
        lambda x: [col for col in genres_cols if x[col] == 1], axis=1
    )

    movies = movies[["id", "Name", "Release Date", "IMDB URL", "genres"]].rename(
        columns={"Name": "name", "Release Date": "release_date", "IMDB URL": "url"}
    )
    movies["release_date"] = pd.to_datetime(movies["release_date"])
    movies.dropna(subset=["release_date"], inplace=True)

    # Insert movies into database
    movies_to_add = []
    for _, row in movies.iterrows():
        movies_to_add.append(Movie(**row))
    client.db_session.add_all(movies_to_add)
    client.db_session.commit()

    logger.info(f"Loaded {client.db_session.query(Movie).count()} movies")

    logger.info("Loading Ratings data")
    ratings = pd.read_csv("scores.csv")
    ratings.columns = ["id", "user_id", "movie_id", "rating", "date"]

    # Remove ratings with invalid movie ids
    ratings = ratings[ratings["movie_id"].isin(movies["id"])]

    # Remove ratings with invalid user ids
    ratings = ratings[ratings["user_id"].isin(users["id"])]

    # Insert ratings into database
    ratings_to_add = []
    for _, row in ratings.iterrows():
        ratings_to_add.append(Rating(**row))
    client.db_session.add_all(ratings_to_add)
    client.db_session.commit()

    logger.info(f"Loaded {client.db_session.query(Rating).count()} ratings")


if __name__ == "__main__":
    load_data()
