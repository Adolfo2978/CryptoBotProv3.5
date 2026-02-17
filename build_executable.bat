@echo off
REM ============================================================================
REM Crypto Bot Pro v34.0.1.2 - Script de Compilación a .exe
REM ============================================================================
REM Este script compila el bot Python en un archivo .exe ejecutable único
REM Sin dependencias externas - TODO empaquetado en 1 archivo
REM
REM USO:
REM   1. Abre una terminal en la carpeta del proyecto
REM   2. Ejecuta: build_executable.bat
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Crypto Bot Pro v34.0.1.2 - Compilador PyInstaller        ║
echo ║  Generando ejecutable único sin dependencias externas      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificaciones previas
echo [*] Realizando verificaciones...

REM 1. Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado
    pause
    exit /b 1
)
echo [✓] Python disponible

REM 2. Verificar PyInstaller
python -m pip show PyInstaller >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller no está instalado
    echo Ejecuta primero: install_dependencies.bat
    pause
    exit /b 1
)
echo [✓] PyInstaller disponible

REM 3. Verificar archivo spec
if not exist "build_executable.spec" (
    echo [ERROR] No se encuentra build_executable.spec
    pause
    exit /b 1
)
echo [✓] build_executable.spec encontrado

REM 4. Verificar script principal
if not exist "Crypto-Pro-Python v34.0.1.2.py" (
    echo [ERROR] No se encuentra Crypto-Pro-Python v34.0.1.2.py
    pause
    exit /b 1
)
echo [✓] Script principal encontrado

echo.
echo [*] Iniciando compilación...
echo    Esto puede tomar 5-15 minutos dependiendo de tu CPU
echo    Por favor, espera...
echo.

REM Limpiar compilaciones anteriores
if exist "build" (
    echo [*] Limpiando compilación anterior...
    rmdir /s /q build >nul 2>&1
)

if exist "dist" (
    echo [*] Limpiando distribución anterior...
    rmdir /s /q dist >nul 2>&1
)

REM Ejecutar PyInstaller
echo [*] Ejecutando PyInstaller...
echo.

python -m PyInstaller build_executable.spec --distpath=dist --buildpath=build --specpath=.

if errorlevel 1 (
    echo.
    echo [ERROR] La compilación falló
    echo Posibles causas:
    echo   - Módulos Python faltantes (ejecuta install_dependencies.bat)
    echo   - Archivos con nombres inválidos
    echo   - Insuficiente memoria RAM
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Compilación completada con éxito                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar resultado
if exist "dist\CryptoBotPro.exe" (
    for /f "tokens=*" %%A in ('powershell -Command "(Get-Item 'dist\CryptoBotPro.exe').Length / 1MB"') do set size=%%A
    echo [✓] Ejecutable creado: dist\CryptoBotPro.exe
    echo    Tamaño: ~!size! MB
    echo.
    echo [✓] LISTO PARA USAR
    echo.
    echo Para ejecutar:
    echo   .\dist\CryptoBotPro.exe
    echo.
    echo El programa creará automáticamente:
    echo   - CryptoBotPro_Data/
    echo   - CryptoBotPro_Data/logs/
    echo   - CryptoBotPro_Data/cache/
    echo   - CryptoBotPro_Data/models/
    echo.
) else (
    echo [ERROR] El ejecutable no se creó correctamente
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo  SIGUIENTE: Distribuir dist\CryptoBotPro.exe
echo ═══════════════════════════════════════════════════════════
echo.

REM Opciones finales
echo ¿Deseas...?
echo   1. Abrir la carpeta dist/
echo   2. Ejecutar el programa ahora
echo   3. Salir
echo.

set /p option="Selecciona una opción (1-3): "

if "%option%"=="1" (
    start explorer.exe dist
) else if "%option%"=="2" (
    cd dist
    CryptoBotPro.exe
) else (
    echo Adiós
)

echo.
pause
