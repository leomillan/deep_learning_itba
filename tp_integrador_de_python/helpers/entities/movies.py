"""File with the movies entities class"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .base_entity import BaseEntity
from .exceptions import AssignIDError, MissingColumnsError, MissingMovieError


class Movies(BaseEntity):

    def __init__(
        self, name: int, date: str, genders: str | list = None, idx: int = None
    ):
        self.name = name
        self.date = pd.to_datetime(date).strftime("%Y-%m-%d")
        self.genders = self._format_genders(genders)
        self.idx = idx

    def __repr__(self) -> str:
        """Prints movies information"""
        return f"name = {self.name} \ndate = {self.date} \ngenders = {self.genders}  \nidx = {self.idx}"

    def write_df(self, df: pd.DataFrame):
        """Function to write the current movie in the dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with movies information.

        Raises
        ------
        ValueError
            If the idx is already assigned.
        """

        if self.idx:
            raise AssignIDError("This movie has an id already assigned")

        new_id = df["id"].max() + 1
        new_index = len(df.index)
        genders = [gender for gender in self.genders if gender in df.columns]
        df.loc[new_index, ["id", "Name", "Release Date"] + genders] = [
            new_id,
            self.name,
            self.date,
        ] + [1.0] * len(genders)
        numeric_columns = df.select_dtypes(include=["number"]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        self.idx = new_id
        print(f"The movie '{self.name}' was added to the dataframe with id {self.idx}")

    @classmethod
    def get_from_df(
        cls,
        df: pd.DataFrame,
        idx: int | list = None,
        name: str | list = None,
        year: list[int] = None,
        gender: str | list = None,
    ) -> list:
        """Class method to filter movies from a dataframe given the idx, name, year or gender

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the movies information.
        idx : int | list, Default None
            Index or list of index to filter.
        name : str | list, Default None
            Movie name or list of names to filter.
        year : list[int], Default None
            List with two years range to filter.
        gender : str | list, Default None
            Gender or list of genders to filter.

        Returns
        -------
        list[Movies]
            List of Movies class instances that match the filters conditions.

        """
        filtered = df.copy()
        movies_list = []
        if idx:
            idx = [idx] if isinstance(idx, int) else idx
            filtered = filtered.loc[df["id"].isin(idx),]

        if name:
            name = [name] if isinstance(name, str) else name
            filtered = filtered[filtered["Name"].isin(name)]

        if year:
            filtered = cls._filter_by_year(filtered, year)

        if gender:
            filtered = cls._filter_by_gender(filtered, cls._format_genders(gender))

        if not filtered.empty:
            for index, row in filtered.iterrows():
                movies_list.append(
                    Movies(
                        name=row["Name"],
                        date=row["Release Date"].strftime("%Y-%m-%d"),
                        genders=[
                            col
                            for col, val in zip(filtered.columns[1:], row[1:])
                            if val == 1
                        ],
                        idx=row["id"],
                    )
                )
        return movies_list

    @classmethod
    def get_stats(
        cls, df: pd.DataFrame, year: list[int] = None, gender: str | list = None
    ):
        """Class method to print the stats from a movies dataframe.

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with movies information.
        year : list[int], Default None
             List with two years range to filter.
        gender : str | list, Default None
            Gender or list of genders to filter.
        """
        filtered = df.copy()

        if year:
            filtered = cls._filter_by_year(filtered, year)

        if gender:
            gender = cls._format_genders(gender)
            filtered = cls._filter_by_gender(filtered, gender)

        if not filtered.empty:

            oldest = filtered.loc[filtered["Release Date"].idxmin()]
            cls._print_stats(oldest, "Oldest Movie")

            newest = filtered.loc[filtered["Release Date"].idxmax()]
            cls._print_stats(newest, "Newest Movie")
            cls._plot_stats(filtered, gender if gender else None)

        else:
            print("There are no movies that match does years and genders")

    def remove_from_df(self, df):
        """Function to delete the curring movie from the given dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the movies information.

        Raises
        ------
        MissingMovieError
            Raises if the movie is not found in the dataframe.
        """
        filtered = self._filter_by_gender(df, list(self.genders))
        filtered = filtered[
            (filtered["Name"] == self.name)
            & (filtered["Release Date"] == self.date)
            & (filtered["id"] == self.idx)
        ]

        if filtered.empty:
            raise MissingMovieError(
                f"The movie '{self.name}' was not found in the dataframe"
            )

        df.drop(index=filtered.index, inplace=True)
        print(f"The movie '{self.name}' was successfully deleted from the dataframe")

    @staticmethod
    def _format_genders(genders: str | list) -> list:
        """Method to format the gender input

        Parameters
        ----------
        genders : str | list
            Gender or list of genders to filter.

        Returns
        -------
        list
            Formatted list of genders

        """
        if not genders:
            return ["unknown"]

        genders = genders.split(",") if isinstance(genders, str) else genders
        return [gender.strip() for gender in genders]

    @classmethod
    def _check_structure(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Class method to validate the structure of a given movies dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with movies information.

        Returns
        -------
        pd.DataFrame
            Pandas dataframe formatted and validated.

        Raises
        ------
        MissingColumnsError
            If the validation fails.
        """
        expected_columns = ["id", "Name", "Release Date"]
        if set(expected_columns).issubset(df.columns):
            df["Release Date"] = pd.to_datetime(df["Release Date"])
            df.dropna(subset=expected_columns, inplace=True)
            return df

        raise MissingColumnsError(
            f"One or more columns are missing from the given dataframe. Expected columns are: {expected_columns}"
        )

    @staticmethod
    def _filter_by_year(df: pd.DataFrame, year: list[int]) -> pd.DataFrame:
        """Helper function to filter a dataframe by a range of years

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe to filter
        year : list[int]
            List with two years range to filter.

        Returns
        -------
        pd.DataFrame
            Filtered pandas dataframe

        """
        min_year = pd.to_datetime(str(min(year)))
        max_year = pd.to_datetime(str(max(year)))
        return df[(df["Release Date"] >= min_year) & (df["Release Date"] <= max_year)]

    @staticmethod
    def _filter_by_gender(df: pd.DataFrame, gender: str | list) -> pd.DataFrame:
        """Helper function to filter a dataframe by a gender or list of genders

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe to filter
        gender : str | list
             Gender or list of genders to filter.

        Returns
        -------
        pd.DataFrame
            Filtered pandas dataframe

        """
        gender = [gender] if isinstance(gender, str) else gender
        gender = [g for g in gender if g in df.columns]
        mask = df.loc[:, gender] == 1
        return df[mask.all(axis=1)]

    @staticmethod
    def _plot_stats(df: pd.DataFrame, gender: list = None) -> None:
        """Helper method to plot movies dataframe stats

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the movies information to be plotted.
        gender : list, default None
            List of genders to filter the Gender bar plot.
        """
        sns.set_style("ticks")
        fig, axes = plt.subplot_mosaic(
            [["Year", "Year"], ["Gender", "Gender"]], figsize=(12, 8)
        )
        if not gender:
            int_cols = df.select_dtypes(include=["int64"]).columns.to_list()
            int_cols.remove("id")
        else:
            int_cols = gender

        gender_df = pd.DataFrame(
            df[int_cols]
            .melt()
            .groupby("variable")
            .value.sum()
            .sort_values(ascending=False)
        ).reset_index()
        year_df = pd.DataFrame(df.groupby("year").id.count()).reset_index()
        year_labels = year_df["year"].to_list()
        gender_labels = gender_df["variable"].to_list()
        sns.barplot(
            data=year_df,
            x="year",
            y="id",
            hue="id",
            palette="Greens_d",
            legend=False,
            ax=axes["Year"],
        )
        sns.barplot(
            data=gender_df,
            x="variable",
            y="value",
            hue="value",
            palette="Greens_d",
            legend=False,
            ax=axes["Gender"],
        )
        axes["Year"].set_ylabel("Frequency")
        axes["Year"].set_xlabel("Year")
        axes["Year"].set_xticks(range(len(year_labels)))  # Set the ticks
        axes["Year"].set_xticklabels(year_labels, rotation=45, ha="right")
        axes["Gender"].set_ylabel("Frequency")
        axes["Gender"].set_xlabel("Gender")
        axes["Gender"].set_xticks(range(len(gender_labels)))  # Set the ticks
        axes["Gender"].set_xticklabels(gender_labels, rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

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
            {bold}- Name:{end} {df['Name']} \n
            {bold}- Release date:{end} {df['Release Date'].strftime("%Y-%m-%d")} \n
            {bold}- Genders:{end} {', '.join([col for col, val in zip(df.keys(), df[1:]) if val == 1])}
           """
        )
