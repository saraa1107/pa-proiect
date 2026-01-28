#!/usr/bin/env python3
"""
Curăță forțat toate simbolurile duplicate.
"""

import sqlite3

DB_PATH = "data/aac_database.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("=== CURĂȚARE FORȚATĂ SIMBOLURI DUPLICATE ===\n")
    
    # 1. Vezi totalul simbolurilor
    cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NULL")
    total_before = cur.fetchone()[0]
    print(f"📋 Total simboluri globale înainte: {total_before}")
    
    # 2. Găsește duplicate pentru simboluri globale (name, category_id)
    cur.execute("""
        SELECT name, category_id, GROUP_CONCAT(id) as ids, COUNT(*) as cnt
        FROM symbols
        WHERE child_id IS NULL
        GROUP BY name, category_id
        HAVING COUNT(*) > 1
        ORDER BY name, category_id
    """)
    duplicates = cur.fetchall()
    
    if not duplicates:
        print("✅ Nu există simboluri globale duplicate!")
    else:
        print(f"\n⚠️  Găsite {len(duplicates)} seturi de simboluri globale duplicate:\n")
        
        deleted_count = 0
        for name, cat_id, ids_str, cnt in duplicates:
            ids = [int(x) for x in ids_str.split(',')]
            keep_id = ids[0]
            delete_ids = ids[1:]
            
            print(f"  '{name}' (cat={cat_id}): {cnt}x - IDs: {ids}")
            print(f"    → Păstrăm ID {keep_id}, ștergem {delete_ids}")
            
            # Șterge duplicate
            placeholders = ','.join('?' * len(delete_ids))
            cur.execute(f"DELETE FROM symbols WHERE id IN ({placeholders})", delete_ids)
            deleted_count += len(delete_ids)
        
        conn.commit()
        print(f"\n✅ {deleted_count} simboluri globale duplicate șterse!")
    
    # 3. Găsește duplicate pentru simboluri personalizate (name, category_id, child_id)
    cur.execute("""
        SELECT name, category_id, child_id, GROUP_CONCAT(id) as ids, COUNT(*) as cnt
        FROM symbols
        WHERE child_id IS NOT NULL
        GROUP BY name, category_id, child_id
        HAVING COUNT(*) > 1
        ORDER BY child_id, name
    """)
    child_duplicates = cur.fetchall()
    
    if not child_duplicates:
        print("\n✅ Nu există simboluri personalizate duplicate!")
    else:
        print(f"\n⚠️  Găsite {len(child_duplicates)} seturi de simboluri personalizate duplicate:\n")
        
        deleted_count = 0
        for name, cat_id, child_id, ids_str, cnt in child_duplicates:
            ids = [int(x) for x in ids_str.split(',')]
            keep_id = ids[0]
            delete_ids = ids[1:]
            
            print(f"  '{name}' (cat={cat_id}, child={child_id}): {cnt}x - IDs: {ids}")
            print(f"    → Păstrăm ID {keep_id}, ștergem {delete_ids}")
            
            # Șterge duplicate
            placeholders = ','.join('?' * len(delete_ids))
            cur.execute(f"DELETE FROM symbols WHERE id IN ({placeholders})", delete_ids)
            deleted_count += len(delete_ids)
        
        conn.commit()
        print(f"\n✅ {deleted_count} simboluri personalizate duplicate șterse!")
    
    # 4. Verificare finală
    cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NULL")
    total_after = cur.fetchone()[0]
    print(f"\n📋 Total simboluri globale după: {total_after} (diferență: -{total_before - total_after})")
    
    # Verifică dacă mai sunt duplicate globale
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
    remaining_global = cur.fetchone()[0]
    
    # Verifică dacă mai sunt duplicate personalizate
    cur.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT name, category_id, child_id
            FROM symbols
            WHERE child_id IS NOT NULL
            GROUP BY name, category_id, child_id
            HAVING COUNT(*) > 1
        )
    """)
    remaining_child = cur.fetchone()[0]
    
    if remaining_global > 0 or remaining_child > 0:
        print(f"\n⚠️  Încă există {remaining_global} globale + {remaining_child} personalizate duplicate!")
    else:
        print("\n✅ Nu mai există duplicate!")
    
    conn.close()
    print("\n✅ Curățare completă!")

if __name__ == "__main__":
    main()
