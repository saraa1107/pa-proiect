# Ghid de Accesare - AAC Communication System

## Pași pentru a accesa aplicația

### PASUL 1: Pornește Backend-ul (Python)

1. Deschide un terminal PowerShell în folderul proiectului
2. Navighează în folderul backend:
   ```powershell
   cd backend
   ```

3. Creează un mediu virtual (dacă nu există deja):
   ```powershell
   python -m venv venv
   ```

4. Activează mediul virtual:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   (Dacă primești o eroare de securitate, rulează: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)

5. Instalează dependențele:
   ```powershell
   pip install -r requirements.txt
   ```

6. Inițializează baza de date cu date de test:
   ```powershell
   python init_db.py
   ```

7. Pornește serverul backend:
   ```powershell
   python main.py
   ```

   **Backend-ul va rula pe: http://localhost:8000**

   Poți verifica dacă funcționează accesând:
   - http://localhost:8000 - Pagina principală API
   - http://localhost:8000/docs - Documentație Swagger interactivă

### PASUL 2: Pornește Frontend-ul (Flutter Web)

1. Deschide un **NOU** terminal PowerShell (lăsând backend-ul să ruleze)
2. Navighează în folderul frontend:
   ```powershell
   cd frontend
   ```

3. Instalează dependențele Flutter:
   ```powershell
   flutter pub get
   ```

4. Pornește aplicația Flutter Web:
   ```powershell
   flutter run -d chrome
   ```

   Aplicația se va deschide automat în browser-ul Chrome.

### PASUL 3: Accesează Aplicația

După ce ambele servere rulează:
- **Frontend**: Se va deschide automat în Chrome, sau accesează URL-ul afișat în terminal
- **Backend API**: http://localhost:8000
- **Documentație API**: http://localhost:8000/docs

## Verificare Rapidă

1. ✅ Backend rulează → Accesează http://localhost:8000 în browser (ar trebui să vezi un mesaj JSON)
2. ✅ Frontend rulează → Aplicația se deschide în Chrome automat

## Dacă întâmpini probleme

### Backend nu pornește:
- Verifică dacă portul 8000 este liber
- Verifică dacă toate dependențele sunt instalate: `pip list`

### Frontend nu pornește:
- Verifică dacă Flutter este instalat: `flutter --version`
- Verifică dacă backend-ul rulează (frontend-ul are nevoie de backend)

### Eroare CORS:
- Backend-ul este configurat să permită toate originile în modul de dezvoltare
- Dacă totuși apare, verifică că backend-ul rulează pe localhost:8000


