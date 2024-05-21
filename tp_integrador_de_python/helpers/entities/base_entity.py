"""This file contains the base class implementation"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseEntity(ABC):

    @abstractmethod
    def __repr__(self) -> str:
        """_summary"""

    @abstractmethod
    def write_df(self, df: pd.DataFrame):
        """_summary"""

    @classmethod
    def create_df_from_csv(cls, filename: str) -> pd.DataFrame:
        """_summary"""
        df = pd.read_csv(filename)
        df = cls._check_structure(df)
        return df

    @classmethod
    def get_from_df(
        cls,
        df: pd.DataFrame,
        idx: int = None,
        name: str = None,
        year: int = None,
        gender: str = None,
    ) -> list:
        """_summary"""

    @classmethod
    def get_stats(cls, df: pd.DataFrame, year: int = None, gender: str = None):
        """_summary"""

    def remove_from_df(self, df_mov):
        """_summary"""

    @classmethod
    @abstractmethod
    def _check_structure(cls, df: pd.DataFrame) -> pd.DataFrame:
        """_summary"""
        return df
