@echo off
echo ========================================
echo   Instalare Manuala Backend
echo   (Pas cu pas pentru debugging)
echo ========================================
echo.

cd backend

echo PASUL 1: Creare mediu virtual...
if not exist "venv" (
    python -m venv venv
    echo Mediu virtual creat!
) else (
    echo Mediu virtual exista deja.
)

echo.
echo PASUL 2: Activare mediu virtual...
call venv\Scripts\activate.bat

echo.
echo PASUL 3: Actualizare pip...
python -m pip install --upgrade pip

echo.
echo PASUL 4: Instalare dependente UNA CATE UNA...
echo.
echo [1/9] Instalare fastapi...
pip install fastapi
if errorlevel 1 (
    echo EROARE la instalarea fastapi!
    pause
    exit /b 1
)

echo [2/9] Instalare uvicorn...
pip install "uvicorn[standard]"
if errorlevel 1 (
    echo EROARE la instalarea uvicorn!
    pause
    exit /b 1
)

echo [3/9] Instalare sqlalchemy...
pip install sqlalchemy
if errorlevel 1 (
    echo EROARE la instalarea sqlalchemy!
    pause
    exit /b 1
)

echo [4/9] Instalare pydantic...
pip install "pydantic[email]"
if errorlevel 1 (
    echo EROARE la instalarea pydantic!
    echo Incercare cu versiune mai veche...
    pip install "pydantic[email]<3.0"
    if errorlevel 1 (
        echo EROARE CRITICA: pydantic nu poate fi instalat!
        echo Vezi SOLUTIE_INSTALARE.txt pentru solutii alternative
        pause
        exit /b 1
    )
)

echo [4.5/9] Instalare email-validator...
pip install email-validator
if errorlevel 1 (
    echo EROARE la instalarea email-validator!
    pause
    exit /b 1
)

echo [5/10] Instalare python-multipart...
pip install python-multipart
if errorlevel 1 (
    echo EROARE la instalarea python-multipart!
    pause
    exit /b 1
)

echo [6/10] Instalare python-jose...
pip install "python-jose[cryptography]"
if errorlevel 1 (
    echo EROARE la instalarea python-jose!
    pause
    exit /b 1
)

echo [7/10] Instalare passlib...
pip install "passlib[bcrypt]"
if errorlevel 1 (
    echo EROARE la instalarea passlib!
    pause
    exit /b 1
)

echo [8/10] Instalare pyttsx3...
pip install pyttsx3
if errorlevel 1 (
    echo EROARE la instalarea pyttsx3!
    pause
    exit /b 1
)

echo [9/10] Instalare gTTS...
pip install gTTS
if errorlevel 1 (
    echo EROARE la instalarea gTTS!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   TOATE DEPENDENTELE INSTALATE CU SUCCES!
echo ========================================
echo.

echo PASUL 5: Verificare instalare...
python -c "import fastapi; print('✓ FastAPI OK')"
python -c "import sqlalchemy; print('✓ SQLAlchemy OK')"
python -c "import pydantic; print('✓ Pydantic OK')"

echo.
echo PASUL 6: Initializare baza de date...
if not exist "data\aac_database.db" (
    python init_db.py
    if errorlevel 1 (
        echo EROARE la initializarea bazei de date!
        pause
        exit /b 1
    )
    echo Baza de date initializata!
) else (
    echo Baza de date exista deja.
)

echo.
echo ========================================
echo   INSTALARE COMPLETA!
echo ========================================
echo.
echo Acum poti rula: python main.py
echo SAU foloseste: start_backend.bat
echo.
pause

