from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os
import shutil

from database import SessionLocal, engine, Base
from models import Category, Symbol, User, Child
from schemas import (CategoryCreate, CategoryResponse, SymbolCreate, SymbolResponse, 
                     UserCreate, UserResponse, TTSRequest, AddImageRequest, 
                     ChildCreate, ChildResponse)
from services import CategoryService, SymbolService, UserService, TTSService, ChildService

# Creează tabelele în baza de date
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AAC Communication System API", version="1.0.0")

# Configurează CORS pentru a permite conexiuni din Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # În producție, specifică domeniul exact
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency pentru a obține sesiunea de bază de date
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency pentru autentificare
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Token de autentificare lipsă")
    
    token = authorization.replace('Bearer ', '')
    user = UserService.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token invalid sau expirat")
    
    # Verifică dacă utilizatorul există în baza de date
    db_user = UserService.get_by_email(db, user['email'])
    if not db_user:
        raise HTTPException(status_code=401, detail="Utilizator inexistent")
    
    return db_user


# ============ ENDPOINTS PENTRU AUTENTIFICARE ============

@app.post("/api/auth/register")
def register(user_data: dict, db: Session = Depends(get_db)):
    """Înregistrează un nou terapeut"""
    try:
        name = user_data.get('name')
        email = user_data.get('email')
        password = user_data.get('password')
        
        if not name or not email or not password:
            raise HTTPException(status_code=400, detail="Toate câmpurile sunt obligatorii")
        
        # Verifică dacă email-ul există deja
        existing_user = UserService.get_by_email(db, email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email-ul este deja folosit")
        
        # Creează utilizatorul cu parolă
        user = UserService.create_with_password(db, name, email, password)
        
        # Generează token
        token = UserService.create_access_token(email)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la înregistrare: {str(e)}")


@app.post("/api/auth/login")
def login(credentials: dict, db: Session = Depends(get_db)):
    """Autentifică un terapeut"""
    try:
        email = credentials.get('email')
        password = credentials.get('password')
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email și parola sunt obligatorii")
        
        # Verifică credențialele
        user = UserService.authenticate(db, email, password)
        if not user:
            raise HTTPException(status_code=401, detail="Email sau parolă greșită")
        
        # Generează token
        token = UserService.create_access_token(email)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la autentificare: {str(e)}")


# ============ ENDPOINTS PENTRU COPII (Children) ============

@app.get("/api/children", response_model=List[ChildResponse])
def get_children(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obține toți copiii terapeutului autentificat"""
    return ChildService.get_all_for_therapist(db, current_user.id)


@app.post("/api/children", response_model=ChildResponse)
def create_child(child_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Creează un nou profil de copil"""
    name = child_data.get('name')
    if not name:
        raise HTTPException(status_code=400, detail="Numele copilului este obligatoriu")
    
    child_create = ChildCreate(name=name)
    return ChildService.create(db, current_user.id, child_create)


@app.delete("/api/children/{child_id}")
def delete_child(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Șterge un copil și toate datele asociate"""
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    db.delete(child)
    db.commit()
    return {"success": True}


@app.get("/api/children/{child_id}/categories", response_model=List[CategoryResponse])
def get_child_categories(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obține categoriile pentru un copil specific"""
    # Verifică dacă copilul aparține terapeutului
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    return CategoryService.get_all_for_child(db, child_id)


@app.get("/api/children/{child_id}/symbols", response_model=List[SymbolResponse])
def get_child_symbols(
    child_id: int,
    category_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obține simbolurile pentru un copil specific"""
    # Verifică dacă copilul aparține terapeutului
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    return SymbolService.get_for_child(db, child_id, category_id)


@app.get("/api/children/{child_id}/favorites", response_model=List[SymbolResponse])
def get_child_favorites(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obține simbolurile favorite ale unui copil"""
    # Verifică dacă copilul aparține terapeutului
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    return SymbolService.get_favorites_for_child(db, child_id)


@app.post("/api/children/{child_id}/favorites/{symbol_id}")
def add_child_favorite(
    child_id: int,
    symbol_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adaugă un simbol la favoritele unui copil"""
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    ChildService.add_favorite(db, child_id, symbol_id)
    return {"success": True}


@app.delete("/api/children/{child_id}/favorites/{symbol_id}")
def remove_child_favorite(
    child_id: int,
    symbol_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Șterge un simbol din favoritele unui copil"""
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    ChildService.remove_favorite(db, child_id, symbol_id)
    return {"success": True}


@app.post("/api/children/{child_id}/categories", response_model=CategoryResponse)
def create_child_category(
    child_id: int,
    category_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creează o nouă categorie pentru un copil"""
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    name = category_data.get('name')
    if not name:
        raise HTTPException(status_code=400, detail="Numele categoriei este obligatoriu")
    
    category = Category(name=name, child_id=child_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.delete("/api/children/{child_id}/categories/{category_id}")
def delete_child_category(
    child_id: int,
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Șterge o categorie a unui copil"""
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.child_id == child_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Categoria nu a fost găsită")
    
    db.delete(category)
    db.commit()
    return {"success": True}


@app.post("/api/children/{child_id}/symbols", response_model=SymbolResponse)
def create_child_symbol(
    child_id: int,
    symbol_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creează un nou simbol pentru un copil"""
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    name = symbol_data.get('name')
    text = symbol_data.get('text')
    image_url = symbol_data.get('image_url')
    category_id = symbol_data.get('category_id')
    
    if not all([name, text, image_url, category_id]):
        raise HTTPException(status_code=400, detail="Toate câmpurile sunt obligatorii")
    
    symbol = Symbol(
        name=name,
        text=text,
        image_url=image_url,
        category_id=category_id,
        child_id=child_id
    )
    db.add(symbol)
    db.commit()
    db.refresh(symbol)
    return symbol


@app.post("/api/children/{child_id}/symbols/upload", response_model=SymbolResponse)
async def create_child_symbol_with_upload(
    child_id: int,
    name: str = Form(...),
    text: str = Form(...),
    category_id: int = Form(...),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creează un nou simbol pentru un copil cu imagine încărcată"""
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    # Salvează imaginea încărcată
    try:
        image_url = SymbolService.save_uploaded_file(image, custom_name=name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la salvarea imaginii: {str(e)}")
    
    # Creează simbolul
    symbol = Symbol(
        name=name,
        text=text,
        image_url=image_url,
        category_id=category_id,
        child_id=child_id
    )
    db.add(symbol)
    db.commit()
    db.refresh(symbol)
    return symbol


@app.delete("/api/children/{child_id}/symbols/{symbol_id}")
def delete_child_symbol(
    child_id: int,
    symbol_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Șterge un simbol al unui copil"""
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    success = SymbolService.delete_for_child(db, child_id, symbol_id)
    if not success:
        raise HTTPException(status_code=404, detail="Simbolul nu a fost găsit")
    
    return {"success": True}


@app.post("/api/children/{child_id}/symbols/reorder")
def reorder_child_symbols(
    child_id: int,
    items: List[dict],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reordonează simbolurile unui copil"""
    child = ChildService.get_by_id(db, child_id)
    if not child or child.therapist_id != current_user.id:
        raise HTTPException(status_code=404, detail="Copilul nu a fost găsit")
    
    for item in items:
        symbol_id = item.get('symbol_id')
        new_order = item.get('new_order')
        if symbol_id and new_order is not None:
            symbol = db.query(Symbol).filter(
                Symbol.id == symbol_id,
                Symbol.child_id == child_id
            ).first()
            if symbol:
                symbol.display_order = new_order
    
    db.commit()
    return {"success": True}


# ============ ENDPOINTS PENTRU CATEGORII ============

@app.get("/api/categories", response_model=List[CategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obține toate categoriile"""
    return CategoryService.get_all(db, skip=skip, limit=limit)


@app.get("/api/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Obține o categorie specifică"""
    category = CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria nu a fost găsită")
    return category


@app.post("/api/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Creează o nouă categorie (BLOCAT - nu permite categorii globale)"""
    # Blochează crearea de categorii globale - doar admin ar trebui să poată face asta
    raise HTTPException(
        status_code=403, 
        detail="Crearea de categorii globale este dezactivată. Folosește endpoint-ul pentru copii."
    )


# ============ ENDPOINTS PENTRU SIMBOLURI ============

@app.get("/api/symbols", response_model=List[SymbolResponse])
def get_symbols(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obține simboluri, opțional filtrate după categorie sau căutare"""
    if category_id:
        return SymbolService.get_by_category(db, category_id, skip=skip, limit=limit)
    if search:
        return SymbolService.search(db, search, skip=skip, limit=limit)
    return SymbolService.get_all(db, skip=skip, limit=limit)


@app.get("/api/symbols/{symbol_id}", response_model=SymbolResponse)
def get_symbol(symbol_id: int, db: Session = Depends(get_db)):
    """Obține un simbol specific"""
    symbol = SymbolService.get_by_id(db, symbol_id)
    if not symbol:
        raise HTTPException(status_code=404, detail="Simbolul nu a fost găsit")
    return symbol


@app.post("/api/symbols", response_model=SymbolResponse)
def create_symbol(symbol: SymbolCreate, db: Session = Depends(get_db)):
    """Creează un nou simbol"""
    return SymbolService.create(db, symbol)


@app.post("/api/symbols/addimage")
def add_image_from_url(request: AddImageRequest, db: Session = Depends(get_db)):
    """
    Descarcă o imagine de la un URL și o asociază cu un simbol existent din baza de date.
    
    Parametri:
    - image_url: URL-ul imaginii de descărcat (obligatoriu)
    - symbol_id: ID-ul simbolului existent din baza de date (obligatoriu)
    - image_name: Nume opțional pentru fișierul imaginii
    
    Exemplu de URL: "https://example.com/image.jpg"
    """
    try:
        if not request.image_url:
            raise HTTPException(status_code=400, detail="URL-ul imaginii este obligatoriu")
        
        if not request.symbol_id:
            raise HTTPException(status_code=400, detail="symbol_id este obligatoriu")
        
        # Verifică dacă simbolul există
        symbol = SymbolService.get_by_id(db, request.symbol_id)
        if not symbol:
            raise HTTPException(
                status_code=404, 
                detail=f"Simbolul cu ID-ul {request.symbol_id} nu a fost găsit în baza de date"
            )
        
        # Descarcă și salvează imaginea (folosește numele simbolului dacă nu se dă image_name)
        image_path = SymbolService.download_and_save_image(
            image_url=request.image_url,
            custom_name=request.image_name or symbol.name
        )
        
        # Actualizează simbolul cu noua imagine
        updated_symbol = SymbolService.update_image(db, request.symbol_id, image_path)
        
        return {
            "success": True,
            "symbol_id": updated_symbol.id,
            "symbol_name": updated_symbol.name,
            "image_path": image_path,
            "message": f"Imaginea a fost descărcată și asociată cu simbolul '{updated_symbol.name}' (ID: {updated_symbol.id})"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la adăugarea imaginii: {str(e)}")


@app.post("/api/symbols/uploadimage")
async def upload_image_file(
    file: UploadFile = File(...),
    symbol_id: int = Form(...),
    image_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Încarcă direct un fișier imagine și îl asociază cu un simbol existent din baza de date.
    
    Parametri (form-data):
    - file: Fișierul imagine de încărcat (obligatoriu)
    - symbol_id: ID-ul simbolului existent din baza de date (obligatoriu)
    - image_name: Nume opțional pentru fișierul imaginii
    
    Exemplu de utilizare:
    - Form-data cu cheia "file" = fișierul tău
    - Form-data cu cheia "symbol_id" = 5
    - Form-data cu cheia "image_name" = "nume_imagine" (opțional)
    """
    try:
        # Verifică tipul fișierului
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Fișierul trebuie să fie o imagine")
        
        # Verifică dacă simbolul există
        symbol = SymbolService.get_by_id(db, symbol_id)
        if not symbol:
            raise HTTPException(
                status_code=404, 
                detail=f"Simbolul cu ID-ul {symbol_id} nu a fost găsit în baza de date"
            )
        
        # Salvează fișierul (folosește numele simbolului dacă nu se dă image_name)
        image_path = SymbolService.save_uploaded_file(
            file=file,
            custom_name=image_name or symbol.name
        )
        
        # Actualizează simbolul cu noua imagine
        updated_symbol = SymbolService.update_image(db, symbol_id, image_path)
        
        return {
            "success": True,
            "symbol_id": updated_symbol.id,
            "symbol_name": updated_symbol.name,
            "image_path": image_path,
            "message": f"Imaginea a fost încărcată și asociată cu simbolul '{updated_symbol.name}' (ID: {updated_symbol.id})"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la încărcarea imaginii: {str(e)}")


# ============ ENDPOINTS PENTRU UTILIZATORI ============

@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Creează un nou utilizator"""
    return UserService.create(db, user)


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Obține un utilizator specific"""
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilizatorul nu a fost găsit")
    return user


# ============ ENDPOINTS PENTRU TEXT-TO-SPEECH ============

@app.post("/api/tts/speak")
def text_to_speech(request: TTSRequest):
    """Convertește text în vorbire folosind vocea specificată"""
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="Textul este obligatoriu")
        audio_url = TTSService.speak(request.text, voice=request.voice)
        return {"audio_url": audio_url, "text": request.text, "voice": request.voice or "ro-RO-EmilNeural"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la generarea vorbirii: {str(e)}")


# Creează directoarele necesare dacă nu există
os.makedirs("data/audio", exist_ok=True)
os.makedirs("data/images", exist_ok=True)

# Servire fișiere statice pentru audio
app.mount("/audio", StaticFiles(directory="data/audio"), name="audio")

# Servire fișiere statice pentru imagini
app.mount("/images", StaticFiles(directory="data/images"), name="images")

@app.get("/")
def root():
    """Endpoint de test"""
    return {"message": "AAC Communication System API", "status": "running"}


if __name__ == "__main__":
    import socket
    import webbrowser
    import threading
    import time
    
    # Obține IP-ul local pentru afișare
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    local_ip = get_local_ip()
    print("\n" + "="*60)
    print("  AAC Communication System API")
    print("="*60)
    print(f"  Serverul rulează pe:")
    print(f"  - Local:   http://localhost:8000")
    print(f"  - Rețea:   http://{local_ip}:8000")
    print(f"  - Docs:    http://localhost:8000/docs")
    print("="*60 + "\n")
    
    # Funcție pentru a deschide browserul după ce serverul pornește
    def open_browser():
        # Așteaptă mai mult pentru ca serverul să fie complet pornit
        time.sleep(2.5)
        try:
            # Verifică dacă serverul răspunde înainte de a deschide browserul
            import urllib.request
            try:
                urllib.request.urlopen("http://localhost:8000/", timeout=2)
            except:
                pass  # Continuă oricum
            
            webbrowser.open("http://localhost:8000/docs")
            print("  ✓ Browser deschis automat la http://localhost:8000/docs\n")
        except Exception as e:
            print(f"  ⚠ Nu s-a putut deschide browserul automat: {e}\n")
            print("  → Deschide manual: http://localhost:8000/docs\n")
    
    # Pornește thread-ul pentru deschiderea browserului
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n\n  Server oprit de utilizator.\n")

