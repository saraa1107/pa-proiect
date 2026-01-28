"""
Script de migrare: Adaugă constrângeri UNIQUE pentru a preveni duplicatele
"""
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def migrate_add_unique_constraints():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    print("🔧 Adăugare constrângeri UNIQUE...")
    
    with engine.connect() as conn:
        try:
            # 1. Verifică dacă există constrângerea pentru Category
            print("\n1. Adaugă constrângere UNIQUE pentru categories (name, child_id)...")
            try:
                conn.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_category_name_child 
                    ON categories(name, child_id)
                """))
                conn.commit()
                print("   ✓ Constrângere adăugată pentru categories")
            except Exception as e:
                if "already exists" in str(e).lower() or "unique" in str(e).lower():
                    print("   ℹ Constrângerea pentru categories există deja")
                else:
                    raise
            
            # 2. Verifică dacă există constrângerea pentru Symbol
            print("\n2. Adaugă constrângere UNIQUE pentru symbols (name, category_id, child_id)...")
            try:
                conn.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_symbol_name_category_child 
                    ON symbols(name, category_id, child_id)
                """))
                conn.commit()
                print("   ✓ Constrângere adăugată pentru symbols")
            except Exception as e:
                if "already exists" in str(e).lower() or "unique" in str(e).lower():
                    print("   ℹ Constrângerea pentru symbols există deja")
                else:
                    raise
            
            # 3. Verifică dacă există constrângerea pentru FavoriteSymbol
            print("\n3. Adaugă constrângere UNIQUE pentru favorite_symbols (child_id, symbol_id)...")
            try:
                conn.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_favorite_child_symbol 
                    ON favorite_symbols(child_id, symbol_id)
                """))
                conn.commit()
                print("   ✓ Constrângere adăugată pentru favorite_symbols")
            except Exception as e:
                if "already exists" in str(e).lower() or "unique" in str(e).lower():
                    print("   ℹ Constrângerea pentru favorite_symbols există deja")
                else:
                    raise
            
            print("\n✅ Migrare completă! Acum duplicatele sunt împiedicate la nivel de bază de date.")
            
        except Exception as e:
            print(f"\n❌ Eroare la migrare: {e}")
            raise
    
    engine.dispose()

if __name__ == "__main__":
    migrate_add_unique_constraints()
