import sqlite3
conn = sqlite3.connect('aac_communication.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")
conn.close()
