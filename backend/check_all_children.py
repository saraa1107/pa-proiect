from database import SessionLocal
from models import Child, Category, Symbol

db = SessionLocal()

print("=== COPII ÎN BAZA DE DATE ===\n")

children = db.query(Child).all()
print(f"Total copii: {len(children)}")

for child in children:
    print(f"\n📋 Copil: {child.name} (ID: {child.id}, Terapeut: {child.therapist_id})")
    
    # Categorii pentru acest copil
    child_cats = db.query(Category).filter(Category.child_id == child.id).count()
    print(f"   Categorii proprii: {child_cats}")
    
    # Simboluri pentru acest copil
    child_symbols = db.query(Symbol).filter(Symbol.child_id == child.id).count()
    print(f"   Simboluri proprii: {child_symbols}")

print("\n\n=== CATEGORII GLOBALE ===")
global_cats = db.query(Category).filter(Category.child_id.is_(None)).all()
print(f"Total: {len(global_cats)}")
for cat in global_cats:
    print(f"  {cat.id}: {cat.name}")

print("\n=== SIMBOLURI GLOBALE ===")
global_symbols = db.query(Symbol).filter(Symbol.child_id.is_(None)).count()
print(f"Total: {global_symbols}")

db.close()
