"""
Script pentru asocierea automată a imaginilor din folder cu simbolurile din baza de date
Pune imaginile în backend/data/images/ și rulează acest script
"""
import os
import re
from database import SessionLocal
from models import Symbol
from services import SymbolService

def normalize_name(name: str) -> str:
    """Normalizează numele pentru matching (elimină diacritice, spații, etc.)"""
    # Elimină diacritice
    replacements = {
        'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't',
        'Ă': 'A', 'Â': 'A', 'Î': 'I', 'Ș': 'S', 'Ț': 'T'
    }
    normalized = name
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    # Convert la lowercase și elimină spații/special chars
    normalized = normalized.lower().strip()
    normalized = re.sub(r'[^a-z0-9]', '', normalized)
    return normalized

def find_matching_symbol(image_filename: str, symbols: list) -> Symbol:
    """Găsește simbolul care se potrivește cu numele imaginii"""
    # Extrage numele fără extensie
    image_name = os.path.splitext(image_filename)[0]
    image_normalized = normalize_name(image_name)
    
    best_match = None
    best_score = 0
    
    for symbol in symbols:
        symbol_normalized = normalize_name(symbol.name)
        
        # Verifică match exact
        if image_normalized == symbol_normalized:
            return symbol
        
        # Verifică dacă numele imaginii conține numele simbolului sau invers
        if image_normalized in symbol_normalized or symbol_normalized in image_normalized:
            score = min(len(image_normalized), len(symbol_normalized))
            if score > best_score:
                best_score = score
                best_match = symbol
    
    return best_match

def main():
    """Funcția principală"""
    print("=" * 60)
    print("  Asociere automată imagini cu simboluri")
    print("=" * 60)
    print()
    
    # Verifică dacă folderul există
    images_dir = "data/images"
    if not os.path.exists(images_dir):
        print(f"✗ Folderul {images_dir} nu există!")
        print(f"  Creează folderul și pune imaginile acolo.")
        return
    
    # Obține toate fișierele din folder
    image_files = [f for f in os.listdir(images_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
    
    if not image_files:
        print(f"✗ Nu s-au găsit imagini în {images_dir}!")
        print(f"  Pune imaginile în acest folder și încearcă din nou.")
        return
    
    print(f"✓ Găsite {len(image_files)} imagini în folder")
    print()
    
    db = SessionLocal()
    try:
        # Obține toate simbolurile
        symbols = db.query(Symbol).all()
        
        if not symbols:
            print("✗ Nu există simboluri în baza de date!")
            print("  Rulează mai întâi: python init_db.py")
            return
        
        print(f"✓ Găsite {len(symbols)} simboluri în baza de date")
        print()
        
        # Procesează fiecare imagine
        matched_count = 0
        updated_count = 0
        not_found = []
        
        print("Procesare imagini...")
        print("-" * 60)
        
        for image_file in image_files:
            # Construiește path-ul relativ
            image_path = f"/images/{image_file}"
            
            # Găsește simbolul potrivit
            symbol = find_matching_symbol(image_file, symbols)
            
            if symbol:
                # Verifică dacă simbolul are deja această imagine
                if symbol.image_url != image_path:
                    # Actualizează simbolul
                    SymbolService.update_image(db, symbol.id, image_path)
                    updated_count += 1
                    print(f"✓ {image_file:30} -> {symbol.name:20} (ID: {symbol.id})")
                else:
                    print(f"⊘ {image_file:30} -> {symbol.name:20} (deja asociat)")
                matched_count += 1
            else:
                not_found.append(image_file)
                print(f"✗ {image_file:30} -> (nu s-a găsit simbol potrivit)")
        
        print("-" * 60)
        print()
        print("=" * 60)
        print("  Rezumat:")
        print(f"  ✓ Imagini asociate: {matched_count}")
        print(f"  ✓ Simboluri actualizate: {updated_count}")
        if not_found:
            print(f"  ⚠ Imagini fără match: {len(not_found)}")
            print()
            print("  Imagini care nu s-au putut asocia:")
            for img in not_found:
                print(f"    - {img}")
                print(f"      Sugestie: verifică dacă numele se potrivește cu un simbol")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Eroare: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
