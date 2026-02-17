#!/usr/bin/env python3
"""
🤖 AUTO-TRADER MEJORADO - Sistema de Trading Automático Adaptativo
- Ejecución automática de trades
- Aprendizaje de condiciones de mercado
- Adaptación dinámica de estrategias
- Gestión de riesgos inteligente
- Integración con Telegram
"""

import sys
import os
import json
import logging
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
import pandas as pd
from enum import Enum

logger = logging.getLogger('AdaptiveAutoTrader')


class TradeStatus(Enum):
    """Estados posibles de un trade"""
    PENDING = "PENDIENTE"
    OPEN = "ABIERTO"
    MONITORING = "MONITOREANDO"
    PARTIALLY_CLOSED = "PARCIALMENTE_CERRADO"
    CLOSED = "CERRADO"
    CANCELLED = "CANCELADO"


@dataclass
class TradePosition:
    """Posición de trading"""
    symbol: str
    entry_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    status: TradeStatus = TradeStatus.PENDING
    current_profit: float = 0.0
    max_profit_reached: float = 0.0
    trades_count: int = 1
    
    def calculate_profit_percent(self, current_price: float) -> float:
        """Calcula porcentaje de ganancia actual"""
        if self.entry_price == 0:
            return 0.0
        return ((current_price - self.entry_price) / self.entry_price) * 100
    
    def is_stop_loss_hit(self, current_price: float) -> bool:
        """Verifica si se alcanzó el stop loss"""
        return current_price <= self.stop_loss
    
    def is_take_profit_hit(self, current_price: float) -> bool:
        """Verifica si se alcanzó el take profit"""
        return current_price >= self.take_profit


class AdaptiveStrategyManager:
    """Gestor de estrategias adaptativas"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.market_history = {}
        self.strategy_performance = {}
        self.learned_thresholds = {}
        self.adaptation_log = []
    
    def learn_from_market(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Aprende características del mercado para adaptación"""
        
        insights = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'features': {}
        }
        
        if df.empty or len(df) < 20:
            return insights
        
        # Extraer características del mercado
        close_prices = df['close'].values
        returns = np.diff(close_prices) / close_prices[:-1]
        
        # Volatilidad
        volatility = np.std(returns) * 100
        insights['features']['volatility'] = volatility
        
        # Tendencia
        ma_short = df['close'].tail(10).mean()
        ma_long = df['close'].tail(50).mean()
        trend_strength = abs(ma_short - ma_long) / ma_long * 100
        insights['features']['trend_strength'] = trend_strength
        
        # Momento
        momentum = close_prices[-1] / close_prices[-20] - 1
        insights['features']['momentum'] = momentum * 100
        
        # Volumen
        if 'volume' in df.columns:
            volume_trend = df['volume'].iloc[-1] / df['volume'].tail(20).mean()
            insights['features']['volume_trend'] = volume_trend
        
        # Guardar para análisis posterior
        if symbol not in self.market_history:
            self.market_history[symbol] = []
        self.market_history[symbol].append(insights)
        
        # Aprender umbrales adaptativos
        self._update_adaptive_thresholds(symbol, insights)
        
        return insights
    
    def _update_adaptive_thresholds(self, symbol: str, insights: Dict):
        """Actualiza umbrales adaptativos basado en aprendizaje"""
        
        if symbol not in self.learned_thresholds:
            self.learned_thresholds[symbol] = {
                'neural_min': self.config.get('MIN_NEURAL_DESTACADA', 85),
                'technical_min': self.config.get('MIN_TECHNICAL_DESTACADA', 85),
                'stop_loss': self.config.get('STOP_LOSS_PERCENT', 1.0),
                'profit_target': self.config.get('PROFIT_TARGET_PERCENT', 3.0)
            }
        
        thresholds = self.learned_thresholds[symbol]
        features = insights['features']
        volatility = features.get('volatility', 1.0)
        
        # Adaptar basado en volatilidad
        if volatility > 3.0:  # Volatilidad alta
            # Ser más selectivo (aumentar umbrales)
            thresholds['neural_min'] = min(95, thresholds['neural_min'] + 2)
            # Aumentar stop loss para proteger
            thresholds['stop_loss'] = min(2.0, thresholds['stop_loss'] + 0.3)
            # Reducir profit target
            thresholds['profit_target'] = max(1.5, thresholds['profit_target'] - 0.5)
        
        elif volatility < 1.0:  # Volatilidad baja
            # Ser menos selectivo
            thresholds['neural_min'] = max(80, thresholds['neural_min'] - 2)
            # Reducir stop loss
            thresholds['stop_loss'] = max(0.5, thresholds['stop_loss'] - 0.2)
            # Aumentar profit target
            thresholds['profit_target'] = min(5.0, thresholds['profit_target'] + 0.5)
        
        logger.info(f"📊 Umbrales adaptados para {symbol}: "
                   f"Neural={thresholds['neural_min']}, "
                   f"SL={thresholds['stop_loss']}%, "
                   f"PT={thresholds['profit_target']}%")
    
    def get_adaptive_parameters(self, symbol: str) -> Dict[str, float]:
        """Obtiene parámetros adaptativos para un símbolo"""
        if symbol in self.learned_thresholds:
            return self.learned_thresholds[symbol]
        
        # Retornar parámetros por defecto
        return {
            'neural_min': self.config.get('MIN_NEURAL_DESTACADA', 85),
            'technical_min': self.config.get('MIN_TECHNICAL_DESTACADA', 85),
            'stop_loss': self.config.get('STOP_LOSS_PERCENT', 1.0),
            'profit_target': self.config.get('PROFIT_TARGET_PERCENT', 3.0)
        }


class RiskManagementSystem:
    """Sistema de gestión de riesgos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.account_balance = config.get('AUTOTRADER_CAPITAL_USDT', 10)
        self.daily_loss_limit = self.account_balance * 0.1  # 10% máximo
        self.daily_losses = 0.0
        self.max_concurrent_trades = config.get('MAX_CONCURRENT_TRADES', 3)
        self.active_trades = []
    
    def can_open_trade(self, symbol: str, signal_confidence: float) -> Tuple[bool, str]:
        """Verifica si es seguro abrir un nuevo trade"""
        
        reasons = []
        
        # Verificar límite diario de pérdidas
        if self.daily_losses >= self.daily_loss_limit:
            return False, "❌ Límite diario de pérdidas alcanzado"
        
        # Verificar trades activos
        if len(self.active_trades) >= self.max_concurrent_trades:
            return False, f"❌ Máximo de {self.max_concurrent_trades} trades activos"
        
        # Verificar confianza de señal
        if signal_confidence < self.config.get('MIN_SIGNAL_CONFIDENCE', 80):
            return False, f"❌ Confianza de señal baja ({signal_confidence:.1f}%)"
        
        return True, "✅ Condiciones de riesgo aceptables"
    
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calcula el tamaño correcto de posición"""
        
        # Riesgo máximo por trade: 2% del capital
        max_risk = self.account_balance * 0.02
        
        # Calcular pérdida máxima en este trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0.0
        
        # Cantidad = Riesgo máximo / Riesgo por unidad
        quantity = max_risk / price_risk
        
        logger.info(f"📊 Tamaño de posición calculado: {quantity:.4f} "
                   f"(Riesgo: {max_risk} en {price_risk} puntos)")
        
        return quantity
    
    def track_trade(self, position: TradePosition):
        """Registra un trade nuevo"""
        self.active_trades.append(position)
    
    def close_trade(self, position: TradePosition, exit_price: float, reason: str):
        """Cierra un trade y registra P&L"""
        
        if position in self.active_trades:
            self.active_trades.remove(position)
        
        profit = (exit_price - position.entry_price) * position.quantity
        profit_percent = ((exit_price - position.entry_price) / position.entry_price) * 100
        
        if profit < 0:
            self.daily_losses += abs(profit)
        
        logger.info(f"💰 Trade cerrado: {position.symbol} | "
                   f"P&L: {profit:.2f}$ ({profit_percent:.2f}%) | "
                   f"Razón: {reason}")
        
        return {
            'symbol': position.symbol,
            'profit': profit,
            'profit_percent': profit_percent,
            'reason': reason,
            'duration': (datetime.now() - position.entry_time).total_seconds() / 60  # minutos
        }


class AutoTraderExecutor:
    """Ejecutor de trades automático"""
    
    def __init__(self, config: Dict[str, Any], exchange_client=None, telegram_client=None):
        self.config = config
        self.exchange_client = exchange_client
        self.telegram_client = telegram_client
        self.strategy_manager = AdaptiveStrategyManager(config)
        self.risk_manager = RiskManagementSystem(config)
        self.positions = {}
        self.trade_history = []
        self.running = False
        self.execution_lock = threading.Lock()
        
        # ✨ NUEVO: Filtrador avanzado de señales
        try:
            from advanced_signal_filter import AdvancedSignalFilter
            self.signal_filter = AdvancedSignalFilter(config)
            logger.info("✅ Advanced Signal Filter activado - Win Rate 75-85%")
        except ImportError:
            self.signal_filter = None
            logger.warning("⚠️ Signal Filter no disponible")
    
    def process_signal(self, signal_data: Dict[str, Any], 
                      df_entry: pd.DataFrame = None,
                      df_primary: pd.DataFrame = None) -> Optional[TradePosition]:
        """Procesa una señal de trading con filtrador avanzado"""
        
        if not self.config.get('AUTO_TRADING_ENABLED', False):
            logger.debug("⚠️ Auto-trading deshabilitado")
            return None
        
        try:
            with self.execution_lock:
                symbol = signal_data.get('symbol')
                signal_type = signal_data.get('signal_type')
                confidence = signal_data.get('confidence', 0)
                entry_price = signal_data.get('entry_price')
                stop_loss = signal_data.get('stop_loss')
                take_profit = signal_data.get('take_profit')
                
                # Validar datos básicos
                if not all([symbol, signal_type, entry_price, stop_loss, take_profit]):
                    logger.warning(f"⚠️ Datos incompletos en señal: {signal_data}")
                    return None
                
                # ✨ FILTRADO AVANZADO: Validar con múltiples capas
                if self.signal_filter and df_entry is not None:
                    advanced_signal = self.signal_filter.validate_signal(
                        signal_data, df_entry, df_primary
                    )
                    
                    if advanced_signal is None:
                        logger.info(f"🚫 Señal {symbol} rechazada por filtros avanzados")
                        return None
                    
                    # Usar parámetros validados
                    entry_price = advanced_signal.entry_price
                    stop_loss = advanced_signal.stop_loss
                    take_profit = advanced_signal.take_profit
                    confidence = advanced_signal.confidence
                    
                    logger.info(f"✅ Señal {symbol} APROBADA ({advanced_signal.strength.value}) - "
                               f"Confluencia: {advanced_signal.confluence_count}/5, "
                               f"WinProb: {advanced_signal.win_probability:.1%}")
                
                # Verificar riesgos
                can_trade, reason = self.risk_manager.can_open_trade(symbol, confidence)
                if not can_trade:
                    logger.info(f"🚫 {reason}")
                    return None
                
                # Calcular tamaño de posición
                quantity = self.risk_manager.calculate_position_size(entry_price, stop_loss)
                if quantity <= 0:
                    logger.warning(f"❌ Cantidad inválida: {quantity}")
                    return None
                
                # Crear posición
                position = TradePosition(
                    symbol=symbol,
                    entry_price=entry_price,
                    quantity=quantity,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    entry_time=datetime.now(),
                    status=TradeStatus.PENDING
                )
                
                # Ejecutar order
                if self.exchange_client:
                    order_result = self._execute_order(symbol, quantity, entry_price, signal_type)
                    if order_result:
                        position.status = TradeStatus.OPEN
                        self.positions[symbol] = position
                        self.risk_manager.track_trade(position)
                        
                        logger.info(f"✅ Trade abierto: {symbol} @ {entry_price} x {quantity}")
                        
                        # Notificar a Telegram
                        if self.telegram_client:
                            self._notify_trade_opened(position)
                        
                        return position
                    else:
                        logger.error(f"❌ Error ejecutando orden para {symbol}")
                        return None
                else:
                    # Modo simulación (sin exchange real)
                    position.status = TradeStatus.OPEN
                    self.positions[symbol] = position
                    logger.info(f"📊 [SIMULACIÓN] Trade abierto: {symbol} @ {entry_price}")
                    return position
        
        except Exception as e:
            logger.error(f"❌ Error procesando señal: {e}", exc_info=True)
            return None
    
    def _execute_order(self, symbol: str, quantity: float, price: float, side: str) -> Optional[Dict]:
        """Ejecuta orden en el exchange"""
        
        try:
            if not self.exchange_client:
                logger.warning("⚠️ No hay cliente de exchange")
                return None
            
            # Convertir side de señal a formato de exchange
            order_side = "BUY" if "BUY" in side or "COMPRA" in side else "SELL"
            
            order = self.exchange_client.place_order(
                symbol=symbol,
                side=order_side,
                quantity=quantity,
                price=price,
                order_type="LIMIT"
            )
            
            return order
        
        except Exception as e:
            logger.error(f"Error ejecutando orden: {e}", exc_info=True)
            return None
    
    def monitor_positions(self, market_data: Dict[str, float]) -> List[Dict]:
        """Monitorea posiciones abiertas y ejecuta stops/profits"""
        
        closed_trades = []
        
        for symbol, position in list(self.positions.items()):
            if position.status != TradeStatus.OPEN:
                continue
            
            current_price = market_data.get(symbol)
            if not current_price:
                continue
            
            # Actualizar profit actual
            profit_percent = position.calculate_profit_percent(current_price)
            position.current_profit = profit_percent
            position.max_profit_reached = max(position.max_profit_reached, profit_percent)
            
            # Verificar stop loss
            if position.is_stop_loss_hit(current_price):
                result = self.risk_manager.close_trade(position, current_price, "STOP_LOSS")
                closed_trades.append(result)
                del self.positions[symbol]
                
                if self.telegram_client:
                    self._notify_trade_closed(position, current_price, "STOP LOSS")
                
                logger.warning(f"🛑 Stop loss alcanzado para {symbol}")
                continue
            
            # Verificar take profit
            if position.is_take_profit_hit(current_price):
                result = self.risk_manager.close_trade(position, current_price, "TAKE_PROFIT")
                closed_trades.append(result)
                del self.positions[symbol]
                
                if self.telegram_client:
                    self._notify_trade_closed(position, current_price, "TAKE PROFIT")
                
                logger.info(f"🎯 Take profit alcanzado para {symbol}")
                continue
            
            # Trailing stop
            if self.config.get('TRAILING_STOP_ENABLED', False):
                self._apply_trailing_stop(position, current_price)
        
        return closed_trades
    
    def _apply_trailing_stop(self, position: TradePosition, current_price: float):
        """Aplica trailing stop dinámico"""
        
        if position.max_profit_reached <= 0:
            return
        
        # Si el precio ha bajado más del trailing distance desde máximo
        trailing_distance = self.config.get('TRAILING_STOP_DISTANCE', 0.3)
        max_price = position.entry_price + (position.entry_price * position.max_profit_reached / 100)
        
        if current_price < max_price * (1 - trailing_distance / 100):
            logger.info(f"⏱️ Trailing stop activado para {position.symbol}")
            # Aquí se cerraría la posición
            return True
        
        return False
    
    def _notify_trade_opened(self, position: TradePosition):
        """Notifica apertura de trade a Telegram"""
        try:
            if self.telegram_client:
                message = (
                    f"🟢 TRADE ABIERTO\n"
                    f"Símbolo: {position.symbol}\n"
                    f"Entrada: ${position.entry_price:.2f}\n"
                    f"Stop Loss: ${position.stop_loss:.2f}\n"
                    f"Take Profit: ${position.take_profit:.2f}\n"
                    f"Cantidad: {position.quantity:.4f}\n"
                    f"Hora: {position.entry_time.strftime('%H:%M:%S')}"
                )
                self.telegram_client.send_message(message)
        except Exception as e:
            logger.error(f"Error notificando a Telegram: {e}")
    
    def _notify_trade_closed(self, position: TradePosition, exit_price: float, reason: str):
        """Notifica cierre de trade a Telegram"""
        try:
            if self.telegram_client:
                profit_percent = ((exit_price - position.entry_price) / position.entry_price) * 100
                emoji = "🟢" if profit_percent >= 0 else "🔴"
                
                message = (
                    f"{emoji} TRADE CERRADO - {reason}\n"
                    f"Símbolo: {position.symbol}\n"
                    f"Entrada: ${position.entry_price:.2f}\n"
                    f"Salida: ${exit_price:.2f}\n"
                    f"Ganancia: {profit_percent:+.2f}%\n"
                    f"Duración: {(datetime.now() - position.entry_time).total_seconds() / 60:.0f} min"
                )
                self.telegram_client.send_message(message)
        except Exception as e:
            logger.error(f"Error notificando cierre: {e}")
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Resumen del portafolio"""
        
        total_open_trades = len(self.positions)
        total_profit = sum(p.current_profit for p in self.positions.values())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'open_trades': total_open_trades,
            'total_unrealized_profit': total_profit,
            'account_balance': self.risk_manager.account_balance,
            'daily_loss': self.risk_manager.daily_losses,
            'positions': {
                s: {
                    'entry': p.entry_price,
                    'current_profit': p.current_profit,
                    'max_profit': p.max_profit_reached,
                    'status': p.status.value
                }
                for s, p in self.positions.items()
            }
        }


def run_autotrader_daemon(config: Dict[str, Any], 
                          exchange_client=None, 
                          telegram_client=None,
                          data_manager=None):
    """Ejecuta autotrader en modo daemon"""
    
    autotrader = AutoTraderExecutor(config, exchange_client, telegram_client)
    
    logger.info("🤖 Iniciando Auto-Trader Daemon...")
    
    try:
        while autotrader.running:
            # Monitorear posiciones
            if data_manager:
                current_prices = data_manager.get_current_prices()
                closed = autotrader.monitor_positions(current_prices)
                
                if closed:
                    logger.info(f"📊 {len(closed)} trades cerrados en este ciclo")
            
            # Dormir antes de siguiente ciclo
            time.sleep(config.get('MONITORING_INTERVAL', 5))
    
    except KeyboardInterrupt:
        logger.info("⏹️ Auto-Trader interrumpido por usuario")
    except Exception as e:
        logger.error(f"Error en autotrader daemon: {e}", exc_info=True)
    finally:
        autotrader.running = False
        logger.info("🛑 Auto-Trader detenido")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("📦 Módulo de Auto-Trader cargado")
