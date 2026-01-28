"""
Script de migrare: Recreează tabelele cu constrângeri UNIQUE corecte
ATENȚIE: Acest script șterge și recrează tabelele!
"""
from database import Base, engine
from models import User, Child, Category, Symbol, FavoriteSymbol
import shutil
import os
from datetime import datetime

def backup_and_recreate():
    db_path = "data/aac_database.db"
    
    # 1. Creează backup
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/aac_database_backup_{timestamp}.db"
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup creat: {backup_path}")
    
    # 2. Șterge toate tabelele
    print("🗑️ Ștergere tabele vechi...")
    Base.metadata.drop_all(bind=engine)
    print("✓ Tabele șterse")
    
    # 3. Recrează tabelele cu noile constrângeri
    print("🔨 Recreare tabele cu constrângeri UNIQUE...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tabele recreate")
    
    print("\n⚠️ IMPORTANT: Trebuie să rulezi init_db.py pentru a reîncărca datele!")
    print("   Comandă: python init_db.py")

if __name__ == "__main__":
    response = input("⚠️ Acest script va șterge și recrea toate tabelele! Vrei să continui? (da/nu): ")
    if response.lower() == "da":
        backup_and_recreate()
    else:
        print("Operațiune anulată.")
