"""
Script pentru curățarea simbolurilor orfane (cu category_id invalid)
"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "aac_database.db")

if not os.path.exists(DB_PATH):
    print(f"Baza de date nu există: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("🔧 Reparare simboluri orfane...\n")

# Găsește simbolurile cu category_id care nu mai există
cur.execute("""
    SELECT s.id, s.name, s.category_id
    FROM symbols s
    LEFT JOIN categories c ON s.category_id = c.id
    WHERE c.id IS NULL
""")

orphan_symbols = cur.fetchall()

if not orphan_symbols:
    print("✓ Nu există simboluri orfane!")
else:
    print(f"Găsite {len(orphan_symbols)} simboluri orfane:\n")
    
    for symbol_id, name, category_id in orphan_symbols:
        print(f"  ✗ Simbol '{name}' (ID: {symbol_id}) are category_id={category_id} invalid")
        # Șterge simbolul orfan
        cur.execute("DELETE FROM symbols WHERE id = ?", (symbol_id,))
    
    conn.commit()
    print(f"\n✓ Șterse {len(orphan_symbols)} simboluri orfane!")

# Verifică statistici finale
cur.execute("SELECT COUNT(*) FROM symbols")
total_symbols = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM categories")
total_categories = cur.fetchone()[0]

print(f"\n📊 Statistici finale:")
print(f"  - Total categorii: {total_categories}")
print(f"  - Total simboluri: {total_symbols}")

conn.close()
print("\n✅ Reparare completă!")
