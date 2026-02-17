#!/usr/bin/env python3
"""
🔍 AUDITOR FORENSE - Sistema de Auditoría Integral del Bot de Trading
Análisis automático de:
- Vulnerabilidades de seguridad
- Errores críticos y bugs
- Performance y optimización
- Integridad de datos
- Riesgos de trading
- Simulación de condiciones de mercado
"""

import sys
import os
import json
import logging
import asyncio
import threading
import traceback
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from collections import defaultdict
import hashlib

logger = logging.getLogger('ForensicAuditor')

class SecurityAudit:
    """Auditoría de seguridad del sistema"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.issues = []
        self.warnings = []
        self.alerts = []
        
    def audit_credentials(self) -> Dict[str, Any]:
        """Audita credenciales y claves API"""
        results = {
            'status': 'PASS',
            'issues': [],
            'warnings': []
        }
        
        # Verificar archivos de credenciales
        cred_files = ['authcreds.json', 'telegram_creds.json']
        for cred_file in cred_files:
            if os.path.exists(cred_file):
                try:
                    with open(cred_file, 'r') as f:
                        data = json.load(f)
                    # Verificar que no estén en claro
                    if 'api_key' in data or 'api_secret' in data:
                        if not self._is_encrypted(str(data)):
                            results['warnings'].append(
                                f"⚠️ {cred_file}: Credenciales posiblemente sin encriptar"
                            )
                            results['status'] = 'WARNING'
                except Exception as e:
                    results['issues'].append(f"❌ Error leyendo {cred_file}: {e}")
                    results['status'] = 'FAIL'
        
        return results
    
    def _is_encrypted(self, text: str) -> bool:
        """Verifica si el texto parece encriptado"""
        # Heurística simple: si contiene solo caracteres hex o base64-like
        import re
        return bool(re.match(r'^[A-Fa-f0-9]{20,}$', text)) or 'encrypted' in text.lower()
    
    def audit_api_connections(self) -> Dict[str, Any]:
        """Audita conexiones a APIs"""
        results = {
            'status': 'PASS',
            'issues': [],
            'tests': {}
        }
        
        # Test Binance API
        try:
            import requests
            resp = requests.get('https://api.binance.com/api/v3/ping', timeout=5)
            results['tests']['binance'] = {
                'status': 'UP' if resp.status_code == 200 else 'ISSUE',
                'latency_ms': resp.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            results['tests']['binance'] = {'status': 'DOWN', 'error': str(e)}
            results['status'] = 'FAIL'
        
        # Test Telegram
        try:
            import requests
            # Test de conectividad (sin API key)
            resp = requests.get('https://api.telegram.org/', timeout=5)
            results['tests']['telegram'] = {
                'status': 'UP' if resp.status_code in [200, 403] else 'ISSUE',
                'latency_ms': resp.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            results['tests']['telegram'] = {'status': 'DOWN', 'error': str(e)}
        
        return results
    
    def audit_file_integrity(self) -> Dict[str, Any]:
        """Verifica integridad de archivos críticos"""
        results = {
            'status': 'PASS',
            'files_checked': 0,
            'corrupted': [],
            'hashes': {}
        }
        
        critical_files = [
            'Crypto-Pro-Python v34.0.1.2.py',
            'config_v20_optimized.json'
        ]
        
        for file in critical_files:
            if os.path.exists(file):
                results['files_checked'] += 1
                try:
                    with open(file, 'rb') as f:
                        content = f.read()
                        hash_val = hashlib.sha256(content).hexdigest()
                        results['hashes'][file] = hash_val
                        
                        # Verificar integridad básica
                        if file.endswith('.json'):
                            json.loads(content.decode('utf-8'))
                        elif file.endswith('.py'):
                            # Compilar para verificar sintaxis
                            compile(content, file, 'exec')
                except Exception as e:
                    results['corrupted'].append(f"{file}: {e}")
                    results['status'] = 'FAIL'
        
        return results


class PerformanceAnalysis:
    """Análisis de performance y optimización"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = time.time()
    
    def analyze_bot_efficiency(self) -> Dict[str, Any]:
        """Analiza eficiencia del bot"""
        results = {
            'cpu_usage': self._estimate_cpu(),
            'memory_usage': self._estimate_memory(),
            'bottlenecks': [],
            'optimization_suggestions': []
        }
        
        # Detectar bottlenecks
        if results['cpu_usage'] > 80:
            results['bottlenecks'].append("⚠️ CPU alta - Optimizar loops de análisis")
            results['optimization_suggestions'].append(
                "Reducir SCAN_INTERVAL o cantidad de símbolos analizados"
            )
        
        if results['memory_usage'] > 1024:  # > 1GB
            results['bottlenecks'].append("⚠️ Memoria alta - Posible fuga")
            results['optimization_suggestions'].append(
                "Implementar limpeza de cache más agresiva"
            )
        
        return results
    
    def _estimate_cpu(self) -> float:
        """Estima uso de CPU (0-100%)"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0.0
    
    def _estimate_memory(self) -> int:
        """Estima uso de memoria en MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)  # MB
        except:
            return 0


class DataIntegrityCheck:
    """Verificación de integridad de datos"""
    
    @staticmethod
    def check_training_data() -> Dict[str, Any]:
        """Verifica datos de entrenamiento"""
        results = {
            'status': 'PASS',
            'training_dir': 'CryptoBotPro_Data/training_data',
            'trades_found': 0,
            'issues': [],
            'stats': {}
        }
        
        training_dir = results['training_dir']
        success_dir = os.path.join(training_dir, 'successful_trades')
        
        if not os.path.exists(success_dir):
            results['status'] = 'WARNING'
            results['issues'].append("📭 Directorio de trades exitosos no existe")
            return results
        
        # Contar y validar JSONs
        json_files = [f for f in os.listdir(success_dir) if f.endswith('.json')]
        results['trades_found'] = len(json_files)
        
        corrupted = []
        total_profit = 0
        profits = []
        
        for json_file in json_files:
            try:
                with open(os.path.join(success_dir, json_file), 'r') as f:
                    data = json.load(f)
                    profit = float(data.get('profit_percent', 0))
                    profits.append(profit)
                    total_profit += profit
            except Exception as e:
                corrupted.append((json_file, str(e)))
        
        if corrupted:
            results['status'] = 'WARNING'
            results['issues'].append(f"⚠️ {len(corrupted)} JSONs corruptos")
        
        if profits:
            results['stats'] = {
                'total_trades': len(json_files),
                'avg_profit': total_profit / len(json_files),
                'max_profit': max(profits),
                'min_profit': min(profits),
                'corrupted': len(corrupted)
            }
        
        return results


class RiskAnalysis:
    """Análisis de riesgos de trading"""
    
    @staticmethod
    def analyze_trading_parameters(config: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza parámetros de riesgo"""
        results = {
            'status': 'PASS',
            'risks': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Verificar stop loss
        if config.get('STOP_LOSS_PERCENT', 1.0) > 5.0:
            results['risks'].append("❌ Stop loss muy alto (>5%)")
            results['recommendations'].append("Reducir STOP_LOSS_PERCENT a ≤ 2%")
        
        # Verificar leverage
        leverage = config.get('AUTOTRADER_LEVERAGE', 1)
        if leverage > 20:
            results['risks'].append(f"❌ Leverage muy alto ({leverage}x)")
            results['recommendations'].append("Reducir leverage a ≤ 10x")
        
        # Verificar capital
        capital = config.get('AUTOTRADER_CAPITAL_USDT', 10)
        if capital < 10:
            results['warnings'].append(f"⚠️ Capital bajo (${capital})")
            results['recommendations'].append("Aumentar capital mínimo a $50")
        
        # Verificar cantidad de trades simultáneos
        max_daily = config.get('MAX_DAILY_SIGNALS', 10)
        if max_daily > 20:
            results['warnings'].append(f"⚠️ Muchas señales diarias ({max_daily})")
            results['recommendations'].append("Reducir MAX_DAILY_SIGNALS a ≤ 10")
        
        return results


class SimulationEngine:
    """Motor de simulación de trading"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.trades_simulated = []
        self.portfolio_value = config.get('AUTOTRADER_CAPITAL_USDT', 10)
        self.initial_capital = self.portfolio_value
    
    def simulate_market_conditions(self, 
                                   historical_data: List[Dict],
                                   num_simulations: int = 100) -> Dict[str, Any]:
        """Simula trading bajo diferentes condiciones de mercado"""
        
        results = {
            'simulations': num_simulations,
            'avg_return': 0,
            'win_rate': 0,
            'max_drawdown': 0,
            'scenarios_tested': [],
            'trades': []
        }
        
        if not historical_data or num_simulations < 1:
            return results
        
        # Generar escenarios de mercado
        scenarios = self._generate_market_scenarios(historical_data, num_simulations)
        
        total_profit = 0
        winning_trades = 0
        total_trades = 0
        max_dd = 0
        
        for scenario in scenarios:
            # Simular trading en este escenario
            sim_result = self._simulate_trading_scenario(scenario)
            
            results['scenarios_tested'].append({
                'name': scenario['name'],
                'trades': sim_result['trades'],
                'profit_percent': sim_result['profit_percent']
            })
            
            total_profit += sim_result['profit_percent']
            winning_trades += sim_result['winning_trades']
            total_trades += sim_result['total_trades']
            max_dd = max(max_dd, sim_result['max_drawdown'])
        
        if total_trades > 0:
            results['avg_return'] = total_profit / num_simulations
            results['win_rate'] = (winning_trades / total_trades) * 100
        
        results['max_drawdown'] = max_dd
        
        return results
    
    def _generate_market_scenarios(self, data: List[Dict], num: int) -> List[Dict]:
        """Genera diferentes escenarios de mercado para testing"""
        scenarios = []
        
        # Escenario 1: Tendencia alcista fuerte
        scenarios.append({
            'name': 'STRONG_UPTREND',
            'volatility': 0.5,
            'trend': 1.0,  # Bullish
            'description': 'Mercado alcista sostenido'
        })
        
        # Escenario 2: Tendencia bajista fuerte
        scenarios.append({
            'name': 'STRONG_DOWNTREND',
            'volatility': 0.7,
            'trend': -1.0,  # Bearish
            'description': 'Mercado bajista con volatilidad alta'
        })
        
        # Escenario 3: Mercado lateral (sideways)
        scenarios.append({
            'name': 'SIDEWAYS',
            'volatility': 0.3,
            'trend': 0.0,
            'description': 'Mercado lateral sin dirección clara'
        })
        
        # Escenario 4: Alta volatilidad
        scenarios.append({
            'name': 'HIGH_VOLATILITY',
            'volatility': 1.5,
            'trend': 0.2,
            'description': 'Volatilidad extrema con picos'
        })
        
        # Escenario 5: Flash crash
        scenarios.append({
            'name': 'FLASH_CRASH',
            'volatility': 2.0,
            'trend': -1.5,
            'description': 'Caída rápida seguida de recuperación'
        })
        
        return scenarios
    
    def _simulate_trading_scenario(self, scenario: Dict) -> Dict[str, Any]:
        """Simula trading en un escenario específico"""
        result = {
            'scenario': scenario['name'],
            'trades': 0,
            'winning_trades': 0,
            'profit_percent': 0,
            'max_drawdown': 0
        }
        
        # Simulación simplificada
        # Basado en parámetros de riesgo
        win_rate = 0.55  # 55% de win rate
        avg_win = self.config.get('PROFIT_TARGET_PERCENT', 3.0)
        avg_loss = self.config.get('STOP_LOSS_PERCENT', 1.0)
        
        # Número de trades esperados en este escenario
        num_trades = np.random.randint(5, 20)
        result['trades'] = num_trades
        
        total_profit = 0
        for _ in range(num_trades):
            if np.random.random() < win_rate:
                # Trade ganador
                profit = avg_win * (0.8 + np.random.random() * 0.4)  # Variación
                total_profit += profit
                result['winning_trades'] += 1
            else:
                # Trade perdedor
                loss = -avg_loss * (0.8 + np.random.random() * 0.4)
                total_profit += loss
        
        result['profit_percent'] = total_profit
        result['max_drawdown'] = avg_loss * 3  # Estimado
        
        return result


class ErrorDetector:
    """Detector de errores y anomalías"""
    
    def __init__(self):
        self.error_log = []
        self.anomalies = []
    
    def analyze_logs(self, log_path: str) -> Dict[str, Any]:
        """Analiza archivos de log para detectar errores"""
        results = {
            'total_errors': 0,
            'total_warnings': 0,
            'critical_errors': [],
            'patterns': {},
            'error_types': defaultdict(int),
            'recommendations': []
        }
        
        if not os.path.exists(log_path):
            return results
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line in lines[-1000:]:  # Últimas 1000 líneas
                if 'ERROR' in line:
                    results['total_errors'] += 1
                    self._categorize_error(line, results)
                elif 'WARNING' in line:
                    results['total_warnings'] += 1
                elif 'CRITICAL' in line:
                    results['critical_errors'].append(line[:100])
        
        except Exception as e:
            logger.error(f"Error leyendo logs: {e}")
        
        return results
    
    def _categorize_error(self, line: str, results: Dict):
        """Categoriza tipos de errores"""
        if 'API' in line or 'connection' in line:
            results['error_types']['API_CONNECTION'] += 1
        elif 'memory' in line or 'Memory' in line:
            results['error_types']['MEMORY'] += 1
        elif 'timeout' in line or 'Timeout' in line:
            results['error_types']['TIMEOUT'] += 1
        elif 'database' in line or 'DB' in line:
            results['error_types']['DATABASE'] += 1
        elif 'trading' in line or 'trade' in line:
            results['error_types']['TRADING'] += 1
        else:
            results['error_types']['OTHER'] += 1


class AdaptiveAILearner:
    """Módulo de aprendizaje adaptativo de IA"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.market_conditions = []
        self.strategy_performance = {}
        self.adaptive_thresholds = {}
    
    def analyze_market_conditions(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza condiciones actuales del mercado"""
        results = {
            'symbol': symbol,
            'volatility': 0,
            'trend': 'NEUTRAL',
            'momentum': 0,
            'volume_profile': 'NORMAL',
            'timestamp': datetime.now().isoformat()
        }
        
        if df.empty:
            return results
        
        # Calcular volatilidad
        returns = df['close'].pct_change()
        results['volatility'] = returns.std() * 100
        
        # Calcular tendencia
        if len(df) >= 20:
            short_ma = df['close'].tail(5).mean()
            long_ma = df['close'].tail(20).mean()
            if short_ma > long_ma * 1.02:
                results['trend'] = 'BULLISH'
            elif short_ma < long_ma * 0.98:
                results['trend'] = 'BEARISH'
        
        # Momentum
        if len(df) >= 14:
            rsi = self._calculate_rsi(df['close'], 14)
            results['momentum'] = rsi[-1] if len(rsi) > 0 else 50
        
        return results
    
    def adapt_strategy_parameters(self, market_conditions: List[Dict]) -> Dict[str, Any]:
        """Adapta parámetros de estrategia según condiciones de mercado"""
        results = {
            'original_parameters': {},
            'adapted_parameters': {},
            'changes': [],
            'adaptation_score': 0
        }
        
        if not market_conditions:
            return results
        
        # Calcular promedio de volatilidad
        avg_volatility = np.mean([m.get('volatility', 1) for m in market_conditions])
        
        # Adaptar parámetros
        if avg_volatility > 5.0:  # Alta volatilidad
            results['adapted_parameters']['STOP_LOSS_PERCENT'] = 1.5
            results['adapted_parameters']['PROFIT_TARGET_PERCENT'] = 2.0
            results['changes'].append("📈 Alta volatilidad: Stop loss aumentado")
        elif avg_volatility < 1.0:  # Baja volatilidad
            results['adapted_parameters']['STOP_LOSS_PERCENT'] = 0.5
            results['adapted_parameters']['PROFIT_TARGET_PERCENT'] = 4.0
            results['changes'].append("📉 Baja volatilidad: Targets aumentados")
        
        results['adaptation_score'] = min(100, avg_volatility * 20)
        
        return results
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> np.ndarray:
        """Calcula RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.values
        except:
            return np.array([50] * len(prices))


class ForensicAuditorReport:
    """Generador de reportes forenses completos"""
    
    def __init__(self):
        self.security_audit = SecurityAudit('config_v20_optimized.json')
        self.performance = PerformanceAnalysis()
        self.data_check = DataIntegrityCheck()
        self.error_detector = ErrorDetector()
        self.risk_analyzer = RiskAnalysis()
    
    def generate_full_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte forense completo"""
        
        print("\n" + "="*80)
        print("🔍 AUDITORÍA FORENSE - ANÁLISIS INTEGRAL DEL SISTEMA")
        print("="*80 + "\n")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'sections': {}
        }
        
        # 1. Auditoría de Seguridad
        print("1️⃣  AUDITORÍA DE SEGURIDAD")
        print("-" * 40)
        security_results = self.security_audit.audit_credentials()
        print(f"   Credenciales: {security_results['status']}")
        for warning in security_results.get('warnings', []):
            print(f"   {warning}")
        
        api_results = self.security_audit.audit_api_connections()
        print(f"\n   APIs: {api_results['status']}")
        for api, test in api_results.get('tests', {}).items():
            print(f"   - {api}: {test.get('status')} ({test.get('latency_ms', '?'):.0f}ms)")
        
        file_integrity = self.security_audit.audit_file_integrity()
        print(f"\n   Integridad de archivos: {file_integrity['status']}")
        print(f"   - Archivos verificados: {file_integrity['files_checked']}")
        if file_integrity['corrupted']:
            for corrupt in file_integrity['corrupted']:
                print(f"   - ❌ {corrupt}")
        
        report['sections']['security'] = {
            'credentials': security_results,
            'apis': api_results,
            'file_integrity': file_integrity
        }
        
        # 2. Análisis de Performance
        print("\n2️⃣  ANÁLISIS DE PERFORMANCE")
        print("-" * 40)
        perf_results = self.performance.analyze_bot_efficiency()
        print(f"   CPU: {perf_results['cpu_usage']:.1f}%")
        print(f"   Memoria: {perf_results['memory_usage']:.0f} MB")
        for bottleneck in perf_results['bottlenecks']:
            print(f"   {bottleneck}")
        
        report['sections']['performance'] = perf_results
        
        # 3. Integridad de Datos
        print("\n3️⃣  INTEGRIDAD DE DATOS")
        print("-" * 40)
        data_results = self.data_check.check_training_data()
        print(f"   Estado: {data_results['status']}")
        print(f"   Trades encontrados: {data_results['trades_found']}")
        if data_results.get('stats'):
            print(f"   - Promedio de ganancia: {data_results['stats'].get('avg_profit', 0):.2f}%")
            print(f"   - Ganancia máxima: {data_results['stats'].get('max_profit', 0):.2f}%")
        
        report['sections']['data'] = data_results
        
        # 4. Análisis de Riesgos
        print("\n4️⃣  ANÁLISIS DE RIESGOS")
        print("-" * 40)
        risk_results = self.risk_analyzer.analyze_trading_parameters(config)
        print(f"   Estado: {risk_results['status']}")
        for risk in risk_results['risks']:
            print(f"   {risk}")
        for warning in risk_results['warnings']:
            print(f"   {warning}")
        if risk_results['recommendations']:
            print("\n   Recomendaciones:")
            for rec in risk_results['recommendations']:
                print(f"   ✅ {rec}")
        
        report['sections']['risks'] = risk_results
        
        # 5. Análisis de Errores
        print("\n5️⃣  ANÁLISIS DE ERRORES")
        print("-" * 40)
        log_path = 'CryptoBotPro_Data/logs/CryptoBotDebug_latest.log'
        if not os.path.exists(log_path):
            logs = list(os.glob('CryptoBotPro_Data/logs/CryptoBotDebug_*.log'))
            if logs:
                log_path = sorted(logs)[-1]  # Usar el más reciente
        
        error_results = self.error_detector.analyze_logs(log_path)
        print(f"   Errores totales: {error_results['total_errors']}")
        print(f"   Advertencias: {error_results['total_warnings']}")
        print(f"   Errores críticos: {len(error_results['critical_errors'])}")
        
        if error_results['error_types']:
            print("\n   Tipos de error:")
            for error_type, count in error_results['error_types'].items():
                print(f"   - {error_type}: {count}")
        
        report['sections']['errors'] = error_results
        
        print("\n" + "="*80)
        print(f"✅ REPORTE FORENSE COMPLETADO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        return report


def run_forensic_audit():
    """Ejecuta auditoría forense completa"""
    try:
        # Cargar configuración
        with open('config_v20_optimized.json', 'r') as f:
            config = json.load(f)
        
        # Generar reporte
        auditor = ForensicAuditorReport()
        report = auditor.generate_full_report(config)
        
        # Guardar reporte
        report_file = f"CryptoBotPro_Data/audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('CryptoBotPro_Data', exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📁 Reporte guardado en: {report_file}\n")
        
        return report
    
    except Exception as e:
        logger.error(f"Error en auditoría forense: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ejecutar auditoría
    run_forensic_audit()
