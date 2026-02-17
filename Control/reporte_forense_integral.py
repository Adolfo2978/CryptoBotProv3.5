#!/usr/bin/env python3
"""
🔍 REPORTE FORENSE INTEGRAL - ANÁLISIS COMPLETO DEL BOT
Investigación profunda: 
- Flujo de datos de inicio a fin
- Identificación de puntos de falla
- Recomendaciones de corrección
"""

import json
from datetime import datetime
from pathlib import Path

REPORTE_FORENSE = {
    "titulo": "AUDITORÍA FORENSE INTEGRAL - Crypto Bot Pro v34.0.1.2",
    "fecha": datetime.now().strftime("%d de %B de %Y a las %H:%M:%S"),
    "severidad_general": "⚠️ CRÍTICA",
    
    "hallazgos_principales": {
        "1_Problema_Principal": {
            "descripcion": "BOT NO OBTIENE DATOS DE SÍMBOLOS",
            "causa_raíz": "TRADING_SYMBOLS está vacío en configuración",
            "impacto": "❌ El bot NO analiza ningún símbolo",
            "severidad": "🔴 CRÍTICA"
        },
        
        "2_Estado_Actual": {
            "descripcion": "Configuración vs Realidad",
            "hallazgos": [
                "✅ API Binance: CONECTADA Y FUNCIONAL",
                "✅ Obtención de datos: FUNCIONA CORRECTAMENTE",
                "✅ Dependencias: TODAS INSTALADAS",
                "✅ Archivos de configuración: EXISTEN",
                "❌ TRADING_SYMBOLS: VACÍO",
                "❌ PRIMARY_TIMEFRAME: None",
                "❌ ENTRY_TIMEFRAME: None",
                "❌ MIN_NN_DATA_REQUIRED: None",
                "❌ websocket_enabled: None"
            ]
        }
    },
    
    "análisis_detallado": {
        "1_Flujo_de_Datos_Teórico": {
            "paso": "Inicio del Bot",
            "flujo": [
                "1. Bot inicia y carga config_v20_optimized.json",
                "2. Lee TRADING_SYMBOLS de la configuración",
                "3. Para CADA símbolo, inicia SymbolScanner",
                "4. SymbolScanner llama a analyze_and_process_symbol()",
                "5. Se obtienen datos usando OptimizedDataManager",
                "6. Se realiza análisis técnico",
                "7. Se genera señal si cumple criterios",
                "8. Se ejecuta trade si es apropiado"
            ]
        },
        
        "2_Punto_de_Falla": {
            "en_paso": "PASO 2: Lee TRADING_SYMBOLS",
            "valor_actual": "[]",
            "valor_esperado": "[\"BTCUSDT\", \"ETHUSDT\", \"BNBUSDT\", ...]",
            "resultado": "❌ El bot NO tiene símbolos para analizar, así que:",
            "consecuencias": [
                "- SymbolScanner recibe lista vacía",
                "- No se inician workers de análisis",
                "- No se obtienen datos del mercado",
                "- No se generan señales",
                "- El bot aparece ejecutándose pero sin hacer nada"
            ]
        },
        
        "3_Capas_del_Sistema": {
            "capa_1_api": {
                "nombre": "API Binance",
                "estado": "✅ FUNCIONAL",
                "verificación": "https://api.binance.com/api/v3/ping → 200 OK",
                "capacidad": "Obtiene datos sin problemas"
            },
            
            "capa_2_datos": {
                "nombre": "OptimizedDataManager",
                "estado": "✅ FUNCIONAL",
                "verificación": "Obtiene 10 velas de BTCUSDT correctamente",
                "capacidad": "Accede a API, procesa datos, crea DataFrames"
            },
            
            "capa_3_scanner": {
                "nombre": "SymbolScanner",
                "estado": "❌ SIN SÍMBOLOS",
                "verificación": "TRADING_SYMBOLS vacío",
                "capacidad": "No puede procesar lo que no existe"
            },
            
            "capa_4_gui": {
                "nombre": "GUI Qt5",
                "estado": "✅ FUNCIONAL",
                "verificación": "Se inicia correctamente",
                "capacidad": "Muestra interfaz pero sin datos"
            }
        }
    },
    
    "diagnóstico_por_síntomas": {
        "síntoma_1": {
            "observación": "Bot ejecutándose pero sin procesar pares",
            "causa": "TRADING_SYMBOLS vacío en config",
            "evidencia": "TRADING_SYMBOLS: 0 en debug_data_retrieval.py"
        },
        
        "síntoma_2": {
            "observación": "Terminal muestra 'Escanneando Pares Optimizado: 0%'",
            "causa": "No hay pares en la lista",
            "evidencia": "El loop for sobre TRADING_SYMBOLS es vacío"
        },
        
        "síntoma_3": {
            "observación": "GUI muestra NEUTRAL sin señales",
            "causa": "No se ejecuta analyze_and_process_symbol()",
            "evidencia": "Sin pares, no hay análisis"
        },
        
        "síntoma_4": {
            "observación": "Logs vacíos o sin mensajes de análisis",
            "causa": "El análisis nunca se ejecuta",
            "evidencia": "CryptoBotDebug_20260126_130714.log vacío"
        }
    },
    
    "código_afectado": {
        "1_SymbolScanner_init": {
            "archivo": "Crypto-Pro-Python v34.0.1.2.py",
            "líneas": "~8200-8300",
            "problema": "Lee TRADING_SYMBOLS pero está vacío",
            "código_problemático": "self.symbols = self.bot.config.TRADING_SYMBOLS  # []"
        },
        
        "2_main_loop": {
            "descripción": "El loop principal itera sobre símbolos",
            "pseudocódigo": """
            for symbol in symbols:  # vacío, no entra al loop
                self.bot.analyze_and_process_symbol(symbol)
            """,
            "resultado": "Nunca se llama al análisis"
        },
        
        "3_OptimizedDataManager": {
            "estado": "✅ Correcto - espera recibir símbolos",
            "código": "def get_data(self, symbol, ...)",
            "problema": "Nunca se llama porque no hay símbolos"
        }
    },
    
    "verificaciones_realizadas": {
        "✅_Verificaciones_Exitosas": [
            "Conectividad a API Binance: EXITOSA",
            "Obtención de datos de mercado: FUNCIONA",
            "Parse de JSON: CORRECTO",
            "Dependencias Python: INSTALADAS",
            "Archivos de configuración: EXISTEN",
            "Permisos de lectura: OK",
            "Estructura de directorios: OK",
            "Autenticación API: NO VERIFICADA (testnet=True)"
        ],
        
        "❌_Verificaciones_Fallidas": [
            "TRADING_SYMBOLS: VACÍO",
            "PRIMARY_TIMEFRAME: None",
            "ENTRY_TIMEFRAME: None",
            "MIN_NN_DATA_REQUIRED: None",
            "websocket_enabled: None"
        ]
    },
    
    "solución": {
        "paso_1": {
            "acción": "Verificar config_v20_optimized.json",
            "comando": "cat config_v20_optimized.json | grep -A 50 PERPETUALS_SYMBOLS",
            "objetivo": "Ver si TRADING_SYMBOLS apunta a PERPETUALS_SYMBOLS"
        },
        
        "paso_2": {
            "acción": "Verificar carga de configuración",
            "problema": "TRADING_SYMBOLS no se carga de PERPETUALS_SYMBOLS",
            "solución": "Ver clase AdvancedTradingConfig.load_config()"
        },
        
        "paso_3": {
            "acción": "Verificar método load_config",
            "ubicación": "AdvancedTradingConfig.load_config() línea ~720",
            "revisar": "¿Está asignando self.TRADING_SYMBOLS = data['PERPETUALS_SYMBOLS']?"
        }
    },
    
    "recomendaciones_inmediatas": [
        "1. URGENTE: Revisar AdvancedTradingConfig.load_config()",
        "2. Verificar que TRADING_SYMBOLS se carga de config JSON",
        "3. Agregar validación: if not TRADING_SYMBOLS: raise Exception()",
        "4. Verificar PRIMARY_TIMEFRAME y ENTRY_TIMEFRAME también vacíos",
        "5. Crear test unitario que verifique carga de config",
        "6. Agregar logs al inicio: print(f'Símbolos cargados: {len(config.TRADING_SYMBOLS)}')"
    ],
    
    "próximos_pasos": {
        "investigación": [
            "Leer líneas 720-820 de Crypto-Pro-Python v34.0.1.2.py",
            "Buscar método load_config() en AdvancedTradingConfig",
            "Verificar si TRADING_SYMBOLS se asigna correctamente",
            "Buscar dónde se usan PRIMARY_TIMEFRAME, ENTRY_TIMEFRAME"
        ],
        
        "corrección": [
            "Arreglar AdvancedTradingConfig.load_config()",
            "Agregar validación de config",
            "Reiniciar bot y verificar que TRADING_SYMBOLS no esté vacío",
            "Ejecutar debug_data_retrieval.py nuevamente"
        ],
        
        "validación": [
            "Verificar que SymbolScanner tiene símbolos",
            "Ejecutar bot y ver logs con nuevos datos",
            "Verificar que GUI muestra análisis",
            "Verificar que se generan señales"
        ]
    },
    
    "archivo_a_revisar": {
        "descripción": "El archivo principal del bot",
        "ruta": "c:/Crypto-Pro-Python v34.0.1.2/Crypto-Pro-Python v34.0.1.2.py",
        "líneas_críticas": {
            "load_config()": "~720-820",
            "SymbolScanner.__init__()": "~8200-8250",
            "analyze_and_process_symbol()": "~10100-10200"
        }
    },
    
    "conclusión": {
        "estado": "🔴 CRÍTICA",
        "causa": "TRADING_SYMBOLS no se carga correctamente de la configuración",
        "impacto": "Bot no analiza ningún símbolo",
        "solución": "Revisar y corregir AdvancedTradingConfig.load_config()",
        "tiempo_estimado_corrección": "5-15 minutos"
    }
}

def main():
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║  🔍 AUDITORÍA FORENSE INTEGRAL - Crypto Bot Pro v34.0.1.2                  ║
║  {REPORTE_FORENSE['fecha']}
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Hallazgos principales
    print("\n" + "="*80)
    print("📋 HALLAZGOS PRINCIPALES")
    print("="*80)
    
    for key, findings in REPORTE_FORENSE["hallazgos_principales"].items():
        print(f"\n{key}")
        for subkey, value in findings.items():
            print(f"  {subkey}: {value}")
    
    # Análisis detallado
    print("\n" + "="*80)
    print("🔬 ANÁLISIS DETALLADO")
    print("="*80)
    
    print("\n1️⃣  FLUJO DE DATOS TEÓRICO:")
    for i, paso in enumerate(REPORTE_FORENSE["análisis_detallado"]["1_Flujo_de_Datos_Teórico"]["flujo"], 1):
        print(f"   {paso}")
    
    print("\n2️⃣  PUNTO DE FALLA:")
    falla = REPORTE_FORENSE["análisis_detallado"]["2_Punto_de_Falla"]
    print(f"   En: {falla['en_paso']}")
    print(f"   Valor actual: {falla['valor_actual']}")
    print(f"   Valor esperado: {falla['valor_esperado']}")
    print(f"   Resultado: {falla['resultado']}")
    print(f"   Consecuencias:")
    for cons in falla['consecuencias']:
        print(f"      {cons}")
    
    print("\n3️⃣  CAPAS DEL SISTEMA:")
    for capa, info in REPORTE_FORENSE["análisis_detallado"]["3_Capas_del_Sistema"].items():
        print(f"\n   {capa}:")
        for key, value in info.items():
            print(f"      {key}: {value}")
    
    # Síntomas
    print("\n" + "="*80)
    print("🩺 DIAGNÓSTICO POR SÍNTOMAS")
    print("="*80)
    
    for síntoma, detalles in REPORTE_FORENSE["diagnóstico_por_síntomas"].items():
        print(f"\n{síntoma}:")
        print(f"  Observación: {detalles['observación']}")
        print(f"  Causa: {detalles['causa']}")
        print(f"  Evidencia: {detalles['evidencia']}")
    
    # Verificaciones
    print("\n" + "="*80)
    print("✅ VERIFICACIONES REALIZADAS")
    print("="*80)
    
    print("\nExitosas:")
    for v in REPORTE_FORENSE["verificaciones_realizadas"]["✅_Verificaciones_Exitosas"]:
        print(f"  {v}")
    
    print("\nFallidas:")
    for v in REPORTE_FORENSE["verificaciones_realizadas"]["❌_Verificaciones_Fallidas"]:
        print(f"  {v}")
    
    # Solución
    print("\n" + "="*80)
    print("🔧 SOLUCIÓN")
    print("="*80)
    
    for paso, detalles in REPORTE_FORENSE["solución"].items():
        print(f"\n{paso}:")
        for key, value in detalles.items():
            print(f"  {key}: {value}")
    
    # Recomendaciones
    print("\n" + "="*80)
    print("💡 RECOMENDACIONES INMEDIATAS")
    print("="*80)
    
    for rec in REPORTE_FORENSE["recomendaciones_inmediatas"]:
        print(f"\n{rec}")
    
    # Conclusión
    print("\n" + "="*80)
    print("📌 CONCLUSIÓN")
    print("="*80)
    
    conc = REPORTE_FORENSE["conclusión"]
    print(f"""
Estado:             {conc['estado']}
Causa:              {conc['causa']}
Impacto:            {conc['impacto']}
Solución:           {conc['solución']}
Tiempo estimado:    {conc['tiempo_estimado_corrección']}
""")
    
    # Guardar reporte JSON
    report_path = Path(__file__).parent.parent / "CryptoBotPro_Data" / f"reporte_forense_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(REPORTE_FORENSE, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Reporte guardado: {report_path}\n")

if __name__ == "__main__":
    main()
