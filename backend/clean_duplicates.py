"""Script pentru curățarea duplicatelor din baza de date"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "aac_database.db")

if not os.path.exists(DB_PATH):
    print(f"Baza de date nu există: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== CURĂȚARE DUPLICATE ===\n")

# Găsește duplicate în simboluri
print("Căutăm duplicate în simboluri...")
cur.execute("""
    SELECT name, category_id, child_id, COUNT(*) as count, GROUP_CONCAT(id) as ids
    FROM symbols
    GROUP BY name, category_id, child_id
    HAVING count > 1
    ORDER BY count DESC
""")

duplicates = cur.fetchall()

if not duplicates:
    print("✓ Nu există duplicate în simboluri!")
else:
    print(f"Găsite {len(duplicates)} grupuri de duplicate:\n")
    
    total_deleted = 0
    for name, cat_id, child_id, count, ids in duplicates:
        ids_list = [int(x) for x in ids.split(',')]
        print(f"Duplicate: '{name}' (category={cat_id}, child={child_id})")
        print(f"  IDs: {ids_list} - păstrăm primul ({ids_list[0]}), ștergem restul")
        
        # Șterge toate în afară de primul
        for duplicate_id in ids_list[1:]:
            cur.execute("DELETE FROM symbols WHERE id = ?", (duplicate_id,))
            total_deleted += 1
            print(f"    ✓ Șters ID {duplicate_id}")
    
    conn.commit()
    print(f"\n✓ Șterse {total_deleted} duplicate!")

# Verifică duplicate în categorii
print("\n\nCăutăm duplicate în categorii...")
cur.execute("""
    SELECT name, child_id, COUNT(*) as count, GROUP_CONCAT(id) as ids
    FROM categories
    GROUP BY name, child_id
    HAVING count > 1
    ORDER BY count DESC
""")

cat_duplicates = cur.fetchall()

if not cat_duplicates:
    print("✓ Nu există duplicate în categorii!")
else:
    print(f"Găsite {len(cat_duplicates)} grupuri de duplicate în categorii:\n")
    
    total_cat_deleted = 0
    for name, child_id, count, ids in cat_duplicates:
        ids_list = [int(x) for x in ids.split(',')]
        print(f"Duplicate: '{name}' (child={child_id})")
        print(f"  IDs: {ids_list} - păstrăm primul ({ids_list[0]}), ștergem restul")
        
        # Șterge toate în afară de primul
        for duplicate_id in ids_list[1:]:
            cur.execute("DELETE FROM categories WHERE id = ?", (duplicate_id,))
            total_cat_deleted += 1
            print(f"    ✓ Șters ID {duplicate_id}")
    
    conn.commit()
    print(f"\n✓ Șterse {total_cat_deleted} categorii duplicate!")

conn.close()
print("\n✅ Curățare completă!")
