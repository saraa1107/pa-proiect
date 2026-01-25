from sqlalchemy.orm import Session
from typing import List, Optional
from models import Category, Symbol, User
from schemas import CategoryCreate, SymbolCreate, UserCreate
from fastapi import UploadFile
import os
import uuid
import shutil
from gtts import gTTS
import io
import base64
import requests
from urllib.parse import urlparse
from pathlib import Path


class CategoryService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
        return db.query(Category).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def create(db: Session, category: CategoryCreate) -> Category:
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category


class SymbolService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Symbol]:
        return db.query(Symbol).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, symbol_id: int) -> Optional[Symbol]:
        return db.query(Symbol).filter(Symbol.id == symbol_id).first()

    @staticmethod
    def get_by_category(db: Session, category_id: int, skip: int = 0, limit: int = 100) -> List[Symbol]:
        return db.query(Symbol).filter(Symbol.category_id == category_id).offset(skip).limit(limit).all()

    @staticmethod
    def search(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Symbol]:
        search_pattern = f"%{search_term}%"
        return db.query(Symbol).filter(
            (Symbol.name.ilike(search_pattern)) | (Symbol.text.ilike(search_pattern))
        ).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, symbol: SymbolCreate) -> Symbol:
        db_symbol = Symbol(**symbol.dict())
        db.add(db_symbol)
        db.commit()
        db.refresh(db_symbol)
        return db_symbol

    @staticmethod
    def increment_usage(db: Session, symbol_id: int):
        symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
        if symbol:
            symbol.usage_count += 1
            db.commit()

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


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db: Session, user: UserCreate) -> User:
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


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


