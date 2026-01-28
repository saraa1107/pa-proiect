#!/usr/bin/env python3
"""
Curăță simbolurile care sunt în categorii greșite.
Un simbol ar trebui să fie doar într-o singură categorie logică.
"""

import sqlite3

DB_PATH = "data/aac_database.db"

# Definim ce simboluri aparțin fiecărei categorii
CORRECT_MAPPING = {
    "Acțiuni": ["Mâncare", "Băutură", "Dormit", "Joc", "Mers", "Alergat", "Citit", "Scris", 
                "Desenat", "Ascultat", "Văzut", "Spălat", "Îmbrăcat", "Plimbat", "Dansat"],
    
    "Alimente": ["Pâine", "Apă", "Lapte", "Fructe", "Măr", "Banane", "Portocale", "Struguri",
                 "Legume", "Morcovi", "Rosii", "Cartofi", "Ouă", "Brânză", "Iaurt", "Carne",
                 "Pui", "Paste", "Orez", "Suc", "Ciocolată", "Biscuiți", "Tort"],
    
    "Emoții": ["Fericit", "Trist", "Supărat", "Înfricat", "Surprins"],
    
    "Persoane": ["Mamă", "Tată", "Soră", "Frate", "Bunică", "Bunic", "Profesor", "Prieten"],
    
    "Locații": ["Casă", "Școală", "Parc", "Magazin", "Spital", "Bucătărie", "Baie", 
                "Dormitor", "Grădiniță", "Stradă"],
    
    "Obiecte": ["Minge", "Carte", "Creion", "Jucărie", "Telefon", "Masă", "Scaun", 
                "Pat", "Canapea", "Televizor", "Computer", "Tablet", "Mașină", 
                "Bicicletă", "Autoturism", "Autobuz"]
}

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("=== CURĂȚARE SIMBOLURI DIN CATEGORII GREȘITE ===\n")
    
    # 1. Obține ID-urile categoriilor
    category_ids = {}
    for cat_name in CORRECT_MAPPING.keys():
        cur.execute("SELECT id FROM categories WHERE name = ? AND child_id IS NULL", (cat_name,))
        result = cur.fetchone()
        if result:
            category_ids[cat_name] = result[0]
    
    print("📋 Categorii găsite:")
    for name, cat_id in category_ids.items():
        print(f"  {name}: ID {cat_id}")
    
    # 2. Pentru fiecare categorie, păstrează doar simbolurile corecte
    deleted_total = 0
    
    for cat_name, correct_symbols in CORRECT_MAPPING.items():
        if cat_name not in category_ids:
            continue
            
        cat_id = category_ids[cat_name]
        
        # Găsește simbolurile din această categorie
        cur.execute("""
            SELECT id, name FROM symbols
            WHERE category_id = ? AND child_id IS NULL
        """, (cat_id,))
        current_symbols = cur.fetchall()
        
        # Identifică simbolurile care NU ar trebui să fie în această categorie
        to_delete = []
        for sym_id, sym_name in current_symbols:
            if sym_name not in correct_symbols:
                to_delete.append((sym_id, sym_name))
        
        if to_delete:
            print(f"\n⚠️  Categorie '{cat_name}' (ID {cat_id}):")
            print(f"   Găsite: {len(current_symbols)} simboluri")
            print(f"   Corecte: {len(correct_symbols)} simboluri")
            print(f"   De șters: {len(to_delete)} simboluri greșite")
            
            for sym_id, sym_name in to_delete[:5]:
                print(f"     - {sym_name} (ID {sym_id})")
            if len(to_delete) > 5:
                print(f"     ... și încă {len(to_delete) - 5}")
            
            # Șterge simbolurile greșite
            ids_to_delete = [sid for sid, _ in to_delete]
            placeholders = ','.join('?' * len(ids_to_delete))
            cur.execute(f"DELETE FROM symbols WHERE id IN ({placeholders})", ids_to_delete)
            deleted_total += len(ids_to_delete)
    
    # 3. Șterge toate duplicatele rămase (același nume în aceeași categorie)
    print("\n\n🔍 Șterge duplicate (același nume în aceeași categorie)...")
    cur.execute("""
        SELECT name, category_id, COUNT(*) as cnt
        FROM symbols
        WHERE child_id IS NULL
        GROUP BY name, category_id
        HAVING COUNT(*) > 1
    """)
    duplicates = cur.fetchall()
    
    if duplicates:
        print(f"   Găsite {len(duplicates)} seturi de duplicate")
        for name, cat_id, cnt in duplicates:
            # Păstrează primul, șterge restul
            cur.execute("""
                SELECT id FROM symbols
                WHERE name = ? AND category_id = ? AND child_id IS NULL
                ORDER BY id
            """, (name, cat_id))
            ids = [row[0] for row in cur.fetchall()]
            
            if len(ids) > 1:
                ids_to_delete = ids[1:]
                placeholders = ','.join('?' * len(ids_to_delete))
                cur.execute(f"DELETE FROM symbols WHERE id IN ({placeholders})", ids_to_delete)
                deleted_total += len(ids_to_delete)
    
    conn.commit()
    print(f"\n✅ Total simboluri șterse: {deleted_total}")
    
    # 4. Verificare finală
    print("\n📋 Verificare finală:")
    for cat_name, correct_symbols in CORRECT_MAPPING.items():
        if cat_name not in category_ids:
            continue
        cat_id = category_ids[cat_name]
        cur.execute("SELECT COUNT(*) FROM symbols WHERE category_id = ? AND child_id IS NULL", (cat_id,))
        count = cur.fetchone()[0]
        expected = len(correct_symbols)
        status = "✅" if count == expected else "⚠️"
        print(f"  {status} {cat_name}: {count} simboluri (așteptat: {expected})")
    
    cur.execute("SELECT COUNT(*) FROM symbols WHERE child_id IS NULL")
    total = cur.fetchone()[0]
    expected_total = sum(len(v) for v in CORRECT_MAPPING.values())
    print(f"\n✅ Total simboluri globale: {total} (așteptat: {expected_total})")
    
    conn.close()
    print("\n✅ Curățare completă!")

if __name__ == "__main__":
    main()
