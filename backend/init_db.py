import sqlite3
import os

print("📂 Current working directory:", os.getcwd())

try:
    with open("schema.sql", "r") as f:
        schema = f.read()
    print("✅ schema.sql read successfully")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ database.db created successfully.")
except Exception as e:
    print("❌ Error occurred:", e)
