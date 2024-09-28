"""File to train keras model"""

import logging
import pickle

import numpy as np
import pandas as pd
from keras import Model
from keras.layers import Add, Dot, Embedding, Flatten, Input
from keras.optimizers import Adam
from keras.regularizers import l2
from sklearn.model_selection import train_test_split

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],  # Ensures logs are sent to stdout
)

logger = logging.getLogger(__name__)


def build_keras_model(
    users_number,
    movies_number,
    latent_factors=5,
    add_bias=False,
    loss="mean_squared_error",
    learning_rate=0.001,
    metrics: list = None,
) -> Model:

    movie_input = Input(shape=[1], name="Item")
    user_input = Input(shape=[1], name="User")

    # Movie Embedding Layer
    movie_embedding = Embedding(
        movies_number + 1,
        latent_factors,
        embeddings_regularizer=l2(0.001),
        name="Movie-Embedding",
    )(movie_input)

    movie_vec = Flatten(name="FlattenMovies")(movie_embedding)

    # User Embedding Layer
    user_embedding = Embedding(users_number + 1, latent_factors, name="User-Embedding")(
        user_input
    )

    user_vec = Flatten(name="FlattenUsers")(user_embedding)

    prod = Dot(axes=1, name="DotProduct")([movie_vec, user_vec])

    if add_bias:
        # Movie Bias Embedding Layer
        movie_bias_embedding = Embedding(
            movies_number + 1,
            1,
            embeddings_regularizer=l2(0.001),
            name="Movie-Bias-Embedding",
        )(movie_input)
        movie_bias = Flatten(name="FlattenMoviesBias")(movie_bias_embedding)

        # User Bias Embedding Layer
        user_bias_embedding = Embedding(
            users_number + 1, 1, name="User-Bias-Embedding"
        )(user_input)
        user_bias = Flatten(name="FlattenUserBias")(user_bias_embedding)
        prod = Add()([prod, user_bias, movie_bias])

    model = Model([user_input, movie_input], prod)
    model.compile(Adam(learning_rate=learning_rate), loss, metrics=metrics)
    return model


def save_embeddings(layers: dict, user_index: dict, movie_index: dict, dir_path: str):
    """Save model helper function"""
    movie_embeddings_matrix = layers["Movie-Embedding"].get_weights()[0]
    user_embeddings_matrix = layers["User-Embedding"].get_weights()[0]

    logger.info("Saving embedding layers and indexes")
    np.save(f"{dir_path}/movie_embeddings_matrix.npy", movie_embeddings_matrix)
    np.save(f"{dir_path}/user_embeddings_matrix.npy", user_embeddings_matrix)

    with open(f"{dir_path}/user2Idx.pkl", "wb") as file:
        pickle.dump(user_index, file, protocol=pickle.HIGHEST_PROTOCOL)

    with open(f"{dir_path}/movie2Idx.pkl", "wb") as file:
        pickle.dump(movie_index, file, protocol=pickle.HIGHEST_PROTOCOL)


def do_train(
    data: pd.DataFrame,
    n_users: int,
    n_movies: int,
    latent_factor: int,
    epochs: int,
    eval_size: float = 0.2,
    add_bias: bool = False,
    metrics: list = None,
) -> dict:
    # split dataset
    eval_size = eval_size
    logger.info("Splitting data for training.")
    ratings_train, ratings_val = train_test_split(data, test_size=eval_size)
    logger.info(
        "- Train size: %s \n - Test Size: %s",
        ratings_train.shape[0],
        ratings_val.shape[0],
    )

    model = build_keras_model(n_users, n_movies)
    model.summary(print_fn=logger.info)

    model = build_keras_model(
        n_users,
        n_movies,
        latent_factors=latent_factor,
        add_bias=add_bias,
        metrics=metrics,
    )
    model.fit(
        [ratings_train.user_id, ratings_train.movie_id],
        ratings_train.rating,
        batch_size=320,
        validation_data=(
            [ratings_val.user_id, ratings_val.movie_id],
            ratings_val.rating,
        ),
        epochs=epochs,
        verbose=1,
    )
    metrics_val = model.evaluate(
        [ratings_val.user_id, ratings_val.movie_id], ratings_val.rating
    )
    layers = {layer.name: layer for layer in model.layers}
    logger.info(f"RMSE: {metrics_val[1]} for latent_factor={latent_factor}")

    return layers
