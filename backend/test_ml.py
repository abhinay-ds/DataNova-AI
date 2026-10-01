import pandas as pd

from app.services.ml_service import MLService


df = pd.DataFrame({

    "Age": [
        21, 25, 30, 35, 40,
        45, 50, 28, 32, 38
    ],

    "Experience": [
        1, 3, 5, 8, 10,
        15, 20, 4, 6, 9
    ],

    "Salary": [
        30000, 35000, 42000, 50000, 58000,
        70000, 85000, 39000, 45000, 54000
    ]

})


result = MLService.train(
    df=df,
    target="Salary"
)


print("=" * 60)
print("ML TRAINING TEST")
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