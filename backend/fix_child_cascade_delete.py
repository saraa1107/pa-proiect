"""
Fix pentru probleme de ștergere copii - adaugă CASCADE delete
"""
import sqlite3
import os

# Path către baza de date SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "aac_database.db")

if not os.path.exists(DB_PATH):
    print(f"❌ Baza de date nu există la: {DB_PATH}")
    exit(1)

print(f"Conectare la baza de date: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    print("\n1. Verificare structură tabele...")
    
    # Verifică structura categories
    cur.execute("PRAGMA table_info(categories)")
    cat_cols = cur.fetchall()
    print(f"   Coloane categories: {[col[1] for col in cat_cols]}")
    
    # Verifică structura symbols
    cur.execute("PRAGMA table_info(symbols)")
    sym_cols = cur.fetchall()
    print(f"   Coloane symbols: {[col[1] for col in sym_cols]}")
    
    # Verifică foreign keys pentru categories
    cur.execute("PRAGMA foreign_key_list(categories)")
    cat_fk = cur.fetchall()
    print(f"\n   Foreign keys categories: {cat_fk}")
    
    # Verifică foreign keys pentru symbols
    cur.execute("PRAGMA foreign_key_list(symbols)")
    sym_fk = cur.fetchall()
    print(f"   Foreign keys symbols: {sym_fk}")
    
    print("\n2. Backup date existente...")
    
    # Salvează toate datele
    cur.execute("SELECT * FROM categories")
    categories_data = cur.fetchall()
    cur.execute("SELECT * FROM symbols")
    symbols_data = cur.fetchall()
    
    print(f"   Backup: {len(categories_data)} categorii, {len(symbols_data)} simboluri")
    
    print("\n3. Recreare tabel categories cu CASCADE DELETE...")
    
    # Drop și recreează categories
    cur.execute("DROP TABLE IF EXISTS categories_backup")
    cur.execute("""
        CREATE TABLE categories_backup AS 
        SELECT * FROM categories
    """)
    
    cur.execute("DROP TABLE categories")
    
    cur.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            icon VARCHAR(255),
            color VARCHAR(7),
            child_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
            UNIQUE (name, child_id)
        )
    """)
    
    # Restore date
    cur.execute("""
        INSERT INTO categories (id, name, description, icon, color, child_id, created_at)
        SELECT id, name, description, icon, color, child_id, created_at
        FROM categories_backup
    """)
    
    print(f"   ✓ Categories recreat cu CASCADE DELETE")
    
    print("\n4. Recreare tabel symbols cu CASCADE DELETE...")
    
    # Drop și recreează symbols
    cur.execute("DROP TABLE IF EXISTS symbols_backup")
    cur.execute("""
        CREATE TABLE symbols_backup AS 
        SELECT * FROM symbols
    """)
    
    cur.execute("DROP TABLE symbols")
    
    cur.execute("""
        CREATE TABLE symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            text VARCHAR(255) NOT NULL,
            image_url VARCHAR(500) NOT NULL,
            category_id INTEGER NOT NULL,
            child_id INTEGER,
            display_order INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
            UNIQUE (name, category_id, child_id)
        )
    """)
    
    # Restore date
    cur.execute("""
        INSERT INTO symbols (id, name, text, image_url, category_id, child_id, display_order, usage_count, created_at)
        SELECT id, name, text, image_url, category_id, child_id, display_order, usage_count, created_at
        FROM symbols_backup
    """)
    
    print(f"   ✓ Symbols recreat cu CASCADE DELETE")
    
    print("\n5. Activare foreign keys...")
    cur.execute("PRAGMA foreign_keys = ON")
    
    print("\n6. Verificare finală...")
    cur.execute("PRAGMA foreign_key_list(categories)")
    cat_fk_new = cur.fetchall()
    print(f"\n   Foreign keys categories: {cat_fk_new}")
    
    cur.execute("PRAGMA foreign_key_list(symbols)")
    sym_fk_new = cur.fetchall()
    print(f"   Foreign keys symbols: {sym_fk_new}")
    
    cur.execute("SELECT COUNT(*) FROM categories")
    cat_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM symbols")
    sym_count = cur.fetchone()[0]
    
    print(f"\n   Date finale: {cat_count} categorii, {sym_count} simboluri")
    
    # Commit toate modificările
    conn.commit()
    
    print("\n7. Curățare backup-uri...")
    cur.execute("DROP TABLE IF EXISTS categories_backup")
    cur.execute("DROP TABLE IF EXISTS symbols_backup")
    conn.commit()
    
    print("\n✅ Migrare completată cu succes!")
    print("\n📝 Acum când ștergi un copil:")
    print("   - Se vor șterge AUTOMAT toate categoriile sale personalizate")
    print("   - Se vor șterge AUTOMAT toate simbolurile sale personalizate")
    print("   - Se vor șterge AUTOMAT toate simbolurile favorite")
    print("   - Nu vor mai rămâne date orfane în bază")

except Exception as e:
    print(f"\n❌ Eroare: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()

finally:
    cur.close()
    conn.close()
    print("\nConexiune închisă.")
