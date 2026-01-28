#!/usr/bin/env python3
"""
Verifică simbolul 202
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "aac_database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== VERIFICARE SIMBOL 202 ===\n")

cur.execute("""
    SELECT s.id, s.name, s.child_id, s.category_id, c.name as category_name
    FROM symbols s
    LEFT JOIN categories c ON s.category_id = c.id
    WHERE s.id = 202
""")

result = cur.fetchone()

if result:
    sid, name, child_id, cat_id, cat_name = result
    print(f"Simbol ID: {sid}")
    print(f"Nume: {name}")
    print(f"Child ID: {child_id} ({'GLOBAL' if child_id is None else 'PERSONALIZAT'})")
    print(f"Categoria: {cat_id} - {cat_name}")
else:
    print("❌ Simbolul 202 nu există!")

conn.close()
