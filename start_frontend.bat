@echo off
setlocal

echo ========================================
echo Pornire Frontend Flutter Web
echo ========================================
echo.

cd /d "%~dp0frontend"

REM Run in a completely clean environment
start cmd /c "title Flutter Frontend & flutter pub get & flutter run -d chrome & pause"

exit /b 0

