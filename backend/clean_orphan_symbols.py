#!/usr/bin/env python3
"""
Șterge simbolurile orfane care aparțin categoriilor inexistente.
"""

import sqlite3

DB_PATH = "data/aac_database.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("=== CURĂȚARE SIMBOLURI ORFANE ===\n")
    
    # Găsește simbolurile care au category_id către categorii inexistente
    cur.execute("""
        SELECT s.id, s.name, s.category_id
        FROM symbols s
        LEFT JOIN categories c ON s.category_id = c.id
        WHERE c.id IS NULL
        ORDER BY s.category_id, s.name
    """)
    
    orphans = cur.fetchall()
    
    if not orphans:
        print("✅ Nu există simboluri orfane!")
        conn.close()
        return
    
    print(f"⚠️  Găsite {len(orphans)} simboluri orfane (cu categorii inexistente):\n")
    
    # Grupează după category_id
    by_cat = {}
    for sid, name, cat_id in orphans:
        if cat_id not in by_cat:
            by_cat[cat_id] = []
        by_cat[cat_id].append((sid, name))
    
    for cat_id in sorted(by_cat.keys()):
        symbols = by_cat[cat_id]
        print(f"  Categoria inexistentă {cat_id}: {len(symbols)} simboluri")
        for sid, name in symbols[:5]:
            print(f"    - ID {sid}: {name}")
        if len(symbols) > 5:
            print(f"    ... și încă {len(symbols) - 5} simboluri")
    
    # Șterge toate simbolurile orfane
    orphan_ids = [oid for oid, _, _ in orphans]
    placeholders = ','.join('?' * len(orphan_ids))
    
    cur.execute(f"DELETE FROM symbols WHERE id IN ({placeholders})", orphan_ids)
    conn.commit()
    
    print(f"\n✅ Șterse {len(orphan_ids)} simboluri orfane!")
    
    # Verificare finală
    cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NULL")
    total_global = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NOT NULL")
    total_child = cur.fetchone()[0]
    
    print(f"\n📋 Total final:")
    print(f"   - Simboluri globale: {total_global}")
    print(f"   - Simboluri personalizate: {total_child}")
    print(f"   - TOTAL: {total_global + total_child}")
    
    conn.close()
    print("\n✅ Curățare completă!")

if __name__ == "__main__":
    main()
