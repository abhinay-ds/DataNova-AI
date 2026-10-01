import pandas as pd

from app.services.prediction_service import PredictionService


# New/unseen data
new_data = pd.DataFrame({

    "Age": [
        29,
        33,
        42
    ],

    "Experience": [
        5,
        7,
        12
    ]
})


result = PredictionService.predict(
    new_data
)


print("=" * 60)
print("PREDICTION TEST")
print("=" * 60)

print(
    "Success:",
    result.success
)

print(
    "Message:",
    result.message
)

print(
    "Data:",
    result.data
)