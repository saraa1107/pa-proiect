#!/usr/bin/env python3
"""
Adaugă constrangere UNIQUE pe (name, therapist_id) pentru tabela children.
Șterge duplicatele înainte de a aplica constrangerea.
"""

import sqlite3
import sys
import os

DB_PATH = "data/aac_database.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("=== MIGRARE: Adăugare constrangere UNIQUE pe children(name, therapist_id) ===\n")
    
    # 1. Verifică duplicatele existente
    print("📋 Verificare duplicate existente...")
    cur.execute("""
        SELECT name, therapist_id, COUNT(*) as cnt
        FROM children
        GROUP BY name, therapist_id
        HAVING COUNT(*) > 1
    """)
    duplicates = cur.fetchall()
    
    if duplicates:
        print(f"⚠️  S-au găsit {len(duplicates)} seturi de duplicate:")
        for name, therapist_id, cnt in duplicates:
            print(f"   - Terapeut {therapist_id}, Copil '{name}': {cnt} intrări")
            
            # Păstrează doar primul copil, șterge restul
            cur.execute("""
                SELECT id FROM children
                WHERE name = ? AND therapist_id = ?
                ORDER BY id
            """, (name, therapist_id))
            ids = [row[0] for row in cur.fetchall()]
            
            if len(ids) > 1:
                ids_to_delete = ids[1:]
                print(f"     → Păstrăm ID {ids[0]}, ștergem IDs {ids_to_delete}")
                
                # Șterge copiii duplicați
                placeholders = ','.join('?' * len(ids_to_delete))
                cur.execute(f"DELETE FROM children WHERE id IN ({placeholders})", ids_to_delete)
        
        conn.commit()
        print("✅ Duplicate șterse!\n")
    else:
        print("✅ Nu există duplicate.\n")
    
    # 2. Verifică dacă constrangerea există deja
    print("📋 Verificare constrangere existentă...")
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='children'")
    table_sql = cur.fetchone()[0]
    
    if 'uq_child_name_therapist' in table_sql or 'UNIQUE' in table_sql:
        print("⚠️  Constrangerea UNIQUE există deja pe tabela children.")
        conn.close()
        return
    
    print("✅ Constrangerea nu există, o vom adăuga.\n")
    
    # 3. Recreează tabela cu constrangere UNIQUE
    print("🔧 Recreare tabelă children cu constrangere UNIQUE...")
    
    # Obține structura actuală
    cur.execute("PRAGMA table_info(children)")
    columns = cur.fetchall()
    
    # Salvează datele existente
    cur.execute("SELECT * FROM children")
    existing_data = cur.fetchall()
    
    # Creează tabelă temporară cu constrangere
    cur.execute("""
        CREATE TABLE children_new (
            id INTEGER PRIMARY KEY,
            therapist_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP,
            FOREIGN KEY (therapist_id) REFERENCES users(id),
            UNIQUE (name, therapist_id)
        )
    """)
    
    # Copiază datele
    if existing_data:
        cur.executemany("""
            INSERT INTO children_new (id, therapist_id, name, created_at)
            VALUES (?, ?, ?, ?)
        """, existing_data)
    
    # Înlocuiește tabela veche
    cur.execute("DROP TABLE children")
    cur.execute("ALTER TABLE children_new RENAME TO children")
    
    conn.commit()
    print("✅ Tabelă recreată cu succes!\n")
    
    # 4. Verificare finală
    print("📋 Verificare finală...")
    cur.execute("SELECT COUNT(*) FROM children")
    total = cur.fetchone()[0]
    print(f"✅ Total copii în baza de date: {total}")
    
    cur.execute("""
        SELECT name, therapist_id, COUNT(*) as cnt
        FROM children
        GROUP BY name, therapist_id
        HAVING COUNT(*) > 1
    """)
    final_duplicates = cur.fetchall()
    
    if final_duplicates:
        print("❌ EROARE: Încă există duplicate!")
        for name, therapist_id, cnt in final_duplicates:
            print(f"   - Terapeut {therapist_id}, Copil '{name}': {cnt} intrări")
    else:
        print("✅ Nu există duplicate!")
    
    conn.close()
    print("\n✅ Migrare completă!")

if __name__ == "__main__":
    main()
