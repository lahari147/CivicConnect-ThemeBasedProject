import psycopg2
import pandas as pd

# Database connection details
DB_NAME = "civicconnect_db"
DB_USER = "postgres"
DB_PASSWORD = "555666"
DB_HOST = "localhost"
DB_PORT = "5432"

# Connect to PostgreSQL
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cursor = conn.cursor()

# ✅ Fetch data using correct column names
query = "SELECT description, severity FROM reports_issue;"
df = pd.read_sql(query, conn)

# Close connection
cursor.close()
conn.close()

# 🛑 Remove empty rows
df = df.dropna()

# Save fetched data to CSV
df.to_csv("issues_dataset.csv", index=False) 
print(f"✅ Data fetched ({len(df)} records) and saved to issues_dataset.csv")
