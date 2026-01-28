import sqlite3

DB_PATH = "data/aac_database.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== ȘTERGERE SIMBOLURI GLOBALE ===\n")

# Numără simbolurile globale
cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NULL")
count_before = cur.fetchone()[0]
print(f"Simboluri globale înainte: {count_before}")

# Șterge toate simbolurile globale
cur.execute("DELETE FROM symbols WHERE child_id IS NULL")
conn.commit()

cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NULL")
count_after = cur.fetchone()[0]
print(f"Simboluri globale după: {count_after}")
print(f"\n✅ {count_before} simboluri șterse!")

conn.close()
