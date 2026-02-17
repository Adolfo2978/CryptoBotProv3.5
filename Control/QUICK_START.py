#!/usr/bin/env python3
"""
⚡ QUICK START - Iniciar sistema en 3 pasos
"""

import os
import sys
import json
import subprocess
import platform

def check_environment():
    """Verifica entorno Python"""
    print("🔍 Verificando entorno...\n")
    
    # Python version
    version_info = sys.version_info
    print(f"✓ Python: {version_info.major}.{version_info.minor}.{version_info.micro}")
    
    # OS
    print(f"✓ SO: {platform.system()} {platform.release()}")
    
    # Required directories
    dirs = [
        'CryptoBotPro_Data',
        'CryptoBotPro_Data/logs',
        'CryptoBotPro_Data/cache',
        'CryptoBotPro_Data/models',
        'CryptoBotPro_Data/training_data'
    ]
    
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
            print(f"✓ Directorio creado: {d}")
        else:
            print(f"✓ Directorio existe: {d}")
    
    print()


def check_credentials():
    """Verifica credenciales necesarias"""
    print("🔐 Verificando credenciales...\n")
    
    checks = []
    
    # authcreds.json
    if os.path.exists('authcreds.json'):
        try:
            with open('authcreds.json', 'r') as f:
                auth = json.load(f)
            if 'api_key' in auth and 'api_secret' in auth:
                print("✅ authcreds.json - ENCONTRADO")
                checks.append(True)
            else:
                print("⚠️ authcreds.json - Incompleto (falta api_key/api_secret)")
                checks.append(False)
        except:
            print("⚠️ authcreds.json - Error al leer")
            checks.append(False)
    else:
        print("❌ authcreds.json - NO ENCONTRADO")
        print("   → Crear archivo: authcreds.json con api_key y api_secret")
        checks.append(False)
    
    # telegram_creds.json
    if os.path.exists('telegram_creds.json'):
        try:
            with open('telegram_creds.json', 'r') as f:
                tg = json.load(f)
            if 'bot_token' in tg and 'chat_id' in tg:
                print("✅ telegram_creds.json - ENCONTRADO")
                checks.append(True)
            else:
                print("⚠️ telegram_creds.json - Incompleto")
                checks.append(False)
        except:
            print("⚠️ telegram_creds.json - Error al leer")
            checks.append(False)
    else:
        print("⚠️ telegram_creds.json - NO ENCONTRADO (opcional)")
        print("   → Sin Telegram no recibirás alertas")
        checks.append(None)
    
    # config
    if os.path.exists('config_v20_optimized.json'):
        print("✅ config_v20_optimized.json - ENCONTRADO")
        checks.append(True)
    else:
        print("❌ config_v20_optimized.json - NO ENCONTRADO")
        checks.append(False)
    
    print()
    return all(c is not False for c in checks)


def check_dependencies():
    """Verifica dependencias Python"""
    print("📦 Verificando dependencias...\n")
    
    required = [
        'numpy',
        'pandas',
        'requests',
        'torch',  # Opcional pero recomendado
        'schedule',
        'sklearn'
    ]
    
    all_ok = True
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - FALTA INSTALAR")
            print(f"   pip install {package}")
            all_ok = False
    
    print()
    return all_ok


def show_quick_start():
    """Muestra guía de inicio rápido"""
    
    guide = """
╔════════════════════════════════════════════════════════════════════════╗
║                   🚀 QUICK START - 3 PASOS                            ║
╚════════════════════════════════════════════════════════════════════════╝

PASO 1: AUDITORÍA DEL SISTEMA (2 minutos)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  python master_executor.py --mode setup

  ✓ Verifica seguridad y credenciales
  ✓ Ejecuta simulaciones de mercado
  ✓ Analiza riesgos
  ✓ Genera plan de ejecución


PASO 2: ELEGIR MODO DE EJECUCIÓN (Elige uno)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  A) AUTO-TRADER (Con monitoreo manual)
     python adaptive_autotrader.py

  B) AUTOMÁTICO 24/7 (Sin intervención)
     python auto_executor.py

  C) SOLO AUDITORÍA (Sin trading)
     python forensic_auditor.py


PASO 3: MONITOREAR Y AJUSTAR (Continuo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓ Revisar alertas de Telegram
  ✓ Monitorear reportes automáticos
  ✓ Ajustar parámetros si es necesario
  ✓ Revisar logs regularmente


╔════════════════════════════════════════════════════════════════════════╗
║              CONFIGURACIÓN RECOMENDADA PARA PRINCIPIANTES             ║
╚════════════════════════════════════════════════════════════════════════╝

En config_v20_optimized.json:

{
    "USE_TESTNET": true,                      ← ⚠️ TESTNET (sin dinero real)
    "AUTOTRADER_CAPITAL_USDT": 50,           ← Capital pequeño
    "AUTO_TRADING_ENABLED": true,
    "STOP_LOSS_PERCENT": 1.0,                ← Stop loss estricto
    "PROFIT_TARGET_PERCENT": 2.0,            ← Target conservador
    "MAX_DAILY_SIGNALS": 5,                  ← Pocas señales
    "AUTOTRADER_LEVERAGE": 5,                ← Leverage bajo
    "telegram_enabled": true                  ← Recibir alertas
}


╔════════════════════════════════════════════════════════════════════════╗
║                      ⚡ PRIMEROS TRADES                               ║
╚════════════════════════════════════════════════════════════════════════╝

Primeros 24-48 horas:

1. ✓ Observar comportamiento del bot
2. ✓ Revisar trades ejecutados
3. ✓ Verificar cálculos de stop loss
4. ✓ Confirmar alertas de Telegram
5. ✓ Revisar logs en CryptoBotPro_Data/logs/

Si todo va bien:

1. ✓ Aumentar AUTOTRADER_CAPITAL_USDT gradualmente
2. ✓ Cambiar a mainnet (USE_TESTNET: false)
3. ✓ Ajustar parámetros según resultados
4. ✓ Activar ejecución automática 24/7


╔════════════════════════════════════════════════════════════════════════╗
║                   📊 ARCHIVOS IMPORTANTES                             ║
╚════════════════════════════════════════════════════════════════════════╝

Revisión diaria:
  - CryptoBotPro_Data/logs/CryptoBotDebug_*.log
  - Alertas de Telegram

Revisión semanal:
  - CryptoBotPro_Data/audit_report_*.json
  - CryptoBotPro_Data/logs/execution_report_*.txt

Configuración (editar si es necesario):
  - config_v20_optimized.json
  - authcreds.json
  - telegram_creds.json


╔════════════════════════════════════════════════════════════════════════╗
║                    ⚠️ ADVERTENCIAS IMPORTANTES                        ║
╚════════════════════════════════════════════════════════════════════════╝

🚨 ANTES DE USAR CON DINERO REAL:

1. ✓ Prueba en TESTNET primero (USE_TESTNET: true)
2. ✓ Comienza con capital pequeño ($50-100)
3. ✓ Monitorea los primeros trades manualmente
4. ✓ Ten alertas de Telegram activas
5. ✓ Establece límites de pérdida estrictos
6. ✓ No dejes el bot sin supervisión
7. ✓ Revisa los logs regularmente
8. ✓ Ante cualquier error: detén el bot y revisa


¡LISTO PARA COMENZAR! 🚀

"""
    
    print(guide)


def main():
    """Función principal"""
    
    print("\n" + "="*70)
    print("🚀 CRYPTO BOT PRO v34.0.1.2 - QUICK START")
    print("="*70 + "\n")
    
    # 1. Verificar entorno
    check_environment()
    
    # 2. Verificar credenciales
    creds_ok = check_credentials()
    
    # 3. Verificar dependencias
    deps_ok = check_dependencies()
    
    # Mostrar guía
    show_quick_start()
    
    # Resumen
    print("╔════════════════════════════════════════════════════════════════════════╗")
    if creds_ok and deps_ok:
        print("║ ✅ SISTEMA LISTO - Ejecuta: python master_executor.py --mode setup  ║")
    else:
        print("║ ⚠️ Revisa los requisitos arriba antes de iniciar                    ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
