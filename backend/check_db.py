import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agentshield.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Database tables:")
for table in tables:
    print(f"  - {table[0]}")

# Check data in each table
print("\nData counts:")
for table_name in [t[0] for t in tables]:
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"  - {table_name}: {count} records")

conn.close()
print("\nDatabase check complete!")
