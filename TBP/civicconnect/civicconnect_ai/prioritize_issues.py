import psycopg2
import pandas as pd
from collections import Counter
import joblib

# ----------------------
# Database Configuration
# ----------------------
DB_NAME = "civicconnect_db"
DB_USER = "postgres"
DB_PASSWORD = "555666"
DB_HOST = "localhost"
DB_PORT = "5432"

# ----------------------
# Load AI Model & Vectorizer
# ----------------------
severity_model = joblib.load("civicconnect_ai/ai_severity_model.pkl")
vectorizer = joblib.load("civicconnect_ai/tfidf_vectorizer.pkl")

# ----------------------
# Connect to PostgreSQL and Fetch Issues
# ----------------------
conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
    host=DB_HOST, port=DB_PORT
)
cursor = conn.cursor()

query = """
SELECT id, description, location_name, latitude, longitude, created_at, user_id
FROM reports_issue;
"""
df = pd.read_sql(query, conn)

cursor.close()
conn.close()

# ----------------------
# Calculate Priority Function
# ----------------------
def calculate_priority(df):
    # Count how many reports in the same coordinates
    area_counts = Counter(zip(df["latitude"], df["longitude"]))
    df["Repeated_Reports"] = df.apply(
        lambda row: area_counts[(row["latitude"], row["longitude"])], axis=1
    )

    # Predict severity from description
    X_text = df["description"].fillna("")
    X_vectorized = vectorizer.transform(X_text)
    df["Severity_Score"] = severity_model.predict(X_vectorized)

    # Add location-based weight (critical areas get higher score)
    df["Location_Weight"] = df["location_name"].apply(
        lambda loc: 1.5 if any(word in loc.lower() for word in ["hospital", "school", "junction", "main road", "market"]) else 1
    )

    # Combine everything into final score
    df["Priority_Score"] = (
        df["Severity_Score"] * 0.6 +          # AI severity has more weight
        df["Repeated_Reports"] * 0.3 +        # Repeat boosts priority
        df["Location_Weight"] * 0.1           # Important area boost
    )

    return df.sort_values(by="Priority_Score", ascending=False)

# ----------------------
# Run Prioritization and Save
# ----------------------
df_prioritized = calculate_priority(df)
df_prioritized.to_csv("civicconnect_ai/prioritized_issues.csv", index=False)

print("✅ Issues prioritized and saved to 'civicconnect_ai/prioritized_issues.csv'")
