"""File with the scores entities class"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .base_entity import BaseEntity
from .exceptions import MissingColumnsError, MissingScoreError


class Scores(BaseEntity):

    def __init__(
        self,
        user_id: int,
        movie_id: int,
        rating: int,
        date: str,
    ):
        self.user_id = user_id
        self.movie_id = movie_id
        self.rating = rating
        self.date = pd.to_datetime(date).strftime("%Y-%m-%d")

    def __repr__(self) -> str:
        """Prints Scores information"""
        return (
            f"user_id = {self.user_id} \nmovie_id = {self.movie_id} \nrating = {self.rating} "
            f"\ndate = {self.date}"
        )

    def write_df(self, df: pd.DataFrame):
        """Function to write the current score in the dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with scores information.

        Raises
        ------
        ValueError
            If the user already rated the movie.
        """

        if not df[
            (df["user_id"] == self.user_id) & (df["movie_id"] == self.movie_id)
        ].empty:
            raise ValueError("This user has already rated this movie")

        new_index = len(df.index)
        df.loc[new_index, ["user_id", "movie_id", "rating", "Date"]] = [
            self.user_id,
            self.movie_id,
            self.rating,
            self.date,
        ]

        print("The rating was successfully added")

    @classmethod
    def get_from_df(
        cls,
        df: pd.DataFrame,
        user_id: int | list = None,
        movie_id: int | list = None,
        rating: int | list = None,
        date: str | list = None,
    ) -> list:
        """Class method to filter scores from a dataframe given the user_id, the movie_id, rating or date

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the scores information.
        user_id : str | list, Default None
            User ID or list of users IDs to filter.
        movie_id : str | list, Default None
            Movie ID or list of movies IDs to filter.
        rating : int | list, Default None
            Rating or list of ratings to filter.
        date : str | list, Default None
            Start date or range of dates in a list to filter.

        Returns
        -------
        list[Scores]
            List of scores class instances that match the filters conditions.

        """
        scores_list = []
        filtered = cls._filter(
            df,
            user_id=user_id,
            movie_id=movie_id,
            rating=rating,
            date=date,
        )

        if not filtered.empty:
            for index, row in filtered.iterrows():
                scores_list.append(
                    Scores(
                        user_id=row["user_id"],
                        movie_id=row["movie_id"],
                        rating=row["rating"],
                        date=row["Date"],
                    )
                )
        return scores_list

    def remove_from_df(self, df):
        """Function to delete the curring score from the given dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the scores information.

        Raises
        ------
        MissingScoreError
            Raises if the score is not found in the dataframe.
        """

        filtered = df[
            (df["user_id"] == self.user_id)
            & (df["movie_id"] == self.movie_id)
            & (df["rating"] == self.rating)
            & (df["Date"] == self.date)
        ]

        if filtered.empty:
            raise MissingScoreError("The score was not found in the dataframe")

        df.drop(index=filtered.index, inplace=True)
        print("The score was successfully deleted from the dataframe")

    @classmethod
    def get_stats(
        cls,
        df: pd.DataFrame,
        date: list[str] = None,
        user_id: int | list = None,
        movie_id: int | list = None,
        rating: int | list = None,
    ):
        """Class method to print the stats from a scores dataframe.

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with scores information.
        date : list[str], Default None
             List with two date range to filter.
        user_id : int | list, Default None
            User ID or list of users IDs to filter.
        movie_id : int | list, Default None
            Movie ID or list of movies IDs to filter.
        rating: int | list, Default None
            Rating or list of ratings to filter.
        """
        filtered = cls._filter(
            df, date=date, user_id=user_id, movie_id=movie_id, rating=rating
        )

        if not filtered.empty:
            ratings_df = pd.DataFrame(
                filtered.groupby("movie_id").rating.mean().sort_values(ascending=False)
            ).reset_index()
            highest = ratings_df.loc[ratings_df["rating"].idxmin()]
            cls._print_stats(highest, "Highest Rating Movie")

            lowest = ratings_df.loc[ratings_df["rating"].idxmax()]
            cls._print_stats(lowest, "Lowest Rating Movie")
            cls._plot_stats(filtered)
        else:
            print(
                "There are no scores that match does dates and users, movies or ratings"
            )

    @classmethod
    def _plot_stats(cls, df: pd.DataFrame) -> None:
        """Helper method to plot scores dataframe stats

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the scores information to be plotted.
        """
        sns.set_style("ticks")
        # Create Positions bar plot.
        fig, axes = plt.subplot_mosaic(
            [
                ["Rating", "Rating", "Rating"],
            ],
            figsize=(12, 8),
        )
        df["year"] = df["Date"].dt.year
        ratings_df = pd.DataFrame(
            df.groupby("year").rating.mean().sort_values(ascending=False)
        ).reset_index()
        sns.barplot(
            data=ratings_df,
            x="year",
            y="rating",
            legend=False,
            ax=axes["Rating"],
        )
        axes["Rating"].set_ylabel("Rating")
        axes["Rating"].set_xlabel("Movie ID")

        plt.tight_layout()
        plt.show()

    @classmethod
    def _check_structure(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Class method to validate the structure of a given scores dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with scores information.

        Returns
        -------
        pd.DataFrame
            Pandas dataframe formatted and validated.

        Raises
        ------
        MissingColumnsError
            If the validation fails.
        """
        expected_columns = ["user_id", "movie_id", "rating", "Date"]
        if set(expected_columns).issubset(df.columns):
            df["Date"] = pd.to_datetime(df["Date"])
            df.dropna(subset=expected_columns, inplace=True)
            return df[expected_columns]

        raise MissingColumnsError(
            f"One or more columns are missing from the given dataframe. Expected columns are: {expected_columns}"
        )

    @staticmethod
    def _print_stats(df: pd.Series, title: str) -> None:
        """Helper function to print the stats

        Parameters
        ----------
        df : pd.Series
            Pandas series with the scores information
        title : str
            Title of the stats to print.

        Returns
        -------

        """
        bold = "\033[1m"
        end = "\033[0m"
        print(
            f"""
               {bold}{title}{end}: \n
                {bold}- Movie ID:{end} {df['movie_id']} \n
                {bold}- Mean Rating:{end} {df['rating']} \n
               """
        )

    @staticmethod
    def _filter(
        df: pd.DataFrame,
        user_id: int | list = None,
        movie_id: int | list = None,
        rating: int | list = None,
        date: str | list = None,
    ) -> pd.DataFrame:
        """Helper function to filter a dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the Scores information.
        user_id : omt | list, Default None
            User ID or list of users IDs to filter.
        movie_id : int | list, Default None
            Movie ID or list of movies IDs to filter.
        rating : int | list, Default None
            Rating or list of ratings to filter.
        date : str | list, Default None
            Start Date or list of dates to use as range to filter.

        Returns
        -------
        pd.DataFrame
            Filtered pandas dataframe.
        """
        filtered = df.copy()
        if user_id:
            user_id = [user_id] if isinstance(user_id, int) else user_id
            filtered = filtered[filtered["user_id"].isin(user_id)]

        if movie_id:
            movie_id = [movie_id] if isinstance(movie_id, int) else movie_id
            filtered = filtered[filtered["movie_id"].isin(movie_id)]

        if rating:
            rating = [rating] if isinstance(rating, int) else rating
            filtered = filtered[filtered["rating"].isin(rating)]

        if date:
            date = [date] if isinstance(date, str) else date
            date = [pd.to_datetime(d).strftime("%Y-%m-%d") for d in date]
            if len(date) == 1:
                filtered = filtered[filtered["Date"] == date[0]]
            else:
                filtered = filtered[filtered["Date"].between(min(date), max(date))]

        return filtered
