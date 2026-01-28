from database import SessionLocal
from models import Child, Category, Symbol
from collections import Counter

db = SessionLocal()

print("=== ANALIZA COPII ===\n")

children = db.query(Child).order_by(Child.id).all()

for child in children:
    print(f"\n📋 Copil: {child.name} (ID: {child.id})")
    
    # Categorii copil
    child_cats = db.query(Category).filter(Category.child_id == child.id).count()
    print(f"   Categorii proprii: {child_cats}")
    
    # Simboluri copil
    child_symbols = db.query(Symbol).filter(Symbol.child_id == child.id).all()
    print(f"   Simboluri proprii: {len(child_symbols)}")
    
    # Verifică duplicate la simboluri
    symbol_names = [s.name for s in child_symbols]
    duplicates = {name: count for name, count in Counter(symbol_names).items() if count > 1}
    
    if duplicates:
        print(f"   ⚠️  DUPLICATE: {len(duplicates)} simboluri sunt duplicate!")
        for name, count in list(duplicates.items())[:5]:
            print(f"      {name}: {count}x")
        if len(duplicates) > 5:
            print(f"      ... și încă {len(duplicates) - 5}")
    else:
        print(f"   ✅ Nu există duplicate")

db.close()
