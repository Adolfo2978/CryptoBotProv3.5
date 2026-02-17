#!/usr/bin/env python3
"""
🔍 TRACE DE CONFIGURACIÓN - Sigue paso a paso cómo se carga la config
"""

import json
import sys
from pathlib import Path

# Setup
base_dir = Path(__file__).parent.parent
sys.path.insert(0, str(base_dir))

print("="*80)
print("🔍 TRACE DE CARGA DE CONFIGURACIÓN")
print("="*80)

# 1. Cargar JSON directamente
print("\n1️⃣  VERIFICANDO JSON")
print("-"*80)

config_path = base_dir / "config_v20_optimized.json"
print(f"Ruta: {config_path}")

with open(config_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

print(f"\nArchivo JSON contiene:")
print(f"  - PERPETUALS_SYMBOLS: {len(json_data.get('PERPETUALS_SYMBOLS', []))} símbolos")
print(f"  - SPOT_SYMBOLS: {len(json_data.get('SPOT_SYMBOLS', []))} símbolos")
print(f"  - perpetuals_symbols: {len(json_data.get('perpetuals_symbols', []))} símbolos")
print(f"  - spot_symbols: {len(json_data.get('spot_symbols', []))} símbolos")

# Mostrar primeros 5
if 'PERPETUALS_SYMBOLS' in json_data and json_data['PERPETUALS_SYMBOLS']:
    print(f"\n  Primeros 5 símbolos en PERPETUALS_SYMBOLS:")
    for sym in json_data['PERPETUALS_SYMBOLS'][:5]:
        print(f"    - {sym}")

# 2. Simular carga de config
print("\n2️⃣  SIMULANDO CARGA DE CONFIGURACIÓN")
print("-"*80)

class TestConfig:
    def __init__(self):
        # Defaults
        self.PERPETUALS_SYMBOLS = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT",
            "DOTUSDT", "LINKUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT", "XLMUSDT", "ETCUSDT", "FILUSDT",
            "ATOMUSDT", "ICPUSDT", "NEARUSDT", "AAVEUSDT", "APTUSDT", "ARBUSDT", "OPUSDT", "SUIUSDT",
            "PEPEUSDT", "SHIBUSDT", "FLOKIUSDT", "BONKUSDT", "WIFUSDT", "FETUSDT", "INJUSDT", "SEIUSDT",
            "TRXUSDT", "HBARUSDT", "SANDUSDT", "MANAUSDT", "AXSUSDT", "GALAUSDT", "APEUSDT", "CRVUSDT",
            "DYDXUSDT", "GMXUSDT", "STXUSDT", "IMXUSDT", "RUNEUSDT", "EGLDUSDT", "FLOWUSDT", "MINAUSDT",
            "KAVAUSDT", "IOTAUSDT"
        ]
        self.SPOT_SYMBOLS = self.PERPETUALS_SYMBOLS.copy()
        self.MARKET_TYPE = "PERPETUALS"
        self.TRADING_SYMBOLS = self.PERPETUALS_SYMBOLS.copy()
        print("  ✓ Inicializados defaults")
        print(f"    - PERPETUALS_SYMBOLS: {len(self.PERPETUALS_SYMBOLS)}")
        print(f"    - TRADING_SYMBOLS: {len(self.TRADING_SYMBOLS)}")

cfg = TestConfig()

print("\n  Paso 1: Después de __init__()")
print(f"    PERPETUALS_SYMBOLS = {len(cfg.PERPETUALS_SYMBOLS)}")
print(f"    TRADING_SYMBOLS = {len(cfg.TRADING_SYMBOLS)}")

# Simular load_config
print("\n  Paso 2: Simulando load_config()")

data = json_data

# Cargar desde JSON
if 'perpetuals_symbols' in data:
    print(f"    Encontrado 'perpetuals_symbols' en JSON: {len(data['perpetuals_symbols'])}")
    cfg.PERPETUALS_SYMBOLS = data['perpetuals_symbols']
    print(f"    ✓ Asignado PERPETUALS_SYMBOLS = {len(cfg.PERPETUALS_SYMBOLS)}")
else:
    print(f"    ❌ 'perpetuals_symbols' NO encontrado en JSON")

if 'PERPETUALS_SYMBOLS' in data:
    print(f"    Encontrado 'PERPETUALS_SYMBOLS' (mayúscula) en JSON: {len(data['PERPETUALS_SYMBOLS'])}")
    cfg.PERPETUALS_SYMBOLS = data['PERPETUALS_SYMBOLS']
    print(f"    ✓ Asignado PERPETUALS_SYMBOLS = {len(cfg.PERPETUALS_SYMBOLS)}")
else:
    print(f"    ❌ 'PERPETUALS_SYMBOLS' (mayúscula) NO encontrado en JSON")

if 'spot_symbols' in data:
    print(f"    Encontrado 'spot_symbols' en JSON: {len(data['spot_symbols'])}")
    cfg.SPOT_SYMBOLS = data['spot_symbols']
else:
    print(f"    ❌ 'spot_symbols' NO encontrado en JSON")

# Simular update_symbols_for_market_type()
print("\n  Paso 3: Simulando update_symbols_for_market_type()")
if cfg.MARKET_TYPE == "PERPETUALS":
    cfg.TRADING_SYMBOLS = cfg.PERPETUALS_SYMBOLS.copy()
    print(f"    ✓ TRADING_SYMBOLS = PERPETUALS_SYMBOLS.copy()")
    print(f"    TRADING_SYMBOLS = {len(cfg.TRADING_SYMBOLS)}")
else:
    cfg.TRADING_SYMBOLS = cfg.SPOT_SYMBOLS.copy()
    print(f"    ✓ TRADING_SYMBOLS = SPOT_SYMBOLS.copy()")
    print(f"    TRADING_SYMBOLS = {len(cfg.TRADING_SYMBOLS)}")

# 3. Resultado final
print("\n3️⃣  RESULTADO FINAL")
print("-"*80)

print(f"\nEstado después de load_config():")
print(f"  MARKET_TYPE: {cfg.MARKET_TYPE}")
print(f"  PERPETUALS_SYMBOLS: {len(cfg.PERPETUALS_SYMBOLS)}")
print(f"  SPOT_SYMBOLS: {len(cfg.SPOT_SYMBOLS)}")
print(f"  TRADING_SYMBOLS: {len(cfg.TRADING_SYMBOLS)}")

if cfg.TRADING_SYMBOLS:
    print(f"\n  ✅ PRIMEROS 5 SÍMBOLOS A ANALIZAR:")
    for sym in cfg.TRADING_SYMBOLS[:5]:
        print(f"     - {sym}")
else:
    print(f"\n  ❌ TRADING_SYMBOLS VACÍO - PROBLEMA ENCONTRADO")

# 4. Investigar
print("\n4️⃣  INVESTIGACIÓN")
print("-"*80)

print("\nClaves disponibles en JSON:")
for key in sorted(json_data.keys()):
    if isinstance(json_data[key], list):
        print(f"  {key}: {len(json_data[key])} items")
    else:
        val = json_data[key]
        if isinstance(val, str) and len(val) > 50:
            val = val[:50] + "..."
        print(f"  {key}: {val}")

print("\n" + "="*80)
print("✅ ANÁLISIS COMPLETADO")
print("="*80 + "\n")
