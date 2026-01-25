@echo off
echo ========================================
echo   Pornire Backend AAC Communication
echo ========================================
echo.

cd backend

echo Verificare mediu virtual...
if not exist "venv" (
    echo Creare mediu virtual...
    python -m venv venv
)

echo Activare mediu virtual...
call venv\Scripts\activate.bat

echo Instalare dependente...
pip install --upgrade pip
echo.
echo Incercare instalare cu requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo EROARE la instalare cu versiuni fixe!
    echo Incercare cu versiuni flexibile...
    pip install -r requirements_simple.txt
    if errorlevel 1 (
        echo.
        echo EROARE: Instalarea dependențelor a eșuat!
        echo Verifică erorile de mai sus.
        pause
        exit /b 1
    )
)

echo.
echo Verificare baza de date...
if not exist "data\aac_database.db" (
    echo Initializare baza de date...
    python init_db.py
    if errorlevel 1 (
        echo EROARE: Inițializarea bazei de date a eșuat!
        pause
        exit /b 1
    )
)

echo.
echo Verificare directoare necesare...
if not exist "data\images" (
    echo Creare director pentru imagini...
    mkdir data\images
)
if not exist "data\audio" (
    echo Creare director pentru audio...
    mkdir data\audio
)

echo.
echo ========================================
echo   Pornire server backend...
echo   Serverul va rula pe:
echo   - Local: http://localhost:8000
echo   - Rețea: http://[IP_LOCAL]:8000
echo   - Docs:  http://localhost:8000/docs
echo   Apasa Ctrl+C pentru a opri serverul
echo ========================================
echo.
echo Deschidere browser automat...
echo.

REM Așteaptă puțin și deschide browserul
timeout /t 3 /nobreak >nul
start http://localhost:8000/docs

python main.py

pause

