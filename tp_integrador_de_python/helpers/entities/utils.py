"""File with utils functions"""

import pandas as pd
from helpers import Movies, People, Scores, Users, Workers


def load_all(
    file_people: str,
    file_workers: str,
    file_users: str,
    file_movies: str,
    file_scores: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Function to load all systems files
    Parameters
    ----------
    file_people : str
        File Path to the people csv.
    file_workers : str
        File Path to the people csv.
    file_users : str
        File Path to the people csv.
    file_movies : str
        File Path to the people csv.
    file_scores : str
        File Path to the people csv.

    Returns
    -------
    tuple[pd.DataFrame]:
        Tuple of the 5 dataframes in the following order:
            1. people_df
            2. workers_df
            3. users_df
            4. movies_df
            5. scores_df
    """

    people_df = People.create_df_from_csv(file_people)
    workers_df = Workers.create_df_from_csv(file_workers)
    users_df = Users.create_df_from_csv(file_users)
    movies_df = Movies.create_df_from_csv(file_movies)
    scores_df = Scores.create_df_from_csv(file_scores)

    # Validate users ids and movies ids in scores_df.
    scores_df = pd.merge(
        scores_df, users_df[["id"]].rename(columns={"id": "user_id"}), on="user_id"
    )
    scores_df = pd.merge(
        scores_df, movies_df[["id"]].rename(columns={"id": "movie_id"}), on="movie_id"
    )

    # Validate people ids in workers_df.
    workers_df = pd.merge(workers_df, people_df[["id"]], on="id")

    return people_df, workers_df, users_df, movies_df, scores_df


def save_all(
    people_df: pd.DataFrame,
    workers_df: pd.DataFrame,
    users_df: pd.DataFrame,
    movies_df: pd.DataFrame,
    scores_df: pd.DataFrame,
    file_people: str,
    file_workers: str,
    file_users: str,
    file_movies: str,
    file_scores: str,
):
    """
    Function to save all systems dataframes in the given csv files.

    Parameters
    ----------
    people_df : pd.DataFrame
        People's dataframe.
    workers_df : pd.DataFrame
        Worker's dataframe.
    users_df : pd.DataFrame
        User's dataframe.
    movies_df : pd.DataFrame
        Movie's dataframe.
    scores_df : pd.DataFrame
        Score's dataframe.
    file_people : str
        File Path to the people csv.
    file_workers : str
        File Path to the people csv.
    file_users : str
        File Path to the people csv.
    file_movies : str
        File Path to the people csv.
    file_scores : str
        File Path to the people csv.

    Returns
    -------

    """
    try:
        people_df.to_csv(file_people, index=False)
        workers_df.to_csv(file_workers, index=False)
        users_df.to_csv(file_users, index=False)
        movies_df.to_csv(file_movies, index=False)
        scores_df.to_csv(file_scores, index=False)
        print("Files saved successfully")
        return 0
    except OSError as error:
        print(f"Files could not be save. Error: {error}")
        return 1
