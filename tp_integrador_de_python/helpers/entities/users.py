"""File with the users entities class"""

from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .base_entity import BaseEntity
from .exceptions import AssignIDError, MissingColumnsError, MissingUserError


class Users(BaseEntity):

    def __init__(
        self,
        occupation: str,
        active_since: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        idx: int = None,
    ):
        self.occupation = occupation
        self.active_since = pd.to_datetime(active_since).strftime("%Y-%m-%d %H:%M:%S")
        self.idx = idx

    def __repr__(self) -> str:
        """Prints users information"""
        return f"user_id = {self.idx} \noccupation = {self.occupation} \nactive_since = {self.active_since}"

    def write_df(self, df: pd.DataFrame):
        """Function to write the current user in the dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with users information.

        Raises
        ------
        ValueError
            If the user already rated the movie.
        """
        if self.idx:
            raise AssignIDError("This user has an id already assigned")

        new_id = df["id"].max() + 1
        new_index = len(df.index)
        df.loc[new_index, ["id", "Occupation", "Active Since"]] = [
            new_id,
            self.occupation,
            self.active_since,
        ]
        self.idx = new_id
        print(f"The user was added to the dataframe with id {self.idx}")

    @classmethod
    def get_from_df(
        cls,
        df: pd.DataFrame,
        idx: int | list = None,
        occupation: str | list = None,
        date: str | list = None,
    ) -> list:
        """Class method to filter users from a dataframe given the idx, the occupation, or active account date.

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the users information.
        idx : int | list, Default None
            Index or list of index to filter.
        occupation : str | list, Default None
            Occupation or list of occupations to filter.
        date : str | list, Default None
            Start date or range of dates in a list to filter.

        Returns
        -------
        list[Users]
            List of users class instances that match the filters conditions.

        """
        users_list = []
        filtered = cls._filter(
            df,
            idx=idx,
            occupation=occupation,
            date=date,
        )

        if not filtered.empty:
            for index, row in filtered.iterrows():
                users_list.append(
                    Users(
                        idx=row["id"],
                        occupation=row["Occupation"],
                        active_since=row["Active Since"],
                    )
                )
        return users_list

    def remove_from_df(self, df):
        """Function to delete the curring user from the given dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the users information.

        Raises
        ------
        MissingUserError
            Raises if the user is not found in the dataframe.
        """

        filtered = df[
            (df["id"] == self.idx)
            & (df["Occupation"] == self.occupation)
            & (df["Active Since"] == self.active_since)
        ]

        if filtered.empty:
            raise MissingUserError("The user was not found in the dataframe")

        df.drop(index=filtered.index, inplace=True)
        self.idx = None
        print("The user was successfully deleted from the dataframe")

    @classmethod
    def get_stats(
        cls,
        df: pd.DataFrame,
        occupation: str | list[str] = None,
        date: list[str] = None,
    ):
        """Class method to print the stats from a users dataframe.

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with users information.
        occupation : int | list, Default None
            Occupation or list of occupations to filter.
        date : list[str], Default None
             List with two date range to filter.
        """
        filtered = cls._filter(df, occupation=occupation, date=date)

        if not filtered.empty:
            oldest = filtered.loc[filtered["Active Since"].idxmin()]
            cls._print_stats(oldest, "Oldest User")

            newest = filtered.loc[filtered["Active Since"].idxmax()]
            cls._print_stats(newest, "Newest User")
            cls._plot_stats(filtered)
        else:
            print("There are no users that match does dates and occupations.")

    @classmethod
    def _plot_stats(cls, df: pd.DataFrame) -> None:
        """Helper method to plot users dataframe stats

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the users information to be plotted.
        """
        sns.set_style("ticks")
        # Create Positions bar plot.
        fig, axes = plt.subplot_mosaic(
            [
                ["Occupation", "Occupation", "Occupation"],
            ],
            figsize=(12, 8),
        )

        users_df = (
            df.groupby("Occupation")["id"].count().reset_index().sort_values(by="id")
        )
        axes["Occupation"] = plt.pie(
            labels=users_df["Occupation"].tolist(),
            x=users_df["id"].tolist(),
        )

        plt.tight_layout()
        plt.show()

    @classmethod
    def _check_structure(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Class method to validate the structure of a given users dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with users information.

        Returns
        -------
        pd.DataFrame
            Pandas dataframe formatted and validated.

        Raises
        ------
        MissingColumnsError
            If the validation fails.
        """
        expected_columns = ["id", "Occupation", "Active Since"]
        if set(expected_columns).issubset(df.columns):
            df["Active Since"] = pd.to_datetime(df["Active Since"])
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
            Pandas series with the users information
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
                {bold}- User ID:{end} {int(df['id'])} \n
                {bold}- Occupation:{end} {df['Occupation']} \n
               """
        )

    @staticmethod
    def _filter(
        df: pd.DataFrame,
        idx: int | list = None,
        occupation: str | list = None,
        date: str | list = None,
    ) -> pd.DataFrame:
        """Helper function to filter a dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the users information.
        idx : int | list, Default None
            Index or list of index to filter.
        occupation : str | list, Default None
            Occupation or list of occupations to filter.
        date : str | list, Default None
            Start date or range of dates in a list to filter.

        Returns
        -------
        pd.DataFrame
            Filtered pandas dataframe.
        """
        filtered = df.copy()
        if occupation:
            occupation = [occupation] if isinstance(occupation, str) else occupation
            filtered = filtered[filtered["Occupation"].isin(occupation)]

        if date:
            date = [date] if isinstance(date, str) else date
            date = [pd.to_datetime(d).strftime("%Y-%m-%d %H:%M:%S") for d in date]
            if len(date) == 1:
                filtered = filtered[filtered["Active Since"] == date[0]]
            else:
                filtered = filtered[
                    filtered["Active Since"].between(min(date), max(date))
                ]

        if idx:
            idx = [idx] if isinstance(idx, int) else idx
            filtered = filtered[filtered["id"].isin(idx)]

        return filtered
