#!/usr/bin/env python3
"""
🔧 DEBUG - Diagnostic de obtención de datos
"""
import json
import sys
import os
from pathlib import Path

# Setup paths
base_dir = Path(__file__).parent.parent
sys.path.insert(0, str(base_dir))

print("="*80)
print("🔧 DIAGNÓSTICO DE OBTENCIÓN DE DATOS - Crypto Bot Pro")
print("="*80)

# 1. Verificar archivos de configuración
print("\n1️⃣  VERIFICACIÓN DE ARCHIVOS DE CONFIGURACIÓN")
print("-" * 80)

config_files = {
    "config_v20_optimized.json": base_dir / "config_v20_optimized.json",
    "authcreds.json": base_dir / "authcreds.json",
    "telegram_creds.json": base_dir / "telegram_creds.json"
}

config_data = {}
for name, path in config_files.items():
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                config_data[name] = data
                # No imprimir credenciales sensibles
                if "api_key" in data:
                    data_preview = {k: (v[:10] + "..." if isinstance(v, str) and len(v) > 10 else v) for k, v in data.items()}
                else:
                    data_preview = {k: v for k, v in list(data.items())[:5]}
                print(f"✅ {name}: ENCONTRADO")
                print(f"   Contenido: {data_preview}")
        except json.JSONDecodeError as e:
            print(f"❌ {name}: JSON INVÁLIDO - {e}")
            print(f"   Ruta: {path}")
    else:
        print(f"❌ {name}: NO ENCONTRADO")
        print(f"   Ruta esperada: {path}")

# 2. Verificar dependencias críticas
print("\n2️⃣  VERIFICACIÓN DE DEPENDENCIAS CRÍTICAS")
print("-" * 80)

deps = ["pandas", "numpy", "requests", "sklearn"]
missing = []

for dep in deps:
    try:
        __import__(dep if dep != "sklearn" else "sklearn")
        print(f"✅ {dep}: Instalado")
    except ImportError:
        print(f"❌ {dep}: NO instalado")
        missing.append(dep)

if missing:
    print(f"\n⚠️  INSTALA: pip install {' '.join(missing)}")

# 3. Prueba conectividad API
print("\n3️⃣  PRUEBA DE CONECTIVIDAD API BINANCE")
print("-" * 80)

try:
    import requests
    
    # Probar endpoint básico
    print("Probando: https://api.binance.com/api/v3/ping")
    response = requests.get("https://api.binance.com/api/v3/ping", timeout=5)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ CONEXIÓN API EXITOSA")
    else:
        print(f"⚠️  Status inesperado: {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

# 4. Prueba obtención de datos
print("\n4️⃣  PRUEBA DE OBTENCIÓN DE DATOS (KLINES)")
print("-" * 80)

try:
    import requests
    import pandas as pd
    
    symbol = "BTCUSDT"
    print(f"Obteniendo datos para {symbol}...")
    
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": "1m", "limit": 10}
    
    response = requests.get(url, params=params, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Datos obtenidos: {len(data)} velas")
        
        # Analizar estructura
        if len(data) > 0:
            first_candle = data[0]
            print(f"   Estructura: {len(first_candle)} campos")
            print(f"   Primer candle: {first_candle[:4]}")
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        print(f"   DataFrame: {df.shape[0]} filas × {df.shape[1]} columnas")
        
        # Mostrar última vela
        print(f"\n   Última vela:")
        print(f"   - Close Price: {float(data[-1][4])}")
        print(f"   - Volume: {float(data[-1][7])}")
    else:
        print(f"❌ Error HTTP: {response.status_code}")
        print(f"   Respuesta: {response.text[:200]}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# 5. Verificar estructura de directorio
print("\n5️⃣  VERIFICACIÓN DE ESTRUCTURA DE DIRECTORIOS")
print("-" * 80)

dirs_to_check = {
    "CryptoBotPro_Data": base_dir / "CryptoBotPro_Data",
    "logs": base_dir / "CryptoBotPro_Data" / "logs",
    "models": base_dir / "CryptoBotPro_Data" / "models",
    "cache": base_dir / "CryptoBotPro_Data" / "cache",
    "Control": base_dir / "Control"
}

for name, path in dirs_to_check.items():
    if path.exists():
        files = list(path.glob("*"))
        print(f"✅ {name}: OK ({len(files)} items)")
    else:
        print(f"❌ {name}: NO EXISTE - {path}")

# 6. Cargar configuración principal
print("\n6️⃣  ANÁLISIS DE CONFIGURACIÓN PRINCIPAL")
print("-" * 80)

if "config_v20_optimized.json" in config_data:
    cfg = config_data["config_v20_optimized.json"]
    
    # Parámetros críticos
    critical_params = {
        "USE_TESTNET": cfg.get("USE_TESTNET"),
        "TRADING_SYMBOLS": len(cfg.get("TRADING_SYMBOLS", [])),
        "PRIMARY_TIMEFRAME": cfg.get("PRIMARY_TIMEFRAME"),
        "ENTRY_TIMEFRAME": cfg.get("ENTRY_TIMEFRAME"),
        "MIN_NN_DATA_REQUIRED": cfg.get("MIN_NN_DATA_REQUIRED"),
        "USE_WEBSOCKET": cfg.get("USE_WEBSOCKET"),
        "websocket_enabled": cfg.get("websocket_enabled"),
    }
    
    print("\nParámetros críticos:")
    for key, value in critical_params.items():
        status = "✅" if value else "❌" if key in ["USE_TESTNET", "websocket_enabled"] else "✅"
        print(f"  {status} {key}: {value}")

print("\n" + "="*80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("="*80 + "\n")

# Recomendaciones finales
print("💡 RECOMENDACIONES:")
print("-" * 80)
print("1. Si 'api_key' está faltante en authcreds.json → Agrégalo")
print("2. Si 'websocket_enabled' es False → El bot usa API REST fallback")
print("3. Si MIN_NN_DATA_REQUIRED > 100 → Puede tardar más en obtener datos")
print("4. Si hay errores de conexión → Verifica tu VPN/Firewall")
print("5. Si los datos no se obtienen → Prueba con este endpoint:")
print("   https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100")
print("")
