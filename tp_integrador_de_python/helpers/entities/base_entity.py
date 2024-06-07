"""This file contains the base class implementation"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseEntity(ABC):
    """Base class to be used for all entities classes"""

    @classmethod
    def create_df_from_csv(cls, filename: str) -> pd.DataFrame:
        """_summary"""
        df = pd.read_csv(filename)
        df = cls._check_structure(df)
        return df

    @abstractmethod
    def __repr__(self) -> str:
        """_summary"""

    @abstractmethod
    def write_df(self, df: pd.DataFrame):
        """_summary"""

    @classmethod
    @abstractmethod
    def get_from_df(
        cls,
        df: pd.DataFrame,
        idx: int = None,
    ) -> list:
        """_summary"""

    @classmethod
    @abstractmethod
    def get_stats(cls, df: pd.DataFrame, year: int = None, gender: str = None):
        """_summary"""

    @abstractmethod
    def remove_from_df(self, df_mov):
        """_summary"""

    @classmethod
    @abstractmethod
    def _check_structure(cls, df: pd.DataFrame) -> pd.DataFrame:
        """_summary"""
        return df
