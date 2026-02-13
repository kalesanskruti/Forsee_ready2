
import sqlite3
import os

db_path = "forsee.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT email, role FROM user")
    users = cursor.fetchall()
    print("--- User Roles ---")
    for email, role in users:
        print(f"Email: {email}, Role: {role}")
    conn.close()
else:
    print(f"❌ Database not found at {db_path}")
