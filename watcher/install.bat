@echo off
echo ============================================
echo  Crimson Desert Save Watcher - Installation
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python nicht gefunden!
    echo Bitte installiere Python 3.10+ von https://www.python.org/downloads/
    echo WICHTIG: Bei der Installation "Add Python to PATH" ankreuzen!
    pause
    exit /b 1
)

echo [OK] Python gefunden:
python --version
echo.

:: Create venv
echo Erstelle virtuelle Umgebung...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [FEHLER] Konnte venv nicht erstellen
    pause
    exit /b 1
)
echo [OK] .venv erstellt
echo.

:: Install dependencies
echo Installiere Abhaengigkeiten...
.venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [FEHLER] pip install fehlgeschlagen
    pause
    exit /b 1
)
echo.
echo [OK] Alle Abhaengigkeiten installiert
echo.

:: Check config
if exist config.json (
    echo [OK] config.json vorhanden
) else (
    echo [WARNUNG] config.json fehlt - kopiere von config.example.json
    copy config.example.json config.json
)
echo.

:: Check save directory
echo Pruefe Crimson Desert Save-Verzeichnis...
if exist "%LOCALAPPDATA%\Pearl Abyss\CD\save" (
    echo [OK] Save-Verzeichnis gefunden: %LOCALAPPDATA%\Pearl Abyss\CD\save
    for /d %%d in ("%LOCALAPPDATA%\Pearl Abyss\CD\save\*") do (
        echo      Steam-ID Ordner: %%~nxd
    )
) else (
    echo [WARNUNG] Save-Verzeichnis nicht gefunden.
    echo           Starte Crimson Desert einmal, damit es angelegt wird.
)
echo.

echo ============================================
echo  Installation abgeschlossen!
echo ============================================
echo.
echo  Starten mit:  start.bat
echo  Oder manuell: .venv\Scripts\python watcher.py
echo.
pause
