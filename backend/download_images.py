"""
Script pentru descărcarea automată a imaginilor reale pentru simboluri
Folosește Unsplash API pentru imagini gratuite și de calitate
"""
import requests
import os
from database import SessionLocal
from models import Symbol
from services import SymbolService

# Configurare Unsplash (opțional - poți folosi și alte surse)
UNSPLASH_ACCESS_KEY = None  # Opțional: obține de la https://unsplash.com/developers
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Alternativă: folosește Pexels (nu necesită API key pentru rate limit mic)
PEXELS_API_KEY = None  # Opțional: obține de la https://www.pexels.com/api/
PEXELS_API_URL = "https://api.pexels.com/v1/search"

# Fallback: folosește placeholder-uri simple sau imagini publice
FALLBACK_IMAGE_SOURCES = {
    # Poți adăuga aici URL-uri directe către imagini publice
    # sau să folosești un serviciu de imagini gratuite
}

def get_image_url_from_unsplash(query: str) -> str:
    """Obține URL-ul unei imagini de pe Unsplash"""
    if not UNSPLASH_ACCESS_KEY:
        return None
    
    try:
        response = requests.get(
            UNSPLASH_API_URL,
            params={
                "query": query,
                "per_page": 1,
                "orientation": "squarish"
            },
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                return data["results"][0]["urls"]["regular"]
    except:
        pass
    return None

def get_image_url_from_pexels(query: str) -> str:
    """Obține URL-ul unei imagini de pe Pexels"""
    if not PEXELS_API_KEY:
        return None
    
    try:
        response = requests.get(
            PEXELS_API_URL,
            params={"query": query, "per_page": 1},
            headers={"Authorization": PEXELS_API_KEY},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("photos"):
                return data["photos"][0]["src"]["medium"]
    except:
        pass
    return None

def get_fallback_image_url(query: str) -> str:
    """Obține un URL de fallback pentru imagine"""
    # Poți folosi un serviciu de imagini gratuite sau să returnezi None
    # Exemple: Pixabay, OpenClipart, etc.
    return None

def download_image_for_symbol(symbol: Symbol, db) -> bool:
    """Descarcă și salvează o imagine pentru un simbol"""
    try:
        # Construiește query-ul pentru căutare
        # Folosește numele simbolului sau textul
        query = symbol.name.lower()
        
        # Traduce sau adaptează query-ul pentru căutare în engleză (dacă e necesar)
        # De exemplu: "Mâncare" -> "food", "Fericit" -> "happy person"
        translation_map = {
            "mâncare": "food eating",
            "băutură": "drinking water",
            "dormit": "sleeping person",
            "fericit": "happy person smiling",
            "trist": "sad person",
            "supărat": "angry person",
            "mama": "mother woman",
            "tata": "father man",
            "prieten": "friend person",
            # Adaugă mai multe traduceri aici
        }
        
        search_query = translation_map.get(query, query)
        
        # Încearcă să obțină URL-ul imaginii
        image_url = None
        
        # 1. Încearcă Unsplash
        if UNSPLASH_ACCESS_KEY:
            image_url = get_image_url_from_unsplash(search_query)
        
        # 2. Încearcă Pexels
        if not image_url and PEXELS_API_KEY:
            image_url = get_image_url_from_pexels(search_query)
        
        # 3. Fallback
        if not image_url:
            image_url = get_fallback_image_url(search_query)
        
        if not image_url:
            print(f"  ⚠ Nu s-a găsit imagine pentru: {symbol.name}")
            return False
        
        # Descarcă și salvează imaginea
        image_path = SymbolService.download_and_save_image(
            image_url=image_url,
            custom_name=symbol.name
        )
        
        # Actualizează simbolul cu noua imagine
        SymbolService.update_image(db, symbol.id, image_path)
        
        print(f"  ✓ Imagine descărcată pentru: {symbol.name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Eroare la descărcarea imaginii pentru '{symbol.name}': {e}")
        return False

def main():
    """Funcția principală"""
    print("=" * 60)
    print("  Descărcare imagini pentru simboluri")
    print("=" * 60)
    print()
    
    # Verifică dacă există API keys
    if not UNSPLASH_ACCESS_KEY and not PEXELS_API_KEY:
        print("⚠ ATENȚIE: Nu ai configurat API keys pentru Unsplash sau Pexels")
        print("  Opțiuni:")
        print("  1. Obține un API key gratuit de la https://unsplash.com/developers")
        print("  2. Sau de la https://www.pexels.com/api/")
        print("  3. Sau folosește endpoint-ul /api/symbols/uploadimage pentru a încărca manual")
        print()
        response = input("Vrei să continui fără API keys? (da/nu): ")
        if response.lower() != 'da':
            return
    
    db = SessionLocal()
    try:
        # Obține toate simbolurile
        symbols = db.query(Symbol).all()
        
        if not symbols:
            print("Nu există simboluri în baza de date!")
            return
        
        print(f"Găsite {len(symbols)} simboluri în baza de date")
        print()
        
        # Procesează fiecare simbol
        success_count = 0
        fail_count = 0
        
        for symbol in symbols:
            print(f"Procesare: {symbol.name}...")
            if download_image_for_symbol(symbol, db):
                success_count += 1
            else:
                fail_count += 1
        
        print()
        print("=" * 60)
        print(f"  Rezumat:")
        print(f"  ✓ Imagini descărcate cu succes: {success_count}")
        print(f"  ✗ Erori: {fail_count}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Eroare: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
