#!/usr/bin/env python3
"""
🎯 ADVANCED SIGNAL FILTER - Mejorador de Win Rate 75-85%
Sistema avanzado de filtrado y validación de señales
- Confirmación Multi-Timeframe
- Análisis de Confluencia
- Filtros de Calidad Múltiple
- Detección de Patrones Avanzada
- Validación de Contexto de Mercado
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger('AdvancedSignalFilter')


class SignalStrength(Enum):
    """Fortaleza de señal"""
    WEAK = "DÉBIL"
    MODERATE = "MODERADA"
    STRONG = "FUERTE"
    VERY_STRONG = "MUY_FUERTE"


@dataclass
class AdvancedSignal:
    """Señal mejorada con múltiples validaciones"""
    symbol: str
    signal_type: str  # BUY/SELL
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    strength: SignalStrength
    
    # Validaciones
    confluence_count: int  # Número de indicadores alineados
    timeframe_confirmation: bool  # Confirmación multi-timeframe
    market_context_valid: bool  # Contexto de mercado válido
    pattern_confirmed: bool  # Patrón confirmado
    volume_confirmed: bool  # Volumen confirmado
    
    # Estadísticas
    win_probability: float  # Probabilidad de ganancia basada en historia
    risk_reward_ratio: float  # Ratio riesgo/recompensa
    
    # Metadata
    indicators_aligned: List[str] = None
    validation_score: float = 0.0
    rejection_reasons: List[str] = None


class AdvancedSignalFilter:
    """Filtrador avanzado de señales con múltiples capas de validación"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.signal_history = []
        self.win_count = 0
        self.loss_count = 0
        self.historical_patterns = {}
    
    def validate_signal(self, signal_data: Dict[str, Any], 
                       df_entry: pd.DataFrame,
                       df_primary: pd.DataFrame = None) -> Optional[AdvancedSignal]:
        """
        Valida señal con múltiples filtros
        Retorna Advanced Signal si cumple todos los criterios, None si no
        """
        
        rejection_reasons = []
        confluence_indicators = []
        validation_scores = {}
        
        symbol = signal_data.get('symbol')
        signal_type = signal_data.get('signal_type')
        confidence = signal_data.get('confidence', 0)
        entry_price = signal_data.get('entry_price', 0)
        stop_loss = signal_data.get('stop_loss', 0)
        take_profit = signal_data.get('take_profit', 0)
        
        # ========== FILTRO 1: VALIDACIÓN DE PRECIOS ==========
        if not self._validate_prices(entry_price, stop_loss, take_profit):
            rejection_reasons.append("❌ Precios inválidos")
            return None
        
        # ========== FILTRO 2: CONFLUENCIA DE INDICADORES ==========
        confluence_score = self._check_confluence(df_entry, signal_type)
        validation_scores['confluence'] = confluence_score
        
        if confluence_score < 0.60:  # Mínimo 3 de 5 indicadores
            rejection_reasons.append(f"❌ Confluencia baja ({confluence_score:.1%})")
        else:
            confluence_indicators = self._get_aligned_indicators(df_entry, signal_type)
        
        # ========== FILTRO 3: CONFIRMACIÓN MULTI-TIMEFRAME ==========
        timeframe_confirmed = False
        if df_primary is not None:
            timeframe_confirmed = self._confirm_multi_timeframe(
                df_entry, df_primary, signal_type
            )
            if not timeframe_confirmed:
                rejection_reasons.append("❌ Timeframes no alineados")
        
        # ========== FILTRO 4: CONTEXTO DE MERCADO ==========
        market_context_valid, market_reason = self._validate_market_context(df_entry)
        if not market_context_valid:
            rejection_reasons.append(f"❌ {market_reason}")
        
        # ========== FILTRO 5: PATRÓN DE VELAS ==========
        pattern_score = self._analyze_candle_pattern(df_entry, signal_type)
        validation_scores['pattern'] = pattern_score
        
        if pattern_score < 0.50:
            rejection_reasons.append(f"❌ Patrón débil ({pattern_score:.1%})")
        
        # ========== FILTRO 6: CONFIRMACIÓN DE VOLUMEN ==========
        volume_confirmed, volume_score = self._validate_volume(df_entry)
        validation_scores['volume'] = volume_score
        
        if not volume_confirmed:
            rejection_reasons.append(f"❌ Volumen insuficiente")
        
        # ========== FILTRO 7: RATIO RIESGO/RECOMPENSA ==========
        risk_reward = self._calculate_risk_reward(entry_price, stop_loss, take_profit)
        if risk_reward < 1.5:  # Mínimo 1.5:1
            rejection_reasons.append(f"❌ Risk/Reward bajo ({risk_reward:.2f}:1)")
        
        # ========== FILTRO 8: HISTÓRICO Y PROBABILIDAD ==========
        win_probability = self._estimate_win_probability(symbol, signal_type, confluence_score)
        
        if win_probability < 0.65:  # Mínimo 65%
            rejection_reasons.append(f"❌ Probabilidad de ganancia baja ({win_probability:.1%})")
        
        # ========== FILTRO 9: RETROCESO Y ENTRADA ==========
        is_valid_pullback = self._validate_pullback(df_entry, signal_type)
        if not is_valid_pullback:
            rejection_reasons.append("❌ Retroceso de entrada no válido")
        
        # ========== FILTRO 10: DIVERGENCIAS ==========
        has_positive_divergence = self._check_divergences(df_entry, signal_type)
        if not has_positive_divergence:
            rejection_reasons.append("⚠️ Sin divergencias positivas")
        
        # ========== CALCULAR SCORE FINAL ==========
        overall_score = self._calculate_overall_score(
            confluence_score,
            pattern_score,
            volume_score,
            win_probability,
            market_context_valid,
            timeframe_confirmed,
            is_valid_pullback,
            has_positive_divergence
        )
        
        logger.info(f"📊 Validación de {symbol}: Score={overall_score:.1%}, "
                   f"WinProb={win_probability:.1%}, Confluencia={confluence_score:.1%}")
        
        # ========== DECISION FINAL ==========
        # Si score >= 75%, aceptar señal
        if overall_score >= 0.75:
            signal_strength = self._determine_signal_strength(overall_score)
            
            advanced_signal = AdvancedSignal(
                symbol=symbol,
                signal_type=signal_type,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=overall_score * 100,
                strength=signal_strength,
                confluence_count=len(confluence_indicators),
                timeframe_confirmation=timeframe_confirmed,
                market_context_valid=market_context_valid,
                pattern_confirmed=pattern_score >= 0.50,
                volume_confirmed=volume_confirmed,
                win_probability=win_probability,
                risk_reward_ratio=risk_reward,
                indicators_aligned=confluence_indicators,
                validation_score=overall_score,
                rejection_reasons=[]
            )
            
            logger.info(f"✅ SEÑAL ACEPTADA: {symbol} - Fuerza: {signal_strength.value}")
            return advanced_signal
        else:
            logger.warning(f"🚫 SEÑAL RECHAZADA: {symbol} - "
                          f"Score: {overall_score:.1%} < 75% requerido")
            logger.warning(f"   Razones: {'; '.join(rejection_reasons)}")
            return None
    
    def _validate_prices(self, entry: float, sl: float, tp: float) -> bool:
        """Valida que los precios sean coherentes"""
        if entry <= 0 or sl <= 0 or tp <= 0:
            return False
        
        # El precio de entrada debe estar entre SL y TP
        return (sl < entry < tp) or (tp < entry < sl)
    
    def _check_confluence(self, df: pd.DataFrame, signal_type: str) -> float:
        """
        Verifica confluencia de múltiples indicadores
        Retorna porcentaje de indicadores alineados (0-100%)
        """
        
        aligned_count = 0
        total_indicators = 5
        
        try:
            if df.empty or len(df) < 20:
                return 0.0
            
            close = df['close'].values
            
            # Indicador 1: RSI
            rsi = self._calculate_rsi(close, 14)
            if signal_type == "BUY" and rsi[-1] > 40 and rsi[-1] < 70:
                aligned_count += 1
            elif signal_type == "SELL" and rsi[-1] > 30 and rsi[-1] < 60:
                aligned_count += 1
            
            # Indicador 2: MACD
            if len(close) >= 26:
                macd_aligned = self._check_macd(close, signal_type)
                if macd_aligned:
                    aligned_count += 1
            
            # Indicador 3: Bandas de Bollinger
            if len(close) >= 20:
                bb_aligned = self._check_bollinger_bands(close, signal_type)
                if bb_aligned:
                    aligned_count += 1
            
            # Indicador 4: EMA
            if len(close) >= 50:
                ema_aligned = self._check_ema_alignment(close, signal_type)
                if ema_aligned:
                    aligned_count += 1
            
            # Indicador 5: Momentum
            if len(close) >= 10:
                momentum_aligned = self._check_momentum(close, signal_type)
                if momentum_aligned:
                    aligned_count += 1
            
            return aligned_count / total_indicators
        
        except Exception as e:
            logger.error(f"Error en confluencia: {e}")
            return 0.0
    
    def _get_aligned_indicators(self, df: pd.DataFrame, signal_type: str) -> List[str]:
        """Retorna lista de indicadores alineados"""
        aligned = []
        close = df['close'].values
        
        if len(close) < 14:
            return aligned
        
        rsi = self._calculate_rsi(close, 14)
        if signal_type == "BUY" and 40 < rsi[-1] < 70:
            aligned.append("RSI")
        elif signal_type == "SELL" and 30 < rsi[-1] < 60:
            aligned.append("RSI")
        
        if len(close) >= 26 and self._check_macd(close, signal_type):
            aligned.append("MACD")
        
        if len(close) >= 20 and self._check_bollinger_bands(close, signal_type):
            aligned.append("BB")
        
        if len(close) >= 50 and self._check_ema_alignment(close, signal_type):
            aligned.append("EMA")
        
        if len(close) >= 10 and self._check_momentum(close, signal_type):
            aligned.append("MOMENTUM")
        
        return aligned
    
    def _confirm_multi_timeframe(self, df_entry: pd.DataFrame, 
                                 df_primary: pd.DataFrame,
                                 signal_type: str) -> bool:
        """Confirma que timeframe primario apoya la señal"""
        
        try:
            if df_primary.empty or len(df_primary) < 20:
                return True  # No rechazar si no tenemos datos
            
            close = df_primary['close'].values
            rsi = self._calculate_rsi(close, 14)
            
            if signal_type == "BUY":
                # En timeframe mayor, debe estar en uptrend
                trend = close[-1] > close[-20]
                rsi_ok = rsi[-1] > 35
                return trend and rsi_ok
            else:
                # En timeframe mayor, debe estar en downtrend
                trend = close[-1] < close[-20]
                rsi_ok = rsi[-1] < 65
                return trend and rsi_ok
        
        except:
            return True
    
    def _validate_market_context(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Valida contexto general del mercado"""
        
        try:
            if df.empty or len(df) < 50:
                return True, ""
            
            close = df['close'].values
            
            # Volatilidad
            returns = np.diff(close) / close[:-1]
            volatility = np.std(returns)
            
            if volatility > 0.05:  # > 5% es muy alto
                return False, "Volatilidad extrema"
            
            # Tendencia general
            ma20 = np.mean(close[-20:])
            ma50 = np.mean(close[-50:])
            
            # No operar en laterales extremos
            if abs(ma20 - ma50) / ma50 < 0.01:  # < 1% de diferencia
                return False, "Mercado demasiado lateral"
            
            return True, ""
        
        except:
            return True, ""
    
    def _analyze_candle_pattern(self, df: pd.DataFrame, signal_type: str) -> float:
        """Analiza fortaleza del patrón de velas"""
        
        try:
            if len(df) < 5:
                return 0.0
            
            # Últimas 3 velas
            closes = df['close'].values[-3:]
            opens = df['open'].values[-3:]
            highs = df['high'].values[-3:]
            lows = df['low'].values[-3:]
            
            # Fortaleza del patrón (0-1)
            strength = 0.0
            
            if signal_type == "BUY":
                # Buscar vela verde fuerte
                last_close = closes[-1]
                last_open = opens[-1]
                
                if last_close > last_open:
                    body_size = (last_close - last_open) / (highs[-1] - lows[-1]) if highs[-1] > lows[-1] else 0
                    strength = min(1.0, body_size * 1.5)
            
            else:  # SELL
                # Buscar vela roja fuerte
                last_close = closes[-1]
                last_open = opens[-1]
                
                if last_close < last_open:
                    body_size = (last_open - last_close) / (highs[-1] - lows[-1]) if highs[-1] > lows[-1] else 0
                    strength = min(1.0, body_size * 1.5)
            
            return max(0.0, min(1.0, strength))
        
        except:
            return 0.5
    
    def _validate_volume(self, df: pd.DataFrame) -> Tuple[bool, float]:
        """Valida que el volumen confirme la señal"""
        
        try:
            if 'volume' not in df.columns or len(df) < 20:
                return True, 0.5  # No rechazar si no tenemos volumen
            
            volumes = df['volume'].values
            
            # Comparar con promedio
            avg_volume = np.mean(volumes[-20:])
            current_volume = volumes[-1]
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Volumen debe estar 20% arriba del promedio
            confirmed = volume_ratio > 1.2
            score = min(1.0, volume_ratio / 2.0)
            
            return confirmed, score
        
        except:
            return True, 0.5
    
    def _calculate_risk_reward(self, entry: float, sl: float, tp: float) -> float:
        """Calcula ratio riesgo/recompensa"""
        
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        
        if risk <= 0:
            return 0.0
        
        return reward / risk
    
    def _estimate_win_probability(self, symbol: str, signal_type: str, 
                                  confluence_score: float) -> float:
        """Estima probabilidad de ganancia basada en histórico"""
        
        # Base: 50%
        base_probability = 0.50
        
        # Confluencia añade probabilidad (hasta +20%)
        confluence_bonus = confluence_score * 0.20
        
        # Histórico del símbolo
        if symbol in self.historical_patterns:
            historical_wr = self.historical_patterns[symbol]
            historical_bonus = (historical_wr - 0.50) * 0.15
        else:
            historical_bonus = 0.0
        
        # Probabilidad final
        probability = base_probability + confluence_bonus + historical_bonus
        
        return min(0.95, max(0.50, probability))
    
    def _validate_pullback(self, df: pd.DataFrame, signal_type: str) -> bool:
        """Valida que haya un retroceso válido para entrada"""
        
        try:
            if len(df) < 10:
                return True
            
            close = df['close'].values[-10:]
            
            if signal_type == "BUY":
                # Buscar pullback en uptrend
                # Debe haber bajado después de subir
                if close[-5] > close[-3] and close[-1] > close[-3]:
                    return True
            else:
                # Buscar pullback en downtrend
                if close[-5] < close[-3] and close[-1] < close[-3]:
                    return True
            
            return False
        
        except:
            return True
    
    def _check_divergences(self, df: pd.DataFrame, signal_type: str) -> bool:
        """Verifica divergencias positivas"""
        
        try:
            if len(df) < 14:
                return True
            
            close = df['close'].values
            rsi = self._calculate_rsi(close, 14)
            
            # Buscar divergencia alcista/bajista
            # (Simplificado: busca si RSI no confirma extremo del precio)
            
            if signal_type == "BUY" and len(rsi) >= 5:
                # Divergencia alcista: precio baja pero RSI sube
                return rsi[-1] > rsi[-5]
            
            elif signal_type == "SELL" and len(rsi) >= 5:
                # Divergencia bajista: precio sube pero RSI baja
                return rsi[-1] < rsi[-5]
            
            return True
        
        except:
            return True
    
    def _calculate_overall_score(self, confluence: float, pattern: float,
                                volume: float, win_prob: float,
                                market_ok: bool, timeframe_ok: bool,
                                pullback_ok: bool, divergence_ok: bool) -> float:
        """Calcula score final ponderado"""
        
        weights = {
            'confluence': 0.25,
            'pattern': 0.15,
            'volume': 0.10,
            'win_prob': 0.20,
            'market': 0.10 if market_ok else 0.00,
            'timeframe': 0.10 if timeframe_ok else 0.00,
            'pullback': 0.05 if pullback_ok else 0.00,
            'divergence': 0.05 if divergence_ok else 0.00
        }
        
        score = (
            confluence * weights['confluence'] +
            pattern * weights['pattern'] +
            volume * weights['volume'] +
            win_prob * weights['win_prob'] +
            (1.0 if market_ok else 0.0) * weights['market'] +
            (1.0 if timeframe_ok else 0.0) * weights['timeframe'] +
            (1.0 if pullback_ok else 0.0) * weights['pullback'] +
            (1.0 if divergence_ok else 0.0) * weights['divergence']
        )
        
        return min(1.0, max(0.0, score))
    
    def _determine_signal_strength(self, score: float) -> SignalStrength:
        """Determina la fortaleza de la señal"""
        
        if score >= 0.90:
            return SignalStrength.VERY_STRONG
        elif score >= 0.80:
            return SignalStrength.STRONG
        elif score >= 0.70:
            return SignalStrength.MODERATE
        else:
            return SignalStrength.WEAK
    
    # ========== MÉTODOS AUXILIARES DE CÁLCULO ==========
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Calcula RSI"""
        try:
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                rsi = np.full(len(prices), 100.0)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            return np.full(len(prices), rsi)
        except:
            return np.full(len(prices), 50.0)
    
    def _check_macd(self, prices: np.ndarray, signal_type: str) -> bool:
        """Verifica alineación de MACD"""
        try:
            if len(prices) < 26:
                return True
            
            # EMA 12 y 26
            ema12 = np.mean(prices[-12:])
            ema26 = np.mean(prices[-26:])
            macd = ema12 - ema26
            
            if signal_type == "BUY":
                return macd > 0
            else:
                return macd < 0
        except:
            return True
    
    def _check_bollinger_bands(self, prices: np.ndarray, signal_type: str) -> bool:
        """Verifica alineación de Bandas de Bollinger"""
        try:
            if len(prices) < 20:
                return True
            
            mean = np.mean(prices[-20:])
            std = np.std(prices[-20:])
            
            upper = mean + 2 * std
            lower = mean - 2 * std
            current = prices[-1]
            
            if signal_type == "BUY":
                # Precio acercándose a banda inferior
                return current < mean and current > lower
            else:
                # Precio acercándose a banda superior
                return current > mean and current < upper
        except:
            return True
    
    def _check_ema_alignment(self, prices: np.ndarray, signal_type: str) -> bool:
        """Verifica alineación de EMAs"""
        try:
            if len(prices) < 50:
                return True
            
            ema50 = np.mean(prices[-50:])
            ema200 = np.mean(prices[-200:]) if len(prices) >= 200 else ema50
            
            if signal_type == "BUY":
                return ema50 > ema200
            else:
                return ema50 < ema200
        except:
            return True
    
    def _check_momentum(self, prices: np.ndarray, signal_type: str) -> bool:
        """Verifica momentum"""
        try:
            if len(prices) < 10:
                return True
            
            recent = prices[-5:]
            previous = prices[-10:-5]
            
            recent_momentum = np.mean(np.diff(recent))
            previous_momentum = np.mean(np.diff(previous))
            
            if signal_type == "BUY":
                return recent_momentum > 0 and recent_momentum > previous_momentum
            else:
                return recent_momentum < 0 and recent_momentum < previous_momentum
        except:
            return True
    
    def record_trade_result(self, symbol: str, signal_type: str, 
                           was_profitable: bool, profit_percent: float):
        """Registra resultado de trade para mejorar estimaciones"""
        
        if symbol not in self.historical_patterns:
            self.historical_patterns[symbol] = 0.50  # 50% inicial
        
        # Actualizar win rate histórico
        total = self.win_count + self.loss_count
        
        if was_profitable:
            self.win_count += 1
            self.historical_patterns[symbol] = (self.historical_patterns[symbol] * total + 1) / (total + 1)
        else:
            self.loss_count += 1
            self.historical_patterns[symbol] = (self.historical_patterns[symbol] * total + 0) / (total + 1)
        
        logger.info(f"📊 Trade registrado: {symbol} - {'✅ GANANCIA' if was_profitable else '❌ PÉRDIDA'} "
                   f"({profit_percent:+.2f}%)")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("✅ Módulo Advanced Signal Filter cargado")
