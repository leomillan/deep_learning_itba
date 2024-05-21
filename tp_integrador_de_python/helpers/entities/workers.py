"""File with the workers entities class"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .base_entity import BaseEntity
from .exceptions import AssignIDError, MissingColumnsError, MissingWorkerError


class Workers(BaseEntity):

    def __init__(
        self,
        position: str,
        category: str,
        working_hours: str | list,
        date: str,
        idx: int = None,
    ):
        self.position = position
        self.category = category
        self.working_hours = working_hours
        self.date = pd.to_datetime(date).strftime("%Y-%m-%d")
        self.idx = idx

    def __repr__(self) -> str:
        """Prints workers information"""
        return (
            f"position = {self.position} \ncategory = {self.category} \nworking_hours = {self.working_hours} "
            f"\ndate = {self.date} \nidx = {self.idx}"
        )

    def write_df(self, df: pd.DataFrame):
        """Function to write the current worker in the dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with workers information.

        Raises
        ------
        ValueError
            If the idx is already assigned.
        """

        if self.idx:
            raise AssignIDError("This worker has an id already assigned")

        new_id = df["id"].max() + 1
        new_index = len(df.index)
        df.loc[
            new_index, ["id", "Position", "Category", "Working Hours", "Start Date"]
        ] = [new_id, self.position, self.category, self.working_hours, self.date]
        self.idx = new_id
        print(f"The worker was added to the dataframe with id {self.idx}")

    @classmethod
    def get_from_df(
        cls,
        df: pd.DataFrame,
        idx: int | list = None,
        position: str | list = None,
        category: str | list = None,
        working_hours: str = None,
        date: str | list = None,
    ) -> list:
        """Class method to filter workers from a dataframe given the idx, position, category, working_hours or date

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the workers information.
        idx : int | list, Default None
            Index or list of index to filter.
        position : str | list, Default None
            Worker position or list of positions to filter.
        category : str | list, Default None
            Category or list of categories to filter.
        working_hours : str, Default None
            Working hours to filter by.
        date : str | list, Default None
            Start date or range of dates in a list to filter.

        Returns
        -------
        list[Workers]
            List of workers class instances that match the filters conditions.

        """
        workers_list = []
        filtered = cls._filter(
            df,
            position=position,
            category=category,
            working_hours=working_hours,
            date=date,
            idx=idx,
        )

        if not filtered.empty:
            for index, row in filtered.iterrows():
                workers_list.append(
                    Workers(
                        position=row["Position"],
                        category=row["Category"],
                        working_hours=row["Working Hours"],
                        date=row["Start Date"],
                        idx=row["id"],
                    )
                )
        return workers_list

    def remove_from_df(self, df):
        """Function to delete the curring worker from the given dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the workers information.

        Raises
        ------
        MissingWorkerError
            Raises if the worker is not found in the dataframe.
        """

        filtered = df[
            (df["Position"] == self.position)
            & (df["Category"] == self.category)
            & (df["id"] == self.idx)
            & (df["Working Hours"] == self.working_hours)
            & (df["Start Date"] == self.date)
        ]

        if filtered.empty:
            raise MissingWorkerError("The worker was not found in the dataframe")

        df.drop(index=filtered.index, inplace=True)
        print("The worker was successfully deleted from the dataframe")

    @classmethod
    def get_stats(
        cls,
        df: pd.DataFrame,
        date: list[str] = None,
        position: str | list = None,
        category: str | list = None,
    ):
        """Class method to print the stats from a workers dataframe.

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with workers information.
        date : list[str], Default None
             List with two date range to filter.
        position : str | list, Default None
            Position or list of genders to filter.
        category : str | list, Default None
            Category or list of categories to filter.
        """
        filtered = cls._filter(df, date=date, position=position, category=category)

        if not filtered.empty:
            oldest = filtered.loc[filtered["Start Date"].idxmin()]
            cls._print_stats(oldest, "Oldest Worker")

            newest = filtered.loc[filtered["Start Date"].idxmax()]
            cls._print_stats(newest, "Newest Worker")
            cls._plot_stats(filtered)
        else:
            print(
                "There are no workers that match does dates and position or categories"
            )

    @classmethod
    def _plot_stats(cls, df: pd.DataFrame) -> None:
        """Helper method to plot workers dataframe stats

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the workers information to be plotted.
        """
        sns.set_style("ticks")
        # Create Positions bar plot.
        fig, axes = plt.subplot_mosaic(
            [
                ["Position", "Position", "Position", "Category", "Category"],
                ["Position", "Position", "Position", "Year", "Year"],
            ],
            figsize=(12, 8),
        )
        position_df = pd.DataFrame(
            df.groupby("Position").id.count().sort_values(ascending=False)
        ).reset_index()
        position_labels = position_df["Position"].to_list()
        sns.barplot(
            data=position_df,
            x="id",
            y="Position",
            hue="id",
            palette="Greens_d",
            legend=False,
            ax=axes["Position"],
        )
        axes["Position"].set_ylabel("Position")
        axes["Position"].set_xlabel("Frequency")
        axes["Position"].set_yticks(range(len(position_labels)))  # Set the ticks
        axes["Position"].set_yticklabels(position_labels)

        # Create Categories bar plot.
        category_df = pd.DataFrame(
            df.groupby("Category").id.count().sort_values(ascending=False)
        ).reset_index()
        category_labels = category_df["Category"].to_list()
        sns.barplot(
            data=category_df,
            x="Category",
            y="id",
            hue="id",
            palette="Greens_d",
            legend=False,
            ax=axes["Category"],
        )
        axes["Category"].set_ylabel("Frequency")
        axes["Category"].set_xlabel("Year")
        axes["Category"].set_xticks(range(len(category_labels)))  # Set the ticks
        axes["Category"].set_xticklabels(category_labels, rotation=45, ha="right")

        # Create Years bar plot.
        year_df = df.copy()
        year_df["year"] = year_df["Start Date"].dt.year
        year_df = pd.DataFrame(
            year_df.groupby("year").id.count().sort_values(ascending=False)
        ).reset_index()
        year_labels = year_df["year"].to_list()
        sns.barplot(
            data=year_df,
            x="year",
            y="id",
            hue="id",
            palette="Greens_d",
            legend=False,
            ax=axes["Year"],
        )
        axes["Year"].set_ylabel("Frequency")
        axes["Year"].set_xlabel("Year")
        axes["Year"].set_xticks(range(len(year_labels)))  # Set the ticks
        axes["Year"].set_xticklabels(year_labels, rotation=45, ha="right")

        plt.tight_layout()
        plt.show()

    @classmethod
    def _check_structure(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Class method to validate the structure of a given workers dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with workers information.

        Returns
        -------
        pd.DataFrame
            Pandas dataframe formatted and validated.

        Raises
        ------
        MissingColumnsError
            If the validation fails.
        """
        expected_columns = ["id", "Position", "Category", "Working Hours", "Start Date"]
        if set(expected_columns).issubset(df.columns):
            df["Start Date"] = pd.to_datetime(df["Start Date"])
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
            Pandas series with the movies information
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
                {bold}- Position:{end} {df['Position']} \n
                {bold}- Start Date:{end} {df['Start Date']} \n
                {bold}- Category:{end} {df['Category']} \n
                {bold}- Working Hours:{end} {df['Working Hours']} \n
               """
        )

    @staticmethod
    def _filter(
        df: pd.DataFrame,
        idx: int | list = None,
        position: str | list = None,
        category: str | list = None,
        working_hours: str = None,
        date: str | list = None,
    ) -> pd.DataFrame:
        """Helper function to filter a dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the workers information.
        idx : int | list, Default None
            Index or list of index to filter.
        position : str | list, Default None
            Worker position or list of positions to filter.
        category : str | list, Default None
            Worker category or list of categories to filter.
        working_hours : str, Default None
            Working hours to filter by.
        date : str | list, Default None
            Start Date or list of dates to use as range to filter.

        Returns
        -------
        pd.DataFrame
            Filtered pandas dataframe.
        """
        filtered = df.copy()
        if position:
            position = [position] if isinstance(position, str) else position
            filtered = filtered[filtered["Position"].isin(position)]

        if category:
            category = [category] if isinstance(category, str) else category
            filtered = filtered[filtered["Category"].isin(category)]

        if working_hours:
            filtered = filtered[filtered["Working Hours"] == working_hours]

        if date:
            date = [date] if isinstance(date, str) else date
            date = [pd.to_datetime(d).strftime("%Y-%m-%d") for d in date]
            if len(date) == 1:
                filtered = filtered[filtered["Start Date"] == date[0]]
            else:
                filtered = filtered[
                    filtered["Start Date"].between(min(date), max(date))
                ]

        if idx:
            idx = [idx] if isinstance(idx, int) else idx
            filtered = filtered[filtered["id"].isin(idx)]

        return filtered
