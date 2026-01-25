@echo off
echo ========================================
echo   Fix: Instalare email-validator
echo ========================================
echo.

cd backend

echo Activare mediu virtual...
call venv\Scripts\activate.bat

echo Instalare email-validator...
pip install email-validator

echo.
echo Verificare instalare...
python -c "import email_validator; print('✓ email-validator OK')"

echo.
echo Acum poti rula: python init_db.py
echo.
pause


