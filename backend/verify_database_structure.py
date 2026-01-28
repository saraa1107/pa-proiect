from database import SessionLocal
from models import Category, Symbol

db = SessionLocal()

print("=== VERIFICARE BAZĂ DE DATE ===\n")

# Categorii globale
global_cats = db.query(Category).filter(Category.child_id.is_(None)).all()
print(f"📋 Categorii globale: {len(global_cats)}")
for cat in global_cats:
    # Numără simboluri pentru fiecare categorie
    count = db.query(Symbol).filter(
        Symbol.category_id == cat.id,
        Symbol.child_id.is_(None)
    ).count()
    print(f"  {cat.id}: {cat.name} - {count} simboluri")

# Total simboluri globale
total_symbols = db.query(Symbol).filter(Symbol.child_id.is_(None)).count()
print(f"\n✅ Total simboluri globale: {total_symbols}")

# Verifică duplicate simboluri
print("\n🔍 Verificare duplicate simboluri globale:")
from collections import Counter
symbols = db.query(Symbol).filter(Symbol.child_id.is_(None)).all()
names = [s.name for s in symbols]
duplicates = {name: count for name, count in Counter(names).items() if count > 1}
if duplicates:
    print(f"  ⚠️ {len(duplicates)} simboluri duplicate găsite:")
    for name, count in list(duplicates.items())[:10]:
        print(f"    {name}: {count}x")
else:
    print("  ✅ Nu există duplicate!")

db.close()
