"""Script pentru verificarea simbolurilor din baza de date"""
import sqlite3
import os

# Path absolut către baza de date
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "aac_database.db")

if not os.path.exists(DB_PATH):
    print(f"Baza de date nu există: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== SIMBOLURI DIN BAZA DE DATE ===\n")

# Toate simbolurile
cur.execute("SELECT id, name, category_id, child_id FROM symbols ORDER BY category_id, id")
symbols = cur.fetchall()

print(f"Total simboluri: {len(symbols)}\n")

# Grupează după (name, category_id, child_id) pentru a găsi duplicatele
from collections import defaultdict
groups = defaultdict(list)

for s_id, name, cat_id, child_id in symbols:
    key = (name, cat_id, child_id)
    groups[key].append(s_id)

# Afișează duplicatele
print("=== DUPLICATES ===\n")
for key, ids in groups.items():
    if len(ids) > 1:
        name, cat_id, child_id = key
        print(f"Duplicate: {name} (category_id={cat_id}, child_id={child_id})")
        print(f"  IDs: {ids}")

print("\n=== TOATE SIMBOLURILE ===\n")
for s_id, name, cat_id, child_id in symbols:
    print(f"ID {s_id}: {name} (cat={cat_id}, child={child_id})")

conn.close()
