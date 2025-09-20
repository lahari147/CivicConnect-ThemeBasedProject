import psycopg2
from datetime import datetime, timedelta
import random

# Database connection details
DB_NAME = "civicconnect_db"
DB_USER = "postgres"
DB_PASSWORD = "555666"
DB_HOST = "localhost"
DB_PORT = "5432"

# Define urgency weights
URGENCY_WEIGHT = {
    "Fire": 2.0,
    "Gas": 2.0,
    "Collapsed": 1.8,
    "Manhole": 1.5,
    "Traffic": 1.5,
    "Water": 1.2,
    "Pothole": 1.1,
}

# Connect to PostgreSQL
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cursor = conn.cursor()

# Fetch a valid user_id, username, and email from auth_user
cursor.execute("SELECT id, username, email FROM auth_user ORDER BY RANDOM() LIMIT 1;")
user_data = cursor.fetchone()

if not user_data:
    print("❌ No users found in auth_user! Please create at least one user.")
    conn.close()
    exit()

user_id, username, email = user_data

# Sample issues
REAL_ISSUES = [
    ("Large pothole causing accidents near school zone", "Main Road, Sector 15", 28.6139, 77.2090, 5, 10),
    ("Streetlights not working, making area unsafe at night", "Green Park, Lane 4", 28.5675, 77.2231, 4, 8),
    ("Garbage overflowing for 3 days, foul smell in the area", "Market Street", 28.6353, 77.2250, 3, 6),
    ("Broken traffic signal causing traffic congestion", "Junction near Mall", 28.6206, 77.2322, 5, 10),
    ("Water leakage from underground pipes leading to water wastage", "ABC Colony", 28.6545, 77.1951, 4, 8),
    ("Open manhole posing danger to pedestrians", "Near Railway Station", 28.6222, 77.2022, 5, 10),
    ("Fire hazard due to exposed electrical wires", "Apartment Complex Block A", 28.6100, 77.2000, 5, 10),
    ("Illegal dumping of waste in residential area", "Sector 8", 28.6089, 77.2123, 3, 6),
    ("Sewage water overflowing onto main road", "XYZ Nagar", 28.5901, 77.1804, 5, 10),
    ("Traffic congestion due to unauthorized street vendors", "Bazaar Road", 28.5789, 77.1675, 4, 8),
    ("Collapsed footpath creating hazard for pedestrians", "Downtown Street", 28.6265, 77.2032, 4, 8),
    ("Tree branches obstructing road visibility", "Maple Avenue", 28.6112, 77.2203, 3, 6),
    ("Frequent power outages affecting businesses", "City Square", 28.6405, 77.1998, 4, 8),
    ("Improper drainage causing road flooding", "Palm Street", 28.6214, 77.1756, 5, 10),
    ("Illegal construction blocking public pathways", "Sector 12", 28.6058, 77.2145, 3, 6),
    ("Unhygienic conditions in public market area", "Central Bazaar", 28.6319, 77.1982, 3, 6),
    ("Defective pedestrian crossing signals", "School Road", 28.6184, 77.2056, 4, 8),
    ("Overgrown vegetation obstructing sidewalks", "Greenway Boulevard", 28.6291, 77.2114, 3, 6),
    ("Inoperative escalators at metro stations", "Metro Station Central", 28.6201, 77.2237, 2, 4),
    ("Street flooding due to blocked storm drains", "Oakwood Street", 28.6127, 77.2275, 5, 10),
    ("Abandoned buildings attracting illegal activities", "Old Town", 28.6324, 77.1849, 5, 10),
    ("Excessive noise pollution from nightclubs", "Entertainment District", 28.6007, 77.1923, 3, 6),
    ("Lack of proper street signage causing confusion", "West End Avenue", 28.6382, 77.2028, 3, 6),
    ("Highway barriers missing, increasing accident risk", "Expressway 22", 28.6510, 77.1772, 5, 10),
    ("Public park benches broken and unusable", "Sunset Park", 28.6192, 77.2187, 2, 4),
    ("Noise pollution from overnight construction work", "Downtown Core", 28.6015, 77.2045, 2, 4),
    ("Heavy truck traffic in residential areas", "Oakridge Avenue", 28.6243, 77.2099, 3, 6),
    ("Deep potholes on highways leading to vehicle damage", "Highway 9", 28.6452, 77.2153, 4, 8),
    ("Lack of wheelchair ramps in public buildings", "City Hall", 28.6295, 77.1961, 2, 4),
    ("Flooded subway station entrance after heavy rain", "Central Station", 28.6135, 77.2162, 4, 8),
    ("Leaking gas pipeline posing explosion risk", "Industrial Zone", 28.6598, 77.2254, 5, 10),
    ("Vandalized bus stop shelters leaving commuters stranded", "Main Bus Terminal", 28.6171, 77.2106, 2, 4),
    ("Uncollected garbage leading to rodent infestation", "Residential Block C", 28.6056, 77.2038, 3, 6),
    ("Damaged pedestrian bridge making crossings unsafe", "River Walk", 28.6208, 77.2157, 4, 8),
    ("Illegal parking blocking emergency vehicle access", "Hospital Road", 28.6129, 77.1986, 4, 8),
    ("Bicycle lanes blocked by parked cars", "Elm Street", 28.6093, 77.2101, 2, 4),
    ("Fire emergency in a commercial building", "Business District", 28.6217, 77.2290, 5, 10),
    ("Water supply disruption in multiple residential areas", "Suburban Area", 28.6349, 77.2003, 3, 6),
    ("Fallen electric pole blocking main road", "Sunset Boulevard", 28.6187, 77.2178, 4, 8),
    ("Traffic congestion due to poor road infrastructure planning", "City Expressway", 28.6262, 77.2225, 3, 6),
]


# Insert issues
for issue in REAL_ISSUES:
    description, location_name, latitude, longitude, severity, priority = issue
    created_at = datetime.now() - timedelta(days=random.randint(1, 30))
    report_count = random.randint(1, 20)

    # Extract issue type from description (first few words as title)
    title = description.split(",")[0][:50]  # Ensure it's not too long

    # Determine urgency factor
    urgency_factor = URGENCY_WEIGHT.get(description.split()[0], 1.0)  # Default to 1.0 if not found

    # Calculate priority_score
    priority_score = (0.6 * severity + 0.4 * report_count) * urgency_factor

    try:
        cursor.execute(
            """
            INSERT INTO reports_issue 
            (user_id, username, email, description, location_name, latitude, longitude, created_at, report_count, severity, priority_score, priority, status, title)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending', %s)
            ON CONFLICT (description, latitude, longitude) DO NOTHING
            """,
            (user_id, username, email, description, location_name, latitude, longitude, created_at, report_count, severity, priority_score, priority, title)
        )
        conn.commit()  # ✅ Commit after each successful insert

    except psycopg2.Error as e:
        conn.rollback()  # ❌ Rollback failed transaction
        print(f"⚠️ Error inserting record: {e}")

# Close the connection
cursor.close()
conn.close()
print("✅ Successfully inserted civic reports into reports_issue, skipping duplicates!")
