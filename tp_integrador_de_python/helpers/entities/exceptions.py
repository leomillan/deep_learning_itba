"""Exceptions for entities classes"""


class MissingColumnsError(Exception):
    """Raises when a dataframe is missing one or more columns"""


class AssignIDError(Exception):
    """Raises when an entity instance has an already assigned id"""


class MissingMovieError(Exception):
    """Raises when the movie doesn't exist in the dataframe"""


class MissingPersonError(Exception):
    """Raises when the person doesn't exist in the dataframe"""


class MissingWorkerError(Exception):
    """Raises when the worker doesn't exist in the dataframe"""


class MissingScoreError(Exception):
    """Raises when the score doesn't exist in the dataframe"""


class MissingUserError(Exception):
    """Raises when the user doesn't exist in the dataframe"""
