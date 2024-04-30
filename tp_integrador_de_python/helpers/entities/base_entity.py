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
        #  Este método recibe el dataframe de películas y agrega la película
        #  Si el id es None, toma el id más alto del DF y le suma uno. Si el
        #  id ya existe, no la agrega y devuelve un error.

    @classmethod
    def create_df_from_csv(cls, filename: str) -> pd.DataFrame:
        """_summary"""
        df = pd.read_csv(filename)
        cls._check_structure(df)
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
        # Este class method devuelve una lista de objetos 'Pelicula' buscando por:
        # id: id
        # nombre: nombre de la película
        # anios: [desde_año, hasta_año]
        # generos: [generos]

    @classmethod
    def get_stats(cls, df: pd.DataFrame, year: int = None, gender: str = None):
        """_summary"""
        # Este class method imprime una serie de estadísticas calculadas sobre
        # los resultados de una consulta al DataFrame df_mov.
        # Las estadísticas se realizarán sobre las filas que cumplan con los requisitos de:
        # anios: [desde_año, hasta_año]
        # generos: [generos]
        # Las estadísticas son:
        # - Datos película más vieja
        # - Datos película más nueva
        # - Bar plots con la cantidad de películas por año/género.

    def remove_from_df(self, df_mov):
        """_summary"""
        # Borra del DataFrame el objeto contenido en esta clase.
        # Para realizar el borrado todas las propiedades del objeto deben coincidir
        # con la entrada en el DF. Caso contrario imprime un error.

    @classmethod
    @abstractmethod
    def _check_structure(cls, df: pd.DataFrame) -> pd.DataFrame:
        """_summary"""
        return df
