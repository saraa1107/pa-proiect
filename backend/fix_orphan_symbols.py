#!/usr/bin/env python3
"""
Repară simbolurile orfane - le mută către categoriile corecte în loc să le șteargă.
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "aac_database.db")

# Mapare categorii șterse -> categorii valide (bazat pe ID-uri văzute)
CATEGORY_MAPPING = {
    # Categorii duplicate șterse care trebuie mapate înapoi
    446: 1,  # Acțiuni
    447: 2,  # Alimente
    448: 3,  # Emoții
    449: 4,  # Persoane
    450: 5,  # Locații
    451: 6,  # Obiecte
    452: 1,  # Acțiuni (al 2-lea duplicat)
    453: 2,  # Alimente
    454: 3,  # Emoții
    455: 4,  # Persoane
    456: 5,  # Locații
    457: 6,  # Obiecte
}

if not os.path.exists(DB_PATH):
    print(f"Baza de date nu există: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== REPARARE SIMBOLURI ORFANE ===\n")

# 1. Găsește toate categoriile valide
cur.execute("SELECT id, name FROM categories WHERE child_id IS NULL ORDER BY id")
valid_cats = cur.fetchall()
print(f"📋 Categorii valide globale:")
for cat_id, name in valid_cats:
    print(f"   {cat_id}: {name}")

# 2. Găsește simbolurile orfane
cur.execute("""
    SELECT s.id, s.name, s.category_id
    FROM symbols s
    LEFT JOIN categories c ON s.category_id = c.id
    WHERE c.id IS NULL
    ORDER BY s.category_id, s.name
""")

orphan_symbols = cur.fetchall()

if not orphan_symbols:
    print("\n✅ Nu există simboluri orfane!")
    conn.close()
    exit(0)

print(f"\n⚠️  Găsite {len(orphan_symbols)} simboluri orfane")

# 3. Grupează după category_id vechi
by_old_cat = {}
for sid, name, old_cat_id in orphan_symbols:
    if old_cat_id not in by_old_cat:
        by_old_cat[old_cat_id] = []
    by_old_cat[old_cat_id].append((sid, name))

print("\n📋 Simboluri orfane grupate pe categorii șterse:")
for old_cat_id in sorted(by_old_cat.keys()):
    symbols = by_old_cat[old_cat_id]
    new_cat_id = CATEGORY_MAPPING.get(old_cat_id)
    print(f"\n   Categoria {old_cat_id} -> {new_cat_id}: {len(symbols)} simboluri")
    for sid, name in symbols[:3]:
        print(f"      - {name}")
    if len(symbols) > 3:
        print(f"      ... și încă {len(symbols) - 3}")

# 4. Migrează simbolurile către categoriile corecte
print("\n🔧 Migrare simboluri...")
migrated = 0

for old_cat_id, symbols in by_old_cat.items():
    new_cat_id = CATEGORY_MAPPING.get(old_cat_id)
    
    if not new_cat_id:
        print(f"\n⚠️  Nu știu unde să mut categoria {old_cat_id} - SKIP!")
        continue
    
    symbol_ids = [sid for sid, _ in symbols]
    placeholders = ','.join('?' * len(symbol_ids))
    
    cur.execute(f"""
        UPDATE symbols 
        SET category_id = ?
        WHERE id IN ({placeholders})
    """, [new_cat_id] + symbol_ids)
    
    migrated += len(symbol_ids)
    print(f"   ✓ Mutate {len(symbol_ids)} simboluri din categoria {old_cat_id} -> {new_cat_id}")

conn.commit()

print(f"\n✅ Migrate {migrated} simboluri!")

# 5. Verificare finală
cur.execute("""
    SELECT COUNT(*)
    FROM symbols s
    LEFT JOIN categories c ON s.category_id = c.id
    WHERE c.id IS NULL
""")
remaining = cur.fetchone()[0]

if remaining > 0:
    print(f"\n⚠️  Încă există {remaining} simboluri orfane!")
else:
    print("\n✅ Nu mai există simboluri orfane!")

# 6. Curăță duplicate create prin migrare
print("\n🔍 Verificare duplicate după migrare...")
cur.execute("""
    SELECT name, category_id, COUNT(*) as cnt
    FROM symbols
    WHERE child_id IS NULL
    GROUP BY name, category_id
    HAVING COUNT(*) > 1
""")

dups = cur.fetchall()
if dups:
    print(f"\n⚠️  Găsite {len(dups)} duplicate după migrare! Curățăm...")
    
    for name, cat_id, cnt in dups:
        cur.execute("""
            SELECT id FROM symbols
            WHERE name = ? AND category_id = ? AND child_id IS NULL
            ORDER BY id
        """, (name, cat_id))
        ids = [row[0] for row in cur.fetchall()]
        
        if len(ids) > 1:
            delete_ids = ids[1:]
            placeholders = ','.join('?' * len(delete_ids))
            cur.execute(f"DELETE FROM symbols WHERE id IN ({placeholders})", delete_ids)
            print(f"   ✓ Șters {len(delete_ids)} duplicate pentru '{name}' (cat {cat_id})")
    
    conn.commit()
    print("\n✅ Duplicate curățate!")
else:
    print("   ✅ Nu există duplicate!")

# 7. Statistici finale
cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NULL")
total_global = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NOT NULL")
total_child = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM categories")
total_categories = cur.fetchone()[0]

print(f"\n📊 Statistici finale:")
print(f"  - Total categorii: {total_categories}")
print(f"  - Simboluri globale: {total_global}")
print(f"  - Simboluri personalizate: {total_child}")
print(f"  - TOTAL simboluri: {total_global + total_child}")

conn.close()
print("\n✅ Reparare completă!")
