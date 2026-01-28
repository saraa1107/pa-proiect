# GitHub Setup Guide

## Inițializare Repository Local

### Pasul 1: Configurare Git

Dacă nu ai configurat Git încă:

```bash
git config --global user.name "Numele Tău"
git config --global user.email "email@example.com"
```

### Pasul 2: Inițializare Repository

În folderul proiectului:

```bash
git init
git add .
git commit -m "Initial commit - AAC Communication System"
```

### Pasul 3: Conectare cu GitHub

1. Creează un repository nou pe GitHub (fără README, .gitignore sau licență)

2. Conectează repository-ul local cu cel de pe GitHub:

```bash
git remote add origin https://github.com/USERNAME/REPOSITORY-NAME.git
git branch -M main
git push -u origin main
```

## .gitignore Recomandat

Asigură-te că ai următoarele în `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Flutter/Dart
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
.pub-cache/
.pub/
build/
*.iml

# Local data
backend/data/audio/
backend/data/images/
data/images/
```

## Comenzi Git Utile

### Verificare stare
```bash
git status
```

### Adăugare modificări
```bash
git add .
git commit -m "Mesaj descriptiv"
```

### Push către GitHub
```bash
git push origin main
```

### Pull ultimele modificări
```bash
git pull origin main
```

### Creare branch nou
```bash
git checkout -b feature/nume-feature
```

### Vezi istoricul
```bash
git log --oneline
```

## Colaborare pe GitHub

### Fork & Pull Request

1. Fork repository-ul pe GitHub
2. Clone fork-ul local:
   ```bash
   git clone https://github.com/USERNAME/FORK-NAME.git
   ```
3. Creează un branch pentru feature:
   ```bash
   git checkout -b feature/new-feature
   ```
4. Fă modificările și commit:
   ```bash
   git add .
   git commit -m "Add new feature"
   ```
5. Push pe fork:
   ```bash
   git push origin feature/new-feature
   ```
6. Creează Pull Request pe GitHub

## Troubleshooting

### Eroare: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/USERNAME/REPO.git
```

### Eroare: "failed to push some refs"
```bash
git pull origin main --rebase
git push origin main
```

### Reset la ultimul commit
```bash
git reset --hard HEAD
```

### Vezi toate remote-urile
```bash
git remote -v
```

## Protecție Date Sensibile

**IMPORTANT**: Nu face push la:
- Chei API/secrete
- Parole
- Baza de date cu date reale
- Token-uri de autentificare

Folosește variabile de mediu (`.env`) și adaugă `.env` în `.gitignore`.

## GitHub Actions (CI/CD) - Opțional

Creează `.github/workflows/test.yml` pentru testare automată:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python -m pytest
```

---

**Ready to collaborate!** 🚀
