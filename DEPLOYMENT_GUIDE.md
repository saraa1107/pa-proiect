# 🚀 Ghid Deployment - AAC Communication System pe Web

## 📋 Overview

Acest ghid te ajută să publici aplicația ca **site web accesibil de pe orice dispozitiv** (Windows, Android, iOS, Mac) **fără instalări**.

### Ce vei obține:
- ✅ Backend API accesibil 24/7 pe internet
- ✅ Frontend Flutter Web (site funcțional)
- ✅ Database PostgreSQL în cloud
- ✅ Imagini hosted pe CDN
- ✅ Acces de pe orice browser (Chrome, Safari, Firefox, Edge)

---

## 🏗️ Arhitectură Deployment

```
┌─────────────────────────────────────────────────┐
│  USERS (orice dispozitiv cu browser)            │
│  Windows / Android / iOS / Mac / Linux          │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  FRONTEND (Flutter Web)                         │
│  Hosted pe: Netlify / Vercel / Firebase        │
│  URL: https://aac-app.netlify.app              │
└──────────────────┬──────────────────────────────┘
                   │ HTTP Requests
                   ▼
┌─────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                              │
│  Hosted pe: Render / Railway / Heroku          │
│  URL: https://aac-backend.onrender.com         │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌─────────────────┐  ┌──────────────────┐
│  DATABASE       │  │  FILE STORAGE    │
│  PostgreSQL     │  │  Cloudinary /    │
│  (Supabase/     │  │  AWS S3          │
│   Render)       │  │  (Imagini)       │
└─────────────────┘  └──────────────────┘
```

---

## 🎯 Planul de Deployment (3 Pași)

### **Pas 1:** Deploy Backend (FastAPI) → **~20 minute**
### **Pas 2:** Deploy Frontend (Flutter Web) → **~15 minute**
### **Pas 3:** Configurare Database & Assets → **~10 minute**

**Total timp estimat:** ~45 minute pentru deployment complet

---

# 📦 Pas 1: Deploy Backend (FastAPI)

## Opțiune Recomandată: Render.com (Gratuit)

**De ce Render?**
- ✅ Gratuit pentru proiecte mici
- ✅ PostgreSQL database inclus
- ✅ Deploy automat din GitHub
- ✅ HTTPS built-in
- ✅ Nu necesită credit card

### 1.1 Pregătire Backend

#### A. Creează `requirements.txt` pentru deployment
Fișierul `backend/requirements_production.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic[email]==2.5.0
bcrypt==4.1.1
python-jose[cryptography]==3.3.0
gTTS==2.5.0
requests==2.31.0
python-multipart==0.0.6
email-validator==2.1.0
psycopg2-binary==2.9.9
python-decouple==3.8
```

**Nota:** `psycopg2-binary` pentru PostgreSQL, `python-decouple` pentru environment variables

#### B. Creează `.env.example`

```env
# Database (PostgreSQL in production)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_ORIGINS=https://aac-app.netlify.app,http://localhost:3000

# File Storage (optional)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

#### C. Modifică `database.py` pentru PostgreSQL

**Fișier:** `backend/database.py`

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# Citește DATABASE_URL din environment
DATABASE_URL = config('DATABASE_URL', default='sqlite:///./data/aac_database.db')

# Fix pentru Render PostgreSQL (folosește postgresql:// nu postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Creează engine
if DATABASE_URL.startswith("postgresql://"):
    # PostgreSQL (production)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # SQLite (development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### D. Modifică `main.py` pentru production

Adaugă la începutul fișierului:

```python
from decouple import config

# Environment variables
SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-in-production')
ALLOWED_ORIGINS_STR = config('ALLOWED_ORIGINS', default='http://localhost:3000,http://localhost:8000')
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(',')]

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # În loc de ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### E. Creează `render.yaml`

**Fișier:** `render.yaml` (root folder)

```yaml
services:
  # Backend API
  - type: web
    name: aac-backend
    env: python
    buildCommand: |
      cd backend
      pip install -r requirements_production.txt
    startCommand: |
      cd backend
      python init_db.py
      uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: aac-database
          property: connectionString
      - key: ALLOWED_ORIGINS
        value: https://aac-app.netlify.app

databases:
  - name: aac-database
    databaseName: aac_db
    user: aac_user
    plan: free
```

### 1.2 Deploy pe Render

**Pași:**

1. **Creează cont Render:** https://render.com/register
2. **Conectează GitHub:**
   - Push codul pe GitHub (vezi secțiunea GitHub Setup)
   - În Render Dashboard → "New +" → "Blueprint"
   - Selectează repository-ul `pa-proiect`
   - Render va detecta automat `render.yaml`
3. **Deploy automat:**
   - Click "Apply"
   - Render va crea:
     - PostgreSQL database
     - Web service (backend)
   - Durată: ~5-10 minute
4. **Notează URL-ul:** `https://aac-backend.onrender.com`

**Testing:**
```bash
curl https://aac-backend.onrender.com/docs
# Ar trebui să vezi Swagger UI
```

---

# 🎨 Pas 2: Deploy Frontend (Flutter Web)

## Opțiune Recomandată: Netlify (Gratuit)

**De ce Netlify?**
- ✅ Gratuit pentru site-uri statice
- ✅ Deploy automat din GitHub
- ✅ HTTPS gratuit
- ✅ CDN global
- ✅ Custom domain support

### 2.1 Build Flutter Web

#### A. Configurare API URL

**Fișier:** `frontend/lib/services/api_service.dart`

Modifică:

```dart
class ApiService {
  // Detectează environment automat
  static String get baseUrl {
    // Production (deployed)
    if (kReleaseMode) {
      return 'https://aac-backend.onrender.com/api';
    }
    // Development (local)
    return 'http://localhost:8000/api';
  }
  
  static String get backendUrl {
    if (kReleaseMode) {
      return 'https://aac-backend.onrender.com';
    }
    return 'http://localhost:8000';
  }
  
  // ... rest of code
}
```

Adaugă import la început:
```dart
import 'package:flutter/foundation.dart'; // pentru kReleaseMode
```

#### B. Build pentru Web

**Comenzi:**

```bash
cd frontend

# Install dependencies
flutter pub get

# Build pentru web (production)
flutter build web --release --web-renderer html

# Output va fi în: frontend/build/web/
```

**Optimizări build:**
```bash
# Build cu optimizări extra
flutter build web --release \
  --web-renderer html \
  --dart-define=FLUTTER_WEB_USE_SKIA=false \
  --pwa-strategy=offline-first
```

#### C. Configurare `netlify.toml`

**Fișier:** `frontend/netlify.toml`

**Important:** Netlify NU instalează Flutter automat. Folosim `build.sh` care descarcă și instalează Flutter SDK în timpul build-ului.

```toml
[build]
  publish = "build/web"
  command = "bash build.sh"
  base = "frontend"

[build.environment]
  FLUTTER_VERSION = "3.16.5"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

### 2.2 Deploy pe Netlify

**Opțiune 1: Deploy manual (quick)**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd frontend
netlify deploy --prod --dir=build/web

# Va returna URL-ul: https://random-name-123.netlify.app
```

**Opțiune 2: Deploy automat din GitHub**

1. **Deschide:** https://app.netlify.com/
2. **New site from Git**
3. **Selectează GitHub → repository pa-proiect**
4. **Build settings:**
   - Base directory: `frontend`
   - Build command: `flutter pub get && flutter build web --release`
   - Publish directory: `frontend/build/web`
5. **Deploy site**

**Customizare nume:**
- Site settings → Change site name → `aac-communication`
- URL final: `https://aac-communication.netlify.app`

---

# 🗄️ Pas 3: Database & File Storage

## 3.1 Database (PostgreSQL)

**Render se ocupă automat** de PostgreSQL când deployezi cu `render.yaml`.

### Inițializare Database

După primul deploy, backend-ul va rula automat `init_db.py` și va crea:
- Toate tabelele (users, children, categories, symbols)
- 6 categorii globale
- 50 simboluri globale

**Verificare:**
```bash
# Conectează-te la database din Render Dashboard
# Render Dashboard → aac-database → Connect → PSQL Command
# Copiază comanda și rulează în terminal

# Verifică tabele
\dt

# Verifică date
SELECT COUNT(*) FROM categories;
SELECT COUNT(*) FROM symbols;
```

## 3.2 File Storage (Imagini)

**Problema:** Render free tier NU păstrează fișiere uploaded (filesystem e ephemeral)

**Soluție:** Cloudinary (gratuit pentru 25GB)

### Setup Cloudinary

1. **Creează cont:** https://cloudinary.com/users/register/free
2. **Notează credențiale:**
   - Cloud name: `dxxxxxx`
   - API Key: `123456789`
   - API Secret: `abcdefgh`
3. **Adaugă în Render Environment Variables:**
   ```
   CLOUDINARY_CLOUD_NAME=dxxxxxx
   CLOUDINARY_API_KEY=123456789
   CLOUDINARY_API_SECRET=abcdefgh
   ```

### Modifică Backend pentru Cloudinary

**Instalează:** `pip install cloudinary`

**Fișier:** `backend/services.py` (modifică SymbolService.upload_image)

```python
import cloudinary
import cloudinary.uploader
from decouple import config

# Configurare Cloudinary
cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME', default=''),
    api_key=config('CLOUDINARY_API_KEY', default=''),
    api_secret=config('CLOUDINARY_API_SECRET', default='')
)

class SymbolService:
    @staticmethod
    def upload_image(db: Session, symbol_id: int, file: UploadFile):
        symbol = db.query(Symbol).filter(Symbol.id == symbol_id).first()
        if not symbol:
            raise ValueError("Simbolul nu există")
        
        # Upload la Cloudinary
        try:
            result = cloudinary.uploader.upload(
                file.file,
                folder="aac-symbols",
                public_id=f"symbol_{symbol_id}",
                overwrite=True
            )
            
            # Salvează URL-ul Cloudinary
            symbol.image_url = result['secure_url']
            db.commit()
            return symbol
        except Exception as e:
            # Fallback la local storage (doar pentru dev)
            # ... (cod existent)
```

### Upload Imagini Inițiale

**Script:** `backend/upload_images_cloudinary.py`

```python
import cloudinary
import cloudinary.uploader
from pathlib import Path
from database import SessionLocal
from models import Symbol
from decouple import config

# Configurare
cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET')
)

db = SessionLocal()

# Upload toate imaginile din data/images/
images_dir = Path("data/images")
for img_path in images_dir.glob("*.jpg"):
    # Găsește simbolul
    symbol_name = img_path.stem
    symbol = db.query(Symbol).filter(Symbol.name.ilike(f"%{symbol_name}%")).first()
    
    if symbol:
        # Upload la Cloudinary
        result = cloudinary.uploader.upload(
            str(img_path),
            folder="aac-symbols",
            public_id=f"symbol_{symbol.id}"
        )
        
        # Update DB
        symbol.image_url = result['secure_url']
        print(f"✓ {symbol.name} → {result['secure_url']}")

db.commit()
db.close()
print("\n✅ Upload complet!")
```

**Rulează:**
```bash
cd backend
python upload_images_cloudinary.py
```

---

# 🔗 Pas 4: Conectare Frontend ↔ Backend

## 4.1 Update Frontend cu Backend URL

Deja făcut în Pas 2.1.A - `api_service.dart` detectează automat production URL.

## 4.2 CORS Configuration

**Fișier:** `backend/main.py`

```python
# CORS - permite access de pe Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aac-communication.netlify.app",  # Production
        "http://localhost:3000",                   # Local dev
        "http://localhost:*",                      # Local dev (orice port)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

# ✅ Verificare Finală

## Testing Production

### 1. Test Backend
```bash
curl https://aac-backend.onrender.com/docs
# Ar trebui să vezi Swagger UI
```

### 2. Test Frontend
Deschide browser: `https://aac-communication.netlify.app`

**Flow test:**
1. ✅ Pagina se încarcă (ModeSelectionScreen)
2. ✅ Click "Mod Terapeut" → LoginScreen
3. ✅ Înregistrează cont nou
4. ✅ Login funcționează
5. ✅ Dashboard arată copii
6. ✅ Creează copil nou
7. ✅ Deschide tabla AAC
8. ✅ Simbolurile se încarcă cu imagini
9. ✅ Click simbol → adaugă în propoziție
10. ✅ Click 🔊 → audio se redă

### 3. Test pe Mobile

**Android/iOS:**
- Deschide Chrome/Safari
- Navighează la: `https://aac-communication.netlify.app`
- **Add to Home Screen** (opțional - PWA)

---

# 🚀 Bonus: PWA (Progressive Web App)

Flutter Web generează automat PWA support.

**Features:**
- ✅ Instalabil pe telefon (ca aplicație nativă)
- ✅ Funcționează offline (cu cache)
- ✅ Icon pe home screen
- ✅ Full screen mode

**Nu necesită cod extra** - deja configurat în Flutter!

---

# 📊 Costuri Estimate

| Serviciu | Plan | Cost |
|----------|------|------|
| **Render** (Backend + DB) | Free Tier | **$0/lună** |
| **Netlify** (Frontend) | Free Tier | **$0/lună** |
| **Cloudinary** (Imagini) | Free (25GB) | **$0/lună** |
| **Domain (opțional)** | .com/.ro | $10-15/an |
| **TOTAL** | | **$0/lună** 🎉 |

**Limitări Free Tier:**
- Render: Backend dorm după 15 min inactivitate (primul request ia ~30s să pornească)
- Netlify: 100GB bandwidth/lună (suficient pentru 1000+ useri/lună)
- Cloudinary: 25GB storage (suficient pentru ~10,000 imagini)

**Upgrade când:**
- Ai >100 utilizatori activi simultan → Render Starter ($7/lună)
- Trafic >100GB/lună → Netlify Pro ($19/lună)

---

# 🔧 Alternative Deployment

## Alte opțiuni Backend:

### Railway.app (Simplu, $5/lună după trial)
```bash
railway login
railway init
railway up
railway add postgresql
```

### Heroku (Classic, $7/lună)
```bash
heroku login
heroku create aac-backend
heroku addons:create heroku-postgresql:mini
git push heroku main
```

### DigitalOcean App Platform ($5/lună)
- Droplet + Docker container
- Mai complex, dar mai mult control

## Alte opțiuni Frontend:

### Vercel (Alternative la Netlify)
```bash
npm i -g vercel
cd frontend
vercel --prod
```

### Firebase Hosting (Google)
```bash
npm install -g firebase-tools
firebase login
firebase init hosting
firebase deploy
```

### GitHub Pages (Gratuit, dar mai limitat)
```bash
cd frontend
flutter build web
# Push build/web/ în branch gh-pages
```

---

# 📱 Custom Domain (Opțional)

## Configurare Domain Propriu

### 1. Cumpără Domain
- Namecheap, GoDaddy, Google Domains
- Ex: `aac-comunicare.ro` (~$15/an)

### 2. Configurare DNS

**Pentru Frontend (Netlify):**
```
A Record: @ → 75.2.60.5
CNAME: www → aac-communication.netlify.app
```

**Pentru Backend (Render):**
```
CNAME: api → aac-backend.onrender.com
```

**Rezultat:**
- Frontend: `https://aac-comunicare.ro`
- Backend: `https://api.aac-comunicare.ro`

### 3. Update Environment Variables

**Render:**
```
ALLOWED_ORIGINS=https://aac-comunicare.ro,https://www.aac-comunicare.ro
```

**Frontend:**
```dart
static const String baseUrl = 'https://api.aac-comunicare.ro/api';
```

---

# 🐛 Troubleshooting

## Backend nu pornește
```bash
# Verifică logs în Render Dashboard
# Render → Services → aac-backend → Logs

# Cauze comune:
# - requirements.txt lipsește pachete
# - DATABASE_URL greșit
# - Port greșit (trebuie să folosească $PORT env variable)
```

## Frontend nu se conectează la Backend
```bash
# Verifică CORS în browser console (F12)
# Verifică că API URL e corect (production vs development)
# Verifică că backend e pornit (https://aac-backend.onrender.com/docs)
```

## Imagini nu se încarcă
```bash
# Verifică Cloudinary credentials
# Verifică că imaginile au fost uploadate
# Verifică URL-urile în database (ar trebui să înceapă cu https://res.cloudinary.com/)
```

## Database connection fails
```bash
# Verifică DATABASE_URL în Render Environment Variables
# Verifică că postgresql:// nu postgres://
# Verifică că psycopg2-binary e instalat
```

---

# 📚 Resurse Utile

- **Render Docs:** https://render.com/docs
- **Netlify Docs:** https://docs.netlify.com
- **Flutter Web:** https://docs.flutter.dev/deployment/web
- **Cloudinary Docs:** https://cloudinary.com/documentation

---

# ✅ Checklist Final

```
□ Backend deployed pe Render
  □ PostgreSQL database creată
  □ Environment variables configurate
  □ init_db.py rulat cu succes
  □ Swagger UI accesibil (/docs)

□ Frontend deployed pe Netlify
  □ Flutter build web generat
  □ API URL configurat pentru production
  □ Site accesibil în browser

□ File Storage
  □ Cloudinary account creat
  □ Imagini uploadate
  □ Backend configurat pentru Cloudinary

□ Testing
  □ Register + Login funcționează
  □ Creare copil funcționează
  □ Simboluri se încarcă cu imagini
  □ TTS funcționează
  □ Testat pe mobile (Chrome/Safari)

□ (Opțional) Custom Domain
  □ Domain cumpărat
  □ DNS configurat
  □ SSL certificat activ
```

---

🎉 **Felicitări! Aplicația ta e acum live pe internet!** 🎉

Toată lumea poate accesa de pe orice dispozitiv cu browser:
- **Frontend:** `https://aac-communication.netlify.app`
- **Backend API:** `https://aac-backend.onrender.com/docs`

**Nu mai e nevoie de instalări - doar un link!** 🚀
