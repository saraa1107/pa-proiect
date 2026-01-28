"""
Test pentru verificarea constrângerilor UNIQUE
"""
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Category, Symbol
import sys

def test_unique_constraints():
    db = SessionLocal()
    
    print("🧪 Testare constrângeri UNIQUE...\n")
    
    try:
        # Test 1: Încercare de a crea categorie globală duplicată
        print("Test 1: Încerc să creez o categorie globală duplicată...")
        try:
            cat1 = Category(name="Test Duplicat", child_id=None)
            db.add(cat1)
            db.commit()
            print("  ✓ Prima categorie creată cu succes (ID: {})".format(cat1.id))
            
            # Încercăm să creăm un duplicat
            cat2 = Category(name="Test Duplicat", child_id=None)
            db.add(cat2)
            db.commit()
            print("  ❌ EROARE: A permis crearea duplicatului!")
            
        except Exception as e:
            db.rollback()
            if "UNIQUE constraint failed" in str(e) or "unique" in str(e).lower():
                print("  ✅ Constrângerea funcționează! Nu permite duplicate.")
            else:
                print(f"  ⚠ Eroare neașteptată: {e}")
        
        # Test 2: Verifică că poate crea categorii cu nume identic dar child_id diferit
        print("\nTest 2: Încerc să creez categorii cu același nume dar copii diferiți...")
        try:
            cat3 = Category(name="Test Child", child_id=17)
            db.add(cat3)
            db.commit()
            print("  ✓ Categorie pentru copil 17 creată (ID: {})".format(cat3.id))
            
            cat4 = Category(name="Test Child", child_id=18)
            db.add(cat4)
            db.commit()
            print("  ✓ Categorie pentru copil 18 creată (ID: {})".format(cat4.id))
            print("  ✅ Permite corect aceeași categorie pentru copii diferiți")
            
        except Exception as e:
            db.rollback()
            print(f"  ❌ Nu ar trebui să dea eroare: {e}")
        
        # Curățare: șterge categoriile de test
        print("\n🧹 Curățare categorii de test...")
        db.query(Category).filter(Category.name.like("Test%")).delete()
        db.commit()
        print("  ✓ Curățare completă")
        
    except Exception as e:
        print(f"\n❌ Eroare: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n✅ Teste complete!")

if __name__ == "__main__":
    test_unique_constraints()
