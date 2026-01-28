"""
Migrare pentru adăugarea coloanei password_hash în tabela users.
"""
import sqlite3
import os

DB_PATH = "data/aac_database.db"


def migrate():
    if not os.path.exists(DB_PATH):
        print("Baza de date nu există.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # Verifică dacă coloana password_hash există
        cur.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cur.fetchall()]
        
        if "password_hash" not in columns:
            print("Adăugăm coloana password_hash...")
            cur.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
            conn.commit()
            print("✓ Coloana password_hash adăugată cu succes")
        else:
            print("✓ Coloana password_hash există deja")

    except Exception as e:
        print(f"Eroare la migrare: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
