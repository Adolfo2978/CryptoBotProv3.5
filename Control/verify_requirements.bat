@echo off
REM ============================================================================
REM Crypto Bot Pro v34.0.1.2 - Verificador de Requisitos Previos
REM ============================================================================
REM Este script verifica que todo esté listo para compilar el .exe
REM Útil para detectar problemas antes de empezar

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Verificador de Requisitos - Crypto Bot Pro v34.0.1.2     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

set error_count=0
set warning_count=0

REM ========================================
REM 1. VERIFICAR PYTHON
REM ========================================
echo [*] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python NO está instalado o no en PATH
    echo         Descarga desde: https://www.python.org/downloads/
    set /a error_count+=1
) else (
    for /f "tokens=*" %%A in ('python --version 2^>^&1') do set python_version=%%A
    echo [OK] !python_version!
)
echo.

REM ========================================
REM 2. VERIFICAR PIP
REM ========================================
echo [*] Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip NO está disponible
    set /a error_count+=1
) else (
    for /f "tokens=*" %%A in ('python -m pip --version 2^>^&1') do set pip_version=%%A
    echo [OK] !pip_version!
)
echo.

REM ========================================
REM 3. VERIFICAR PYINSTALLER
REM ========================================
echo [*] Verificando PyInstaller...
python -m pip show PyInstaller >nul 2>&1
if errorlevel 1 (
    echo [WARNING] PyInstaller NO está instalado
    echo          Se instalará automáticamente al compilar
    set /a warning_count+=1
) else (
    for /f "tokens=2" %%A in ('python -m pip show PyInstaller ^| findstr Version') do set pyinstaller_version=%%A
    echo [OK] PyInstaller !pyinstaller_version!
)
echo.

REM ========================================
REM 4. VERIFICAR ARCHIVOS NECESARIOS
REM ========================================
echo [*] Verificando archivos necesarios...

if not exist "Crypto-Pro-Python v34.0.1.2.py" (
    echo [ERROR] No se encuentra: Crypto-Pro-Python v34.0.1.2.py
    set /a error_count+=1
) else (
    echo [OK] Crypto-Pro-Python v34.0.1.2.py
)

if not exist "build_executable.spec" (
    echo [ERROR] No se encuentra: build_executable.spec
    set /a error_count+=1
) else (
    echo [OK] build_executable.spec
)

if not exist "config_v20_optimized.json" (
    echo [WARNING] No se encuentra: config_v20_optimized.json (se creará en ejecución)
    set /a warning_count+=1
) else (
    echo [OK] config_v20_optimized.json
)

if not exist "CryptoBotPro_Data\models" (
    echo [WARNING] Carpeta CryptoBotPro_Data\models NO existe
    echo          Se creará al ejecutar el .exe
    set /a warning_count+=1
) else (
    echo [OK] Carpeta de modelos detectada
)

echo.

REM ========================================
REM 5. VERIFICAR DEPENDENCIAS CLAVE
REM ========================================
echo [*] Verificando librerías Python críticas...

setlocal enabledelayedexpansion
set packages=pandas numpy torch PyQt5 matplotlib requests websocket-client

for %%P in (!packages!) do (
    python -m pip show %%P >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] %%P NO instalado (se instalará al compilar)
        set /a warning_count+=1
    ) else (
        echo [OK] %%P
    )
)

echo.

REM ========================================
REM 6. VERIFICAR ESPACIO EN DISCO
REM ========================================
echo [*] Verificando espacio en disco...

for /f "tokens=4" %%A in ('wmic logicaldisk where name="C:" get FreeSpace /format:list ^| findstr .*') do (
    set space=%%A
)

if defined space (
    set /a space_gb=space/1024/1024/1024
    if !space_gb! geq 2 (
        echo [OK] Espacio disponible: !space_gb! GB (suficiente)
    ) else (
        echo [WARNING] Espacio disponible: !space_gb! GB (mínimo recomendado 2GB)
        set /a warning_count+=1
    )
) else (
    echo [INFO] No se puede determinar espacio en disco
)

echo.

REM ========================================
REM 7. RESUMEN
REM ========================================
echo ╔════════════════════════════════════════════════════════════╗
echo ║  RESUMEN DE VERIFICACIÓN                                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

if %error_count% equ 0 (
    if %warning_count% equ 0 (
        echo [✓] TODO ESTÁ OK - LISTO PARA COMPILAR
        echo.
        echo Puedes iniciar la compilación con:
        echo   .\build_executable.bat
        echo   O
        echo   .\build_executable.ps1
    ) else (
        echo [!] %warning_count% ADVERTENCIAS (pero se pueden resolver)
        echo.
        echo Algunas dependencias se instalarán automáticamente.
        echo Puedes compilar si lo deseas.
    )
) else (
    echo [✗] %error_count% ERRORES - NO SE PUEDE COMPILAR
    echo.
    echo Soluciona los errores marcados arriba:
    echo 1. Python no instalado - Descarga desde python.org
    echo 2. pip no funciona - Reinstala Python
    echo 3. Archivos faltantes - Verifica que estén en la carpeta
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════
echo.

pause
