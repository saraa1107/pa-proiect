# 🚀 Quick Start - Deployment în 5 Minute

## Prerequisite: GitHub Account

**Dacă nu ai cont GitHub:**
1. https://github.com/join
2. Confirmă email-ul
3. Install Git: https://git-scm.com/downloads

---

## Step 1: Push la GitHub (2 minute)

```bash
# Navighează în folder
cd "C:\Users\gabri\OneDrive\Desktop\pa-proiect"

# Inițializează Git (dacă nu e deja)
git init

# Adaugă .gitignore
echo "data/" >> .gitignore
echo ".env" >> .gitignore
echo "**/__pycache__/" >> .gitignore
echo "**/build/" >> .gitignore
echo "**/.dart_tool/" >> .gitignore

# Adaugă toate fișierele
git add .
git commit -m "Initial commit - AAC Communication System"

# Creează repository pe GitHub
# https://github.com/new
# Nume: "aac-communication-system"
# Public sau Private

# Link la GitHub (înlocuiește USERNAME)
git remote add origin https://github.com/USERNAME/aac-communication-system.git
git branch -M main
git push -u origin main
```

**✅ Checkpoint:** Verifică că toate fișierele sunt pe GitHub

---

## Step 2: Deploy Backend pe Render (1 minut setup)

1. **Deschide:** https://render.com/
2. **Sign Up** cu GitHub
3. **New** → **Blueprint**
4. **Conectează repository:** `aac-communication-system`
5. Render detectează `render.yaml` automat
6. **Apply**

**⏱️ Așteptare:** ~5-10 minute pentru build & deploy

**✅ Checkpoint:** 
- Accesează: `https://aac-backend-xxxx.onrender.com/docs`
- Ar trebui să vezi Swagger UI

---

## Step 3: Deploy Frontend pe Netlify (1 minut setup)

### Opțiunea A: Via Website (Recomandat)

1. **Deschide:** https://app.netlify.com/
2. **Sign Up** cu GitHub
3. **Add new site** → **Import from Git**
4. **Selectează:** `aac-communication-system`
5. **Build settings:**
   - Base directory: `frontend`
   - Build command: `bash build.sh` (scriptul instalează Flutter automat)
   - Publish directory: `frontend/build/web`
   - Environment variables: `FLUTTER_VERSION = 3.16.5`
6. **Deploy site**

### Opțiunea B: Via CLI (Pentru devs)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Build Flutter
cd frontend
flutter build web --release

# Deploy
netlify deploy --prod --dir=build/web
```

**⏱️ Așteptare:** ~5-10 minute pentru build

**✅ Checkpoint:**
- Accesează URL-ul (ex: `https://random-name-123.netlify.app`)
- Website se încarcă

---

## Step 4: Configurare Finală (1 minut)

### A. Update Backend URL în Frontend

**Fișier:** `frontend/lib/services/api_service.dart`

Linia 15 - schimbă URL-ul:
```dart
return 'https://TAU-BACKEND-URL.onrender.com/api';
```

### B. Update CORS în Backend

**În Render Dashboard:**
1. Backend Service → Environment
2. Adaugă variabilă:
   - Key: `ALLOWED_ORIGINS`
   - Value: `https://TAU-FRONTEND-URL.netlify.app`
3. **Manual Deploy** (buton sus-dreapta)

### C. Re-deploy Frontend

```bash
cd frontend
flutter build web --release
netlify deploy --prod --dir=build/web
```

**SAU** push pe GitHub și Netlify va rebuilda automat:
```bash
git add .
git commit -m "Update backend URL"
git push
```

---

## ✅ GATA! Aplicația e LIVE

**Frontend:** `https://TAU-APP.netlify.app`
**Backend API:** `https://TAU-BACKEND.onrender.com`

### Testare Finală

1. Deschide frontend în browser
2. Click "Mod Terapeut"
3. Înregistrează cont nou
4. Login
5. Creează copil
6. Deschide tabla AAC
7. Click simboluri
8. Click 🔊 pentru audio

**Dacă totul funcționează → 🎉 SUCCESS! 🎉**

---

## 🔧 Troubleshooting Rapid

### Backend nu pornește
```bash
# Verifică logs în Render Dashboard
# Cauze comune:
# - DATABASE_URL lipsă → Render ar trebui să-l seteze automat
# - requirements.txt greșit → verifică fișierul
```

### Frontend 404 la API calls
```bash
# Verifică în browser console (F12)
# Cauze:
# - Backend URL greșit în api_service.dart
# - CORS blocat → verifică ALLOWED_ORIGINS în Render
```

### First deploy slow
```
Render free tier: backend dorm după 15 min inactivitate
Prima cerere ia ~30-60s să pornească
NORMAL! După pornire merge rapid.
```

---

## 📱 Bonus: Instalare ca PWA pe Telefon

### Android (Chrome)
1. Deschide site-ul
2. Menu (⋮) → "Add to Home screen"
3. Icon apare pe home screen
4. Se deschide fullscreen ca aplicație

### iOS (Safari)
1. Deschide site-ul
2. Share button → "Add to Home Screen"
3. Icon apare pe home screen

**Acum aplicația arată ca o aplicație nativă!** 📱

---

## 🎯 Next Steps (Opțional)

### Custom Domain
1. Cumpără domain: `aac-comunicare.ro`
2. Netlify → Domain settings → Add custom domain
3. Update DNS records
4. SSL automat activat

### Cloudinary (Imagini în Cloud)
1. Cont gratuit: https://cloudinary.com/users/register/free
2. Copiază credentials în Render Environment Variables
3. Rulează: `python backend/upload_images_cloudinary.py`
4. Upload imagini demo

### Monitoring
- Render: Built-in monitoring (CPU, Memory, Response time)
- Netlify: Analytics (Free 100k pageviews/lună)
- Sentry: Error tracking (opțional)

---

## 💰 Costuri

**FREE TIER (suficient pentru start):**
- Render Backend: $0/lună (cu inactivitate sleep)
- Netlify Frontend: $0/lună (100GB bandwidth)
- Database: $0/lună (90 zile free, apoi $7/lună)
- Cloudinary: $0/lună (25GB storage)

**TOTAL: $0/lună pentru primele 90 zile**

**După 90 zile:** $7/lună (doar database)

---

🎉 **Felicitări! Ai un site AAC live accesibil de peste tot!** 🎉
