#!/usr/bin/env python3
"""
Șterge simbolurile globale duplicate, păstrând doar primele pentru fiecare (name, category_id).
"""

import sqlite3

DB_PATH = "data/aac_database.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("=== CURĂȚARE SIMBOLURI GLOBALE DUPLICATE ===\n")
    
    # 1. Vezi totalul simbolurilor globale
    cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NULL")
    total_before = cur.fetchone()[0]
    print(f"📋 Total simboluri globale înainte: {total_before}")
    
    # 2. Găsește duplicate (name, category_id, child_id=NULL)
    cur.execute("""
        SELECT name, category_id, COUNT(*) as cnt
        FROM symbols
        WHERE child_id IS NULL
        GROUP BY name, category_id
        HAVING COUNT(*) > 1
    """)
    duplicates = cur.fetchall()
    
    if not duplicates:
        print("✅ Nu există simboluri duplicate!")
        conn.close()
        return
    
    print(f"\n⚠️  Găsite {len(duplicates)} seturi de simboluri duplicate:")
    for name, cat_id, cnt in duplicates[:10]:
        print(f"  {name} (categoria {cat_id}): {cnt}x")
    if len(duplicates) > 10:
        print(f"  ... și încă {len(duplicates) - 10} seturi duplicate")
    
    # 3. Pentru fiecare set de duplicate, păstrează doar primul (ID cel mai mic)
    deleted_count = 0
    
    for name, cat_id, cnt in duplicates:
        # Găsește toate ID-urile pentru acest simbol
        cur.execute("""
            SELECT id FROM symbols
            WHERE name = ? AND category_id = ? AND child_id IS NULL
            ORDER BY id
        """, (name, cat_id))
        ids = [row[0] for row in cur.fetchall()]
        
        # Păstrează primul, șterge restul
        if len(ids) > 1:
            ids_to_delete = ids[1:]
            placeholders = ','.join('?' * len(ids_to_delete))
            cur.execute(f"""
                DELETE FROM symbols WHERE id IN ({placeholders})
            """, ids_to_delete)
            deleted_count += len(ids_to_delete)
    
    conn.commit()
    print(f"\n✅ {deleted_count} simboluri duplicate șterse!")
    
    # 4. Verificare finală
    cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NULL")
    total_after = cur.fetchone()[0]
    print(f"\n📋 Total simboluri globale după curățare: {total_after}")
    print(f"   Diferență: -{total_before - total_after}")
    
    # Verifică dacă mai sunt duplicate
    cur.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT name, category_id
            FROM symbols
            WHERE child_id IS NULL
            GROUP BY name, category_id
            HAVING COUNT(*) > 1
        )
    """)
    remaining = cur.fetchone()[0]
    
    if remaining > 0:
        print(f"\n⚠️  Încă există {remaining} seturi de duplicate!")
    else:
        print("\n✅ Nu mai există duplicate!")
    
    conn.close()
    print("\n✅ Curățare completă!")

if __name__ == "__main__":
    main()
