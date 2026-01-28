from database import SessionLocal
from models import Child

db = SessionLocal()
child = db.query(Child).filter(Child.name == 'Test Duplicate').first()
if child:
    db.delete(child)
    db.commit()
    print('Copil de test șters')
else:
    print('Copil nu găsit')
db.close()
