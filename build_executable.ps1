#!/usr/bin/env powershell
<#
============================================================================
Crypto Bot Pro v34.0.1.2 - Script de Compilación PyInstaller (PowerShell)
============================================================================

DESCRIPCIÓN:
Este script automatiza completamente la creación del .exe desde cero

CARACTERÍSTICAS:
✅ Instalación automática de dependencias
✅ Compilación a .exe (archivo único)
✅ Sin dependencias externas
✅ Optimizaciones de rendimiento
✅ Manejo de errores robusto
✅ Logs detallados

USO:
    # En PowerShell como administrador:
    .\build_executable.ps1

    # O con opciones:
    .\build_executable.ps1 -SkipDependencies -Verbose

PARÁMETROS:
    -SkipDependencies      No reinstalar paquetes
    -CleanBuild            Limpiar compilaciones previas
    -RunAfterBuild         Ejecutar el .exe tras compilación
    -Verbose               Mostrar logs detallados

REQUISITOS:
    - Windows 7+ o Windows 10/11
    - PowerShell 5.1+
    - Python 3.8+
    - Conexión a internet
    - 2GB RAM libre mínimo
    - 500MB espacio en disco
#>

param(
    [switch]$SkipDependencies,
    [switch]$CleanBuild,
    [switch]$RunAfterBuild,
    [switch]$Verbose
)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

$ScriptVersion = "34.0.1.2"
$ProjectName = "CryptoBotPro"
$SpecFile = "build_executable.spec"
$MainScript = "Crypto-Pro-Python v34.0.1.2.py"
$ExeName = "CryptoBotPro.exe"

$OutputFolder = "dist"
$BuildFolder = "build"

# Lista de dependencias PyPI
$Dependencies = @(
    "PyInstaller",
    "pandas",
    "numpy",
    "torch",
    "scikit-learn",
    "scipy",
    "requests",
    "matplotlib",
    "mplfinance",
    "PyQt5",
    "PyQtWebEngine",
    "websocket-client",
    "schedule",
    "psutil",
    "Pillow",
    "python-binance",
    "python-telegram-bot",
    "aiohttp",
    "certifi",
    "joblib"
)

# ============================================================================
# FUNCIONES
# ============================================================================

function Show-Banner {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  Crypto Bot Pro v$ScriptVersion - Compilador PyInstaller        ║" -ForegroundColor Cyan
    Write-Host "║  Generando ejecutable único sin dependencias externas      ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Log-Message {
    param($Message, $Type = "INFO")
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prefix = switch($Type) {
        "INFO"    { "[*]"; "White" }
        "SUCCESS" { "[✓]"; "Green" }
        "ERROR"   { "[✗]"; "Red" }
        "WARNING" { "[!]"; "Yellow" }
        default   { "[*]"; "White" }
    }
    
    Write-Host "$prefix $Message" -ForegroundColor (switch($Type) {
        "INFO"    { "White" }
        "SUCCESS" { "Green" }
        "ERROR"   { "Red" }
        "WARNING" { "Yellow" }
        default   { "White" }
    })
    
    if ($Verbose) {
        Add-Content -Path "build_log.txt" -Value "$timestamp [$Type] $Message"
    }
}

function Test-Prerequisites {
    Log-Message "Verificando requisitos previos..."
    
    # 1. Verificar Python
    try {
        $pythonVersion = python --version 2>&1
        Log-Message "Python detectado: $pythonVersion" "SUCCESS"
    } catch {
        Log-Message "Python no está instalado o no en PATH" "ERROR"
        Log-Message "Descarga desde: https://www.python.org/downloads/" "INFO"
        exit 1
    }
    
    # 2. Verificar pip
    try {
        python -m pip --version | Out-Null
        Log-Message "pip disponible" "SUCCESS"
    } catch {
        Log-Message "pip no está disponible" "ERROR"
        exit 1
    }
    
    # 3. Verificar archivos necesarios
    if (-not (Test-Path $SpecFile)) {
        Log-Message "$SpecFile no encontrado" "ERROR"
        exit 1
    }
    Log-Message "$SpecFile encontrado" "SUCCESS"
    
    if (-not (Test-Path $MainScript)) {
        Log-Message "$MainScript no encontrado" "ERROR"
        exit 1
    }
    Log-Message "$MainScript encontrado" "SUCCESS"
    
    Log-Message "Todas las verificaciones pasaron" "SUCCESS"
}

function Install-Dependencies {
    Log-Message "Instalando dependencias Python..."
    Log-Message "Total: $($Dependencies.Count) paquetes"
    
    # Actualizar pip primero
    Log-Message "Actualizando pip..."
    python -m pip install --upgrade pip setuptools wheel --quiet
    
    $total = $Dependencies.Count
    $current = 0
    
    foreach ($pkg in $Dependencies) {
        $current++
        $percent = [math]::Round(($current / $total) * 100)
        Log-Message "[$current/$total] Instalando $pkg... ($percent%)"
        
        python -m pip install $pkg --quiet 2>$null
        
        if ($?) {
            Log-Message "$pkg instalado correctamente" "SUCCESS"
        } else {
            Log-Message "$pkg: instalación con advertencias" "WARNING"
        }
    }
    
    Log-Message "Dependencias instaladas" "SUCCESS"
}

function Clean-PreviousBuild {
    if ($CleanBuild) {
        Log-Message "Limpiando compilaciones previas..."
        
        if (Test-Path $BuildFolder) {
            Log-Message "Eliminando $BuildFolder..."
            Remove-Item -Path $BuildFolder -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        if (Test-Path $OutputFolder) {
            Log-Message "Eliminando $OutputFolder..."
            Remove-Item -Path $OutputFolder -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        Log-Message "Limpieza completada" "SUCCESS"
    }
}

function Build-Executable {
    Log-Message "Iniciando compilación PyInstaller..."
    Log-Message "Esto puede tomar 5-15 minutos, por favor espera..."
    
    $startTime = Get-Date
    
    # Ejecutar PyInstaller
    python -m PyInstaller $SpecFile `
        --distpath=$OutputFolder `
        --buildpath=$BuildFolder `
        --specpath=. `
        2>&1 | ForEach-Object {
            if ($Verbose) { Log-Message $_ "INFO" }
        }
    
    $endTime = Get-Date
    $duration = [math]::Round(($endTime - $startTime).TotalSeconds, 2)
    
    if ($LASTEXITCODE -eq 0) {
        Log-Message "Compilación completada en ${duration}s" "SUCCESS"
        return $true
    } else {
        Log-Message "Error en compilación (código: $LASTEXITCODE)" "ERROR"
        return $false
    }
}

function Verify-Executable {
    $exePath = Join-Path $OutputFolder $ExeName
    
    if (Test-Path $exePath) {
        $size = [math]::Round((Get-Item $exePath).Length / 1MB, 2)
        Log-Message "Ejecutable creado: $exePath" "SUCCESS"
        Log-Message "Tamaño: $size MB" "INFO"
        return $true
    } else {
        Log-Message "Ejecutable no encontrado" "ERROR"
        return $false
    }
}

function Show-Results {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  Compilación completada exitosamente                      ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "RESULTADO:" -ForegroundColor Yellow
    Write-Host "  Ubicación: .\$OutputFolder\$ExeName" -ForegroundColor White
    Write-Host "  Tamaño: ~150-300 MB (depende de modelos)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "CÓMO USAR:" -ForegroundColor Yellow
    Write-Host "  1. Distribución: Copia .\$OutputFolder\$ExeName a cualquier máquina Windows" -ForegroundColor White
    Write-Host "  2. Ejecución: Doble click en $ExeName" -ForegroundColor White
    Write-Host "  3. Automático: Crea CryptoBotPro_Data/ en la carpeta de ejecución" -ForegroundColor White
    Write-Host ""
    
    Write-Host "ARCHIVOS GENERADOS:" -ForegroundColor Yellow
    Write-Host "  ✓ dist/$ExeName - Ejecutable único" -ForegroundColor Green
    Write-Host "  ✓ build/ - Archivos intermedios de compilación" -ForegroundColor Green
    Write-Host "  ✓ *.spec - Archivo de configuración PyInstaller" -ForegroundColor Green
    
    if ($Verbose) {
        Write-Host "  ✓ build_log.txt - Log detallado de compilación" -ForegroundColor Green
    }
    Write-Host ""
}

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

Show-Banner

try {
    # 1. Verificaciones
    Test-Prerequisites
    
    # 2. Dependencias
    if (-not $SkipDependencies) {
        Install-Dependencies
    } else {
        Log-Message "Saltando instalación de dependencias" "WARNING"
    }
    
    # 3. Limpiar previos
    Clean-PreviousBuild
    
    # 4. Compilar
    if (Build-Executable) {
        # 5. Verificar resultado
        if (Verify-Executable) {
            Show-Results
            
            # 6. Ejecutar si se solicita
            if ($RunAfterBuild) {
                Log-Message "Ejecutando $ExeName..."
                & ".\$OutputFolder\$ExeName"
            }
        }
    } else {
        Log-Message "Compilación fallida. Revisa los errores arriba" "ERROR"
        exit 1
    }
    
} catch {
    Log-Message "Error no previsto: $_" "ERROR"
    exit 1
}

Write-Host ""
Write-Host "Script completado" -ForegroundColor Cyan
Write-Host ""
