# 📋 ARCHIVOS DE CONFIGURACIÓN RECOMENDADOS

## Archivo 1: authcreds.json
```json
{
    "api_key": "tu_api_key_de_binance",
    "api_secret": "tu_api_secret_de_binance",
    "testnet": true,
    "testnet_api_key": "tu_testnet_api_key",
    "testnet_api_secret": "tu_testnet_api_secret"
}
```

**⚠️ IMPORTANTE:**
- NO compartas este archivo
- NO lo subas a GitHub
- Mantén las credenciales seguras
- Para obtener las claves: https://www.binance.com/es/account/api-management


## Archivo 2: telegram_creds.json
```json
{
    "bot_token": "tu_bot_token",
    "chat_id": "tu_chat_id",
    "enabled": true
}
```

**Como obtener:**
1. Abre Telegram y busca @BotFather
2. Usa /newbot para crear un nuevo bot
3. Copia el token que te da
4. Inicia una conversación con tu bot
5. Usa @userinfobot para obtener tu chat_id


## Archivo 3: config_v20_optimized.json (RECOMENDADO PARA TESTNET)

```json
{
    "MARKET_TYPE": "PERPETUALS",
    "AUTO_TRADING_ENABLED": true,
    "AUTO_TRADE_QUANTITY_USDT": 10,
    "AUTOTRADER_MODE": "testnet",
    "USE_TESTNET": true,
    "AUTOTRADER_CAPITAL_USDT": 50,
    "AUTOTRADER_LEVERAGE": 5,
    "AUTOTRADER_COMPOUND_ENABLED": false,
    "AUTOTRADER_COMPOUND_PERCENT": 0,
    "MAX_CONCURRENT_TRADES": 2,
    "MAX_DAILY_SIGNALS": 5,
    "PROFIT_TARGET_PERCENT": 2.0,
    "STOP_LOSS_PERCENT": 1.0,
    "MILESTONE_1": 1.0,
    "MILESTONE_2": 2.0,
    "MILESTONE_3": 3.0,
    "TRAILING_STOP_ENABLED": true,
    "TRAILING_STOP_DISTANCE": 0.3,
    "MIN_NEURAL_DESTACADA": 85.0,
    "MIN_TECHNICAL_DESTACADA": 85.0,
    "MIN_NEURAL_CONFIRMADA": 88.0,
    "MIN_TECHNICAL_CONFIRMADA": 88.0,
    "MIN_ALIGNMENT_DESTACADA": 85.0,
    "MIN_ALIGNMENT_CONFIRMADA": 88.0,
    "NEURAL_WEIGHT": 0.5,
    "TECHNICAL_WEIGHT": 0.5,
    "EMA_FAST": 50,
    "EMA_SLOW": 200,
    "SCAN_INTERVAL": 60,
    "telegram_enabled": true,
    "MONITORING_INTERVAL": 5,
    "REQUIRE_ENTRY_SETUP": true,
    "REQUIRE_CANDLE_PATTERN": false
}
```


## Configuración para DIFERENTES ESTILOS:

### CONSERVADOR (Mínimo Riesgo)
```json
{
    "USE_TESTNET": true,
    "AUTOTRADER_CAPITAL_USDT": 50,
    "AUTOTRADER_LEVERAGE": 3,
    "STOP_LOSS_PERCENT": 0.8,
    "PROFIT_TARGET_PERCENT": 4.0,
    "MAX_DAILY_SIGNALS": 3,
    "MAX_CONCURRENT_TRADES": 1,
    "MIN_NEURAL_DESTACADA": 90,
    "TRAILING_STOP_ENABLED": true
}
```

### BALANCEADO (Medio Riesgo)
```json
{
    "USE_TESTNET": false,
    "AUTOTRADER_CAPITAL_USDT": 200,
    "AUTOTRADER_LEVERAGE": 8,
    "STOP_LOSS_PERCENT": 1.0,
    "PROFIT_TARGET_PERCENT": 3.0,
    "MAX_DAILY_SIGNALS": 8,
    "MAX_CONCURRENT_TRADES": 2,
    "MIN_NEURAL_DESTACADA": 85,
    "TRAILING_STOP_ENABLED": true
}
```

### AGRESIVO (Mayor Riesgo/Retorno)
```json
{
    "USE_TESTNET": false,
    "AUTOTRADER_CAPITAL_USDT": 500,
    "AUTOTRADER_LEVERAGE": 15,
    "STOP_LOSS_PERCENT": 1.5,
    "PROFIT_TARGET_PERCENT": 5.0,
    "MAX_DAILY_SIGNALS": 15,
    "MAX_CONCURRENT_TRADES": 4,
    "MIN_NEURAL_DESTACADA": 80,
    "TRAILING_STOP_ENABLED": true
}
```


## Configuración para DIFERENTES MERCADOS:

### MERCADO ALCISTA (Bullish)
```json
{
    "EMA_FAST": 50,
    "EMA_SLOW": 200,
    "PROFIT_TARGET_PERCENT": 4.0,
    "STOP_LOSS_PERCENT": 0.8,
    "MIN_NEURAL_DESTACADA": 82
}
```

### MERCADO BAJISTA (Bearish)
```json
{
    "EMA_FAST": 20,
    "EMA_SLOW": 100,
    "PROFIT_TARGET_PERCENT": 2.0,
    "STOP_LOSS_PERCENT": 1.5,
    "MIN_NEURAL_DESTACADA": 88
}
```

### MERCADO LATERAL (Sideways)
```json
{
    "EMA_FAST": 12,
    "EMA_SLOW": 26,
    "PROFIT_TARGET_PERCENT": 1.5,
    "STOP_LOSS_PERCENT": 0.5,
    "MIN_NEURAL_DESTACADA": 90,
    "MAX_DAILY_SIGNALS": 20
}
```


## CHECKLIST ANTES DE INICIAR:

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas: pip install -r requirements.txt
- [ ] authcreds.json creado con API keys de Binance
- [ ] telegram_creds.json creado con token de Telegram
- [ ] config_v20_optimized.json actualizado
- [ ] USE_TESTNET en true para pruebas iniciales
- [ ] Capital inicial configurado (comenzar con $50-100)
- [ ] Stop loss y take profit configurados
- [ ] Directorio CryptoBotPro_Data creado
- [ ] Logs directory verificado
- [ ] Primero ejecutar: python master_executor.py --mode setup


## PASOS INICIALES RECOMENDADOS:

1. **Día 1-3: Pruebas en TESTNET**
   - USE_TESTNET: true
   - Observar 3-5 trades
   - Verificar alertas de Telegram
   - Revisar logs para errores

2. **Día 4-7: Small Real Capital**
   - USE_TESTNET: false
   - AUTOTRADER_CAPITAL_USDT: 50-100
   - MAX_DAILY_SIGNALS: 3-5
   - Monitoreo diario activo

3. **Semana 2+: Scaling Up**
   - Aumentar capital gradualmente
   - Ajustar parámetros según performance
   - Activar ejecución automática 24/7
   - Revisar reportes semanales


## MONITOREO DIARIO:

- [ ] Revisar alertas de Telegram
- [ ] Verificar último log: CryptoBotPro_Data/logs/CryptoBotDebug_latest.log
- [ ] Confirmar que bot está running
- [ ] Notar número de trades ejecutados
- [ ] Revisar P&L total
- [ ] Confirmar stops loss funcionando
- [ ] Verificar que no hay errores críticos


## OPTIMIZACIÓN CONTINUA:

Cada semana ajusta basado en:
- Win rate actual
- Promedio de ganancias/pérdidas
- Volatilidad del mercado
- Número de false signals
- Tiempo promedio de trade


¡Buena suerte con tu bot de trading! 🚀
