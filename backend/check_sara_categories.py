from database import SessionLocal
from models import Child, Category

db = SessionLocal()
child = db.query(Child).filter(Child.name.like('%ara%')).first()

if child:
    print(f'Copil: {child.name} (ID: {child.id})')
    cats = db.query(Category).filter(Category.child_id == child.id).all()
    print(f'\nCategorii proprii copil: {len(cats)}')
    for c in cats:
        print(f'  {c.id}: {c.name}')
    
    print('\nCategorii globale:')
    global_cats = db.query(Category).filter(Category.child_id.is_(None)).all()
    print(f'Total: {len(global_cats)}')
    for c in global_cats:
        print(f'  {c.id}: {c.name}')
else:
    print('Copil Sara nu gasit')
    
db.close()
