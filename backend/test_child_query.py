"""Script pentru testarea query-urilor pentru copii (mod terapeut)"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "aac_database.db")

if not os.path.exists(DB_PATH):
    print(f"Baza de date nu există: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== TEST QUERY-URI PENTRU COPII ===\n")

# Test 1: Listează toți copiii
print("1. TOȚI COPIII:")
cur.execute("SELECT id, therapist_id, name, created_at FROM children ORDER BY id")
children = cur.fetchall()

if not children:
    print("  Nu există copii în baza de date\n")
else:
    for child_id, therapist_id, name, created in children:
        print(f"  ID {child_id}: {name} (terapeut: {therapist_id}, creat: {created})")
    print()

# Test 2: Categorii per copil
print("2. CATEGORII PER COPIL:")
for child_id, therapist_id, name, created in children:
    cur.execute("""
        SELECT id, name, description
        FROM categories
        WHERE child_id = ?
        ORDER BY id
    """, (child_id,))
    
    categories = cur.fetchall()
    print(f"\n  Copil: {name} (ID {child_id})")
    if not categories:
        print(f"    Nu are categorii personalizate")
    else:
        for cat_id, cat_name, cat_desc in categories:
            print(f"    - {cat_name} (ID {cat_id})")

# Test 3: Simboluri per copil
print("\n\n3. SIMBOLURI PER COPIL:")
for child_id, therapist_id, name, created in children:
    cur.execute("""
        SELECT COUNT(*)
        FROM symbols
        WHERE child_id = ?
    """, (child_id,))
    
    count = cur.fetchone()[0]
    print(f"\n  Copil: {name} (ID {child_id}) - {count} simboluri")
    
    if count > 0:
        cur.execute("""
            SELECT s.id, s.name, c.name as category_name
            FROM symbols s
            JOIN categories c ON s.category_id = c.id
            WHERE s.child_id = ?
            ORDER BY c.name, s.display_order, s.name
            LIMIT 10
        """, (child_id,))
        
        symbols = cur.fetchall()
        for s_id, s_name, cat_name in symbols:
            print(f"    - {s_name} ({cat_name})")
        
        if count > 10:
            print(f"    ... și încă {count - 10} simboluri")

# Test 4: Favorite per copil
print("\n\n4. SIMBOLURI FAVORITE PER COPIL:")
for child_id, therapist_id, name, created in children:
    cur.execute("""
        SELECT s.id, s.name, s.text
        FROM symbols s
        JOIN favorite_symbols f ON s.id = f.symbol_id
        WHERE f.child_id = ?
        ORDER BY f.created_at DESC
    """, (child_id,))
    
    favorites = cur.fetchall()
    print(f"\n  Copil: {name} (ID {child_id}) - {len(favorites)} favorite")
    
    for s_id, s_name, s_text in favorites:
        print(f"    ⭐ {s_name} ({s_text})")

# Test 5: Statistici generale
print("\n\n5. STATISTICI:")
cur.execute("SELECT COUNT(*) FROM children")
total_children = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM categories WHERE child_id IS NOT NULL")
total_custom_cats = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NOT NULL")
total_custom_symbols = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM favorite_symbols")
total_favorites = cur.fetchone()[0]

print(f"  Total copii: {total_children}")
print(f"  Total categorii personalizate: {total_custom_cats}")
print(f"  Total simboluri personalizate: {total_custom_symbols}")
print(f"  Total simboluri favorite: {total_favorites}")

conn.close()
print("\n✓ Test complet!")
