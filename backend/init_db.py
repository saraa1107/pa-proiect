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

    # Creează simboluri de exemplu
    symbols_data = [
        # Acțiuni
        {"name": "Mâncare", "text": "Vreau să mănânc", "image_url": "/images/mananc.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Băutură", "text": "Vreau să beau", "image_url": "/images/beau.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Dormit", "text": "Vreau să dorm", "image_url": "/images/dorm.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Joc", "text": "Vreau să mă joc", "image_url": "/images/joc.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Mers", "text": "Vreau să merg", "image_url": "/images/merg.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Alergat", "text": "Vreau să alerg", "image_url": "/images/alerg.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Citit", "text": "Vreau să citesc", "image_url": "/images/citesc.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Scris", "text": "Vreau să scriu", "image_url": "/images/scriu.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Desenat", "text": "Vreau să desenez", "image_url": "/images/desenez.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Ascultat", "text": "Vreau să ascult", "image_url": "/images/ascult.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Văzut", "text": "Vreau să văd", "image_url": "/images/vad.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Spălat", "text": "Vreau să mă spăl", "image_url": "/images/spal.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Îmbrăcat", "text": "Vreau să mă îmbrac", "image_url": "/images/imbrac.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Plimbat", "text": "Vreau să mă plimb", "image_url": "/images/plimb.jpg", "category_id": created_categories["Acțiuni"]},
        {"name": "Dansat", "text": "Vreau să dansez", "image_url": "/images/dansez.jpg", "category_id": created_categories["Acțiuni"]},
        
        # Alimente
        {"name": "Pâine", "text": "Pâine", "image_url": "/images/paine.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Apă", "text": "Apă", "image_url": "/images/apa.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Lapte", "text": "Lapte", "image_url": "/images/lapte.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Fructe", "text": "Fructe", "image_url": "/images/fructe.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Măr", "text": "Măr", "image_url": "/images/mar.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Banane", "text": "Banane", "image_url": "/images/banane.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Portocale", "text": "Portocale", "image_url": "/images/portocale.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Struguri", "text": "Struguri", "image_url": "/images/struguri.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Legume", "text": "Legume", "image_url": "/images/legume.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Morcovi", "text": "Morcovi", "image_url": "/images/morcovi.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Rosii", "text": "Roșii", "image_url": "/images/rosii.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Cartofi", "text": "Cartofi", "image_url": "/images/cartofi.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Ouă", "text": "Ouă", "image_url": "/images/oua.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Brânză", "text": "Brânză", "image_url": "/images/branza.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Iaurt", "text": "Iaurt", "image_url": "/images/iaurt.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Carne", "text": "Carne", "image_url": "/images/carne.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Pui", "text": "Pui", "image_url": "/images/pui.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Paste", "text": "Paste", "image_url": "/images/paste.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Orez", "text": "Orez", "image_url": "/images/orez.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Suc", "text": "Suc", "image_url": "/images/suc.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Ciocolată", "text": "Ciocolată", "image_url": "/images/ciocolata.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Biscuiți", "text": "Biscuiți", "image_url": "/images/biscuiti.jpg", "category_id": created_categories["Alimente"]},
        {"name": "Tort", "text": "Tort", "image_url": "/images/tort.jpg", "category_id": created_categories["Alimente"]},
        
        # Emoții
        {"name": "Fericit", "text": "Sunt fericit", "image_url": "/images/fericit.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Trist", "text": "Sunt trist", "image_url": "/images/trist.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Supărat", "text": "Sunt supărat", "image_url": "/images/suparat.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Înfricat", "text": "Sunt înfricat", "image_url": "/images/infricat.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Surprins", "text": "Sunt surprins", "image_url": "/images/surprins.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Obosit", "text": "Sunt obosit", "image_url": "/images/obosit.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Însetat", "text": "Sunt însetat", "image_url": "/images/insetat.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Foame", "text": "Mi-e foame", "image_url": "/images/foame.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Mândru", "text": "Sunt mândru", "image_url": "/images/mandru.jpg", "category_id": created_categories["Emoții"]},
        {"name": "Iubit", "text": "Mă simt iubit", "image_url": "/images/iubit.jpg", "category_id": created_categories["Emoții"]},
        
        # Persoane
        {"name": "Mama", "text": "Mama", "image_url": "/images/mama.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Tata", "text": "Tata", "image_url": "/images/tata.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Prieten", "text": "Prieten", "image_url": "/images/prieten.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Bunică", "text": "Bunica", "image_url": "/images/bunica.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Bunic", "text": "Bunicul", "image_url": "/images/bunic.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Frate", "text": "Fratele", "image_url": "/images/frate.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Soră", "text": "Sora", "image_url": "/images/sora.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Copil", "text": "Copil", "image_url": "/images/copil.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Bebeluș", "text": "Bebeluș", "image_url": "/images/bebelus.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Profesor", "text": "Profesorul", "image_url": "/images/profesor.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Doctor", "text": "Doctorul", "image_url": "/images/doctor.jpg", "category_id": created_categories["Persoane"]},
        {"name": "Asistent", "text": "Asistentul", "image_url": "/images/asistent.jpg", "category_id": created_categories["Persoane"]},
        
        # Locații
        {"name": "Casă", "text": "Casă", "image_url": "/images/casa.jpg", "category_id": created_categories["Locații"]},
        {"name": "Școală", "text": "Școală", "image_url": "/images/scoala.jpg", "category_id": created_categories["Locații"]},
        {"name": "Grădină", "text": "Grădină", "image_url": "/images/gradina.jpg", "category_id": created_categories["Locații"]},
        {"name": "Parc", "text": "Parc", "image_url": "/images/parc.jpg", "category_id": created_categories["Locații"]},
        {"name": "Spital", "text": "Spital", "image_url": "/images/spital.jpg", "category_id": created_categories["Locații"]},
        {"name": "Magazin", "text": "Magazin", "image_url": "/images/magazin.jpg", "category_id": created_categories["Locații"]},
        {"name": "Bucătărie", "text": "Bucătărie", "image_url": "/images/bucatarie.jpg", "category_id": created_categories["Locații"]},
        {"name": "Dormitor", "text": "Dormitor", "image_url": "/images/dormitor.jpg", "category_id": created_categories["Locații"]},
        {"name": "Baie", "text": "Baie", "image_url": "/images/baie.jpg", "category_id": created_categories["Locații"]},
        {"name": "Sufragerie", "text": "Sufragerie", "image_url": "/images/sufragerie.jpg", "category_id": created_categories["Locații"]},
        {"name": "Curte", "text": "Curte", "image_url": "/images/curte.jpg", "category_id": created_categories["Locații"]},
        {"name": "Plajă", "text": "Plajă", "image_url": "/images/plaja.jpg", "category_id": created_categories["Locații"]},
        {"name": "Pădure", "text": "Pădure", "image_url": "/images/padure.jpg", "category_id": created_categories["Locații"]},
        {"name": "Munte", "text": "Munte", "image_url": "/images/munte.jpg", "category_id": created_categories["Locații"]},
        {"name": "Lac", "text": "Lac", "image_url": "/images/lac.jpg", "category_id": created_categories["Locații"]},
        
        # Obiecte
        {"name": "Măsuță", "text": "Măsuță", "image_url": "/images/masuta.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Scaun", "text": "Scaun", "image_url": "/images/scaun.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Pat", "text": "Pat", "image_url": "/images/pat.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Jucărie", "text": "Jucărie", "image_url": "/images/jucarie.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Minge", "text": "Minge", "image_url": "/images/minge.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Cărți", "text": "Cărți", "image_url": "/images/carti.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Caiet", "text": "Caiet", "image_url": "/images/caiet.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Creion", "text": "Creion", "image_url": "/images/creion.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Pix", "text": "Pix", "image_url": "/images/pix.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Culori", "text": "Culori", "image_url": "/images/culori.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Telefon", "text": "Telefon", "image_url": "/images/telefon.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Tabletă", "text": "Tabletă", "image_url": "/images/tableta.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Televizor", "text": "Televizor", "image_url": "/images/televizor.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Lampă", "text": "Lampă", "image_url": "/images/lampa.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Ceas", "text": "Ceas", "image_url": "/images/ceas.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Haină", "text": "Haină", "image_url": "/images/haina.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Pantofi", "text": "Pantofi", "image_url": "/images/pantofi.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Șapcă", "text": "Șapcă", "image_url": "/images/sapca.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Cămașă", "text": "Cămașă", "image_url": "/images/camasa.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Pantaloni", "text": "Pantaloni", "image_url": "/images/pantaloni.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Rochie", "text": "Rochie", "image_url": "/images/rochie.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Tricou", "text": "Tricou", "image_url": "/images/tricou.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Farfurie", "text": "Farfurie", "image_url": "/images/farfurie.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Tacâmuri", "text": "Tacâmuri", "image_url": "/images/tacamuri.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Cană", "text": "Cană", "image_url": "/images/cana.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Pahar", "text": "Pahar", "image_url": "/images/pahar.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Autoturism", "text": "Mașină", "image_url": "/images/masina.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Bicicletă", "text": "Bicicletă", "image_url": "/images/bicicleta.jpg", "category_id": created_categories["Obiecte"]},
        {"name": "Trotinetă", "text": "Trotinetă", "image_url": "/images/trotineta.jpg", "category_id": created_categories["Obiecte"]},
    ]

    # Adaugă simbolurile (doar cele care nu există deja)
    symbols_added = 0
    symbols_skipped = 0
    
    for sym_data in symbols_data:
        # Verifică dacă simbolul există deja după nume
        existing_symbol = db.query(Symbol).filter(Symbol.name == sym_data["name"]).first()
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


