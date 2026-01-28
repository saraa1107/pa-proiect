from sqlalchemy.orm import Session
from typing import List, Optional
from models import Category, Symbol, User, Child, FavoriteSymbol
from schemas import CategoryCreate, SymbolCreate, UserCreate, ChildCreate, SymbolReorderItem
from fastapi import UploadFile, HTTPException
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import uuid
import shutil
from gtts import gTTS
import io
import base64
import requests
from urllib.parse import urlparse
from pathlib import Path

# Configurare pentru hash-ul parolelor (bcrypt direct, fără passlib – evită 72-byte limit bug)


def _password_to_bcrypt_bytes(password: str) -> bytes:
    """Bcrypt acceptă max 72 octeți. Returnează parola ca bytes, trunchiată dacă e cazul."""
    if not isinstance(password, str):
        password = str(password)
    pw_bytes = password.encode("utf-8")
    return pw_bytes[:72] if len(pw_bytes) > 72 else pw_bytes

# Configurare JWT
SECRET_KEY = "aac-communication-secret-key-2024-change-in-production"  # În producție, folosește o cheie sigură
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 zile


class CategoryService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
        """Categorii globale (child_id is None)."""
        return db.query(Category).filter(Category.child_id.is_(None)).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def get_all_for_child(db: Session, child_id: int, skip: int = 0, limit: int = 100) -> List[Category]:
        """
        Categorii pentru un copil.
        Dacă copilul are categorii proprii, returnează doar pe acelea.
        Altfel, returnează categoriile globale.
        """
        # Verifică dacă copilul are categorii proprii
        child_categories = db.query(Category).filter(Category.child_id == child_id).all()
        
        if child_categories:
            # Copilul are categorii proprii, returnează doar pe acelea
            return child_categories[skip:skip+limit] if limit else child_categories[skip:]
        else:
            # Copilul nu are categorii proprii, returnează cele globale
            global_categories = db.query(Category).filter(Category.child_id.is_(None)).all()
            return global_categories[skip:skip+limit] if limit else global_categories[skip:]

    @staticmethod
    def create(db: Session, category: CategoryCreate) -> Category:
        # Evită duplicatele pe combinația (name, child_id) – global sau per copil
        query = db.query(Category).filter(Category.name == category.name)
        
        # Verifică child_id explicit - None pentru categorii globale, ID pentru copil
        if category.child_id is None:
            query = query.filter(Category.child_id.is_(None))
        else:
            query = query.filter(Category.child_id == category.child_id)
        
        existing = query.first()
        if existing:
            return existing

        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def delete_for_child(db: Session, child_id: int, category_id: int) -> bool:
        """
        Șterge o categorie care aparține unui copil (mod terapeut).
        Nu atinge categoriile globale.
        """
        cat = (
            db.query(Category)
            .filter(Category.id == category_id, Category.child_id == child_id)
            .first()
        )
        if not cat:
            return False
        db.delete(cat)
        db.commit()
        return True


class SymbolService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Symbol]:
        """Simboluri globale (child_id is None)."""
        return db.query(Symbol).filter(Symbol.child_id.is_(None)).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, symbol_id: int) -> Optional[Symbol]:
        return db.query(Symbol).filter(Symbol.id == symbol_id).first()

    @staticmethod
    def get_by_category(db: Session, category_id: int, skip: int = 0, limit: int = 100) -> List[Symbol]:
        """Simboluri globale din categoria dată."""
        q = db.query(Symbol).filter(
            Symbol.category_id == category_id,
            Symbol.child_id.is_(None),
        )
        q = q.order_by(Symbol.display_order.asc(), Symbol.id.asc())
        return q.offset(skip).limit(limit).all()

    @staticmethod
    def get_by_category_for_child(db: Session, child_id: int, category_id: int, skip: int = 0, limit: int = 100) -> List[Symbol]:
        """
        Simbolurile dintr-o anumită categorie pentru un copil.
        Dacă copilul are simboluri proprii în categoria aia, returnează doar pe acelea.
        Altfel, returnează simbolurile globale din categoria respectivă.
        """
        # Verifică dacă copilul are simboluri proprii în categoria respectivă
        child_symbols = db.query(Symbol).filter(
            Symbol.category_id == category_id,
            Symbol.child_id == child_id
        ).order_by(Symbol.display_order.asc(), Symbol.id.asc()).all()
        
        if child_symbols:
            # Copilul are simboluri proprii în această categorie
            return child_symbols[skip:skip+limit] if limit else child_symbols[skip:]
        else:
            # Returnează simbolurile globale din această categorie
            global_symbols = db.query(Symbol).filter(
                Symbol.category_id == category_id,
                Symbol.child_id.is_(None)
            ).order_by(Symbol.display_order.asc(), Symbol.id.asc()).all()
            return global_symbols[skip:skip+limit] if limit else global_symbols[skip:]

    @staticmethod
    def get_all_for_child(db: Session, child_id: int, skip: int = 0, limit: int = 100) -> List[Symbol]:
        """
        Toate simbolurile copilului. 
        Dacă copilul are simboluri proprii, returnează doar pe acelea.
        Altfel, returnează simbolurile globale (tabla de bază).
        """
        # Verifică dacă copilul are simboluri proprii
        child_symbols = db.query(Symbol).filter(Symbol.child_id == child_id).all()
        
        if child_symbols:
            # Copilul are simboluri proprii, returnează doar pe acelea
            return child_symbols[skip:skip+limit] if limit else child_symbols[skip:]
        else:
            # Copilul nu are simboluri proprii, returnează cele globale
            global_symbols = db.query(Symbol).filter(Symbol.child_id.is_(None)).order_by(Symbol.display_order.asc(), Symbol.id.asc()).all()
            return global_symbols[skip:skip+limit] if limit else global_symbols[skip:]

    @staticmethod
    def get_for_child(db: Session, child_id: int, category_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Symbol]:
        """Obține simboluri pentru un copil, opțional filtrate după categorie"""
        if category_id:
            return SymbolService.get_by_category_for_child(db, child_id, category_id, skip, limit)
        return SymbolService.get_all_for_child(db, child_id, skip, limit)

    @staticmethod
    def get_favorites_for_child(db: Session, child_id: int) -> List[Symbol]:
        """Obține simbolurile favorite ale unui copil"""
        return ChildService.get_favorite_symbols(db, child_id)

    @staticmethod
    def search(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Symbol]:
        search_pattern = f"%{search_term}%"
        return db.query(Symbol).filter(
            Symbol.child_id.is_(None),
            (Symbol.name.ilike(search_pattern)) | (Symbol.text.ilike(search_pattern))
        ).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, symbol: SymbolCreate) -> Symbol:
        d = symbol.dict()

        # Evită duplicatele pe (name, category_id, child_id)
        query = db.query(Symbol).filter(
            Symbol.name == d["name"],
            Symbol.category_id == d["category_id"],
        )
        
        # Verifică child_id explicit - None pentru simboluri globale, ID pentru copil
        if d.get("child_id") is None:
            query = query.filter(Symbol.child_id.is_(None))
        else:
            query = query.filter(Symbol.child_id == d.get("child_id"))
        
        existing = query.first()
        if existing:
            return existing

        db_symbol = Symbol(**d)
        db.add(db_symbol)
        db.commit()
        db.refresh(db_symbol)
        return db_symbol

    @staticmethod
    def reorder_for_child(db: Session, child_id: int, items: List[SymbolReorderItem]) -> None:
        """Actualizează display_order pentru simbolurile copilului."""
        for it in items:
            s = db.query(Symbol).filter(Symbol.id == it.symbol_id, Symbol.child_id == child_id).first()
            if s:
                s.display_order = it.display_order
        db.commit()

    @staticmethod
    def increment_usage(db: Session, symbol_id: int):
        symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
        if symbol:
            symbol.usage_count += 1
            db.commit()

    @staticmethod
    def delete_for_child(db: Session, child_id: int, symbol_id: int) -> bool:
        """
        Șterge un simbol care aparține unui copil (mod terapeut).
        Nu atinge simbolurile globale.
        """
        symbol = (
            db.query(Symbol)
            .filter(Symbol.id == symbol_id, Symbol.child_id == child_id)
            .first()
        )
        if not symbol:
            return False
        db.delete(symbol)
        db.commit()
        return True

    @staticmethod
    def update_image(db: Session, symbol_id: int, image_path: str) -> Symbol:
        """Actualizează imaginea unui simbol existent"""
        symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
        if not symbol:
            raise Exception(f"Simbolul cu ID-ul {symbol_id} nu a fost găsit")
        symbol.image_url = image_path
        db.commit()
        db.refresh(symbol)
        return symbol

    @staticmethod
    def save_uploaded_file(file: UploadFile, custom_name: Optional[str] = None) -> str:
        """
        Salvează un fișier încărcat direct.
        Returnează path-ul relativ al imaginii salvate.
        """
        try:
            # Creează directorul pentru imagini dacă nu există
            images_dir = "data/images"
            os.makedirs(images_dir, exist_ok=True)
            
            # Determină extensia din numele fișierului
            original_filename = file.filename or "image"
            ext = os.path.splitext(original_filename)[1] or '.jpg'
            
            # Generează numele fișierului
            if custom_name:
                # Elimină caractere invalide din nume
                safe_name = "".join(c for c in custom_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                filename = f"{safe_name}{ext}"
            else:
                # Folosește numele original sau generează unul unic
                safe_original = "".join(c for c in os.path.splitext(original_filename)[0] if c.isalnum() or c in (' ', '-', '_')).strip()
                if safe_original:
                    filename = f"{safe_original.replace(' ', '_')}{ext}"
                else:
                    filename = f"{uuid.uuid4().hex}{ext}"
            
            # Salvează fișierul
            filepath = os.path.join(images_dir, filename)
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            
            # Returnează path-ul relativ pentru a fi servit de server
            return f"/images/{filename}"
            
        except Exception as e:
            raise Exception(f"Eroare la salvarea fișierului: {str(e)}")

    @staticmethod
    def download_and_save_image(image_url: str, custom_name: Optional[str] = None) -> str:
        """
        Descarcă o imagine de la un URL și o salvează local.
        Returnează path-ul relativ al imaginii salvate.
        """
        try:
            # Creează directorul pentru imagini dacă nu există
            images_dir = "data/images"
            os.makedirs(images_dir, exist_ok=True)
            
            # Descarcă imaginea
            response = requests.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Determină extensia fișierului
            parsed_url = urlparse(image_url)
            path = parsed_url.path
            ext = os.path.splitext(path)[1] or '.jpg'  # Default la .jpg dacă nu există extensie
            
            # Generează numele fișierului
            if custom_name:
                # Elimină caractere invalide din nume
                safe_name = "".join(c for c in custom_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                filename = f"{safe_name}{ext}"
            else:
                # Generează un nume unic
                filename = f"{uuid.uuid4().hex}{ext}"
            
            # Salvează imaginea
            filepath = os.path.join(images_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Returnează path-ul relativ pentru a fi servit de server
            return f"/images/{filename}"
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Eroare la descărcarea imaginii: {str(e)}")
        except Exception as e:
            raise Exception(f"Eroare la salvarea imaginii: {str(e)}")

    @staticmethod
    def auto_fetch_image_for_word(word: str) -> Optional[str]:
        """
        Caută automat o imagine ilustrată/colorată pentru un cuvânt,
        folosind un API de căutare imagini (ex: Bing Image Search).

        IMPORTANT:
        - Necesită variabila de mediu BING_IMAGE_SEARCH_KEY setată cu cheia API.
        - Nu garantează 100% imagini „tip AAC”, dar query-ul este optimizat
          pentru pictograme / desene simple, colorate.
        """
        api_key = os.getenv("BING_IMAGE_SEARCH_KEY")
        if not api_key:
            # Fără cheie, nu încercăm nimic – caller-ul va folosi fallback-ul existent
            return None

        try:
            endpoint = "https://api.bing.microsoft.com/v7.0/images/search"
            # Căutăm termeni orientați spre pictograme / desene pentru copii
            query = f"{word} pictograma desen colorat copii"
            headers = {
                "Ocp-Apim-Subscription-Key": api_key,
            }
            params = {
                "q": query,
                "safeSearch": "Strict",
                "imageType": "Clipart",  # favorizează ilustrații
                "size": "Medium",
                "count": 10,
            }

            resp = requests.get(endpoint, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("value") or []
            if not results:
                return None

            # Alege primul rezultat „rezonabil” (minim ~200x200 dacă există info)
            chosen_url = None
            for item in results:
                try:
                    w = int(item.get("width") or 0)
                    h = int(item.get("height") or 0)
                    if w >= 200 and h >= 200:
                        chosen_url = item.get("contentUrl")
                        break
                except Exception:
                    continue

            if not chosen_url:
                chosen_url = results[0].get("contentUrl")

            if not chosen_url:
                return None

            # Salvează local, folosind deja utilitarul existent
            return SymbolService.download_and_save_image(chosen_url, custom_name=word)

        except Exception as e:
            # Nu oprim fluxul doar pentru că nu am găsit imagine – log și fallback
            print(f"[auto_fetch_image_for_word] Eroare pentru '{word}': {e}")
            return None


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create(db: Session, user: UserCreate) -> User:
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash-uiește o parolă (trunchiată la 72 octeți, limită bcrypt)."""
        pw = _password_to_bcrypt_bytes(password)
        return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifică dacă parola este corectă."""
        if not hashed_password:
            return False
        pw = _password_to_bcrypt_bytes(plain_password)
        return bcrypt.checkpw(pw, hashed_password.encode("utf-8"))

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Autentifică un utilizator"""
        user = UserService.get_by_email(db, email)
        if not user:
            return None
        if not UserService.verify_password(password, user.password_hash or ""):
            return None
        return user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        """Alias pentru authenticate_user"""
        return UserService.authenticate_user(db, email, password)

    @staticmethod
    def create_access_token(email: str, expires_delta: Optional[timedelta] = None) -> str:
        """Creează un JWT token"""
        to_encode = {"sub": email, "email": email}
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verifică un JWT token și returnează datele utilizatorului"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("email")
            if email is None:
                return None
            return {"email": email}
        except JWTError:
            return None

    @staticmethod
    def create_with_password(db: Session, name: str, email: str, password: str) -> User:
        """Creează un utilizator nou cu parolă"""
        password_hash = UserService.hash_password(password)
        db_user = User(name=name, email=email, password_hash=password_hash)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        return encoded_jwt

    @staticmethod
    def register_user(db: Session, name: str, email: str, password: str) -> User:
        """Înregistrează un nou utilizator sau actualizează unul existent fără parolă"""
        # Verifică dacă email-ul există deja
        existing_user = UserService.get_by_email(db, email)
        
        if existing_user:
            # Dacă utilizatorul există dar nu are parolă, actualizează parola
            if not existing_user.password_hash:
                existing_user.password_hash = UserService.hash_password(password)
                existing_user.name = name  # Actualizează și numele dacă e necesar
                db.commit()
                db.refresh(existing_user)
                return existing_user
            else:
                # Utilizatorul există și are deja parolă
                raise HTTPException(status_code=400, detail="Email-ul este deja înregistrat. Folosește autentificare.")
        
        # Creează utilizatorul nou cu parola hash-uită
        password_hash = UserService.hash_password(password)
        db_user = User(
            name=name,
            email=email,
            password_hash=password_hash
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


class ChildService:
    @staticmethod
    def get_by_therapist(db: Session, therapist_id: int) -> List[Child]:
        return db.query(Child).filter(Child.therapist_id == therapist_id).all()

    @staticmethod
    def get_all_for_therapist(db: Session, therapist_id: int) -> List[Child]:
        """Alias pentru get_by_therapist"""
        return ChildService.get_by_therapist(db, therapist_id)

    @staticmethod
    def get_by_id(db: Session, child_id: int) -> Optional[Child]:
        return db.query(Child).filter(Child.id == child_id).first()

    @staticmethod
    def create(db: Session, therapist_id: int, data: ChildCreate) -> Child:
        """
        Creează un copil nou și îi copiază automat tabla de bază
        (toate categoriile și simbolurile globale – child_id is None).
        """
        from sqlalchemy.exc import IntegrityError
        
        # 0. Verifică dacă există deja un copil cu același nume pentru acest terapeut
        existing_child = db.query(Child).filter(
            Child.name == data.name,
            Child.therapist_id == therapist_id
        ).first()
        
        if existing_child:
            # Returnează copilul existent în loc să creezi unul nou
            return existing_child
        
        # 1. Creează copilul
        child = Child(therapist_id=therapist_id, name=data.name)
        db.add(child)
        try:
            db.commit()
            db.refresh(child)
        except IntegrityError:
            db.rollback()
            # Dacă a apărut o eroare de duplicate, returnează copilul existent
            existing_child = db.query(Child).filter(
                Child.name == data.name,
                Child.therapist_id == therapist_id
            ).first()
            if existing_child:
                return existing_child
            raise

        # 2. Verifică dacă copilul are deja categorii (poate că a fost creat anterior și a eșuat)
        existing_categories = db.query(Category).filter(Category.child_id == child.id).all()
        
        if existing_categories:
            # Copilul are deja categorii, nu mai copia
            return child

        # 3. Copiază categoriile globale (child_id is None) pentru acest copil
        # Ia doar categoriile DISTINCTE după nume pentru a evita duplicatele
        base_categories = db.query(Category).filter(Category.child_id.is_(None)).all()
        
        # Elimină duplicatele - păstrează doar prima categorie pentru fiecare nume
        seen_names = set()
        unique_base_categories = []
        for cat in base_categories:
            if cat.name not in seen_names:
                seen_names.add(cat.name)
                unique_base_categories.append(cat)
        
        category_id_map = {}  # mapare: categorie_baza_id -> categorie_noua_id

        for base_cat in unique_base_categories:
            try:
                # Creează categoria nouă
                new_cat = Category(
                    name=base_cat.name,
                    description=base_cat.description,
                    icon=base_cat.icon,
                    color=base_cat.color,
                    child_id=child.id,
                )
                db.add(new_cat)
                db.flush()
                category_id_map[base_cat.id] = new_cat.id
            except IntegrityError:
                # Categoria există deja, caută-o și folosește-o
                db.rollback()
                existing_cat = db.query(Category).filter(
                    Category.name == base_cat.name,
                    Category.child_id == child.id
                ).first()
                if existing_cat:
                    category_id_map[base_cat.id] = existing_cat.id

        # Mapează și categoriile duplicate la noile categorii create
        # Pentru a permite copierea simbolurilor care ar putea fi legate de duplicate
        for cat in base_categories:
            if cat.id not in category_id_map and cat.name in [bc.name for bc in unique_base_categories]:
                # Găsește categoria nouă corespunzătoare după nume
                new_cat = db.query(Category).filter(
                    Category.name == cat.name,
                    Category.child_id == child.id
                ).first()
                if new_cat:
                    category_id_map[cat.id] = new_cat.id

        # 4. Copiază simbolurile globale (child_id is None) pentru acest copil,
        #    legându-le de noile categorii ale copilului
        base_symbols = db.query(Symbol).filter(Symbol.child_id.is_(None)).all()

        for base_sym in base_symbols:
            # Dacă simbolul aparține unei categorii care nu a fost copiată
            new_cat_id = category_id_map.get(base_sym.category_id)
            if not new_cat_id:
                continue

            try:
                # Creează simbolul nou
                new_sym = Symbol(
                    name=base_sym.name,
                    text=base_sym.text,
                    image_url=base_sym.image_url,
                    category_id=new_cat_id,
                    child_id=child.id,
                    display_order=base_sym.display_order,
                    usage_count=0,
                )
                db.add(new_sym)
            except IntegrityError:
                # Simbolul există deja, ignoră
                db.rollback()
                continue

        # 5. Commit final pentru toate categoriile și simbolurile copilului
        try:
            db.commit()
        except IntegrityError:
            # Dacă mai apar duplicate la commit, fă rollback
            db.rollback()
        
        db.refresh(child)
        return child

    @staticmethod
    def update(db: Session, child_id: int, therapist_id: int, name: str) -> Optional[Child]:
        child = db.query(Child).filter(Child.id == child_id, Child.therapist_id == therapist_id).first()
        if not child:
            return None
        child.name = name
        db.commit()
        db.refresh(child)
        return child

    @staticmethod
    def delete(db: Session, child_id: int, therapist_id: int) -> bool:
        child = db.query(Child).filter(Child.id == child_id, Child.therapist_id == therapist_id).first()
        if not child:
            return False
        db.delete(child)
        db.commit()
        return True

    @staticmethod
    def get_favorite_symbols(db: Session, child_id: int) -> List[Symbol]:
        rows = db.query(FavoriteSymbol).filter(FavoriteSymbol.child_id == child_id).all()
        out = []
        for r in rows:
            s = SymbolService.get_by_id(db, r.symbol_id)
            if s:
                out.append(s)
        return out

    @staticmethod
    def add_favorite(db: Session, child_id: int, symbol_id: int) -> bool:
        existing = db.query(FavoriteSymbol).filter(
            FavoriteSymbol.child_id == child_id,
            FavoriteSymbol.symbol_id == symbol_id,
        ).first()
        if existing:
            return True
        fav = FavoriteSymbol(child_id=child_id, symbol_id=symbol_id)
        db.add(fav)
        db.commit()
        return True

    @staticmethod
    def remove_favorite(db: Session, child_id: int, symbol_id: int) -> bool:
        r = db.query(FavoriteSymbol).filter(
            FavoriteSymbol.child_id == child_id,
            FavoriteSymbol.symbol_id == symbol_id,
        ).first()
        if not r:
            return False
        db.delete(r)
        db.commit()
        return True

    @staticmethod
    def is_favorite(db: Session, child_id: int, symbol_id: int) -> bool:
        return db.query(FavoriteSymbol).filter(
            FavoriteSymbol.child_id == child_id,
            FavoriteSymbol.symbol_id == symbol_id,
        ).first() is not None


class TTSService:
    @staticmethod
    def speak(text: str, voice: Optional[str] = None) -> str:
        """Generează audio pentru text în limba română și returnează URL-ul"""
        try:
            # Creează directorul pentru audio dacă nu există
            os.makedirs("data/audio", exist_ok=True)
            
            # Generează un nume unic pentru fișier
            filename = f"{uuid.uuid4().hex}.mp3"
            filepath = f"data/audio/{filename}"
            
            # Încearcă mai întâi cu edge-tts (Microsoft Edge TTS - voci excelente pentru română)
            try:
                import edge_tts
                import asyncio
                
                async def generate_with_edge():
                    # Voci disponibile pentru română:
                    # - ro-RO-EmilNeural (masculină, naturală și clară) - RECOMANDAT
                    # - ro-RO-AlinaNeural (feminină, naturală și clară)
                    # EmilNeural oferă o pronunție excelentă pentru cuvintele românești
                    selected_voice = voice or "ro-RO-EmilNeural"  # Folosește vocea dată sau default masculină
                    communicate = edge_tts.Communicate(text, selected_voice)
                    await communicate.save(filepath)
                
                # Rulează funcția async
                asyncio.run(generate_with_edge())
                return f"/audio/{filename}"
            except ImportError:
                # Dacă edge-tts nu este instalat, folosește gTTS
                pass
            except Exception as e:
                print(f"Eroare cu edge-tts, încerc gTTS: {e}")
            
            # Fallback la gTTS (Google Text-to-Speech) cu configurație optimizată pentru română
            try:
                # Folosește 'ro' pentru română, cu viteză normală pentru claritate
                tts = gTTS(text=text, lang='ro', slow=False, tld='ro')
                tts.save(filepath)
                return f"/audio/{filename}"
            except Exception as e:
                print(f"Eroare cu gTTS: {e}")
                raise
            
        except Exception as e:
            # Fallback final la pyttsx3 dacă niciunul nu funcționează
            try:
                import pyttsx3
                engine = pyttsx3.init()
                
                # Încearcă să seteze o voce română dacă este disponibilă
                voices = engine.getProperty('voices')
                for voice in voices:
                    if 'romanian' in voice.name.lower() or 'română' in voice.name.lower() or 'ro' in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
                
                # Configurează parametrii pentru claritate
                engine.setProperty('rate', 150)  # Viteză moderată
                engine.setProperty('volume', 1.0)  # Volum maxim
                
                os.makedirs("data/audio", exist_ok=True)
                filename = f"{uuid.uuid4().hex}.mp3"
                filepath = f"data/audio/{filename}"
                engine.save_to_file(text, filepath)
                engine.runAndWait()
                return f"/audio/{filename}"
            except Exception as fallback_error:
                raise Exception(f"Nu s-a putut genera audio. gTTS: {str(e)}, pyttsx3: {str(fallback_error)}")


