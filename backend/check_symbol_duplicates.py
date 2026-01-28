from database import SessionLocal
from models import Symbol
from collections import Counter

db = SessionLocal()
symbols = db.query(Symbol).filter(Symbol.child_id.is_(None)).all()
print(f'Total simboluri globale: {len(symbols)}')

names = [s.name for s in symbols]
duplicates = {name: count for name, count in Counter(names).items() if count > 1}
print(f'Simboluri duplicate: {len(duplicates)}')

if duplicates:
    print('\nPrimele 20 simboluri duplicate:')
    for name, count in list(duplicates.items())[:20]:
        print(f'  {name}: {count}x')

db.close()
