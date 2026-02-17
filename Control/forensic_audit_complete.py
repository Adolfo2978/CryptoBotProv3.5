#!/usr/bin/env python3
"""
🔍 AUDITORÍA FORENSE COMPLETA - Crypto Bot Pro v34.0.1.2
Análisis profundo de:
- Conectividad API
- Obtención de datos
- Flujo de procesamiento
- Estado del sistema
"""

import json
import sys
import os
import traceback
import logging
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Agregar ruta parent para importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ======================== CONFIGURAR LOGGING ========================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
audit_logger = logging.getLogger('ForensicAudit')

# ======================== ESTRUCTURA DE REPORTE ========================
AUDIT_REPORT = {
    "timestamp": datetime.now().isoformat(),
    "version": "34.0.1.2",
    "system_checks": {},
    "api_connectivity": {},
    "data_retrieval": {},
    "data_flow": {},
    "performance": {},
    "warnings": [],
    "errors": [],
    "recommendations": []
}

def log_and_report(level, message, category="general"):
    """Registra en log y en reporte"""
    print(f"[{level.upper()}] {message}")
    if level == "error":
        AUDIT_REPORT["errors"].append(message)
    elif level == "warning":
        AUDIT_REPORT["warnings"].append(message)
    audit_logger.log(getattr(logging, level.upper()), message)

# ======================== 1. VERIFICACIÓN DEL ENTORNO ========================
def check_environment():
    """Verifica el entorno Python"""
    print("\n" + "="*70)
    print("📋 1. VERIFICACIÓN DEL ENTORNO")
    print("="*70)
    
    checks = {
        "Python Version": f"{sys.version.split()[0]}",
        "Platform": sys.platform,
        "Architecture": f"{sys.maxsize.bit_length() + 1} bits",
        "Working Directory": os.getcwd(),
        "Script Location": os.path.abspath(__file__)
    }
    
    for key, value in checks.items():
        print(f"  ✓ {key}: {value}")
        AUDIT_REPORT["system_checks"][key] = value
    
    return True

# ======================== 2. VERIFICACIÓN DE DEPENDENCIAS ========================
def check_dependencies():
    """Verifica todas las dependencias necesarias"""
    print("\n" + "="*70)
    print("📦 2. VERIFICACIÓN DE DEPENDENCIAS")
    print("="*70)
    
    dependencies = {
        "pandas": False,
        "numpy": False,
        "requests": False,
        "sklearn": False,
        "torch": False,
        "PyQt5": False,
        "websocket": False,
        "scipy": False
    }
    
    for dep in dependencies:
        try:
            __import__(dep.replace("sklearn", "sklearn").replace("torch", "torch"))
            dependencies[dep] = True
            print(f"  ✅ {dep}: Instalado")
        except ImportError as e:
            dependencies[dep] = False
            msg = f"  ❌ {dep}: NO instalado - {str(e)}"
            print(msg)
            log_and_report("warning", msg, "dependencies")
    
    AUDIT_REPORT["system_checks"]["dependencies"] = dependencies
    return all(dependencies.values())

# ======================== 3. VERIFICACIÓN DE ARCHIVOS DE CONFIGURACIÓN ========================
def check_configuration_files():
    """Verifica que existan archivos de configuración"""
    print("\n" + "="*70)
    print("⚙️  3. VERIFICACIÓN DE ARCHIVOS DE CONFIGURACIÓN")
    print("="*70)
    
    config_files = {
        "config_v20_optimized.json": "../config_v20_optimized.json",
        "authcreds.json": "../authcreds.json",
        "telegram_creds.json": "../telegram_creds.json"
    }
    
    config_status = {}
    
    for name, path in config_files.items():
        full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
        exists = os.path.exists(full_path)
        
        if exists:
            print(f"  ✅ {name}: Encontrado")
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    config_status[name] = "✅ Válido"
                    print(f"     - JSON válido, {len(str(data))} bytes")
            except json.JSONDecodeError as e:
                config_status[name] = f"❌ JSON Inválido: {str(e)}"
                log_and_report("error", f"{name} JSON inválido: {str(e)}", "config")
        else:
            config_status[name] = "❌ No encontrado"
            msg = f"  ❌ {name}: NO encontrado en {full_path}"
            print(msg)
            log_and_report("error", msg, "config")
    
    AUDIT_REPORT["system_checks"]["config_files"] = config_status
    return all("✅" in v for v in config_status.values())

# ======================== 4. VERIFICACIÓN DE CONECTIVIDAD API ========================
def check_api_connectivity():
    """Verifica conectividad con APIs"""
    print("\n" + "="*70)
    print("🌐 4. VERIFICACIÓN DE CONECTIVIDAD API")
    print("="*70)
    
    try:
        import requests
    except ImportError:
        log_and_report("error", "requests no disponible", "api")
        return False
    
    # Endpoints a probar
    endpoints = {
        "Binance REST (data-api)": "https://data-api.binance.vision/api/v3/ping",
        "Binance REST (api.binance.com)": "https://api.binance.com/api/v3/ping",
        "Binance Futures": "https://fapi.binance.com/fapi/v1/ping",
        "Google DNS": "https://8.8.8.8/ping"
    }
    
    api_status = {}
    
    for name, url in endpoints.items():
        try:
            # Timeout corto para no bloquear
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 404]:
                print(f"  ✅ {name}: Conectado ({response.status_code})")
                api_status[name] = "✅ Conectado"
            else:
                print(f"  ⚠️  {name}: Respuesta {response.status_code}")
                api_status[name] = f"⚠️ Status {response.status_code}"
        except requests.exceptions.Timeout:
            print(f"  ⏱️  {name}: TIMEOUT")
            api_status[name] = "❌ Timeout"
            log_and_report("warning", f"{name}: Timeout", "api")
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ {name}: CONEXIÓN FALLIDA")
            api_status[name] = f"❌ No conectado"
            log_and_report("warning", f"{name}: {str(e)}", "api")
        except Exception as e:
            print(f"  ❌ {name}: ERROR - {str(e)}")
            api_status[name] = f"❌ {str(e)}"
    
    AUDIT_REPORT["api_connectivity"] = api_status
    return any("✅" in v for v in api_status.values())

# ======================== 5. PRUEBA DE OBTENCIÓN DE DATOS ========================
def check_data_retrieval():
    """Prueba obtención de datos de mercado"""
    print("\n" + "="*70)
    print("📊 5. PRUEBA DE OBTENCIÓN DE DATOS")
    print("="*70)
    
    try:
        import requests
        import pandas as pd
    except ImportError as e:
        log_and_report("error", f"Dependencias faltantes: {str(e)}", "data")
        return False
    
    # Símbolos para probar
    test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    data_status = {}
    
    for symbol in test_symbols:
        try:
            print(f"\n  🔍 Probando {symbol}...")
            
            # Intentar obtener datos de 1 minuto (últimas 100 velas)
            url = "https://data-api.binance.vision/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": "1m",
                "limit": 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                msg = f"  ❌ {symbol}: Status {response.status_code}"
                print(msg)
                data_status[symbol] = f"❌ HTTP {response.status_code}"
                log_and_report("error", msg, "data")
                continue
            
            data = response.json()
            
            if not isinstance(data, list) or len(data) == 0:
                msg = f"  ❌ {symbol}: No hay datos en respuesta"
                print(msg)
                data_status[symbol] = "❌ Respuesta vacía"
                log_and_report("error", msg, "data")
                continue
            
            # Crear DataFrame para validar estructura
            df = pd.DataFrame(data)
            
            # Klines debería tener 12 columnas
            if len(df.columns) < 12:
                msg = f"  ❌ {symbol}: DataFrame inválido ({len(df.columns)} columnas)"
                print(msg)
                data_status[symbol] = "❌ Estructura inválida"
                log_and_report("error", msg, "data")
                continue
            
            # Validar que tenga datos suficientes
            last_price = float(df.iloc[-1][4])  # close price
            volume = float(df.iloc[-1][7])
            
            msg = f"  ✅ {symbol}: OK - {len(df)} velas, Precio: ${last_price:.2f}, Vol: {volume:.2f}"
            print(msg)
            data_status[symbol] = f"✅ {len(df)} velas"
            
        except requests.exceptions.Timeout:
            print(f"  ⏱️  {symbol}: TIMEOUT")
            data_status[symbol] = "❌ Timeout"
            log_and_report("warning", f"{symbol}: Timeout en obtención de datos", "data")
        except Exception as e:
            msg = f"  ❌ {symbol}: {str(e)}"
            print(msg)
            data_status[symbol] = f"❌ {type(e).__name__}"
            log_and_report("error", msg, "data")
    
    AUDIT_REPORT["data_retrieval"] = data_status
    return all("✅" in v for v in data_status.values())

# ======================== 6. ANÁLISIS DEL FLUJO DE DATOS ========================
def analyze_data_flow():
    """Analiza el flujo de datos en el sistema"""
    print("\n" + "="*70)
    print("🔄 6. ANÁLISIS DEL FLUJO DE DATOS")
    print("="*70)
    
    flow_analysis = {
        "WebSocket Connection": "❓ No probado",
        "Data Cache": "❓ No probado",
        "Technical Analysis": "❓ No probado",
        "Signal Generation": "❓ No probado",
        "Order Execution": "❓ No probado"
    }
    
    # Verificar si los módulos se pueden importar
    try:
        # Intentar importar módulos principales
        print("\n  📦 Importando módulos del bot...")
        
        # Cargar configuración
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config_v20_optimized.json"))
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"  ✅ Configuración cargada")
                flow_analysis["Configuration"] = "✅ Cargada"
        else:
            print(f"  ❌ Configuración no encontrada")
            flow_analysis["Configuration"] = "❌ No encontrada"
        
        # Verificar módulos de análisis
        try:
            import pandas as pd
            import numpy as np
            print(f"  ✅ Pandas y NumPy disponibles")
            flow_analysis["Analysis Libraries"] = "✅ Disponibles"
        except ImportError:
            print(f"  ❌ Pandas/NumPy no disponible")
            flow_analysis["Analysis Libraries"] = "❌ No disponibles"
        
    except Exception as e:
        msg = f"  ❌ Error en importación de módulos: {str(e)}"
        print(msg)
        log_and_report("error", msg, "data_flow")
        flow_analysis["Module Import"] = f"❌ {str(e)}"
    
    AUDIT_REPORT["data_flow"] = flow_analysis
    return True

# ======================== 7. ANÁLISIS DE RENDIMIENTO ========================
def analyze_performance():
    """Analiza el rendimiento del sistema"""
    print("\n" + "="*70)
    print("⚡ 7. ANÁLISIS DE RENDIMIENTO")
    print("="*70)
    
    performance = {
        "CPU Usage": "❓ No medido",
        "Memory Usage": "❓ No medido",
        "Disk Space": "❓ No medido",
        "Network Latency": "❓ No medido"
    }
    
    try:
        import psutil
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        performance["CPU Usage"] = f"{cpu_percent}%"
        print(f"  📊 CPU: {cpu_percent}%")
        
        # Memoria
        mem = psutil.virtual_memory()
        performance["Memory Usage"] = f"{mem.percent}% ({mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB)"
        print(f"  📊 Memoria: {mem.percent}% ({mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB)")
        
        # Disco
        disk = psutil.disk_usage('/')
        performance["Disk Space"] = f"{disk.percent}% ({disk.free / (1024**3):.1f}GB libre)"
        print(f"  📊 Disco: {disk.percent}% ({disk.free / (1024**3):.1f}GB libre)")
        
    except ImportError:
        print(f"  ⚠️  psutil no instalado - información de sistema limitada")
    except Exception as e:
        print(f"  ❌ Error midiendo rendimiento: {str(e)}")
    
    AUDIT_REPORT["performance"] = performance
    return True

# ======================== 8. GENERACIÓN DE RECOMENDACIONES ========================
def generate_recommendations():
    """Genera recomendaciones basadas en auditoría"""
    print("\n" + "="*70)
    print("💡 8. RECOMENDACIONES")
    print("="*70)
    
    recommendations = []
    
    # Verificar errores y warnings
    if AUDIT_REPORT["errors"]:
        recommendations.append("🔴 CRÍTICO: Hay errores que necesitan solución inmediata")
        for error in AUDIT_REPORT["errors"][:3]:
            recommendations.append(f"   - {error}")
    
    if not AUDIT_REPORT["api_connectivity"]:
        recommendations.append("🔴 Verifica tu conexión a Internet")
        recommendations.append("🔴 Los endpoints de Binance podrían estar bloqueados/no disponibles")
    
    if AUDIT_REPORT["warnings"]:
        recommendations.append("🟡 ADVERTENCIAS: Revisar")
        for warning in AUDIT_REPORT["warnings"][:3]:
            recommendations.append(f"   - {warning}")
    
    if "Instalado" not in str(AUDIT_REPORT["system_checks"].get("dependencies", {})):
        recommendations.append("🟡 Instalar dependencias faltantes: pip install -r requirements.txt")
    
    if not os.path.exists("../config_v20_optimized.json"):
        recommendations.append("🟡 Crear archivo de configuración: config_v20_optimized.json")
    
    if not os.path.exists("../authcreds.json"):
        recommendations.append("🟡 Crear archivo con credenciales: authcreds.json")
        recommendations.append("   Formato: {\"api_key\": \"...\", \"api_secret\": \"...\"}")
    
    for rec in recommendations:
        print(f"\n{rec}")
        AUDIT_REPORT["recommendations"].append(rec)

# ======================== 9. RESUMEN EJECUTIVO ========================
def print_summary():
    """Imprime resumen de auditoría"""
    print("\n" + "="*70)
    print("📋 RESUMEN EJECUTIVO")
    print("="*70)
    
    total_errors = len(AUDIT_REPORT["errors"])
    total_warnings = len(AUDIT_REPORT["warnings"])
    
    print(f"\n  ✅ Errores: {total_errors}")
    print(f"  ⚠️  Warnings: {total_warnings}")
    
    if total_errors == 0:
        print("\n  ✅ SISTEMA LISTO - No hay errores críticos")
    else:
        print(f"\n  ❌ {total_errors} ERROR(ES) ENCONTRADO(S) - Ver detalles arriba")
    
    return total_errors == 0

# ======================== FUNCIÓN PRINCIPAL ========================
def main():
    """Ejecuta auditoría completa"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║  🔍 AUDITORÍA FORENSE COMPLETA - Crypto Bot Pro v34.0.1.2".ljust(68) + "║")
    print("║  Análisis profundo de conectividad, datos y rendimiento".ljust(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    # Ejecutar todas las verificaciones
    check_environment()
    check_dependencies()
    check_configuration_files()
    api_ok = check_api_connectivity()
    data_ok = check_data_retrieval()
    analyze_data_flow()
    analyze_performance()
    generate_recommendations()
    system_ok = print_summary()
    
    # Guardar reporte JSON
    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../CryptoBotPro_Data/audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"))
    try:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(AUDIT_REPORT, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Reporte guardado en: {report_path}")
    except Exception as e:
        print(f"❌ Error guardando reporte: {str(e)}")
    
    print("\n" + "="*70)
    print("✅ AUDITORÍA COMPLETADA")
    print("="*70 + "\n")
    
    return 0 if (system_ok and api_ok and data_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
