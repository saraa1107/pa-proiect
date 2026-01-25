@echo off
echo ========================================
echo   Instalare Flutter pentru Windows
echo ========================================
echo.

REM Verificare daca Flutter este deja instalat
where flutter >nul 2>&1
if %errorlevel% == 0 (
    echo Flutter este deja instalat!
    flutter --version
    echo.
    echo Verificare configuratie...
    flutter doctor
    pause
    exit /b 0
)

echo PASUL 1: Verificare locatie instalare...
set FLUTTER_DIR=%USERPROFILE%\flutter
set FLUTTER_ZIP=%TEMP%\flutter_windows.zip
set FLUTTER_URL=https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.24.5-stable.zip

echo Flutter va fi instalat in: %FLUTTER_DIR%
echo.

REM Verificare daca directorul exista deja
if exist "%FLUTTER_DIR%" (
    echo Directorul Flutter exista deja: %FLUTTER_DIR%
    echo Vrei sa continui? (S/N)
    set /p continue=
    if /i not "%continue%"=="S" (
        echo Instalare anulata.
        pause
        exit /b 1
    )
)

echo.
echo PASUL 2: Descarcare Flutter SDK...
echo Aceasta poate dura cateva minute...
echo.

REM Verificare daca exista deja arhiva
if exist "%FLUTTER_ZIP%" (
    echo Arhiva exista deja. Folosire arhiva existenta...
) else (
    echo Descarcare de la: %FLUTTER_URL%
    echo.
    
    REM Incercare cu PowerShell pentru descarcare
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%FLUTTER_URL%' -OutFile '%FLUTTER_ZIP%'}"
    
    if errorlevel 1 (
        echo.
        echo EROARE: Descarcarea a esuat!
        echo.
        echo SOLUTIE ALTERNATIVA:
        echo 1. Deschide: https://docs.flutter.dev/get-started/install/windows
        echo 2. Descarca manual Flutter SDK
        echo 3. Extrage in: %FLUTTER_DIR%
        echo 4. Adauga %FLUTTER_DIR%\bin in PATH
        echo.
        pause
        exit /b 1
    )
    
    echo Descarcare completa!
)

echo.
echo PASUL 3: Extragere Flutter SDK...
if exist "%FLUTTER_DIR%" (
    echo Directorul exista. Stergere...
    rmdir /s /q "%FLUTTER_DIR%"
)

REM Extragere cu PowerShell
powershell -Command "Expand-Archive -Path '%FLUTTER_ZIP%' -DestinationPath '%USERPROFILE%' -Force"

if errorlevel 1 (
    echo EROARE: Extragerea a esuat!
    echo Incercare cu 7-Zip sau WinRAR manual...
    pause
    exit /b 1
)

echo Extragere completa!

echo.
echo PASUL 4: Adaugare Flutter in PATH...
echo.
echo ATENTIE: Trebuie sa adaugi manual Flutter in PATH!
echo.
echo Urmeaza acesti pasi:
echo.
echo 1. Apasa Windows + R
echo 2. Scrie: sysdm.cpl
echo 3. Tab "Advanced" ^> "Environment Variables"
echo 4. In "User variables", selecteaza "Path" ^> "Edit"
echo 5. Adauga: %FLUTTER_DIR%\bin
echo 6. Click OK pe toate ferestrele
echo 7. Repornește terminalul sau computerul
echo.
echo SAU ruleaza manual in PowerShell (ca Administrator):
echo [Environment]::SetEnvironmentVariable("Path", $env:Path + ";%FLUTTER_DIR%\bin", "User")
echo.

REM Incercare adaugare automata in PATH (necesita restart terminal)
setx PATH "%PATH%;%FLUTTER_DIR%\bin" >nul 2>&1

echo.
echo PASUL 5: Verificare instalare...
echo.
echo IMPORTANT: Repornește terminalul dupa aceasta pentru ca PATH sa fie actualizat!
echo.
echo Dupa restart, ruleaza:
echo   flutter doctor
echo.
echo Pentru a verifica acum (poate nu functiona pana la restart):
if exist "%FLUTTER_DIR%\bin\flutter.bat" (
    echo Flutter SDK instalat cu succes in: %FLUTTER_DIR%
    "%FLUTTER_DIR%\bin\flutter.bat" doctor
) else (
    echo EROARE: Flutter nu a fost extras corect!
)

echo.
echo ========================================
echo   Instalare Flutter - Finalizata!
echo ========================================
echo.
echo URMATORII PASI:
echo 1. Repornește terminalul (sau computerul)
echo 2. Ruleaza: flutter doctor
echo 3. Instaleaza componentele lipsa dupa indicatii
echo 4. Ruleaza: flutter pub get in folderul frontend
echo.
pause


