import pandas as pd

df = pd.read_csv("issues_dataset.csv")  # Correct filename

expected_columns = ["description", "severity"]  # Ensure correct columns

for col in expected_columns:
    if col not in df.columns:
        print(f"Missing column: {col}")
    else:
        print(f"Column {col} exists")
