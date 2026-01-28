#!/usr/bin/env python3
"""
Analiză detaliată a duplicatelor în baza de date.
"""

import sqlite3

DB_PATH = "data/aac_database.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("=== ANALIZĂ DUPLICATE SIMBOLURI ===\n")
    
    # Verifică duplicate după (name, category_id) pentru simboluri globale
    cur.execute("""
        SELECT name, category_id, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
        FROM symbols
        WHERE child_id IS NULL
        GROUP BY name, category_id
        ORDER BY cnt DESC, name
    """)
    
    results = cur.fetchall()
    
    print(f"Total grupuri de simboluri globale unice: {len(results)}")
    
    duplicates = [r for r in results if r[2] > 1]
    
    if duplicates:
        print(f"Găsite {len(duplicates)} grupuri de duplicate:\n")
        for name, cat_id, cnt, ids in duplicates[:30]:
            print(f"  '{name}' (categoria {cat_id}): {cnt}x - IDs: {ids}")
    else:
        print("✅ Nu există duplicate!\n")
    
    # Verifică și după name doar
    print("\n--- Analiză după nume (ignorând categoria) ---\n")
    cur.execute("""
        SELECT name, COUNT(*) as cnt, COUNT(DISTINCT category_id) as cats
        FROM symbols
        WHERE child_id IS NULL
        GROUP BY name
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
        LIMIT 30
    """)
    
    name_duplicates = cur.fetchall()
    if name_duplicates:
        print(f"Găsite {len(name_duplicates)} nume care apar de mai multe ori (poate în categorii diferite):\n")
        for name, cnt, cats in name_duplicates:
            print(f"  '{name}': {cnt}x în {cats} categorii diferite")
            
            # Vezi detalii
            cur.execute("""
                SELECT id, category_id, child_id FROM symbols
                WHERE name = ? AND child_id IS NULL
                ORDER BY category_id
            """, (name,))
            details = cur.fetchall()
            for sid, cid, chid in details:
                print(f"    - ID {sid}: categoria {cid}")
    
    conn.close()

if __name__ == "__main__":
    main()
