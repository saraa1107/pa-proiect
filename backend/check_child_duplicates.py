"""Check for duplicate symbols in child view"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "aac_database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Găsește toate child_id-urile
cur.execute("SELECT DISTINCT id, name FROM children")
children = cur.fetchall()

print("=== VERIFICARE DUPLICATE ÎN CHILD GRID ===\n")

for child_id, child_name in children:
    print(f"\n📋 Copil: {child_name} (ID: {child_id})")
    
    # Găsește duplicate vizuale (același nume+categorie pentru copil sau global)
    cur.execute("""
        SELECT s.name, s.category_id, COUNT(*) as cnt, GROUP_CONCAT(s.id) as ids, 
               GROUP_CONCAT(CASE WHEN s.child_id IS NULL THEN 'global' ELSE 'copil' END) as types
        FROM symbols s
        WHERE (s.child_id = ? OR s.child_id IS NULL)
        GROUP BY s.name, s.category_id
        HAVING cnt > 1
    """, (child_id,))
    
    duplicates = cur.fetchall()
    
    if not duplicates:
        print("  ✓ Nu există duplicate vizuale!")
    else:
        print(f"  ✗ Găsite {len(duplicates)} grupuri de duplicate vizuale:")
        for name, cat_id, cnt, ids, types in duplicates[:10]:
            print(f"    '{name}' (cat={cat_id}): {cnt}x - IDs: {ids} - Tipuri: {types}")

conn.close()
print("\n✅ Verificare completă!")
