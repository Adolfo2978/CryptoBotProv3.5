@echo off
REM ============================================================================
REM Crypto Bot Pro v34.0.1.2 - Installer de Dependencias
REM ============================================================================
REM Este script instala TODAS las dependencias necesarias para crear el .exe
REM 
REM USO:
REM   1. Abre PowerShell como administrador
REM   2. Navega a la carpeta del proyecto
REM   3. Ejecuta: .\install_dependencies.bat
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Crypto Bot Pro v34.0.1.2 - Instalador de Dependencias    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en PATH
    echo Descarga Python desde: https://www.python.org/downloads/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

echo [✓] Python detectado:
python --version
echo.

REM Actualizar pip
echo [*] Actualizando pip...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERROR] No se pudo actualizar pip
    pause
    exit /b 1
)
echo [✓] pip actualizado
echo.

REM Tabla de dependencias
echo [*] Instalando dependencias principales...
echo.

setlocal enabledelayedexpansion
set "packages=^
    PyInstaller ^
    pandas ^
    numpy ^
    torch ^
    scikit-learn ^
    scipy ^
    requests ^
    matplotlib ^
    mplfinance ^
    PyQt5 ^
    PyQtWebEngine ^
    websocket-client ^
    schedule ^
    psutil ^
    Pillow ^
    python-binance ^
    python-telegram-bot ^
    aiohttp ^
    certifi ^
    joblib"

set count=0
for %%P in (!packages!) do (
    set /a count+=1
)

set current=0
for %%P in (!packages!) do (
    set /a current+=1
    echo [!current!/!count!] Instalando %%P...
    python -m pip install %%P --quiet
    if errorlevel 1 (
        echo [!] Advertencia: Falló %%P, continuando...
    ) else (
        echo [✓] %%P instalado
    )
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Instalación completada                                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo Ahora puedes crear el .exe ejecutando:
echo   pyinstaller build_executable.spec
echo.
echo O usa el script:
echo   .\build_executable.bat
echo.

pause
