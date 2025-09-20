import psycopg2
import pandas as pd

# ----------------------
# Database Configuration
# ----------------------
DB_NAME = "civicconnect_db"
DB_USER = "postgres"
DB_PASSWORD = "555666"
DB_HOST = "localhost"
DB_PORT = "5432"

# ----------------------
# Load Prioritized Data
# ----------------------
df = pd.read_csv("civicconnect_ai/prioritized_issues.csv")

# Optional: Round the score for consistency
df["Priority_Score"] = df["Priority_Score"].round(2)

# ----------------------
# Connect to PostgreSQL
# ----------------------
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# ----------------------
# Update Each Record
# ----------------------
for index, row in df.iterrows():
    try:
        cursor.execute("""
            UPDATE reports_issue
            SET priority_score = %s
            WHERE id = %s;
        """, (row["Priority_Score"], row["id"]))
    except Exception as e:
        print(f"❌ Failed to update issue ID {row['id']}: {e}")

# ----------------------
# Finalize
# ----------------------
conn.commit()
cursor.close()
conn.close()

print("✅ Database updated with priority scores!")
