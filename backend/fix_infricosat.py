"""Script pentru fixarea problemelor legate de simbolul 'înfricoșat'"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "aac_database.db")

if not os.path.exists(DB_PATH):
    print(f"Baza de date nu există: {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== FIX SIMBOLUL 'ÎNFRICOȘAT' ===\n")

# Caută simboluri cu înfricoșat
cur.execute("""
    SELECT id, name, text, image_url, category_id, child_id
    FROM symbols
    WHERE LOWER(name) LIKE '%înfricoșat%' OR LOWER(name) LIKE '%infricosat%'
       OR LOWER(text) LIKE '%înfricoșat%' OR LOWER(text) LIKE '%infricosat%'
""")

symbols = cur.fetchall()

if not symbols:
    print("Nu s-au găsit simboluri cu 'înfricoșat'")
else:
    print(f"Găsite {len(symbols)} simboluri:\n")
    
    for s_id, name, text, img, cat_id, child_id in symbols:
        print(f"ID {s_id}: {name}")
        print(f"  Text: {text}")
        print(f"  Imagine: {img}")
        print(f"  Category: {cat_id}, Child: {child_id}")
        
        # Verifică dacă are imagine validă
        if not img or img.endswith('/images/casa.jpg') or 'placeholder' in img.lower():
            print(f"  ⚠ Lipsește imagine validă!")
            
            # Încearcă să seteze o imagine pentru emoții negative
            new_image = "/images/infricosat.jpg"  # sau "scared.jpg"
            
            response = input(f"  Dorești să actualizezi imaginea la '{new_image}'? (y/n): ")
            if response.lower() == 'y':
                cur.execute("UPDATE symbols SET image_url = ? WHERE id = ?", (new_image, s_id))
                conn.commit()
                print(f"  ✓ Imagine actualizată!")
        else:
            print(f"  ✓ Are imagine validă")
        
        print()

# Verifică dacă categoria Emoții există
cur.execute("SELECT id, name FROM categories WHERE LOWER(name) LIKE '%emo%'")
emotions_cat = cur.fetchone()

if emotions_cat:
    cat_id, cat_name = emotions_cat
    print(f"\n✓ Categoria '{cat_name}' există (ID: {cat_id})")
    
    # Verifică dacă simbolurile sunt în categoria corectă
    for s_id, name, text, img, symbol_cat_id, child_id in symbols:
        if symbol_cat_id != cat_id and child_id is None:  # doar simboluri globale
            print(f"\n⚠ Simbolul '{name}' (ID {s_id}) nu este în categoria Emoții")
            response = input(f"  Dorești să-l muți în categoria '{cat_name}'? (y/n): ")
            if response.lower() == 'y':
                cur.execute("UPDATE symbols SET category_id = ? WHERE id = ?", (cat_id, s_id))
                conn.commit()
                print(f"  ✓ Simbol mutat în categoria Emoții!")
else:
    print("\n⚠ Nu există categoria Emoții!")

conn.close()
print("\n✓ Fix complet!")
