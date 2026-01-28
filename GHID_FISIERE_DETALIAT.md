# 📄 Ghid Detaliat Fișiere - AAC Communication System

Acest document explică în detaliu ce face fiecare fișier din proiect.

---

## 🔧 Fișiere Backend Principale

### `main.py` (700+ linii) ⭐ CORE
**Rol:** Aplicația principală FastAPI - inima backend-ului

**Ce face:**
- Definește toate endpoint-urile API REST
- Configurare CORS pentru comunicare cross-origin între frontend și backend
- Servire fișiere statice (imagini din `/images/`, audio din `/audio/`)
- Middleware pentru gestionarea erorilor
- Documentare automată API (Swagger UI la `/docs`)

**Endpoint-uri implementate:**

#### Categorii
```python
GET    /api/children/{child_id}/categories
# Returnează categoriile pentru un copil specific
# Logică: Dacă copilul are categorii proprii → doar acelea, altfel → tabla globală

POST   /api/categories
# ⚠️ BLOCAT - returnează 403 Forbidden
# Previne crearea accidentală de categorii globale
```

#### Simboluri
```python
GET    /api/children/{child_id}/symbols
# Toate simbolurile copilului (sau tabla globală)

GET    /api/children/{child_id}/categories/{category_id}/symbols
# Simboluri filtrate pe categorie pentru copil specific

POST   /api/symbols
# Creează simbol nou (verifică duplicate)

DELETE /api/symbols/{symbol_id}
# Șterge simbol

PUT    /api/symbols/reorder
# Reordonare simboluri (schimbă display_order)

POST   /api/symbols/{symbol_id}/upload-image
# Upload imagine pentru simbol
```

#### Autentificare
```python
POST   /api/auth/register
# Înregistrare terapeut nou
# Body: {name, email, password}
# Returnează: {access_token, token_type, user}

POST   /api/auth/login
# Login terapeut
# Body: {email, password}
# Returnează: {access_token, token_type, user}

GET    /api/auth/me
# Verificare token JWT (cine sunt eu?)
# Header: Authorization: Bearer <token>
# Returnează: {id, name, email}
```

#### Terapeut - Gestionare Copii
```python
GET    /api/therapist/children
# Lista copii terapeut autentificat
# Requires: JWT token

POST   /api/therapist/children
# Creează copil nou
# Body: {name}
# Proces automat:
#   1. Creează copil
#   2. Copiază toate categoriile globale (6)
#   3. Copiază toate simbolurile globale (50)
#   4. Returnează copilul creat

GET    /api/therapist/children/{id}
# Detalii copil specific

DELETE /api/therapist/children/{id}
# Șterge copil (cascade: categorii, simboluri, favorite)
```

#### Text-to-Speech
```python
POST   /api/tts/speak
# Generează audio din text
# Body: {text, language: 'ro'}
# Returnează: {audio_url: '/audio/xyz.mp3'}
```

**Protecții implementate:**
- POST `/api/categories` returnează 403 pentru prevenire creări accidentale
- JWT authentication pentru toate endpoint-urile `/api/therapist/`
- Validare automată date cu Pydantic schemas
- Gestionare centralizată excepții (try-catch global)
- CORS configurat pentru `http://localhost:*`

---

### `database.py` (30 linii)
**Rol:** Configurare conexiune bază de date SQLite

**Ce face:**
```python
# 1. Creează engine SQLAlchemy
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/aac_database.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Important pentru SQLite
)

# 2. SessionLocal pentru sesiuni
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 3. Base pentru modele ORM
Base = declarative_base()

# 4. Dependency injection pentru FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Când se folosește:**
- Automat în toate endpoint-urile FastAPI via `Depends(get_db)`
- Manual în scripturi (init_db.py, migrări, cleanup)

---

### `models.py` (150+ linii) ⭐ SCHEMA BAZĂ DE DATE
**Rol:** Modele ORM SQLAlchemy - definește structura tabelelor

**Ce face:**
- Definește schema bazei de date
- Relații între tabele (foreign keys, relationships)
- Unique constraints pentru prevenirea duplicatelor
- Indexuri pentru performanță

**Modele definite:**

#### 1. User - Terapeuți
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)  # bcrypt hash (max 72 bytes)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relații
    children = relationship("Child", back_populates="therapist")
```

**Câmpuri importante:**
- `email` - UNIQUE, folosit pentru login
- `password_hash` - NICIODATĂ parola în clar!

#### 2. Child - Profile copii
```python
class Child(Base):
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    therapist_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ⚠️ CONSTRAINT IMPORTANT
    __table_args__ = (
        UniqueConstraint('name', 'therapist_id', 
                        name='uq_child_name_therapist'),
    )
    
    # Relații
    therapist = relationship("User", back_populates="children")
    categories = relationship("Category", back_populates="child")
    symbols = relationship("Symbol", back_populates="child")
    favorites = relationship("FavoriteSymbol", back_populates="child")
```

**De ce unique constraint?**
- Un terapeut nu poate avea 2 copii cu același nume
- Previne erori când adaugi "Maria" de 2 ori

#### 3. Category - Categorii simboluri
```python
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    color = Column(String)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ⚠️ CONSTRAINT IMPORTANT
    __table_args__ = (
        UniqueConstraint('name', 'child_id', 
                        name='uq_category_name_child'),
    )
    
    # Relații
    child = relationship("Child", back_populates="categories")
    symbols = relationship("Symbol", back_populates="category")
```

**Logica child_id:**
- `child_id = NULL` → categorie GLOBALĂ (tabla de bază)
- `child_id = 5` → categorie PERSONALIZATĂ pentru copilul cu ID 5

**Unique constraint:**
- Nu pot exista 2 categorii "Acțiuni" pentru același copil
- Pot exista "Acțiuni" globale ȘI "Acțiuni" pentru copilul 5 (diferite child_id)

#### 4. Symbol - Simboluri individuale
```python
class Symbol(Base):
    __tablename__ = "symbols"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    text = Column(String)
    image_url = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    child_id = Column(Integer, ForeignKey("children.id"), nullable=True)
    display_order = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ⚠️ CONSTRAINT CEL MAI IMPORTANT
    __table_args__ = (
        UniqueConstraint('name', 'category_id', 'child_id',
                        name='uq_symbol_name_category_child'),
    )
    
    # Relații
    category = relationship("Category", back_populates="symbols")
    child = relationship("Child", back_populates="symbols")
```

**Logica child_id:**
- Similar cu Category
- `child_id = NULL` → simbol GLOBAL
- `child_id = 5` → simbol PERSONALIZAT pentru copil

**Unique constraint:**
- Nu pot exista 2 simboluri "Mama" în categoria "Persoane" pentru copilul 5
- Pot exista "Mama" globală ȘI "Mama" personalizată (diferite child_id)

**Câmpuri speciale:**
- `display_order` - ordonare customizabilă în UI
- `usage_count` - statistici folosire (viitor)

#### 5. FavoriteSymbol - Simboluri favorite
```python
class FavoriteSymbol(Base):
    __tablename__ = "favorite_symbols"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    symbol_id = Column(Integer, ForeignKey("symbols.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relații
    child = relationship("Child", back_populates="favorites")
    symbol = relationship("Symbol")
```

**Folosire:**
- Marchează simboluri des folosite
- Acces rapid în UI (⭐ icon)

---

### `schemas.py` (200+ linii)
**Rol:** Scheme Pydantic pentru validare request/response

**Ce face:**
- Validare automată date primite de la frontend
- Serializare/deserializare JSON ↔ obiecte Python
- Documentare automată în Swagger UI (`/docs`)
- Type hints pentru IDE autocomplete

**Scheme definite:**

#### Categorii
```python
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: str

class CategoryCreate(CategoryBase):
    child_id: Optional[int] = None  # NULL = global

class CategoryResponse(CategoryBase):
    id: int
    child_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pentru SQLAlchemy models
```

#### Simboluri
```python
class SymbolBase(BaseModel):
    name: str
    text: str
    image_url: Optional[str] = None

class SymbolCreate(SymbolBase):
    category_id: int
    child_id: Optional[int] = None
    display_order: Optional[int] = 0

class SymbolResponse(SymbolBase):
    id: int
    category_id: int
    child_id: Optional[int]
    display_order: int
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### Autentificare
```python
class UserRegister(BaseModel):
    name: str
    email: EmailStr  # ✅ Validare automată format email
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Parola trebuie să aibă minim 6 caractere')
        if len(v) > 72:
            # bcrypt limitare
            raise ValueError('Parola trebuie să aibă maxim 72 caractere')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

#### Copii
```python
class ChildCreate(BaseModel):
    name: str

class ChildResponse(BaseModel):
    id: int
    name: str
    therapist_id: int
    created_at: datetime
```

#### TTS
```python
class TTSRequest(BaseModel):
    text: str
    language: str = 'ro'  # Default limba română
```

**Validări automate:**
- Email valid (`@domain.com`)
- Câmpuri obligatorii vs opționale
- Tipuri de date (int, str, datetime)
- Lungime minimă/maximă
- Custom validators (decorator `@validator`)

---

### `services.py` (800+ linii) ⭐ LOGICA BUSINESS
**Rol:** Servicii business - toată logica aplicației

**De ce servicii separate?**
- Separare responsabilități (main.py = routes, services.py = logic)
- Refolosire cod (același serviciu în mai multe endpoint-uri)
- Testare mai ușoară
- Mentenanță simplificată

#### 1. CategoryService

```python
class CategoryService:
    @staticmethod
    def get_all_for_child(db: Session, child_id: int):
        """
        ⭐ LOGICĂ CEA MAI IMPORTANTĂ
        
        Returnează categoriile pentru un copil.
        
        Logică:
        1. Verifică dacă copilul ARE categorii proprii
        2. Dacă DA → returnează DOAR categoriile copilului
        3. Dacă NU → returnează categoriile GLOBALE (tabla de bază)
        
        De ce așa?
        - Previne duplicarea vizuală
        - Copilul "a" (fără categorii) → vede tabla globală
        - Copilul "b" (cu categorii) → vede DOAR tabla lui
        """
        child_categories = db.query(Category).filter(
            Category.child_id == child_id
        ).all()
        
        if child_categories:
            return child_categories
        else:
            return db.query(Category).filter(
                Category.child_id.is_(None)
            ).all()
    
    @staticmethod
    def create(db: Session, category: CategoryCreate):
        """
        Creează categorie nouă.
        
        Verificări:
        1. Dacă este globală (child_id = None), verifică duplicate globale
        2. Dacă este per copil, verifică duplicate pentru acel copil
        3. Previne erori de unique constraint
        """
        # Verifică dacă există deja
        query = db.query(Category).filter(Category.name == category.name)
        
        if category.child_id is None:
            existing = query.filter(Category.child_id.is_(None)).first()
        else:
            existing = query.filter(Category.child_id == category.child_id).first()
        
        if existing:
            raise ValueError(f"Categoria '{category.name}' există deja")
        
        # Creează
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def get_by_id(db: Session, category_id: int):
        """Găsește categorie după ID"""
        return db.query(Category).filter(Category.id == category_id).first()
```

#### 2. SymbolService

```python
class SymbolService:
    @staticmethod
    def get_all_for_child(db: Session, child_id: int, skip=0, limit=100):
        """
        ⭐ LOGICĂ CEA MAI IMPORTANTĂ
        
        Similar cu CategoryService.get_all_for_child()
        
        Returnează:
        - Simbolurile copilului DACĂ are
        - Simbolurile globale DACĂ nu are
        
        NU returnează ambele simultan (cauza duplicării anterioare)
        """
        child_symbols = db.query(Symbol).filter(
            Symbol.child_id == child_id
        ).all()
        
        if child_symbols:
            return child_symbols[skip:skip+limit]
        else:
            global_symbols = db.query(Symbol).filter(
                Symbol.child_id.is_(None)
            ).order_by(Symbol.display_order.asc(), Symbol.id.asc()).all()
            return global_symbols[skip:skip+limit]
    
    @staticmethod
    def get_by_category_for_child(db: Session, child_id: int, 
                                   category_id: int, skip=0, limit=100):
        """
        Similar cu get_all_for_child, dar filtrat pe categorie.
        
        Folosit când selectezi o categorie în UI.
        """
        child_symbols = db.query(Symbol).filter(
            Symbol.category_id == category_id,
            Symbol.child_id == child_id
        ).order_by(Symbol.display_order.asc()).all()
        
        if child_symbols:
            return child_symbols[skip:skip+limit]
        else:
            global_symbols = db.query(Symbol).filter(
                Symbol.category_id == category_id,
                Symbol.child_id.is_(None)
            ).order_by(Symbol.display_order.asc()).all()
            return global_symbols[skip:skip+limit]
    
    @staticmethod
    def create(db: Session, symbol: SymbolCreate):
        """
        Creează simbol nou.
        
        Verifică duplicate după (name, category_id, child_id).
        """
        # Verificare duplicate
        query = db.query(Symbol).filter(
            Symbol.name == symbol.name,
            Symbol.category_id == symbol.category_id
        )
        
        if symbol.child_id is None:
            existing = query.filter(Symbol.child_id.is_(None)).first()
        else:
            existing = query.filter(Symbol.child_id == symbol.child_id).first()
        
        if existing:
            raise ValueError(f"Simbolul '{symbol.name}' există deja în această categorie")
        
        # Creează
        db_symbol = Symbol(**symbol.dict())
        db.add(db_symbol)
        db.commit()
        db.refresh(db_symbol)
        return db_symbol
    
    @staticmethod
    def download_image_from_url(db: Session, symbol_id: int, image_url: str):
        """
        Descarcă imagine de la URL extern.
        
        Proces:
        1. Face GET request la URL
        2. Salvează în data/images/
        3. Actualizează symbol.image_url cu calea locală
        """
        import requests
        from pathlib import Path
        
        symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
        if not symbol:
            raise ValueError("Simbolul nu există")
        
        # Download
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Salvează
        filename = f"symbol_{symbol_id}.jpg"
        filepath = Path("data/images") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Actualizează DB
        symbol.image_url = f"/images/{filename}"
        db.commit()
        return symbol
    
    @staticmethod
    def upload_image(db: Session, symbol_id: int, file: UploadFile):
        """
        Upload imagine de pe disk local.
        
        Similar cu download_image_from_url, dar cu fișier local.
        """
        from pathlib import Path
        
        symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
        if not symbol:
            raise ValueError("Simbolul nu există")
        
        # Salvează
        filename = f"symbol_{symbol_id}_{file.filename}"
        filepath = Path("data/images") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(file.file.read())
        
        # Actualizează DB
        symbol.image_url = f"/images/{filename}"
        db.commit()
        return symbol
    
    @staticmethod
    def reorder(db: Session, symbol_id: int, new_order: int):
        """
        Schimbă display_order pentru un simbol.
        
        Folosit pentru drag & drop în UI.
        """
        symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
        if not symbol:
            raise ValueError("Simbolul nu există")
        
        symbol.display_order = new_order
        db.commit()
        return symbol
    
    @staticmethod
    def delete(db: Session, symbol_id: int):
        """Șterge simbol din baza de date."""
        symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
        if not symbol:
            raise ValueError("Simbolul nu există")
        
        db.delete(symbol)
        db.commit()
```

#### 3. UserService

```python
class UserService:
    @staticmethod
    def create(db: Session, user: UserRegister):
        """
        Creează cont terapeut nou.
        
        Securitate:
        1. Verifică dacă email-ul există deja
        2. Hash-uiește parola cu bcrypt (max 72 bytes!)
        3. Salvează în DB
        """
        import bcrypt
        
        # Verifică duplicate
        existing = db.query(User).filter(User.email == user.email).first()
        if existing:
            raise ValueError("Email-ul este deja înregistrat")
        
        # Hash parolă
        # ⚠️ bcrypt limitare: max 72 bytes (validat în schema)
        password_bytes = user.password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Creează user
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed.decode('utf-8')
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate(db: Session, email: str, password: str):
        """
        Verifică credențiale login.
        
        Returns:
        - User object dacă credențialele sunt corecte
        - None dacă email sau parolă greșită
        """
        import bcrypt
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        # Verifică parolă
        password_bytes = password.encode('utf-8')
        hashed_bytes = user.password_hash.encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, hashed_bytes):
            return user
        return None
    
    @staticmethod
    def get_by_email(db: Session, email: str):
        """Găsește user după email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        """
        Generează JWT token.
        
        Configurare:
        - Algoritm: HS256
        - Secret: SECRET_KEY din environment sau default
        - Expirare: 30 zile (default)
        
        Payload:
        - sub: user_id
        - exp: timestamp expirare
        - iat: timestamp creare
        """
        from jose import jwt
        from datetime import datetime, timedelta
        
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=30)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        SECRET_KEY = "your-secret-key-here"  # TODO: Move to .env
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str):
        """
        Verifică și decodează JWT token.
        
        Raises:
        - JWTError dacă token invalid sau expirat
        
        Returns:
        - Payload (dict cu user_id, exp, iat)
        """
        from jose import jwt, JWTError
        
        try:
            SECRET_KEY = "your-secret-key-here"
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except JWTError:
            raise ValueError("Token invalid sau expirat")
```

#### 4. ChildService

```python
class ChildService:
    @staticmethod
    def create(db: Session, child: ChildCreate, therapist_id: int):
        """
        ⭐ PROCES CEL MAI COMPLEX ⭐
        
        Creează copil nou și îi copiază tabla AAC globală.
        
        Pași:
        1. Verifică dacă terapeutul are deja copil cu acest nume
        2. Creează copilul în DB
        3. Găsește TOATE categoriile globale (6 categorii)
        4. Pentru fiecare categorie globală:
           a. Creează copie pentru copil (child_id = copil_id)
           b. Mapează category_id vechi → category_id nou
        5. Găsește TOATE simbolurile globale (50 simboluri)
        6. Pentru fiecare simbol global:
           a. Găsește category_id nou (din mapare)
           b. Creează copie pentru copil
        7. Returnează copilul creat
        
        Rezultat:
        - Copilul are propria tablă AAC editabilă
        - Poate adăuga/șterge/modifica fără a afecta tabla globală
        - Alți copii nu sunt afectați
        """
        # 1. Verifică duplicate
        existing = db.query(Child).filter(
            Child.name == child.name,
            Child.therapist_id == therapist_id
        ).first()
        
        if existing:
            raise ValueError(f"Copilul '{child.name}' există deja")
        
        # 2. Creează copil
        db_child = Child(name=child.name, therapist_id=therapist_id)
        db.add(db_child)
        db.commit()
        db.refresh(db_child)
        
        # 3. Găsește categorii globale
        global_categories = db.query(Category).filter(
            Category.child_id.is_(None)
        ).all()
        
        # 4. Copiază categorii + mapare ID-uri
        category_id_map = {}  # {old_id: new_id}
        
        for global_cat in global_categories:
            new_cat = Category(
                name=global_cat.name,
                description=global_cat.description,
                icon=global_cat.icon,
                color=global_cat.color,
                child_id=db_child.id  # ⚠️ IMPORTANT
            )
            db.add(new_cat)
            db.flush()  # Obține ID fără commit
            
            category_id_map[global_cat.id] = new_cat.id
        
        # 5. Găsește simboluri globale
        global_symbols = db.query(Symbol).filter(
            Symbol.child_id.is_(None)
        ).all()
        
        # 6. Copiază simboluri cu category_id corect
        for global_sym in global_symbols:
            # Găsește categoria nouă corespunzătoare
            new_category_id = category_id_map.get(global_sym.category_id)
            
            if not new_category_id:
                # Skip dacă categoria nu a fost copiată (nu ar trebui să se întâmple)
                continue
            
            new_sym = Symbol(
                name=global_sym.name,
                text=global_sym.text,
                image_url=global_sym.image_url,
                category_id=new_category_id,  # ⚠️ MAPARE
                child_id=db_child.id,          # ⚠️ IMPORTANT
                display_order=global_sym.display_order
            )
            db.add(new_sym)
        
        # 7. Commit totul
        db.commit()
        db.refresh(db_child)
        
        return db_child
    
    @staticmethod
    def get_all_for_therapist(db: Session, therapist_id: int):
        """Lista tuturor copiilor unui terapeut"""
        return db.query(Child).filter(
            Child.therapist_id == therapist_id
        ).all()
    
    @staticmethod
    def get_by_id(db: Session, child_id: int):
        """Găsește copil după ID"""
        return db.query(Child).filter(Child.id == child_id).first()
    
    @staticmethod
    def delete(db: Session, child_id: int):
        """
        Șterge copil și toate datele asociate.
        
        Cascade delete (automat via SQLAlchemy):
        - Toate categoriile copilului
        - Toate simbolurile copilului
        - Toate favorite-urile copilului
        """
        child = db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise ValueError("Copilul nu există")
        
        db.delete(child)
        db.commit()
    
    @staticmethod
    def add_favorite(db: Session, child_id: int, symbol_id: int):
        """Marchează simbol ca favorit pentru copil"""
        # Verifică dacă deja favorit
        existing = db.query(FavoriteSymbol).filter(
            FavoriteSymbol.child_id == child_id,
            FavoriteSymbol.symbol_id == symbol_id
        ).first()
        
        if existing:
            return existing  # Deja favorit
        
        # Adaugă
        favorite = FavoriteSymbol(child_id=child_id, symbol_id=symbol_id)
        db.add(favorite)
        db.commit()
        return favorite
    
    @staticmethod
    def remove_favorite(db: Session, child_id: int, symbol_id: int):
        """Elimină simbol din favorite"""
        favorite = db.query(FavoriteSymbol).filter(
            FavoriteSymbol.child_id == child_id,
            FavoriteSymbol.symbol_id == symbol_id
        ).first()
        
        if favorite:
            db.delete(favorite)
            db.commit()
    
    @staticmethod
    def get_favorites(db: Session, child_id: int):
        """Lista simboluri favorite pentru copil"""
        favorites = db.query(FavoriteSymbol).filter(
            FavoriteSymbol.child_id == child_id
        ).all()
        
        # Returnează simbolurile (nu FavoriteSymbol objects)
        return [fav.symbol for fav in favorites]
```

#### 5. TTSService

```python
class TTSService:
    @staticmethod
    def generate_audio(text: str, language: str = 'ro'):
        """
        Generează audio folosind gTTS (Google Text-to-Speech).
        
        Proces:
        1. Creează obiect gTTS cu text și limbă
        2. Salvează în data/audio/ cu nume unic (timestamp)
        3. Returnează calea către fișier
        
        Cleanup automat:
        - Șterge fișiere audio mai vechi de 24h (evită umplere disk)
        """
        from gtts import gTTS
        from pathlib import Path
        import hashlib
        from datetime import datetime, timedelta
        
        # Generează nume fișier unic
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        filename = f"tts_{timestamp}_{text_hash}.mp3"
        
        # Creează folder dacă nu există
        audio_dir = Path("data/audio")
        audio_dir.mkdir(parents=True, exist_ok=True)
        filepath = audio_dir / filename
        
        # Generează audio
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(str(filepath))
        
        # Cleanup fișiere vechi (>24h)
        cutoff_time = datetime.now() - timedelta(days=1)
        for old_file in audio_dir.glob("tts_*.mp3"):
            if old_file.stat().st_mtime < cutoff_time.timestamp():
                old_file.unlink()
        
        return f"/audio/{filename}"
    
    @staticmethod
    def speak(text: str):
        """Wrapper pentru generare audio"""
        return TTSService.generate_audio(text, language='ro')
```

---

### `init_db.py` (200+ linii) ⭐ INIȚIALIZARE
**Rol:** Inițializare bază de date cu date demo

**Ce face:**

```python
from database import SessionLocal, engine, Base
from models import Category, Symbol
from services import CategoryService, SymbolService
from schemas import CategoryCreate, SymbolCreate

# 1. Creează toate tabelele
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # 2. Verifică dacă există deja categorii
    existing_categories = db.query(Category).count()
    
    # 3. Creează 6 categorii globale
    categories_data = [
        {"name": "Acțiuni", "description": "Verbe și acțiuni comune", 
         "color": "#FF6B6B"},
        {"name": "Alimente", "description": "Mâncare și băuturi", 
         "color": "#4ECDC4"},
        {"name": "Emoții", "description": "Sentimente și emoții", 
         "color": "#FFE66D"},
        {"name": "Persoane", "description": "Membri ai familiei și persoane", 
         "color": "#95E1D3"},
        {"name": "Locații", "description": "Locuri și destinații", 
         "color": "#A8E6CF"},
        {"name": "Obiecte", "description": "Obiecte de uz zilnic", 
         "color": "#FFD3B6"},
    ]
    
    created_categories = {}
    
    for cat_data in categories_data:
        if existing_categories > 0:
            # Găsește categoria existentă
            existing_cat = db.query(Category).filter(
                Category.name == cat_data["name"]
            ).first()
            if existing_cat:
                created_categories[cat_data["name"]] = existing_cat.id
                print(f"✓ Categorie existentă: {existing_cat.name}")
                continue
        
        # Creează categoria nouă
        category = CategoryService.create(db, CategoryCreate(**cat_data))
        created_categories[cat_data["name"]] = category.id
        print(f"✓ Categorie creată: {category.name}")
    
    # 4. Creează EXACT 50 simboluri globale
    symbols_data = [
        # Acțiuni (8 simboluri)
        {"name": "Mâncare", "text": "Vreau să mănânc", 
         "image_url": "/images/mananc.jpg", 
         "category_id": created_categories["Acțiuni"]},
        {"name": "Băutură", "text": "Vreau să beau", 
         "image_url": "/images/beau.jpg", 
         "category_id": created_categories["Acțiuni"]},
        {"name": "Dormit", "text": "Vreau să dorm", 
         "image_url": "/images/dorm.jpg", 
         "category_id": created_categories["Acțiuni"]},
        {"name": "Joc", "text": "Vreau să mă joc", 
         "image_url": "/images/joc.jpg", 
         "category_id": created_categories["Acțiuni"]},
        {"name": "Mers", "text": "Vreau să merg", 
         "image_url": "/images/merg.jpg", 
         "category_id": created_categories["Acțiuni"]},
        {"name": "Citit", "text": "Vreau să citesc", 
         "image_url": "/images/citesc.jpg", 
         "category_id": created_categories["Acțiuni"]},
        {"name": "Spălat", "text": "Vreau să mă spăl", 
         "image_url": "/images/spal.jpg", 
         "category_id": created_categories["Acțiuni"]},
        {"name": "Îmbrăcat", "text": "Vreau să mă îmbrac", 
         "image_url": "/images/imbrac.jpg", 
         "category_id": created_categories["Acțiuni"]},
        
        # Alimente (12 simboluri)
        {"name": "Pâine", "text": "Pâine", 
         "image_url": "/images/paine.jpg", 
         "category_id": created_categories["Alimente"]},
        # ... (total 12)
        
        # Emoții (5 simboluri)
        {"name": "Fericit", "text": "Sunt fericit", 
         "image_url": "/images/fericit.jpg", 
         "category_id": created_categories["Emoții"]},
        # ... (total 5)
        
        # Persoane (6 simboluri)
        {"name": "Mama", "text": "Mama", 
         "image_url": "/images/mama.jpg", 
         "category_id": created_categories["Persoane"]},
        # ... (total 6)
        
        # Locații (9 simboluri)
        {"name": "Casă", "text": "Casă", 
         "image_url": "/images/casa.jpg", 
         "category_id": created_categories["Locații"]},
        # ... (total 9)
        
        # Obiecte (10 simboluri)
        {"name": "Scaun", "text": "Scaun", 
         "image_url": "/images/scaun.jpg", 
         "category_id": created_categories["Obiecte"]},
        # ... (total 10)
    ]
    
    # 5. Adaugă simbolurile (skip duplicate)
    symbols_added = 0
    symbols_skipped = 0
    
    for sym_data in symbols_data:
        # Verifică dacă simbolul există deja
        existing_symbol = db.query(Symbol).filter(
            Symbol.name == sym_data["name"],
            Symbol.category_id == sym_data["category_id"],
            Symbol.child_id.is_(None)
        ).first()
        
        if existing_symbol:
            print(f"⊘ Simbol deja există: {sym_data['name']}")
            symbols_skipped += 1
        else:
            try:
                symbol = SymbolService.create(db, SymbolCreate(**sym_data))
                print(f"✓ Simbol creat: {symbol.name}")
                symbols_added += 1
            except Exception as e:
                print(f"✗ Eroare: {e}")
    
    # 6. Raport final
    print(f"\n✅ Actualizare completă!")
    print(f"  - Simboluri noi: {symbols_added}")
    print(f"  - Simboluri existente: {symbols_skipped}")
    print(f"  - Total în DB: {db.query(Symbol).count()}")

except Exception as e:
    print(f"❌ Eroare: {e}")
    db.rollback()
finally:
    db.close()
```

**Când să-l rulezi:**
```bash
# Prima instalare (OBLIGATORIU)
cd backend
python init_db.py

# După modificări în models.py (recreează tabelele)
rm data/aac_database.db  # Șterge DB veche
python init_db.py

# Pentru resetare la starea inițială
rm data/aac_database.db
python init_db.py
```

**Output tipic:**
```
✓ Categorie creată: Acțiuni
✓ Categorie creată: Alimente
✓ Categorie creată: Emoții
✓ Categorie creată: Persoane
✓ Categorie creată: Locații
✓ Categorie creată: Obiecte
✓ Simbol creat: Mâncare
✓ Simbol creat: Băutură
...
✅ Actualizare completă!
  - Simboluri noi: 50
  - Simboluri existente: 0
  - Total în DB: 50
```

---

### `run.py` (10 linii)
**Rol:** Script simplu pentru pornire backend

```python
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",  # Acceptă conexiuni de pe orice IP
        port=8000,       # Port standard
        reload=True      # Auto-reload la modificări cod
    )
```

**Folosire:**
```bash
cd backend
python run.py
```

**Alternativă (direct cu uvicorn):**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

### `requirements.txt` (20+ linii)
**Rol:** Dependințe Python cu versiuni exacte (pinned)

**Conținut:**
```
fastapi==0.104.1          # Framework API REST modern
uvicorn[standard]==0.24.0 # Server ASGI pentru FastAPI
sqlalchemy==2.0.23        # ORM baza de date
pydantic==2.5.0           # Validare date și schemas
pydantic[email]==2.5.0    # Email validation
bcrypt==4.1.1             # Hash parole (securitate)
python-jose[cryptography]==3.3.0  # JWT tokens
gTTS==2.5.0               # Google Text-to-Speech
requests==2.31.0          # HTTP requests (download imagini)
python-multipart==0.0.6   # Upload fișiere (FormData)
email-validator==2.1.0    # Validare email addresses
```

**De ce versiuni exacte?**
- Reproductibilitate (instalare identică pe orice mașină)
- Evită breaking changes din versiuni noi
- Production-ready

**Instalare:**
```bash
pip install -r requirements.txt
```

**Update (cu atenție!):**
```bash
pip install --upgrade fastapi uvicorn sqlalchemy
pip freeze > requirements.txt
```

---

### `requirements_simple.txt`
**Rol:** Dependințe Python cu versiuni flexibile (fără pinning)

**Conținut:**
```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
pydantic[email]
bcrypt
python-jose[cryptography]
gTTS
requests
python-multipart
email-validator
```

**Când să folosești:**
- Dezvoltare rapidă
- Prototyping
- Când vrei ultima versiune a fiecărei librării

**⚠️ Risc:**
- Breaking changes neprevăzute
- Incompatibilități între versiuni
- NU recomand pentru production

---

## 🔧 Scripturi Utilitare Backend

### `upload_images_from_folder.py` (100 linii)
**Rol:** Upload în masă imagini din folder local

**Ce face:**
```python
"""
1. Scanează folderul data/images/
2. Pentru fiecare fișier găsit (ex: mama.jpg):
   - Extrage numele simbolului din nume fișier
   - Caută simbolul în baza de date
   - Actualizează symbol.image_url cu calea corectă
3. Raportează rezultatele
"""

from pathlib import Path
from database import SessionLocal
from models import Symbol

db = SessionLocal()

# Scanează folder
images_dir = Path("data/images")
images = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))

found = 0
not_found = 0
updated = 0

for image_path in images:
    # Ex: "mama.jpg" → "mama"
    symbol_name = image_path.stem.lower()
    
    # Caută simbolul în DB (case-insensitive)
    symbols = db.query(Symbol).filter(
        Symbol.name.ilike(f"%{symbol_name}%")
    ).all()
    
    if symbols:
        for symbol in symbols:
            # Actualizează image_url
            symbol.image_url = f"/images/{image_path.name}"
            found += 1
            updated += 1
            print(f"✓ {symbol.name} → {image_path.name}")
    else:
        print(f"✗ Nu s-a găsit simbol pentru: {image_path.name}")
        not_found += 1

db.commit()
db.close()

print(f"\n📊 Raport:")
print(f"  - Găsite și actualizate: {updated}")
print(f"  - Nu s-au găsit simboluri: {not_found}")
```

**Folosire:**
```bash
# 1. Pune imaginile în backend/data/images/
# Ex: mama.jpg, tata.jpg, fericit.jpg, etc.

# 2. Rulează scriptul
cd backend
python upload_images_from_folder.py

# Output:
# ✓ Mama → mama.jpg
# ✓ Tata → tata.jpg
# ✓ Fericit → fericit.jpg
# ✗ Nu s-a găsit simbol pentru: imagine_random.jpg
#
# 📊 Raport:
#   - Găsite și actualizate: 47
#   - Nu s-au găsit simboluri: 3
```

---

### `clean_global_category_duplicates.py` (150 linii) 🧹
**Rol:** Curățare duplicate categorii globale

**Ce face:**
```python
"""
1. Găsește toate categoriile globale (child_id = NULL)
2. Grupează după nume
3. Pentru fiecare grup de duplicate:
   - Păstrează prima categorie (ID cel mai mic)
   - Remapă toate simbolurile la categoria păstrată
   - Șterge categoriile duplicate
4. Afișează raport cleanup
"""

from collections import defaultdict
from database import SessionLocal
from models import Category, Symbol

db = SessionLocal()

# 1. Găsește categorii globale
global_categories = db.query(Category).filter(
    Category.child_id.is_(None)
).all()

# 2. Grupează după nume
categories_by_name = defaultdict(list)
for cat in global_categories:
    categories_by_name[cat.name].append(cat)

# 3. Procesează duplicate
total_deleted = 0

for name, cats in categories_by_name.items():
    if len(cats) > 1:
        # Duplicate găsite!
        print(f"\n🔍 Categoria '{name}' are {len(cats)} duplicate:")
        
        # Sortează după ID (păstrează cel mai vechi)
        cats.sort(key=lambda c: c.id)
        keep_cat = cats[0]
        duplicate_cats = cats[1:]
        
        print(f"  ✅ Păstrează: ID {keep_cat.id}")
        print(f"  ❌ Șterge: {[c.id for c in duplicate_cats]}")
        
        # Remapă simbolurile
        for dup_cat in duplicate_cats:
            symbols = db.query(Symbol).filter(
                Symbol.category_id == dup_cat.id
            ).all()
            
            for sym in symbols:
                sym.category_id = keep_cat.id
            
            print(f"     Remaped {len(symbols)} simboluri")
            
            # Șterge categoria duplicat
            db.delete(dup_cat)
            total_deleted += 1

db.commit()
db.close()

print(f"\n✅ Cleanup complet!")
print(f"  - Categorii șterse: {total_deleted}")
```

**Când să-l folosești:**
- După importuri greșite de date
- Dacă vezi duplicate în UI
- Pentru curățare periodică

**Output tipic:**
```
🔍 Categoria 'Acțiuni' are 3 duplicate:
  ✅ Păstrează: ID 1
  ❌ Șterge: [7, 13]
     Remaped 8 simboluri
     Remaped 8 simboluri

🔍 Categoria 'Alimente' are 2 duplicate:
  ✅ Păstrează: ID 2
  ❌ Șterge: [8]
     Remaped 12 simboluri

✅ Cleanup complet!
  - Categorii șterse: 4
```

---

### `clean_global_symbol_duplicates.py` (150 linii) 🧹
**Rol:** Curățare duplicate simboluri globale

**Similar cu `clean_global_category_duplicates.py`, dar pentru simboluri**

**Ce face:**
```python
"""
1. Găsește toate simbolurile globale (child_id = NULL)
2. Grupează după (name, category_id)
3. Pentru fiecare grup de duplicate:
   - Păstrează primul simbol (ID cel mai mic)
   - Șterge simbolurile duplicate
4. Afișează raport
"""

from collections import defaultdict
from database import SessionLocal
from models import Symbol

db = SessionLocal()

# 1. Găsește simboluri globale
global_symbols = db.query(Symbol).filter(
    Symbol.child_id.is_(None)
).all()

# 2. Grupează după (name, category_id)
symbols_by_key = defaultdict(list)
for sym in global_symbols:
    key = (sym.name, sym.category_id)
    symbols_by_key[key].append(sym)

# 3. Procesează duplicate
total_deleted = 0

for (name, cat_id), syms in symbols_by_key.items():
    if len(syms) > 1:
        print(f"\n🔍 Simbolul '{name}' (cat {cat_id}) are {len(syms)} duplicate:")
        
        # Sortează după ID
        syms.sort(key=lambda s: s.id)
        keep_sym = syms[0]
        duplicate_syms = syms[1:]
        
        print(f"  ✅ Păstrează: ID {keep_sym.id}")
        print(f"  ❌ Șterge: {[s.id for s in duplicate_syms]}")
        
        # Șterge duplicate
        for dup_sym in duplicate_syms:
            db.delete(dup_sym)
            total_deleted += 1

db.commit()
db.close()

print(f"\n✅ Cleanup complet!")
print(f"  - Simboluri șterse: {total_deleted}")
```

---

### `verify_database_structure.py` (200 linii) ✅
**Rol:** Verificare integritate bază de date

**Ce face:**
```python
"""
Verifică:
1. Număr categorii globale (așteptat: 6)
2. Număr simboluri globale (așteptat: 50)
3. Distribuție simboluri pe categorii (8+12+5+6+9+10)
4. Duplicate în categorii
5. Duplicate în simboluri
6. Simboluri orfane (fără categorie)
7. Categorii goale (fără simboluri)
"""

from database import SessionLocal
from models import Category, Symbol
from collections import defaultdict

db = SessionLocal()

print("✅ VERIFICARE BAZĂ DE DATE")
print("━" * 50)

# 1. Categorii globale
global_cats = db.query(Category).filter(Category.child_id.is_(None)).all()
print(f"\n📊 CATEGORII GLOBALE: {len(global_cats)}")
if len(global_cats) == 6:
    print("   ✅ Corect (6 categorii așteptate)")
else:
    print(f"   ⚠️ Incorect (așteptat: 6, găsit: {len(global_cats)})")

for cat in global_cats:
    print(f"   - {cat.name} (ID: {cat.id})")

# 2. Simboluri globale
global_syms = db.query(Symbol).filter(Symbol.child_id.is_(None)).all()
print(f"\n📊 SIMBOLURI GLOBALE: {len(global_syms)}")
if len(global_syms) == 50:
    print("   ✅ Corect (50 simboluri așteptate)")
else:
    print(f"   ⚠️ Incorect (așteptat: 50, găsit: {len(global_syms)})")

# 3. Distribuție pe categorii
syms_by_cat = defaultdict(int)
for sym in global_syms:
    cat = db.query(Category).filter(Category.id == sym.category_id).first()
    if cat:
        syms_by_cat[cat.name] += 1

expected = {
    "Acțiuni": 8,
    "Alimente": 12,
    "Emoții": 5,
    "Persoane": 6,
    "Locații": 9,
    "Obiecte": 10
}

print("\n📊 DISTRIBUȚIE SIMBOLURI PE CATEGORII:")
all_correct = True
for cat_name, count in syms_by_cat.items():
    exp = expected.get(cat_name, 0)
    status = "✅" if count == exp else "⚠️"
    print(f"   {status} {cat_name}: {count} (așteptat: {exp})")
    if count != exp:
        all_correct = False

if all_correct:
    print("   ✅ Toate distribuțiile sunt corecte")

# 4. Duplicate categorii
cat_names = defaultdict(int)
for cat in global_cats:
    cat_names[cat.name] += 1

duplicates_found = False
print("\n📊 VERIFICARE DUPLICATE CATEGORII:")
for name, count in cat_names.items():
    if count > 1:
        print(f"   ⚠️ '{name}' apare de {count} ori")
        duplicates_found = True

if not duplicates_found:
    print("   ✅ Nu există duplicate în categorii")

# 5. Duplicate simboluri
sym_keys = defaultdict(int)
for sym in global_syms:
    key = (sym.name, sym.category_id)
    sym_keys[key] += 1

duplicates_found = False
print("\n📊 VERIFICARE DUPLICATE SIMBOLURI:")
for (name, cat_id), count in sym_keys.items():
    if count > 1:
        cat = db.query(Category).filter(Category.id == cat_id).first()
        cat_name = cat.name if cat else "Unknown"
        print(f"   ⚠️ '{name}' în categoria '{cat_name}' apare de {count} ori")
        duplicates_found = True

if not duplicates_found:
    print("   ✅ Nu există duplicate în simboluri")

# 6. Simboluri orfane
orphans = []
for sym in global_syms:
    cat = db.query(Category).filter(Category.id == sym.category_id).first()
    if not cat:
        orphans.append(sym)

print("\n📊 VERIFICARE SIMBOLURI ORFANE:")
if orphans:
    print(f"   ⚠️ {len(orphans)} simboluri fără categorie:")
    for orphan in orphans:
        print(f"      - {orphan.name} (cat_id: {orphan.category_id})")
else:
    print("   ✅ Nu există simboluri orfane")

# 7. Categorii goale
print("\n📊 VERIFICARE CATEGORII GOALE:")
empty_cats = []
for cat in global_cats:
    sym_count = len([s for s in global_syms if s.category_id == cat.id])
    if sym_count == 0:
        empty_cats.append(cat)
        print(f"   ⚠️ Categoria '{cat.name}' nu are simboluri")

if not empty_cats:
    print("   ✅ Toate categoriile au simboluri")

print("\n" + "━" * 50)
print("✅ VERIFICARE COMPLETĂ")

db.close()
```

**Output exemplu (bază de date corectă):**
```
✅ VERIFICARE BAZĂ DE DATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 CATEGORII GLOBALE: 6
   ✅ Corect (6 categorii așteptate)
   - Acțiuni (ID: 1)
   - Alimente (ID: 2)
   - Emoții (ID: 3)
   - Persoane (ID: 4)
   - Locații (ID: 5)
   - Obiecte (ID: 6)

📊 SIMBOLURI GLOBALE: 50
   ✅ Corect (50 simboluri așteptate)

📊 DISTRIBUȚIE SIMBOLURI PE CATEGORII:
   ✅ Acțiuni: 8 (așteptat: 8)
   ✅ Alimente: 12 (așteptat: 12)
   ✅ Emoții: 5 (așteptat: 5)
   ✅ Persoane: 6 (așteptat: 6)
   ✅ Locații: 9 (așteptat: 9)
   ✅ Obiecte: 10 (așteptat: 10)
   ✅ Toate distribuțiile sunt corecte

📊 VERIFICARE DUPLICATE CATEGORII:
   ✅ Nu există duplicate în categorii

📊 VERIFICARE DUPLICATE SIMBOLURI:
   ✅ Nu există duplicate în simboluri

📊 VERIFICARE SIMBOLURI ORFANE:
   ✅ Nu există simboluri orfane

📊 VERIFICARE CATEGORII GOALE:
   ✅ Toate categoriile au simboluri

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ VERIFICARE COMPLETĂ
```

---

### `analyze_children_duplicates.py` (100 linii) 🔍
**Rol:** Analizează duplicate pentru fiecare copil

**Ce face:**
```python
"""
Pentru fiecare copil din baza de date:
1. Numără categorii proprii
2. Numără simboluri proprii
3. Verifică duplicate în categorii
4. Verifică duplicate în simboluri
5. Afișează raport per copil
"""

from database import SessionLocal
from models import Child, Category, Symbol
from collections import defaultdict

db = SessionLocal()

children = db.query(Child).all()

print(f"📋 ANALIZĂ COPII ({len(children)} total)")
print("=" * 50)

for child in children:
    print(f"\n📋 Copil: {child.name} (ID: {child.id})")
    
    # Categorii
    child_cats = db.query(Category).filter(
        Category.child_id == child.id
    ).all()
    print(f"   Categorii proprii: {len(child_cats)}")
    
    # Simboluri
    child_syms = db.query(Symbol).filter(
        Symbol.child_id == child.id
    ).all()
    print(f"   Simboluri proprii: {len(child_syms)}")
    
    # Duplicate categorii
    cat_names = defaultdict(int)
    for cat in child_cats:
        cat_names[cat.name] += 1
    
    cat_dups = {name: count for name, count in cat_names.items() if count > 1}
    if cat_dups:
        print(f"   ⚠️ Duplicate categorii:")
        for name, count in cat_dups.items():
            print(f"      - '{name}': {count} copii")
    
    # Duplicate simboluri
    sym_keys = defaultdict(int)
    for sym in child_syms:
        key = (sym.name, sym.category_id)
        sym_keys[key] += 1
    
    sym_dups = {key: count for key, count in sym_keys.items() if count > 1}
    if sym_dups:
        print(f"   ⚠️ Duplicate simboluri:")
        for (name, cat_id), count in sym_dups.items():
            print(f"      - '{name}' (cat {cat_id}): {count} copii")
    
    if not cat_dups and not sym_dups:
        print("   ✅ Nu există duplicate")

db.close()
```

**Output exemplu:**
```
📋 ANALIZĂ COPII (2 total)
==================================================

📋 Copil: a (ID: 1)
   Categorii proprii: 0
   Simboluri proprii: 0
   ✅ Nu există duplicate

📋 Copil: b (ID: 2)
   Categorii proprii: 6
   Simboluri proprii: 50
   ✅ Nu există duplicate
```

---

### `check_all_children.py` (60 linii) 📋
**Rol:** Listează toți copiii cu statistici

**Ce face:**
```python
"""
Afișează listă compactă cu toți copiii și statisticile lor.
"""

from database import SessionLocal
from models import Child, Category, Symbol

db = SessionLocal()

children = db.query(Child).all()

print(f"\n📋 LISTĂ COPII ({len(children)} total)\n")

for child in children:
    cat_count = db.query(Category).filter(
        Category.child_id == child.id
    ).count()
    
    sym_count = db.query(Symbol).filter(
        Symbol.child_id == child.id
    ).count()
    
    print(f"👶 {child.name} (ID: {child.id})")
    print(f"   📦 Categorii: {cat_count}")
    print(f"   🖼️ Simboluri: {sym_count}")
    print(f"   📅 Creat: {child.created_at.strftime('%Y-%m-%d')}")
    print()

db.close()
```

---

### `IMAGINI_NEcesARE.txt` (80 linii) 📝
**Rol:** Documentație imagini necesare

**Conținut:**
```
LISTA IMAGINI NECESARE PENTRU SIMBOLURI (50 TOTAL)
===================================================

Toate imaginile trebuie să fie plasate în folderul: backend/data/images/

ACȚIUNI (8 imagini):
-------------------
- mananc.jpg
- beau.jpg
- dorm.jpg
- joc.jpg
- merg.jpg
- citesc.jpg
- spal.jpg
- imbrac.jpg

ALIMENTE (12 imagini):
---------------------
- paine.jpg
- apa.jpg
- lapte.jpg
- fructe.jpg
- mar.jpg
- banane.jpg
- portocale.jpg
- legume.jpg
- oua.jpg
- branza.jpg
- suc.jpg
- ciocolata.jpg

EMOȚII (5 imagini):
------------------
- fericit.jpg
- trist.jpg
- suparat.jpg
- infricat.jpg
- obosit.jpg

PERSOANE (6 imagini):
--------------------
- mama.jpg
- tata.jpg
- prieten.jpg
- bunica.jpg
- frate.jpg
- profesor.jpg

LOCAȚII (9 imagini):
-------------------
- casa.jpg
- scoala.jpg
- parc.jpg
- magazin.jpg
- spital.jpg
- bucatarie.jpg
- dormitor.jpg
- baie.jpg
- curte.jpg

OBIECTE (10 imagini):
--------------------
- scaun.jpg
- pat.jpg
- jucarie.jpg
- minge.jpg
- carti.jpg
- creion.jpg
- telefon.jpg
- haina.jpg
- pantofi.jpg
- masina.jpg

TOTAL: 50 imagini necesare

NOTĂ: 
- Imaginile trebuie să fie în format JPG sau PNG
- Dimensiunea recomandată: minim 200x200 pixeli
- Poți folosi imagini simple și clare pentru fiecare cuvânt
- După ce adaugi imaginile, rulează din nou: python init_db.py
```

---

### `ANTI_DUPLICATE_PROTECTION.md` (200 linii) 📚
**Rol:** Documentație protecție duplicate

**Conținut (sumar):**
```markdown
# Protecție Anti-Duplicate

## Problema Inițială
- Categorii se multiplicau la fiecare cleanup
- Simboluri apareau de 2-3 ori în UI
- Copii duplicați cu același nume

## Soluții Implementate

### 1. Unique Constraints (Nivel Bază de Date)

```sql
-- Children
UNIQUE (name, therapist_id)

-- Categories
UNIQUE (name, child_id)

-- Symbols
UNIQUE (name, category_id, child_id)
```

### 2. Logica Deduplicare (Nivel Aplicație)

#### services.py - CategoryService.get_all_for_child()
```python
# Dacă copilul ARE categorii → DOAR acelea
# Dacă copilul NU ARE categorii → tabla globală
# NU returnează ambele simultan!
```

#### services.py - SymbolService.get_all_for_child()
```python
# Similar cu categoriile
# Previne duplicarea vizuală
```

### 3. Blocări API

```python
# main.py - POST /api/categories
@app.post("/api/categories")
def create_category():
    raise HTTPException(403, "Creare categorii globale blocată")
```

### 4. Verificări în ChildService.create()
```python
# Verifică copil duplicat înainte de creare
# Mapează corect category_id la copiere simboluri
```

## Best Practices

1. ✅ Rulează verify_database_structure.py periodic
2. ✅ Folosește clean_*_duplicates.py dacă vezi probleme
3. ✅ NU crea categorii/simboluri globale manual
4. ✅ Folosește init_db.py pentru resetare completă
```

---

### `MANUAL_IMAGE_UPLOAD.md` (150 linii) 📚
**Rol:** Ghid upload manual imagini

**Conținut (sumar):**
```markdown
# Manual Upload Imagini

## Metoda 1: Via Script Python

```bash
# 1. Pune imaginile în backend/data/images/
cp ~/Downloads/*.jpg backend/data/images/

# 2. Rulează scriptul
python backend/upload_images_from_folder.py
```

## Metoda 2: Via API

```python
import requests

# Upload imagine pentru simbol
url = "http://localhost:8000/api/symbols/5/upload-image"
files = {"file": open("mama.jpg", "rb")}
headers = {"Authorization": "Bearer YOUR_TOKEN"}

response = requests.post(url, files=files, headers=headers)
print(response.json())
```

## Metoda 3: Via Frontend

```
1. Login ca terapeut
2. Deschide tabla unui copil
3. Click pe simbol → "Editează"
4. "Upload imagine" → Selectează fișier
5. Salvează
```

## Format Imagini

- Formate acceptate: JPG, PNG, GIF
- Dimensiune recomandată: 200x200px - 512x512px
- Mărime fișier: max 5MB per imagine
- Nume fișier: preferabil lowercase, fără spații

## Troubleshooting

**Imaginile nu apar în UI:**
- Verifică că backend-ul servește `/images/` corect
- Verifică permisiunile folder-ului data/images/
- Verifică că image_url în DB este corect (/images/nume.jpg)

**Eroare "Image not found":**
- Verifică că fișierul există fizic în data/images/
- Verifică că numele fișierului corespunde cu image_url din DB
```

---

## 🎨 Fișiere Frontend (va urma în partea 2)

Documentația continuă cu fișierele Flutter în fișierul separat...

---

**NOTA:** Acest fișier conține explicații DETALIATE pentru fiecare fișier backend. Pentru explicații complete frontend, vezi partea 2 a documentației.
