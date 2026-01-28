"""Script pentru verificarea simbolurilor legate de frică/teamă"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "aac_database.db")

if not os.path.exists(DB_PATH):
    print(f"Baza de date nu există: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== SIMBOLURI LEGATE DE FRICĂ/TEAMĂ ===\n")

# Caută simboluri care conțin cuvinte legate de frică
keywords = ['fric', 'team', 'sperie', 'înfricoșat', 'înfricoșător', 'groaz']

for keyword in keywords:
    cur.execute("""
        SELECT id, name, text, category_id, child_id 
        FROM symbols 
        WHERE LOWER(name) LIKE ? OR LOWER(text) LIKE ?
        ORDER BY id
    """, (f'%{keyword}%', f'%{keyword}%'))
    
    results = cur.fetchall()
    if results:
        print(f"\n--- Simboluri cu '{keyword}' ---")
        for s_id, name, text, cat_id, child_id in results:
            print(f"  ID {s_id}: {name} ({text}) - cat={cat_id}, child={child_id}")

# Verifică categoria "Emoții"
cur.execute("""
    SELECT s.id, s.name, s.text, c.name as category_name
    FROM symbols s
    JOIN categories c ON s.category_id = c.id
    WHERE LOWER(c.name) LIKE '%emo%' OR LOWER(c.name) LIKE '%sentiment%'
    ORDER BY s.name
""")

emotions = cur.fetchall()
if emotions:
    print(f"\n\n=== SIMBOLURI DIN CATEGORIA EMOȚII ===")
    for s_id, name, text, cat_name in emotions:
        print(f"  ID {s_id}: {name} ({text}) - {cat_name}")

conn.close()
print("\n✓ Verificare completă")
