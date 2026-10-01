from enum import Enum


class Intent(str, Enum):
    """
    Supported AI intents.
    """

    GENERAL = "GENERAL"

    PROFILE = "PROFILE"

    ANALYSIS = "ANALYSIS"

    VISUALIZATION = "VISUALIZATION"

    ML = "ML"

    SQL = "SQL"

    CODE = "CODE"

    REPORT = "REPORT"

    VISION = "VISION"