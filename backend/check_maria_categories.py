"""Check categories for Maria"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "aac_database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Găsește copilul Maria
cur.execute("SELECT id, name FROM children WHERE LOWER(name) = 'maria'")
child = cur.fetchone()

if child:
    child_id, child_name = child
    print(f"Child: {child_name} (ID: {child_id})\n")
    
    # Găsește toate categoriile (globale + specifice copilului)
    cur.execute("""
        SELECT id, name, child_id 
        FROM categories 
        WHERE child_id = ? OR child_id IS NULL 
        ORDER BY name
    """, (child_id,))
    
    cats = cur.fetchall()
    print(f"Total categories: {len(cats)}\n")
    
    for cat_id, name, cid in cats:
        type_str = "global" if cid is None else f"child_{cid}"
        print(f"  {cat_id}: {name} ({type_str})")
else:
    print("Child 'maria' not found!")

conn.close()
