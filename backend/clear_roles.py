
import sqlite3
import os

db_path = "forsee.db" # Standard path in root

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET role = NULL")
    conn.commit()
    print(f"✅ Cleared roles for {cursor.rowcount} users in {db_path}")
    conn.close()
else:
    print(f"❌ Database not found at {db_path}")
