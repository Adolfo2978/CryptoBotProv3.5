#!/usr/bin/env python3
"""
🔍 REPRODUCIR EXACTAMENTE LA INICIALIZACIÓN DEL BOT
Simular lo que hace el bot al iniciar
"""

import json
import sys
import os
from pathlib import Path

base_dir = Path(__file__).parent.parent
sys.path.insert(0, str(base_dir))

print("="*80)
print("🔍 REPRODUCIR INICIALIZACIÓN DEL BOT")
print("="*80)

# Simular lo que hace el bot
print("\n1️⃣  INICIALIZANDO CONFIG COMO LO HACE EL BOT")
print("-"*80)

# Importar la clase de config del bot (sin iniciar GUI)
print("Importando AdvancedTradingConfig...")
try:
    # Cargar manualmente la clase
    config_code = open(base_dir / "Crypto-Pro-Python v34.0.1.2.py", 'r', encoding='utf-8').read()
    
    # Extraer solo lo que necesitamos
    import importlib.util
    
    # En su lugar, vamos a simular
    class AdvancedTradingConfig:
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
            
            self.PRIMARY_TIMEFRAME = "30m"
            self.ENTRY_TIMEFRAME = "15m"
            self.MIN_NN_DATA_REQUIRED = 100
            
        def load_config(self):
            """Cargar configuración COMPLETA desde archivo JSON"""
            try:
                config_path = base_dir / 'config_v20_optimized.json'
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Ver qué se carga
                    print(f"\n  📖 Leyendo JSON:")
                    print(f"     - PERPETUALS_SYMBOLS en JSON: {'Sí' if 'PERPETUALS_SYMBOLS' in data else 'No'}")
                    if 'PERPETUALS_SYMBOLS' in data:
                        print(f"       Cantidad: {len(data['PERPETUALS_SYMBOLS'])}")
                    
                    if 'perpetuals_symbols' in data:
                        self.PERPETUALS_SYMBOLS = data['perpetuals_symbols']
                        print(f"     - Asignado desde 'perpetuals_symbols': {len(self.PERPETUALS_SYMBOLS)}")
                    elif 'PERPETUALS_SYMBOLS' in data:
                        self.PERPETUALS_SYMBOLS = data['PERPETUALS_SYMBOLS']
                        print(f"     - Asignado desde 'PERPETUALS_SYMBOLS': {len(self.PERPETUALS_SYMBOLS)}")
                    
                    if 'spot_symbols' in data:
                        self.SPOT_SYMBOLS = data['spot_symbols']
                    elif 'SPOT_SYMBOLS' in data:
                        self.SPOT_SYMBOLS = data['SPOT_SYMBOLS']
                    
                    # Actualizar símbolos según tipo de mercado
                    self.update_symbols_for_market_type()
                    print(f"     - update_symbols_for_market_type() ejecutado")
                    print(f"     - TRADING_SYMBOLS: {len(self.TRADING_SYMBOLS)}")
                else:
                    print(f"\n  ❌ Archivo de config no encontrado: {config_path}")
            except Exception as e:
                print(f"\n  ❌ Error: {e}")
        
        def update_symbols_for_market_type(self):
            """Actualizar lista de símbolos según tipo de mercado"""
            if self.MARKET_TYPE == "PERPETUALS":
                self.TRADING_SYMBOLS = self.PERPETUALS_SYMBOLS.copy()
            else:
                self.TRADING_SYMBOLS = self.SPOT_SYMBOLS.copy()
            print(f"     Símbolos para {self.MARKET_TYPE}: {len(self.TRADING_SYMBOLS)}")
    
    print("✅ Clase creada\n")
    
    # Crear instancia
    config = AdvancedTradingConfig()
    print(f"✓ Config inicializada")
    print(f"  TRADING_SYMBOLS INICIAL: {len(config.TRADING_SYMBOLS)}")
    
    # Cargar desde JSON
    print(f"\n2️⃣  CARGANDO CONFIGURACIÓN DESDE JSON")
    print("-"*80)
    config.load_config()
    
    # Verificar resultado
    print(f"\n3️⃣  VERIFICACIÓN FINAL")
    print("-"*80)
    print(f"MARKET_TYPE: {config.MARKET_TYPE}")
    print(f"PERPETUALS_SYMBOLS: {len(config.PERPETUALS_SYMBOLS)}")
    print(f"TRADING_SYMBOLS: {len(config.TRADING_SYMBOLS)}")
    
    if config.TRADING_SYMBOLS:
        print(f"\n✅ PRIMEROS 10 SÍMBOLOS:")
        for sym in config.TRADING_SYMBOLS[:10]:
            print(f"   - {sym}")
    else:
        print(f"\n❌ TRADING_SYMBOLS VACÍO - PROBLEMA ENCONTRADO")
    
    # 4. Investigar SymbolScanner
    print(f"\n4️⃣  VERIFICANDO SYMBOL SCANNER")
    print("-"*80)
    print(f"El bot pasaría a SymbolScanner:")
    print(f"  symbols = {len(config.TRADING_SYMBOLS)} para analizar")
    print(f"  Loop: for symbol in symbols:")
    print(f"           bot.analyze_and_process_symbol(symbol)")
    
    if not config.TRADING_SYMBOLS:
        print(f"\n❌ SIN SÍMBOLOS - El loop NO se ejecutará nunca")
    else:
        print(f"\n✅ {len(config.TRADING_SYMBOLS)} símbolos para procesar")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("✅ ANÁLISIS COMPLETADO")
print("="*80 + "\n")
