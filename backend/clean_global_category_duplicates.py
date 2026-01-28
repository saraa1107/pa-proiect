#!/usr/bin/env python3
"""
Șterge categoriile globale duplicate, păstrând doar primele 6 originale.
"""

import sqlite3

DB_PATH = "data/aac_database.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("=== CURĂȚARE CATEGORII GLOBALE DUPLICATE ===\n")
    
    # 1. Vezi toate categoriile globale
    print("📋 Categorii globale înainte de curățare:")
    cur.execute("""
        SELECT id, name, child_id
        FROM categories
        WHERE child_id IS NULL
        ORDER BY id
    """)
    global_cats = cur.fetchall()
    
    print(f"Total: {len(global_cats)} categorii globale")
    for cat_id, name, child_id in global_cats:
        print(f"  ID: {cat_id}, Name: {name}")
    
    # 2. Identifică categoriile originale (primele 6 cu ID-urile cele mai mici)
    expected_categories = ["Acțiuni", "Alimente", "Emoții", "Persoane", "Locații", "Obiecte"]
    original_ids = {}
    
    for cat_name in expected_categories:
        cur.execute("""
            SELECT id FROM categories
            WHERE name = ? AND child_id IS NULL
            ORDER BY id
            LIMIT 1
        """, (cat_name,))
        result = cur.fetchone()
        if result:
            original_ids[cat_name] = result[0]
    
    print(f"\n📋 Categorii originale identificate:")
    for name, cat_id in original_ids.items():
        print(f"  {name}: ID {cat_id}")
    
    # 3. Găsește categoriile duplicate care trebuie șterse
    ids_to_keep = list(original_ids.values())
    cur.execute(f"""
        SELECT id, name FROM categories
        WHERE child_id IS NULL AND id NOT IN ({','.join('?' * len(ids_to_keep))})
    """, ids_to_keep)
    duplicates = cur.fetchall()
    
    if not duplicates:
        print("\n✅ Nu există categorii duplicate de șters!")
        conn.close()
        return
    
    print(f"\n⚠️  Categorii duplicate de șters: {len(duplicates)}")
    for cat_id, name in duplicates:
        print(f"  ID: {cat_id}, Name: {name}")
    
    # 4. Verifică dacă există simboluri legate de categoriile duplicate
    duplicate_ids = [d[0] for d in duplicates]
    placeholders = ','.join('?' * len(duplicate_ids))
    cur.execute(f"""
        SELECT COUNT(*) FROM symbols
        WHERE category_id IN ({placeholders}) AND child_id IS NULL
    """, duplicate_ids)
    symbol_count = cur.fetchone()[0]
    
    if symbol_count > 0:
        print(f"\n⚠️  ATENȚIE: {symbol_count} simboluri globale sunt legate de categoriile duplicate!")
        print("  Aceste simboluri vor fi reatribuite către categoriile originale.")
        
        # Reatribuie simbolurile către categoriile originale
        for dup_id, dup_name in duplicates:
            if dup_name in original_ids:
                original_id = original_ids[dup_name]
                cur.execute("""
                    UPDATE symbols
                    SET category_id = ?
                    WHERE category_id = ? AND child_id IS NULL
                """, (original_id, dup_id))
                print(f"  ✓ Simboluri mutate de la categoria {dup_id} ({dup_name}) → {original_id}")
    
    # 5. Șterge categoriile duplicate
    cur.execute(f"""
        DELETE FROM categories
        WHERE id IN ({placeholders})
    """, duplicate_ids)
    
    conn.commit()
    print(f"\n✅ {len(duplicates)} categorii duplicate șterse!")
    
    # 6. Verificare finală
    print("\n📋 Categorii globale după curățare:")
    cur.execute("""
        SELECT id, name, child_id
        FROM categories
        WHERE child_id IS NULL
        ORDER BY id
    """)
    final_cats = cur.fetchall()
    
    print(f"Total: {len(final_cats)} categorii globale")
    for cat_id, name, child_id in final_cats:
        print(f"  ID: {cat_id}, Name: {name}")
    
    # Verifică simbolurile
    cur.execute("""
        SELECT COUNT(*) FROM symbols WHERE child_id IS NULL
    """)
    symbol_count = cur.fetchone()[0]
    print(f"\n✅ Total simboluri globale: {symbol_count}")
    
    conn.close()
    print("\n✅ Curățare completă!")

if __name__ == "__main__":
    main()
