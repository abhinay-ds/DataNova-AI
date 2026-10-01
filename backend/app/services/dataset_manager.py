import pandas as pd


class DatasetManager:
    """
    Stores uploaded datasets in memory.

    Later this can be replaced with
    Redis / PostgreSQL / Workspace storage.
    """

    _datasets = {}

    @classmethod
    def save(
        cls,
        session_id: str,
        dataframe: pd.DataFrame,
        filename: str,
    ):

        cls._datasets[session_id] = {
            "filename": filename,
            "dataframe": dataframe,
        }

    @classmethod
    def get(
        cls,
        session_id: str,
    ):

        return cls._datasets.get(session_id)

    @classmethod
    def remove(
        cls,
        session_id: str,
    ):

        cls._datasets.pop(session_id, None)

    @classmethod
    def list_sessions(cls):

        return list(cls._datasets.keys())