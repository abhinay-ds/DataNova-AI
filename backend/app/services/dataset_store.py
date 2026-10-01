import pandas as pd


_dataset: pd.DataFrame | None = None


def set_dataset(df: pd.DataFrame):

    global _dataset

    _dataset = df


def get_dataset():

    return _dataset


def clear_dataset():

    global _dataset

    _dataset = None


def has_dataset():

    return _dataset is not None