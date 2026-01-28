"""
Script pentru inițializarea bazei de date cu date de test
"""
from database import SessionLocal, engine, Base
from models import Category, Symbol
from services import CategoryService, SymbolService
from schemas import CategoryCreate, SymbolCreate

# Creează toate tabelele
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Verifică dacă există deja categorii
    existing_categories = db.query(Category).count()
    
    # Creează categorii
    categories_data = [
        {"name": "Acțiuni", "description": "Verbe și acțiuni comune", "color": "#FF6B6B"},
        {"name": "Alimente", "description": "Mâncare și băuturi", "color": "#4ECDC4"},
        {"name": "Emoții", "description": "Sentimente și emoții", "color": "#FFE66D"},
        {"name": "Persoane", "description": "Membri ai familiei și persoane", "color": "#95E1D3"},
        {"name": "Locații", "description": "Locuri și destinații", "color": "#A8E6CF"},
        {"name": "Obiecte", "description": "Obiecte de uz zilnic", "color": "#FFD3B6"},
    ]

    created_categories = {}
    
    if existing_categories > 0:
        print("Baza de date există deja. Se actualizează cu simbolurile noi...")
        # Obține categoriile existente
        for cat_data in categories_data:
            existing_cat = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if existing_cat:
                created_categories[cat_data["name"]] = existing_cat.id
                print(f"✓ Categorie existentă găsită: {existing_cat.name}")
            else:
                # Creează categoria dacă nu există
                category = CategoryService.create(db, CategoryCreate(**cat_data))
                created_categories[cat_data["name"]] = category.id
                print(f"✓ Categorie nouă creată: {category.name}")
    else:
        print("Inițializare baza de date cu date de test...")
        # Creează toate categoriile
        for cat_data in categories_data:
            category = CategoryService.create(db, CategoryCreate(**cat_data))
            created_categories[cat_data["name"]] = category.id
            print(f"✓ Categorie creată: {category.name}")

    # Creează simboluri de exemplu (50 simboluri în total)
    symbols_data = [
        # Acțiuni (8 simboluri)
        {"name": "Mâncare", "text": "Vreau să mănânc", "image_url": "/images/mananc.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Băutură", "text": "Vreau să beau", "image_url": "/images/beau.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Dormit", "text": "Vreau să dorm", "image_url": "/images/dorm.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Joc", "text": "Vreau să mă joc", "image_url": "/images/joc.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Mers", "text": "Vreau să merg", "image_url": "/images/merg.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Citit", "text": "Vreau să citesc", "image_url": "/images/citesc.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Spălat", "text": "Vreau să mă spăl", "image_url": "/images/spal.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Îmbrăcat", "text": "Vreau să mă îmbrac", "image_url": "/images/imbrac.jpg", "category_id": created_categories["Acțiuni"]},
        
        # Alimente (12 simboluri)
        {"name": "Pâine", "text": "Pâine", "image_url": "/images/paine.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Apă", "text": "Apă", "image_url": "/images/apa.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Lapte", "text": "Lapte", "image_url": "/images/lapte.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Fructe", "text": "Fructe", "image_url": "/images/fructe.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Măr", "text": "Măr", "image_url": "/images/mar.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Banane", "text": "Banane", "image_url": "/images/banane.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Portocale", "text": "Portocale", "image_url": "/images/portocale.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Legume", "text": "Legume", "image_url": "/images/legume.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Ouă", "text": "Ouă", "image_url": "/images/oua.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Brânză", "text": "Brânză", "image_url": "/images/branza.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Suc", "text": "Suc", "image_url": "/images/suc.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Ciocolată", "text": "Ciocolată", "image_url": "/images/ciocolata.jpg", "category_id": created_categories["Alimente"]},
        
        # Emoții (5 simboluri)
        {"name": "Fericit", "text": "Sunt fericit", "image_url": "/images/fericit.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Trist", "text": "Sunt trist", "image_url": "/images/trist.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Supărat", "text": "Sunt supărat", "image_url": "/images/suparat.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Înfricat", "text": "Sunt înfricat", "image_url": "/images/infricat.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Obosit", "text": "Sunt obosit", "image_url": "/images/obosit.jpg", "category_id": created_categories["Emoții"]},
        
        # Persoane (6 simboluri)
        {"name": "Mama", "text": "Mama", "image_url": "/images/mama.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Tata", "text": "Tata", "image_url": "/images/tata.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Prieten", "text": "Prieten", "image_url": "/images/prieten.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Bunică", "text": "Bunica", "image_url": "/images/bunica.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Frate", "text": "Fratele", "image_url": "/images/frate.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Profesor", "text": "Profesorul", "image_url": "/images/profesor.jpg", "category_id": created_categories["Persoane"]},
        
        # Locații (9 simboluri)
        {"name": "Casă", "text": "Casă", "image_url": "/images/casa.jpg", "category_id": created_categories["Locații"]},
        {"name": "Școală", "text": "Școală", "image_url": "/images/scoala.jpg", "category_id": created_categories["Locații"]},
        {"name": "Parc", "text": "Parc", "image_url": "/images/parc.jpg", "category_id": created_categories["Locații"]},
        {"name": "Magazin", "text": "Magazin", "image_url": "/images/magazin.jpg", "category_id": created_categories["Locații"]},
        {"name": "Spital", "text": "Spital", "image_url": "/images/spital.jpg", "category_id": created_categories["Locații"]},
        {"name": "Bucătărie", "text": "Bucătărie", "image_url": "/images/bucatarie.jpg", "category_id": created_categories["Locații"]},
        {"name": "Dormitor", "text": "Dormitor", "image_url": "/images/dormitor.jpg", "category_id": created_categories["Locații"]},
        {"name": "Baie", "text": "Baie", "image_url": "/images/baie.jpg", "category_id": created_categories["Locații"]},
        {"name": "Curte", "text": "Curte", "image_url": "/images/curte.jpg", "category_id": created_categories["Locații"]},
        
        # Obiecte (10 simboluri)
        {"name": "Scaun", "text": "Scaun", "image_url": "/images/scaun.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Pat", "text": "Pat", "image_url": "/images/pat.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Jucărie", "text": "Jucărie", "image_url": "/images/jucarie.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Minge", "text": "Minge", "image_url": "/images/minge.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Cărți", "text": "Cărți", "image_url": "/images/carti.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Creion", "text": "Creion", "image_url": "/images/creion.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Telefon", "text": "Telefon", "image_url": "/images/telefon.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Haină", "text": "Haină", "image_url": "/images/haina.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Pantofi", "text": "Pantofi", "image_url": "/images/pantofi.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Autoturism", "text": "Mașină", "image_url": "/images/masina.jpg", "category_id": created_categories["Obiecte"]},
    ]

    # Adaugă simbolurile (doar cele care nu există deja)
    symbols_added = 0
    symbols_skipped = 0
    
    for sym_data in symbols_data:
        # Verifică dacă simbolul există deja după nume și category_id (doar globale, child_id = None)
        existing_symbol = db.query(Symbol).filter(
            Symbol.name == sym_data["name"],
            Symbol.category_id == sym_data["category_id"],
            Symbol.child_id.is_(None)
        ).first()
        if existing_symbol:
            print(f"⊘ Simbol deja există (sărit): {sym_data['name']}")
            symbols_skipped += 1
        else:
            try:
                symbol = SymbolService.create(db, SymbolCreate(**sym_data))
                print(f"✓ Simbol creat: {symbol.name}")
                symbols_added += 1
            except Exception as e:
                print(f"✗ Eroare la crearea simbolului '{sym_data['name']}': {e}")

    print(f"\n✓ Actualizare completă!")
    print(f"  - Simboluri noi adăugate: {symbols_added}")
    print(f"  - Simboluri existente (sărite): {symbols_skipped}")
    print(f"  - Total simboluri în baza de date: {db.query(Symbol).count()}")

except Exception as e:
    print(f"Eroare la inițializarea bazei de date: {e}")
    db.rollback()
finally:
    db.close()


