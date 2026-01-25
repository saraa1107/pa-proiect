from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ============ SCHEMAS PENTRU CATEGORII ============

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ SCHEMAS PENTRU SIMBOLURI ============

class SymbolBase(BaseModel):
    name: str
    text: str
    image_url: str
    category_id: int


class SymbolCreate(SymbolBase):
    pass


class SymbolResponse(SymbolBase):
    id: int
    usage_count: int
    created_at: datetime
    category: CategoryResponse

    class Config:
        from_attributes = True


# ============ SCHEMAS PENTRU UTILIZATORI ============

class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ SCHEMAS PENTRU TTS ============

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None  # Opțional: "ro-RO-EmilNeural" (masculină) sau "ro-RO-AlinaNeural" (feminină)


# ============ SCHEMAS PENTRU ADĂUGARE IMAGINE ============

class AddImageRequest(BaseModel):
    image_url: str
    symbol_id: int  # ID-ul simbolului existent (obligatoriu)
    image_name: Optional[str] = None  # Nume opțional pentru fișierul imaginii
