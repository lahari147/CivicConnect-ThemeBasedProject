import pandas as pd

df = pd.read_csv("issues_dataset.csv")

# Check for missing values
print("Missing values:\n", df.isnull().sum())

# Check dataset shape
print("Dataset shape:", df.shape)

# Display first few rows
print(df.head())
