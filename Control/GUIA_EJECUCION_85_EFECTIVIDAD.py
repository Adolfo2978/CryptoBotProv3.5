#!/usr/bin/env python3
"""
🚀 GUÍA DE EJECUCIÓN - Sistema 85% Efectividad
Instrucciones paso a paso para activar el sistema
"""

GUIA_EJECUCION = """

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║      🚀 GUÍA DE EJECUCIÓN - SISTEMA 85% EFECTIVIDAD                    ║
║                                                                           ║
║      Crypto Bot Pro v34.0.1.2 + Advanced Signal Filter                   ║
║      Fecha: 26 de Enero de 2026                                          ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝


═══════════════════════════════════════════════════════════════════════════
FASE 1: VERIFICACIÓN PRE-EJECUCIÓN (5 minutos)
═══════════════════════════════════════════════════════════════════════════

✅ PASO 1: Verificar estructura de archivos
────────────────────────────────────────────

Asegúrate que existen estos archivos en la carpeta raíz:

  ✓ advanced_signal_filter.py (651 líneas)
  ✓ adaptive_autotrader.py (559 líneas)
  ✓ config_v20_optimized.json (actualizado)
  ✓ Crypto-Pro-Python v34.0.1.2.py (archivo principal)
  ✓ CryptoBotPro_Data/ (directorio con logs/)

COMANDO DE VERIFICACIÓN:
  dir /B | find "advanced_signal_filter.py"
  dir /B | find "adaptive_autotrader.py"
  dir /B | find "config_v20_optimized.json"


✅ PASO 2: Verificar configuración
──────────────────────────────────

Abre config_v20_optimized.json y confirma:

  ✓ "AUTO_TRADING_ENABLED": true
  ✓ "ADVANCED_SIGNAL_FILTER_ENABLED": true
  ✓ "MIN_SIGNAL_SCORE": 0.75
  ✓ "USE_TESTNET": true (para pruebas iniciales)
  ✓ "MAX_DAILY_SIGNALS": 5
  ✓ "MAX_CONCURRENT_TRADES": 2

NOTA: Mantener USE_TESTNET = true durante primeras 48-72 horas


✅ PASO 3: Verificar credenciales
─────────────────────────────────

En config_v20_optimized.json, confirmar:

  ✓ "binance_api_key": [presente y válida]
  ✓ "binance_secret_key": [presente y válida]
  ✓ "telegram_bot_token": [presente y válida]
  ✓ "telegram_chat_id": [presente y válida]

ADVERTENCIA: No compartir credenciales. Están encriptadas en el sistema.


✅ PASO 4: Crear directorio de logs
──────────────────────────────────

El sistema creará automáticamente los directorios necesarios:

  C:\Crypto-Pro-Python v34.0.1.2\CryptoBotPro_Data\logs\

Los logs se guardarán aquí para análisis.


═══════════════════════════════════════════════════════════════════════════
FASE 2: EJECUCIÓN EN TESTNET (48-72 horas)
═══════════════════════════════════════════════════════════════════════════

🎯 OBJETIVO: Validar 75-85% win rate

⚠️ IMPORTANTE: Mantener USE_TESTNET = true durante esta fase


OPCIÓN A: Ejecución GUI (Recomendado para monitoreo)
──────────────────────────────────────────────────────

COMANDO:
  python "Crypto-Pro-Python v34.0.1.2.py"

ESPERADO:
  1. Aparecerá ventana de selección de modo
  2. Seleccionar "Modo Gráfico"
  3. GUI se abrirá con controles
  4. Sistema comenzará a analizar mercados
  5. Señales aparecerán en tiempo real
  6. Telegram enviará notificaciones

MONITOREO:
  ✓ Verificar número de señales generadas (meta: 3-5/día)
  ✓ Observar señales aceptadas vs rechazadas
  ✓ Ver Win Rate en GUI
  ✓ Revisar P&L diario


OPCIÓN B: Ejecución Consola (Para servidor/background)
─────────────────────────────────────────────────────

COMANDO:
  python "Crypto-Pro-Python v34.0.1.2.py"

ESPERADO:
  1. Aparecerá ventana de selección de modo
  2. Seleccionar "Modo Consola"
  3. Sistema ejecutará en background
  4. Logs se guardarán en CryptoBotPro_Data/logs/
  5. Telegram enviará notificaciones

MONITOREO:
  Ver logs en tiempo real:
    tail -f CryptoBotPro_Data/logs/crypto_bot.log

O revisar con comandos:
    powershell
    Get-Content "CryptoBotPro_Data\logs\crypto_bot.log" -Wait


═══════════════════════════════════════════════════════════════════════════
FASE 3: VALIDACIÓN Y MONITOREO
═══════════════════════════════════════════════════════════════════════════

📊 MÉTRICAS A OBSERVAR (Cada 24 horas)

SEMANA 1 - APRENDIZAJE (Días 1-3):
──────────────────────────────────

  META: Win Rate 70% + (mientras aprende)
  
  ✓ Señales generadas: 10-15 totales
  ✓ Señales aceptadas: 3-5 por día
  ✓ Win rate observado: 65-75%
  ✓ P&L esperado: +2% a +5%
  ✓ Drawdown: < 3%
  
  ACCIONES:
    - Revisar logs buscando "Advanced Signal Filter"
    - Verificar que 10 capas de validación se aplican
    - Confirmar que el score es ≥75% para aceptadas


SEMANA 1-2 - ESTABILIZACIÓN (Días 4-7):
──────────────────────────────────────

  META: Win Rate 75-78%
  
  ✓ Señales generadas: 15-20 totales
  ✓ Señales aceptadas: 3-5 por día
  ✓ Win rate observado: 75-78%
  ✓ P&L esperado: +5% a +10%
  ✓ Drawdown: < 2.5%
  
  ACCIONES:
    - Si por debajo de meta: revisar parámetros
    - Si por arriba: puede escalar ligeramente
    - Mantener USE_TESTNET = true


SEMANA 3+ - OPERACIÓN OPTIMAL (Días 15+):
────────────────────────────────────────

  META: Win Rate 78-85%
  
  ✓ Señales generadas: 15-20 totales
  ✓ Señales aceptadas: 3-5 por día
  ✓ Win rate observado: 78-85%
  ✓ P&L esperado: +10% a +20%
  ✓ Drawdown: < 2%
  
  ACCIONES:
    - Sistema está en óptimo
    - Puede considerar MAINNET
    - Comenzar con capital pequeño


═══════════════════════════════════════════════════════════════════════════
FASE 4: ANÁLISIS DE LOGS
═══════════════════════════════════════════════════════════════════════════

📝 UBICACIÓN DE LOGS:

  C:\Crypto-Pro-Python v34.0.1.2\CryptoBotPro_Data\logs\
  
  Archivos generados:
    ├── crypto_bot.log (log general)
    ├── advanced_filter.log (filtrador avanzado)
    ├── autotrader.log (ejecución de trades)
    └── telegram.log (notificaciones)


🔍 QUÉ BUSCAR EN LOS LOGS:

1. FILTRADOR ACTIVO:
   
   ✅ Buscar: "Advanced Signal Filter"
   ✅ Buscar: "10 capas de validación"
   ✅ Buscar: "Score: 0.75"


2. SEÑALES ACEPTADAS:
   
   ✅ Buscar: "Señal APROBADA"
   ✅ Verificar: "Confluencia: X/5"
   ✅ Verificar: "WinProb: XX%"


3. SEÑALES RECHAZADAS:
   
   ✅ Buscar: "Señal rechazada"
   ✅ Verificar: "Score < 0.75"
   ✅ Buscar razón del rechazo


4. TRADES EJECUTADOS:
   
   ✅ Buscar: "Trade abierto"
   ✅ Verificar: "Entry: $X, SL: $Y, TP: $Z"
   ✅ Buscar: "Trade cerrado"


═══════════════════════════════════════════════════════════════════════════
FASE 5: AJUSTES Y OPTIMIZACIONES
═══════════════════════════════════════════════════════════════════════════

⚡ SI WIN RATE ESTÁ POR DEBAJO DE 75%

OPCIÓN 1: Aumentar MIN_SIGNAL_SCORE
  
  En config_v20_optimized.json:
    "MIN_SIGNAL_SCORE": 0.75  →  "MIN_SIGNAL_SCORE": 0.80
  
  EFECTO: Más selectivo, menos señales pero de mejor calidad


OPCIÓN 2: Aumentar MIN_CONFLUENCE
  
  En config_v20_optimized.json:
    "MIN_CONFLUENCE": 0.60  →  "MIN_CONFLUENCE": 0.70
  
  EFECTO: Requiere 4/5 indicadores en lugar de 3/5


OPCIÓN 3: Aumentar MIN_NEURAL_DESTACADA
  
  En config_v20_optimized.json:
    "MIN_NEURAL_DESTACADA": 90  →  "MIN_NEURAL_DESTACADA": 92
  
  EFECTO: Red neuronal más precisa, menos falsos positivos


⚡ SI SEÑALES SON MUY POCAS (< 2 por día)

OPCIÓN 1: Reducir MIN_SIGNAL_SCORE

  "MIN_SIGNAL_SCORE": 0.75  →  "MIN_SIGNAL_SCORE": 0.70

  EFECTO: Menos selectivo, más señales


OPCIÓN 2: Reducir MIN_CONFLUENCE

  "MIN_CONFLUENCE": 0.60  →  "MIN_CONFLUENCE": 0.50

  EFECTO: Requiere 2.5/5 indicadores


OPCIÓN 3: Aumentar MAX_DAILY_SIGNALS

  "MAX_DAILY_SIGNALS": 5  →  "MAX_DAILY_SIGNALS": 8

  EFECTO: Permite más señales por día


═══════════════════════════════════════════════════════════════════════════
FASE 6: PREPARACIÓN PARA MAINNET (Después del TESTNET)
═══════════════════════════════════════════════════════════════════════════

✅ CHECKLIST ANTES DE MAINNET:

  [ ] Win Rate testnet alcanzó 75-85% mínimo
  [ ] Sistema ha operado 48-72 horas estable
  [ ] Logs muestran que filtrador funciona correcto
  [ ] P&L diario ha sido consistentemente positivo
  [ ] Drawdown se mantuvo bajo (< 3%)
  [ ] Telegram notificaciones funcionando
  [ ] Documentación de configuración guardada


⚠️ CAMBIOS NECESARIOS PARA MAINNET:

1. Actualizar config_v20_optimized.json:

   "USE_TESTNET": true  →  "USE_TESTNET": false
   "AUTOTRADER_MODE": "testnet"  →  "AUTOTRADER_MODE": "live"


2. REDUCIR CAPITAL INICIAL:

   "AUTO_TRADE_QUANTITY_USDT": 10  →  "AUTO_TRADE_QUANTITY_USDT": 5
   "AUTOTRADER_CAPITAL_USDT": 10  →  "AUTOTRADER_CAPITAL_USDT": 5


3. AUMENTAR PRECAUCIONES:

   "MAX_DAILY_SIGNALS": 5  →  "MAX_DAILY_SIGNALS": 3
   "MAX_CONCURRENT_TRADES": 2  →  "MAX_CONCURRENT_TRADES": 1


4. GUARDAR CONFIGURACIÓN:

   Copiar config_v20_optimized.json a carpeta de respaldo


═══════════════════════════════════════════════════════════════════════════
TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════

❌ PROBLEMA: No se genera ninguna señal

SOLUCIONES:
  1. Verificar que AUTO_TRADING_ENABLED = true
  2. Verificar que MIN_SIGNAL_SCORE no está muy alto (probar 0.70)
  3. Revisar logs buscando "ERROR" o "WARNING"
  4. Verificar conexión a Binance (API keys)
  5. Verificar que no hay límite de rate en Binance


❌ PROBLEMA: Todas las señales son rechazadas

SOLUCIONES:
  1. Verificar MIN_SIGNAL_SCORE (reducir a 0.70 o 0.65)
  2. Verificar MIN_CONFLUENCE (reducir a 0.50)
  3. Revisar logs para ver razón de rechazo
  4. Verificar que dataframes tienen suficiente historia
  5. Comprobar que indicadores calculan correctamente


❌ PROBLEMA: Win rate no mejora

SOLUCIONES:
  1. Aumentar MIN_SIGNAL_SCORE a 0.80 o 0.85
  2. Aumentar MIN_NEURAL_DESTACADA a 92-94
  3. Aumentar MIN_VOLUME_RATIO a 1.5
  4. Esperar más tiempo (mínimo 1 semana de datos)
  5. Revisar parámetros de stop loss / take profit


❌ PROBLEMA: Errores de conexión

SOLUCIONES:
  1. Verificar credenciales Binance
  2. Verificar que NO está bloqueado el IP
  3. Revisar logs para mensajes de error específicos
  4. Intentar conexión manual con credenciales
  5. Esperar 5-10 minutos y reintentar


═══════════════════════════════════════════════════════════════════════════
MONITOREO DIARIO - CHECKLIST
═══════════════════════════════════════════════════════════════════════════

CADA MAÑANA (5 minutos):

  [ ] Proceso Python está ejecutándose
  [ ] Revisar logs para errores
  [ ] Contar señales generadas ayer
  [ ] Verificar P&L del día anterior
  [ ] Revisar notificaciones de Telegram
  [ ] Confirmar que ningún trade está "stuck"


CADA SEMANA (15 minutos):

  [ ] Calcular Win Rate acumulado
  [ ] Revisar Drawdown máximo
  [ ] Analizar patrones de señales
  [ ] Verificar si ajustes son necesarios
  [ ] Generar reporte de performance
  [ ] Consultar documentación si hay dudas


═══════════════════════════════════════════════════════════════════════════
REFERENCIAS Y DOCUMENTACIÓN
═══════════════════════════════════════════════════════════════════════════

ARCHIVOS IMPORTANTES:

  📄 VERIFICACION_85_EFECTIVIDAD.md
     └─ Reporte completo de verificación (leer primero)

  📄 MEJORAS_WIN_RATE_75_85.md
     └─ Documentación técnica detallada

  📄 CHECKLIST_WIN_RATE_75_85.txt
     └─ Checklist de implementación

  📄 REPORTE_VERIFICACION_85.json
     └─ Reporte JSON con todos los cambios

  📄 GUIA_EJECUCION_85_EFECTIVIDAD.py
     └─ Esta guía que estás leyendo


═══════════════════════════════════════════════════════════════════════════
SOPORTE Y AYUDA
═══════════════════════════════════════════════════════════════════════════

SI NECESITAS AYUDA:

1. Revisa VERIFICACION_85_EFECTIVIDAD.md
2. Busca tu error en la sección TROUBLESHOOTING
3. Revisa los logs en CryptoBotPro_Data/logs/
4. Consulta MEJORAS_WIN_RATE_75_85.md para detalles técnicos
5. Verifica config_v20_optimized.json


═══════════════════════════════════════════════════════════════════════════
RESUMEN RÁPIDO
═══════════════════════════════════════════════════════════════════════════

🚀 PARA EMPEZAR AHORA:

  1. Ejecutar: python "Crypto-Pro-Python v34.0.1.2.py"
  2. Seleccionar modo (GUI o Consola)
  3. Sistema comenzará automáticamente
  4. Monitorear logs y señales
  5. Esperar 48-72 horas en TESTNET
  6. Validar Win Rate 75-85%
  7. Pasar a MAINNET si satisfactorio

⏱️  TIEMPO ESTIMADO:

  Verificación: 5 minutos
  TESTNET: 72 horas
  Análisis: 1-2 horas
  MAINNET: Gradual (1-2 semanas)


🎯 META FINAL:

  ✅ Win Rate: 75-85%
  ✅ Trades selectivos: 3-5 por día
  ✅ Risk/Reward: 2:1 mínimo
  ✅ Profit sostenible: 10-20% mensual
  ✅ Operación 24/7 automática

═══════════════════════════════════════════════════════════════════════════

¡SISTEMA LISTO PARA OPERAR!

Presiona ENTER para continuar...

"""

if __name__ == '__main__':
    import sys
    import io
    
    # Configurar encoding UTF-8
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except:
            pass
    
    print(GUIA_EJECUCION)
    
    # Guardar como archivo
    try:
        with open('GUIA_EJECUCION_85_EFECTIVIDAD.md', 'w', encoding='utf-8') as f:
            f.write(GUIA_EJECUCION.replace('═', '═').replace('╔', '╔').replace('╚', '╚'))
        print("\n✅ Guía guardada como: GUIA_EJECUCION_85_EFECTIVIDAD.md")
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
