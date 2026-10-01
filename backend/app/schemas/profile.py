class DatasetOverview(BaseModel):
    rows: int
    columns: int
    memory_usage_mb: float
    numeric_columns: int
    categorical_columns: int
    datetime_columns: int
    boolean_columns: int

class DataQuality(BaseModel):
    score: float
    missing_percentage: float
    duplicate_rows: int
    constant_columns: list[str]
    high_cardinality_columns: list[str]

class ProfileResponse(BaseModel):
    overview: DatasetOverview
    quality: DataQuality
    statistics: dict
    missing_values: list
    correlations: dict
    outliers: dict
    target_detection: dict
    recommendations: list[str]