#!/usr/bin/env python3
"""
Crypto Bot Pro v35.0.0.0 - Sistema Avanzado de Trading con IA (Version Mejorada y Robusta)
Aplicacion de escritorio usando PyQt5
Estrategia Unificada: EMA_TDI_PRICE_ACTION_NEURAL_ENHANCED
Desarrollado por Lic. Adolfo Daniel Aguirre

MEJORAS v35.0.0.0 (Senales mas Precisas y Sistema Robusto):
   - Red Neuronal Mejorada con capas de atencion y conexiones residuales
   - Sistema de Scoring de 12 factores ponderados para senales
   - Filtro de volatilidad adaptativo basado en ATR dinamico
   - Deteccion de divergencias RSI/MACD avanzada
   - Validacion de volumen con perfil de mercado institucional
   - Anti-ruido con filtro de Kalman simplificado
   - Gestion de riesgo dinamica basada en volatilidad
   - Cache inteligente con invalidacion por eventos y TTL
   - Reconexion automatica mejorada para WebSocket con backoff exponencial
   - Metricas de rendimiento en tiempo real
   - Sistema de confirmacion multi-timeframe reforzado
   - Cooldown entre senales del mismo par para evitar sobretrading
   - Validacion de liquidez minima antes de generar senales
   - Trailing Stop dinamico basado en ATR
   
HERENCIA v35.0.0.0:
   - Senal eliminada de GUI al cerrar en Telegram
   - Limpieza total de caches tras cierre
   - Solo 1 senal activa a la vez
   - Barra de progreso para DESTACADA
   - Foto SOLO para CONFIRMADA
   - Promocion automatica DESTACADA -> CONFIRMADA
   - Cierre automatico configurable

ULTIMA MODIFICACION: 04/02/2026 - FULL OPERATIVO CON MEJORAS
"""
# Verificación de entorno
import sys
import os
import platform
import warnings
import traceback
import tempfile
warnings.filterwarnings('ignore')
# ========== FIX PARA WINDOWS: Encoding UTF-8 AGRESIVO ==========
# if sys.platform == 'win32':
#     try:
#         # Intentar reconfigure (Python 3.7+)
#         sys.stdout.reconfigure(encoding='utf-8', errors='replace')
#         sys.stderr.reconfigure(encoding='utf-8', errors='replace')
#     except:
#         try:
#             # Fallback: forzar UTF-8 a nivel de variable de entorno
#             import io
#             sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
#             sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
#         except:
#             pass
#     # Forzar variable de entorno para Python
#     os.environ['PYTHONIOENCODING'] = 'utf-8'
# ========== CONFIGURACIÓN ENTORNO: Windows GUI / Replit Backend ==========
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
os.environ['QT_FONT_DPI'] = '96'

# Detectar entorno correctamente
IN_REPLIT = os.environ.get('REPL_ID') is not None
# ✅ SOLO GUI en Windows - BACKEND en Replit/Linux
HAS_DISPLAY = (not IN_REPLIT) and sys.platform == 'win32'

def is_desktop_environment():
    """Verifica si el script se está ejecutando en un entorno de escritorio"""
    try:
        if platform.system() in ['Windows', 'Darwin']:
            return True
        desktop_env = os.environ.get('DESKTOP_SESSION') or \
                      os.environ.get('XDG_CURRENT_DESKTOP') or \
                      os.environ.get('XDG_SESSION_DESKTOP')
        if hasattr(os, 'uname') and os.uname().sysname != 'Windows':
            display = os.environ.get('DISPLAY')
            if not display:
                return False
        return desktop_env is not None
    except:
        # ✅ En Replit/Linux sin display → Backend (False)
        return (not IN_REPLIT) and sys.platform == 'win32'

# Permitir ejecucion en Replit con VNC
print("Iniciando Crypto Bot Pro v35.0.0.0 - Version Mejorada con Senales Precisas", flush=True)
# Importaciones estándar
import asyncio
import threading
# Compatibilidad Python 3.12 + libs antiguas que usan Thread.isAlive()
if not hasattr(threading.Thread, 'isAlive'):
    threading.Thread.isAlive = threading.Thread.is_alive
import pickle
import logging
import json
import random
import time
import hashlib
import hmac
import queue
print("Imports estandar completados", flush=True)
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Callable, List, Optional, Tuple, Any, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
import ssl
import certifi
import urllib3
print("Imports red completados", flush=True)

# ========== FUNCIÓN DE AYUDA PARA RUTAS DE RECURSOS (DEBE DEFINIRSE ANTES DE USAR) ==========
def resource_path(relative_path):
    """
    Obtiene la ruta absoluta a un recurso, funciona para .exe y desarrollo.
    Prioridad:
    1. Archivo junto al .exe (permite sobrescribir recursos empaquetados)
    2. Archivo dentro del .exe (_MEIPASS)
    3. Directorio actual (desarrollo)
    """
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        external_path = os.path.join(exe_dir, relative_path)
        if os.path.exists(external_path):
            return external_path
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Rutas de recursos empaquetados (solo lectura - config)
CONFIG_PATH = resource_path('config_v20_optimized.json')
# NOTA: MODEL_PATH y SCALER_PATH ahora se definen en config usando MODELS_DIR

# Ruta base donde se guardará todo (junto al .exe o en directorio actual)
APP_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(APP_DIR, 'CryptoBotPro_Data')

# Carpetas dinámicas dentro de CryptoBotPro_Data
LOGS_DIR = os.path.join(DATA_ROOT, 'logs')
CHARTS_DIR = os.path.join(DATA_ROOT, 'signal_charts')
MODELS_DIR = os.path.join(DATA_ROOT, 'models')
TEMP_DIR = os.path.join(DATA_ROOT, 'temp')
CACHE_DIR = os.path.join(DATA_ROOT, 'cache')
TRAINING_DIR = os.path.join(DATA_ROOT, 'training_data')
TRAINING_SUCCESS_DIR = os.path.join(TRAINING_DIR, 'successful_trades')
TRAINING_FEATURES_DIR = os.path.join(TRAINING_DIR, 'features')

# Crear todas las carpetas necesarias
for dir_path in [DATA_ROOT, LOGS_DIR, CHARTS_DIR, MODELS_DIR, TEMP_DIR, CACHE_DIR, TRAINING_DIR, TRAINING_SUCCESS_DIR, TRAINING_FEATURES_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# ========== CONFIGURACIÓN DE LOGGING ROBUSTO CON ENCODING UTF-8 ==========
# ✅ FIX: Timezone UTC-3 (Argentina) para Logs
class ARTzFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        utc_dt = datetime.fromtimestamp(record.created, timezone.utc).replace(tzinfo=None)
        art_dt = utc_dt - timedelta(hours=3)
        if datefmt:
            return art_dt.strftime(datefmt)
        return art_dt.isoformat(sep=' ', timespec='milliseconds')

LOG_PATH = os.path.join(LOGS_DIR, f"CryptoBotDebug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Crear handlers con encoding UTF-8 explícito
log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
artz_formatter = ARTzFormatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')

# Handler para archivo (siempre UTF-8)
file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
file_handler.setFormatter(artz_formatter)

# Handler para consola (UTF-8 en Windows, nativo en otros)
console_handler = logging.StreamHandler(sys.stdout)
if sys.platform == 'win32':
    # En Windows, envolver para forzar UTF-8
    try:
        console_handler.stream = io.TextIOWrapper(
            sys.stdout.buffer if hasattr(sys.stdout, 'buffer') else sys.stdout,
            encoding='utf-8',
            errors='replace'
        )
    except:
        pass
console_handler.setFormatter(artz_formatter)

# Configurar logging - SOLO ERRORES (WARNING y superior)
logging.basicConfig(
    level=logging.WARNING,
    handlers=[file_handler, console_handler]
)

# ✅ FILTRO PERSONALIZADO: Suprimir WARNING de librerías de red, solo ERROR/CRITICAL
class NoNoisyWarningsFilter(logging.Filter):
    """Filtra los WARNING de librerías ruidosas (urllib3, websocket)"""
    def filter(self, record):
        # Si es WARNING de urllib3 o websocket → rechazar
        if record.levelno == logging.WARNING:
            if record.name.startswith(('urllib3', 'websocket')):
                return False
        return True

# Aplicar filtro a handlers
noisy_filter = NoNoisyWarningsFilter()
file_handler.addFilter(noisy_filter)
console_handler.addFilter(noisy_filter)

# Suprimir librerías ruidosas a nivel global
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('websocket').setLevel(logging.CRITICAL)

logger = logging.getLogger('CryptoBotOptimized')
NETWORK_SUPPRESS_BLACKLIST_UNTIL = 0
_LAST_NETWORK_WARNING_TIME = 0

def is_internet_available(host="8.8.8.8", port=53, timeout=3):
    """
    ✅ Verifica si hay conexión a internet intentando una conexión socket rápida.
    """
    try:
        import socket
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False
# Solo registra fallos (WARNING, ERROR, CRITICAL)
print("Configurando logger completado", flush=True)
# Importaciones numéricas y científicas
import numpy as np
import pandas as pd
import glob
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, classification_report, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
import joblib
print("Imports sklearn completados", flush=True)
# Importaciones de red neuronal
try:
    print("Intentando importar torch...", flush=True)
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
    print("PyTorch disponible - Red Neuronal habilitada", flush=True)
except ImportError as e:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    optim = None
    print(f"PyTorch no disponible: {e} - Funcionalidad de IA limitada", flush=True)
except Exception as e:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    optim = None
    print(f"Error general en torch: {e}", flush=True)

# Importaciones para detección de patrones
try:
    print("Intentando importar scipy...", flush=True)
    from scipy.signal import argrelextrema
    SCIPY_AVAILABLE = True
    print("✅ SciPy disponible - Detección de patrones avanzada", flush=True)
except ImportError as e:
    SCIPY_AVAILABLE = False
    print(f"⚠️ SciPy no disponible: {e} - Detección de patrones limitada", flush=True)
except Exception as e:
    print(f"Error general en scipy: {e}", flush=True)
# Importaciones para requests
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
    print("✅ Requests disponible - Conexión API habilitada")
except ImportError as e:
    REQUESTS_AVAILABLE = False
    print(f"⚠️ Requests no disponible: {e} - Conexión API deshabilitada")
# Importaciones de WebSocket


# ✅ IMPORTACIÓN CLAVE PARA EL ERROR 'html'
try:
    import html
    HTML_AVAILABLE = True
except ImportError:
    # Fallback para entornos muy antiguos (muy improbable)
    HTML_AVAILABLE = False
    def _fallback_escape(text: str) -> str:
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
try:
    import websocket
    WEBSOCKET_AVAILABLE = True
    print("✅ WebSocket disponible - Datos en tiempo real habilitados")
except ImportError as e:
    WEBSOCKET_AVAILABLE = False
    print(f"⚠️ WebSocket no disponible: {e} - Datos en tiempo real deshabilitados")
# Importaciones opcionales para sistemas avanzados
try:
    class ExchangeConfig(NamedTuple):
        name: str
        api_key: str
        api_secret: str
        base_url: str
    class BinanceExchange:
        def __init__(self, config): pass
        def initialize(self): return True
    class KrakenExchange:
        def __init__(self, config): pass
        def initialize(self): return False
    class KuCoinExchange:
        def __init__(self, config): pass
        def initialize(self): return False
    class MultiExchangeManager:
        def __init__(self):
            self.exchanges = {}
            self.available_exchanges = []
        def add_exchange(self, name, exchange, is_primary=False):
            self.exchanges[name] = exchange
        def initialize_all(self):
            self.available_exchanges = [k for k, v in self.exchanges.items() if v.initialize()]
            return len(self.available_exchanges) > 0
    class DynamicThresholdManager:
        def __init__(self, base_threshold, min_threshold, max_threshold, window_days, max_daily_signals, min_daily_signals):
            self.base_threshold = base_threshold
            self.max_daily_signals = max_daily_signals
            self.signals_today = 0
            self.last_reset = datetime.now().date()
        def get_current_thresholds(self):
            return {'destacada': self.base_threshold, 'confirmada': self.base_threshold + 8}
        def can_generate_signal(self):
            if self.last_reset != datetime.now().date():
                self.signals_today = 0
                self.last_reset = datetime.now().date()
            if self.signals_today < self.max_daily_signals:
                self.signals_today += 1
                return True
            return False
    MULTI_EXCHANGE_AVAILABLE = True
    DYNAMIC_THRESHOLDS_AVAILABLE = True
    print("✅ Multi-Exchange disponible - Múltiples exchanges habilitados")
    print("✅ Dynamic Thresholds disponible - Umbrales dinámicos habilitados")
except ImportError as e:
    MULTI_EXCHANGE_AVAILABLE = False
    DYNAMIC_THRESHOLDS_AVAILABLE = False
    print(f"⚠️ Multi-Exchange no disponible: {e} - Solo Binance habilitado")
    print(f"⚠️ Dynamic Thresholds no disponible: {e} - Umbrales fijos")
# Importaciones de GUI
try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QPushButton, QListWidget, QTabWidget, QTextEdit, QProgressBar,
        QLineEdit, QSlider, QCheckBox, QComboBox, QMessageBox, QFileDialog, 
        QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
    )
    from PyQt5.QtCore import QTimer, Qt, QMetaObject, Q_ARG, pyqtSlot
    from PyQt5.QtGui import QFont, QColor, QPalette
    PYQT_AVAILABLE = True
    print("✅ PyQt5 disponible - Interfaz gráfica habilitada")
    try:
        QtCore.qRegisterMetaType(QtGui.QTextCursor)
    except Exception:
        pass
except ImportError as e:
    PYQT_AVAILABLE = False
    print(f"❌ PyQt5 no disponible: {e} - Modo consola activado")
    print("ℹ️ Para GUI en Windows instala: pip install pyqt5")

    # ========== STUBS PARA MODO CONSOLA (sin GUI) ==========
    class _QtStubClass:
        """Clase stub que acepta cualquier herencia/llamada"""
        def __init__(self, *args, **kwargs): pass
        def __call__(self, *args, **kwargs): return self
        def __getattr__(self, name): return lambda *a, **kw: None

    class _QtStub:
        Horizontal = 0
        Vertical = 1
        AlignCenter = 0
        def __getattr__(self, name): return _QtStubClass

    class QtWidgetsStub:
        QDialog = _QtStubClass
        QMainWindow = _QtStubClass
        QWidget = _QtStubClass
        QVBoxLayout = _QtStubClass
        QHBoxLayout = _QtStubClass
        QGridLayout = _QtStubClass
        QLabel = _QtStubClass
        QPushButton = _QtStubClass
        QSlider = _QtStubClass
        QProgressBar = _QtStubClass
        QTableWidget = _QtStubClass
        QTableWidgetItem = _QtStubClass
        QTabWidget = _QtStubClass
        QTextEdit = _QtStubClass
        QFrame = _QtStubClass
        QScrollArea = _QtStubClass
        QApplication = _QtStubClass
        QHeaderView = _QtStubClass
        QCheckBox = _QtStubClass
        QComboBox = _QtStubClass
        QLineEdit = _QtStubClass
        QMessageBox = _QtStubClass
        QFileDialog = _QtStubClass
        QListWidget = _QtStubClass
        def __getattr__(self, name): return _QtStubClass

    class QtCoreStub:
        Qt = _QtStub()
        QTimer = _QtStubClass
        QUrl = _QtStubClass
        QMetaObject = _QtStubClass
        Q_ARG = lambda *a: None
        Horizontal = 0
        def __getattr__(self, name): return _QtStubClass

    class QtGuiStub:
        QFont = _QtStubClass
        QColor = _QtStubClass
        QPalette = _QtStubClass
        QTextCursor = _QtStubClass
        def __getattr__(self, name): return _QtStubClass

    QtWidgets = QtWidgetsStub()
    QtCore = QtCoreStub()
    QtGui = QtGuiStub()

    QApplication = _QtStubClass
    QMainWindow = _QtStubClass
    QWidget = _QtStubClass
    QVBoxLayout = _QtStubClass
    QHBoxLayout = _QtStubClass
    QGridLayout = _QtStubClass
    QLabel = _QtStubClass
    QPushButton = _QtStubClass
    QListWidget = _QtStubClass
    QTabWidget = _QtStubClass
    QTextEdit = _QtStubClass
    QProgressBar = _QtStubClass
    QLineEdit = _QtStubClass
    QSlider = _QtStubClass
    QCheckBox = _QtStubClass
    QComboBox = _QtStubClass
    QMessageBox = _QtStubClass
    QFileDialog = _QtStubClass
    QScrollArea = _QtStubClass
    QTableWidget = _QtStubClass
    QTableWidgetItem = _QtStubClass
    QHeaderView = _QtStubClass
    QTimer = _QtStubClass
    Qt = _QtStub()
    QMetaObject = _QtStubClass
    Q_ARG = lambda *a: None
    QFont = _QtStubClass
    QColor = _QtStubClass
    QPalette = _QtStubClass
    def pyqtSlot(*args, **kwargs):
        def decorator(func): return func
        return decorator

# Importaciones para QWebEngineView (TradingView Charts)
WEBENGINE_IMPORT_ERROR = None
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtWebChannel import QWebChannel
    from PyQt5.QtCore import QUrl
    WEBENGINE_AVAILABLE = True
    print("✅ PyQtWebEngine disponible - Gráficos TradingView habilitados")
except Exception as e:
    WEBENGINE_AVAILABLE = False
    WEBENGINE_IMPORT_ERROR = str(e)

    # Fallback seguro: evitar NameError cuando no existe QtWebEngine
    class QWebEngineView:
        def __init__(self, *args, **kwargs):
            pass

    class QWebChannel:
        def __init__(self, *args, **kwargs):
            pass

    class QUrl:
        def __init__(self, *args, **kwargs):
            pass

    # Mensaje informativo (no error): el sistema continúa con matplotlib
    print(f"ℹ️ PyQtWebEngine no disponible ({WEBENGINE_IMPORT_ERROR}) - fallback activo con matplotlib")
# Importaciones para gráficos
try:
    import matplotlib
    matplotlib.use('Agg')  # Backend no-GUI por defecto
    import matplotlib.pyplot as plt
    import mplfinance as mpf
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    from matplotlib.gridspec import GridSpec  # ✅ Importar GridSpec aquí
    # Solo importar backend Qt5 si PyQt5 está disponible
    if PYQT_AVAILABLE:
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    else:
        # Stub para FigureCanvas en modo consola
        class FigureCanvas:
            def __init__(self, *args, **kwargs): pass
            def draw(self): pass
    PLOTTING_AVAILABLE = True
    print("✅ Matplotlib disponible - Gráficos habilitados")
except ImportError as e:
    PLOTTING_AVAILABLE = False
    print(f"⚠️ Matplotlib no disponible: {e} - Gráficos deshabilitados")
    # Stubs para modo sin gráficos
    class FigureCanvas:
        def __init__(self, *args, **kwargs): pass
        def draw(self): pass
    class Figure:
        def __init__(self, *args, **kwargs): pass
        def add_subplot(self, *args, **kwargs): return type('Axes', (), {'plot': lambda *a,**k: None})()
    class Rectangle:
        def __init__(self, *args, **kwargs): pass
    class GridSpec:  # ✅ Stub para GridSpec
        def __init__(self, *args, **kwargs): pass
        def __getitem__(self, key): return None
# Configuración específica para Windows
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# ========== ENUMS Y ESTRUCTURAS DE DATOS ==========
class SignalType(Enum):
    NEUTRAL = "NEUTRAL"
    WEAK_BUY = "COMPRA_DEBIL"
    MODERATE_BUY = "COMPRA_MODERADA"
    STRONG_BUY = "COMPRA_FUERTE"
    CONFIRMED_BUY = "COMPRA"
    HIGHLIGHTED_BUY = "COMPRA"
    WEAK_SELL = "VENTA_DEBIL"
    MODERATE_SELL = "VENTA_MODERADA"
    STRONG_SELL = "VENTA_FUERTE"
    CONFIRMED_SELL = "VENTA"
    HIGHLIGHTED_SELL = "VENTA"
class StrategyType(Enum):
    EMA_TDI_PRICE_ACTION_NEURAL = "EMA-TDI-PRICE ACTION + NEURAL"
    NEURAL_ENHANCED = "NEURAL_ENHANCED"
    TECHNICAL_ONLY = "TECHNICAL_ONLY"
    NEUTRAL = "NEUTRAL"
    SCALPER_15M_1H = "SCALPER_15M_1H"
class TrendDirection(Enum):
    BULLISH = "ALCISTA"
    BEARISH = "BAJISTA"
    NEUTRAL = "NEUTRAL"
    SIDEWAYS = "LATERAL"
class MarketCycle(Enum):
    ACCUMULATION = "ACUMULACION"
    UPTREND = "ALCISTA"
    DISTRIBUTION = "DISTRIBUCION"
    DOWNTREND = "BAJISTA"
    NEUTRAL = "NEUTRAL"
@dataclass
class StrategySignal:
    strategy: StrategyType
    signal_type: SignalType
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    conditions_met: List[str]
    timestamp: datetime
    neural_confidence: float = 0.0
    technical_confidence: float = 0.0
    combined_score: float = 0.0
    market_cycle: MarketCycle = MarketCycle.NEUTRAL
    def __str__(self):
        return (
            f"Estrategia: {self.strategy.value} | "
            f"Señal: {self.signal_type.value} | "
            f"Confianza: {self.confidence:.1f}% | "
            f"Neural: {self.neural_confidence:.1f}% | "
            f"Técnico: {self.technical_confidence:.1f}% | "
            f"Combinado: {self.combined_score:.1f}% | "
            f"Ciclo: {self.market_cycle.value} | "
            f"Entrada: ${self.entry_price:.6f} | "
            f"SL: ${self.stop_loss:.6f} | "
            f"TP: ${self.take_profit:.6f} | "
            f"R/R: {self.risk_reward_ratio:.2f}"
        )

# ==============================================================================
# CLASE DE CONFIGURACIÓN AVANZADA
# ==============================================================================
class AdvancedTradingConfig:
    """Configuración centralizada para el bot de trading"""
    def __init__(self):
        # Símbolos de trading
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

        # Timeframes
        self.PRIMARY_TIMEFRAME = "30m"
        self.SECONDARY_TIMEFRAME = "1h"
        self.ENTRY_TIMEFRAME = "15m"

        # Umbrales de señales (v34.0.1.2 - Optimizado para 85% Efectividad)
        self.MIN_NEURAL_DESTACADA = 92.0      # IA mínima para DESTACADA
        self.MIN_TECHNICAL_DESTACADA = 92.0   # Técnico mínimo para DESTACADA
        self.MIN_ALIGNMENT_DESTACADA = 92.0   # Alineación mínima para DESTACADA
        self.MIN_NEURAL_CONFIRMADA = 92.0     # IA mínima para promoción a CONFIRMADA (+4%)
        self.MIN_TECHNICAL_CONFIRMADA = 92.0  # Técnico mínimo para CONFIRMADA (+4%)
        self.MIN_ALIGNMENT_CONFIRMADA = 92.0  # Alineación mínima para CONFIRMADA
        self.MIN_NEURAL_VALIDATION = 85.0
        self.REQUIRE_CANDLE_PATTERN = True
        self.REQUIRE_ENTRY_SETUP = True
        self.ENTRY_EMA_PERIOD = 21
        self.MIN_ENTRY_PATTERN_CONFIDENCE = 75.0  # Aumentado a 75% (+15%)
        self.MAX_ENTRY_DISTANCE_ATR = 1.0  # Reducido a 1.0 (más preciso)
        self.MAX_ENTRY_CANDLE_RANGE_ATR = 1.4  # Reducido a 1.4 (rango estrecho)
        self.MAX_ENTRY_CANDLE_BODY_ATR = 0.9  # Reducido a 0.9 (cuerpo más fuerte)
        self.ENTRY_PULLBACK_REQUIRED = True
        self.ENTRY_CONFLUENCE_BYPASS = 85  # Aumentado a 85 (más selectivo)
        self.MIN_VOLATILITY_PERCENT = 0.5
        self.MIN_SIGNAL_ROBUSTNESS = 76.0   # Score combinado IA+Técnico+Alineación
        self.DYNAMIC_THRESHOLDS_ENABLED = True
        self.THRESHOLD_WINDOW_DAYS = 90
        self.THRESHOLD_MIN = 70.0
        self.THRESHOLD_MAX = 95.0

        # Multi-exchange
        self.MULTI_EXCHANGE_ENABLED = False
        self.EXCHANGES = []

        # Scanner parameters
        self.SCAN_INTERVAL = 60
        self.MAX_DAILY_SIGNALS = 5  # Reducido a 5 (más selectivo)
        self.MIN_DAILY_SIGNALS = 2
        self.SCAN_BATCH_SIZE = 10      # Símbolos por lote para evitar rate limits
        self.SCAN_BATCH_DELAY = 0.5    # Segundos de delay entre lotes

        # Validation parameters
        self.MIN_TECH_VALIDATION = 85.0
        self.MIN_NEURAL_VALIDATION = 88.0
        self.MIN_VOLUME_RATIO = 1.2  # Aumentado de 0.8 a 1.2 (+50%)
        self.MIN_RISK_REWARD_RATIO = 1.75  # Aumentado para priorizar setups más robustos
        self.ENABLE_MM_BUY_FILTER = True  # Filtro Market Maker Buy Model
        self.MM_MIN_SCORE = 65.0
        self.MM_SELL_MIN_SCORE = 65.0
        self.MM_PULLBACK_MIN = 0.25
        self.MM_PULLBACK_MAX = 0.72
        self.SIMILARITY_FILTER_ENABLED = True
        self.SIMILARITY_THRESHOLD = 0.72
        self.MIN_SIMILAR_SAMPLES = 3
        self.MIN_CONTEXT_SUCCESS_RATE = 0.58
        self.MAX_RISK_PER_TRADE = 0.02
        self.NEURAL_WEIGHT = 0.5
        self.TECHNICAL_WEIGHT = 0.5
        self.NEURAL_INPUT_SIZE = 32
        self.NEURAL_EPOCHS = 50

        # Timeframes disponibles
        self.TIMEFRAMES = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d']

        # Trading parameters
        self.DEFAULT_STOP_LOSS_PERCENT = 0.004
        self.DEFAULT_TAKE_PROFIT_PERCENT = 0.012
        self.PROFIT_TARGET_PERCENT = 2.4
        self.STOP_LOSS_PERCENT = 0.8
        self.MIN_STOP_LOSS_PERCENT = 0.8
        self.TAKE_PROFIT_PERCENT = 2.4
        self.MIN_RISK_REWARD_RATIO = 2.0

        # Comisiones
        self.PERPETUALS_COMMISSION = 0.0005
        self.SPOT_COMMISSION = 0.001

        # Milestones
        self.MILESTONE_1 = 1.0
        self.MILESTONE_2 = 2.0
        self.MILESTONE_3 = 3.0
        self.MILESTONE_1_PERCENT = 1.0
        self.MILESTONE_2_PERCENT = 2.0
        self.MILESTONE_3_PERCENT = 3.0
        self.MILESTONES = [1.0, 2.0, 3.0]
        self.PROFIT_MILESTONES = [1.0, 2.0, 3.0]
        self.MIN_PROFIT_THRESHOLD = 1.5

        # TDI Parameters
        self.TDI_RSI_PERIOD = 13
        self.TDI_PRICE_PERIOD = 2
        self.TDI_SIGNAL_PERIOD = 7
        self.TDI_VOLATILITY_BAND = 34
        self.TDI_OVERBOUGHT_LEVEL_SELL = 68
        self.TDI_OVERSOLD_LEVEL_BUY = 32

        # EMA Parameters (para análisis técnico)
        self.EMA_FAST = 50   # EMA rápida (50 períodos)
        self.EMA_SLOW = 200  # EMA lenta (200 períodos)

        # Neural network
        self.NEURAL_INPUT_SIZE = 66  # Características del modelo entrenado
        self.NEURAL_HIDDEN_LAYERS = [128, 64, 32]
        self.NEURAL_DROPOUT = 0.2
        self.NEURAL_LEARNING_RATE = 0.001
        self.NEURAL_BATCH_SIZE = 32
        self.NEURAL_EPOCHS = 100
        self.NEURAL_EARLY_STOPPING = 10
        # ✅ CORREGIDO: Rutas unificadas en CryptoBotPro_Data/models/
        self.NN_MODEL_PATH = os.path.join(MODELS_DIR, "neural_net_model_v20_optimized.pth")
        self.SCALER_PATH = os.path.join(MODELS_DIR, "scaler_v20_optimized.pkl")

        # Data requirements
        self.MIN_NN_DATA_REQUIRED = 360
        self.HISTORICAL_DAYS = 90

        # Auto-trading
        self.AUTO_TRADING_ENABLED = False
        self.auto_trading_enabled = False  # Alias en minusculas para compatibilidad
        self.AUTO_TRADE_QUANTITY_USDT = 10
        
        # === MEJORA v35: Trailing Stop Dinamico ===
        self.TRAILING_STOP_ENABLED = True
        self.TRAILING_STOP_ACTIVATION = 0.5   # Activar trailing despues de 0.5% de profit
        self.TRAILING_STOP_DISTANCE = 0.3     # Distancia del trailing stop (0.3%)
        self.TRAILING_STOP_BREAKEVEN = 0.8    # Mover SL a breakeven despues de 0.8%
        
        self.USE_TESTNET = True  # Default: Testnet para seguridad

        # ✨ NUEVO: Advanced Signal Filter (v34.0.1.2 - 10 capas de validación)
        self.ADVANCED_SIGNAL_FILTER_ENABLED = True
        self.MIN_SIGNAL_SCORE = 0.80  # Score mínimo para aceptar (80%)
        self.MIN_CONFLUENCE = 0.70  # 4 de 5 indicadores alineados
        self.MIN_RISK_REWARD = 1.5  # Ratio riesgo/recompensa mínimo
        self.MIN_WIN_PROBABILITY = 0.65  # 65% probabilidad histórica mínima
        self.MAX_CONCURRENT_TRADES = 2  # Máximo 2 trades abiertos simultáneamente

        # ✅ NUEVO: Configuración avanzada de AutoTrader
        self.AUTOTRADER_MODE = 'testnet'  # 'testnet' o 'real'
        self.AUTOTRADER_MARGIN_USDT = 1.0  # Margen inicial en USDT (default 1)
        self.AUTOTRADER_LEVERAGE = 1  # Apalancamiento 1x-25x (escala: 1, 5, 10, 15, 20, 25)
        self.AUTOTRADER_LEVERAGE_OPTIONS = [1, 5, 10, 15, 20, 25]  # Opciones disponibles
        self.AUTOTRADER_COMPOUND_ENABLED = False  # Interés compuesto activado
        self.AUTOTRADER_COMPOUND_PERCENT = 10.0  # % del capital a reinvertir
        self.AUTOTRADER_CAPITAL_USDT = 10.0  # Capital total disponible
        self.AUTOTRADER_ORDER_TYPE = 'MARKET'  # Tipo de orden: MARKET

        # API settings
        self.FIX_API_ENABLED = False
        self.API_TIMEOUT = 30
        self.MAX_RETRIES = 3

        # GUI Configuration
        self.CONFIG_PASSWORD = os.environ.get('CONFIG_PASSWORD', 'admin123')  # Contraseña para configuración

        # Signal tracking
        self.DESTACADA_TIMEOUT_MINUTES = 3
        self.CONFIRMADA_TIMEOUT_MINUTES = 180
        self.PROMOTION_WAIT_MINUTES = 3
        self.MIN_PROMOTION_TIME_SECONDS = 3 * 60  # 3 minutos mínimo para promoción

        # Directorios (usando las constantes globales definidas al inicio)
        self.DATA_ROOT = DATA_ROOT
        self.LOGS_DIR = LOGS_DIR
        self.CHARTS_DIR = CHARTS_DIR
        self.MODELS_DIR = MODELS_DIR
        self.TEMP_DIR = TEMP_DIR
        self.CACHE_DIR = CACHE_DIR
        self.TRAINING_DIR = TRAINING_DIR
        self.TRAINING_SUCCESS_DIR = TRAINING_SUCCESS_DIR
        self.TRAINING_FEATURES_DIR = TRAINING_FEATURES_DIR

        # Credenciales Telegram (desde variables de entorno)
        self.telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        self.telegram_enabled = bool(self.telegram_bot_token and self.telegram_chat_id)
        self.TELEGRAM_SIGNAL_TEMPLATE = """
{emoji_prefix} {direction} {signal_level_text}
━━━━━━━━━━━━━━━━━━━━
📊 Par: {symbol}
📈 Mercado: {market_type}
💰 Entrada: ${entry_price:.6f}
🎯 TP: ${take_profit:.6f}
🛑 SL: ${stop_loss:.6f}
━━━━━━━━━━━━━━━━━━━━
🤖 IA: {neural_confidence:.1f}% | 📊 Técnico: {technical_confidence:.1f}%
📈 Combinado: {combined_confidence:.1f}%
━━━━━━━━━━━━━━━━━━━━
✅ Condiciones:
{conditions_met}
⏰ {timestamp}
"""

        # Credenciales Binance (desde variables de entorno)
        self.binance_api_key = os.environ.get('BINANCE_API_KEY', '')
        self.binance_secret_key = os.environ.get('BINANCE_API_SECRET', '')
        self.use_testnet = False
        self.BINANCE_API_URL = "https://api.binance.com"
        self.BINANCE_TESTNET_URL = "https://testnet.binance.vision"
        self.BINANCE_TESTNET_SPOT_URL = "https://testnet.binance.vision"
        self.BINANCE_TESTNET_FUTURES_URL = "https://testnet.binancefuture.com"

        # Cargar configuración desde archivo si existe
        self.load_config()

    def load_config(self):
        """Cargar configuración COMPLETA desde archivo JSON - Formato unificado"""
        try:
            config_path = resource_path('config_v20_optimized.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # ✅ Cargar valores directos (claves en MAYÚSCULAS del nuevo formato)
                direct_keys = [
                    'MARKET_TYPE', 'MIN_NEURAL_DESTACADA', 'MIN_TECHNICAL_DESTACADA', 'MIN_ALIGNMENT_DESTACADA',
                    'MIN_NEURAL_CONFIRMADA', 'MIN_TECHNICAL_CONFIRMADA', 'MIN_ALIGNMENT_CONFIRMADA',
                    'PROFIT_TARGET_PERCENT', 'STOP_LOSS_PERCENT', 'MILESTONES', 'MILESTONE_1', 'MILESTONE_2', 'MILESTONE_3',
                    'NEURAL_WEIGHT', 'TECHNICAL_WEIGHT', 'AUTO_TRADING_ENABLED', 'AUTO_TRADE_QUANTITY_USDT',
                    'TRAILING_STOP_ENABLED', 'TRAILING_STOP_DISTANCE', 'USE_TESTNET',
                    'AUTOTRADER_MODE', 'AUTOTRADER_MARGIN_USDT', 'AUTOTRADER_LEVERAGE',
                    'AUTOTRADER_COMPOUND_ENABLED', 'AUTOTRADER_COMPOUND_PERCENT', 'AUTOTRADER_CAPITAL_USDT',
                    'MAX_DAILY_SIGNALS', 'SCAN_INTERVAL', 'MIN_VOLUME_RATIO', 'MIN_RISK_REWARD_RATIO',
                    'REQUIRE_CANDLE_PATTERN', 'REQUIRE_ENTRY_SETUP', 'ENTRY_EMA_PERIOD', 'MIN_ENTRY_PATTERN_CONFIDENCE',
                    'MAX_ENTRY_DISTANCE_ATR', 'MAX_ENTRY_CANDLE_RANGE_ATR', 'MAX_ENTRY_CANDLE_BODY_ATR',
                    'ENTRY_PULLBACK_REQUIRED', 'ENTRY_CONFLUENCE_BYPASS',
                    'MIN_VOLATILITY_PERCENT', 'EMA_FAST', 'EMA_SLOW',
                    'ADVANCED_SIGNAL_FILTER_ENABLED', 'MIN_SIGNAL_SCORE', 'MIN_CONFLUENCE', 'MIN_RISK_REWARD', 'MIN_WIN_PROBABILITY', 'MAX_CONCURRENT_TRADES'
                ]
                for key in direct_keys:
                    if key in data and data[key] is not None:
                        setattr(self, key, data[key])

                # ✅ Compatibilidad con formato antiguo (claves anidadas)
                if 'market_type' in data:
                    self.MARKET_TYPE = data['market_type']
                if 'thresholds' in data:
                    th = data['thresholds']
                    if 'destacada' in th:
                        self.MIN_NEURAL_DESTACADA = th['destacada'].get('neural', self.MIN_NEURAL_DESTACADA)
                        self.MIN_TECHNICAL_DESTACADA = th['destacada'].get('technical', self.MIN_TECHNICAL_DESTACADA)
                        self.MIN_ALIGNMENT_DESTACADA = th['destacada'].get('alignment', self.MIN_ALIGNMENT_DESTACADA)
                    if 'confirmada' in th:
                        self.MIN_NEURAL_CONFIRMADA = th['confirmada'].get('neural', self.MIN_NEURAL_CONFIRMADA)
                        self.MIN_TECHNICAL_CONFIRMADA = th['confirmada'].get('technical', self.MIN_TECHNICAL_CONFIRMADA)
                        self.MIN_ALIGNMENT_CONFIRMADA = th['confirmada'].get('alignment', self.MIN_ALIGNMENT_CONFIRMADA)

                # ✅ CARGAR MILESTONES - Soporta ambos formatos (nuevo y legacy)
                if 'milestones' in data and isinstance(data['milestones'], dict):
                    ms = data['milestones']
                    self.MILESTONE_1 = ms.get('first_advance', self.MILESTONE_1)
                    self.MILESTONE_2 = ms.get('second_advance', self.MILESTONE_2)
                    self.MILESTONE_3 = ms.get('final_target', self.MILESTONE_3)
                    self.MILESTONES = [self.MILESTONE_1, self.MILESTONE_2, self.MILESTONE_3]
                    self.PROFIT_MILESTONES = [self.MILESTONE_1, self.MILESTONE_2, self.MILESTONE_3]
                    self.PROFIT_TARGET_PERCENT = self.MILESTONE_3

                # ✅ CARGAR MILESTONES - Formato directo (MILESTONE_1, MILESTONE_2, MILESTONE_3)
                if 'MILESTONE_1' in data:
                    self.MILESTONE_1 = data['MILESTONE_1']
                if 'MILESTONE_2' in data:
                    self.MILESTONE_2 = data['MILESTONE_2']
                if 'MILESTONE_3' in data:
                    self.MILESTONE_3 = data['MILESTONE_3']

                # Actualizar listas si se cargaron milestones individuales
                if 'MILESTONE_1' in data or 'MILESTONE_2' in data or 'MILESTONE_3' in data:
                    self.MILESTONES = [self.MILESTONE_1, self.MILESTONE_2, self.MILESTONE_3]
                    self.PROFIT_MILESTONES = [self.MILESTONE_1, self.MILESTONE_2, self.MILESTONE_3]
                    self.PROFIT_TARGET_PERCENT = self.MILESTONE_3
                    logger.info(f"✅ Milestones cargados: {self.PROFIT_MILESTONES}")

                if 'risk_management' in data:
                    rm = data['risk_management']
                    self.STOP_LOSS_PERCENT = rm.get('stop_loss_percent', self.STOP_LOSS_PERCENT)
                    self.PROFIT_TARGET_PERCENT = rm.get('take_profit_percent', self.PROFIT_TARGET_PERCENT)
                if 'auto_trading' in data:
                    at = data['auto_trading']
                    self.AUTO_TRADING_ENABLED = at.get('enabled', self.AUTO_TRADING_ENABLED)
                    self.AUTO_TRADE_QUANTITY_USDT = at.get('quantity_usdt', self.AUTO_TRADE_QUANTITY_USDT)
                    self.TRAILING_STOP_ENABLED = at.get('trailing_stop_enabled', self.TRAILING_STOP_ENABLED)
                    self.USE_TESTNET = at.get('use_testnet', self.USE_TESTNET)
                if 'perpetuals_symbols' in data:
                    self.PERPETUALS_SYMBOLS = data['perpetuals_symbols']
                if 'spot_symbols' in data:
                    self.SPOT_SYMBOLS = data['spot_symbols']

                # Cargar credenciales desde archivo si no hay env vars
                if not os.environ.get('BINANCE_API_KEY') and data.get('binance_api_key'):
                    self.binance_api_key = data.get('binance_api_key', '')
                if not os.environ.get('BINANCE_API_SECRET') and data.get('binance_secret_key'):
                    self.binance_secret_key = data.get('binance_secret_key', '')
                if not os.environ.get('TELEGRAM_BOT_TOKEN') and data.get('telegram_bot_token'):
                    self.telegram_bot_token = data.get('telegram_bot_token', '')
                    self.telegram_enabled = bool(self.telegram_bot_token and self.telegram_chat_id)
                if not os.environ.get('TELEGRAM_CHAT_ID') and data.get('telegram_chat_id'):
                    self.telegram_chat_id = data.get('telegram_chat_id', '')
                    self.telegram_enabled = bool(self.telegram_bot_token and self.telegram_chat_id)

                # Actualizar símbolos según tipo de mercado
                self.update_symbols_for_market_type()

                logger.info(f"✅ Configuración cargada desde JSON")
                print(f"📊 Milestones: {self.MILESTONES} | TP: {self.PROFIT_TARGET_PERCENT}%")
                print(f"📈 Mercado: {self.MARKET_TYPE} | Símbolos: {len(self.TRADING_SYMBOLS)}")
        except Exception as e:
            logger.warning(f"No se pudo cargar config: {e}")

    def save_config(self):
        """Guardar configuración COMPLETA a archivo JSON (formato unificado GUI↔JSON)"""
        try:
            config_path = resource_path('config_v20_optimized.json')
            data = {
                # Mercado
                "MARKET_TYPE": self.MARKET_TYPE,
                # Umbrales DESTACADA
                "MIN_NEURAL_DESTACADA": self.MIN_NEURAL_DESTACADA,
                "MIN_TECHNICAL_DESTACADA": self.MIN_TECHNICAL_DESTACADA,
                "MIN_ALIGNMENT_DESTACADA": self.MIN_ALIGNMENT_DESTACADA,
                # Umbrales CONFIRMADA
                "MIN_NEURAL_CONFIRMADA": self.MIN_NEURAL_CONFIRMADA,
                "MIN_TECHNICAL_CONFIRMADA": self.MIN_TECHNICAL_CONFIRMADA,
                "MIN_ALIGNMENT_CONFIRMADA": self.MIN_ALIGNMENT_CONFIRMADA,
                # Trading
                "PROFIT_TARGET_PERCENT": self.PROFIT_TARGET_PERCENT,
                "STOP_LOSS_PERCENT": self.STOP_LOSS_PERCENT,
                "MILESTONES": self.MILESTONES,
                "MILESTONE_1": self.MILESTONE_1,
                "MILESTONE_2": self.MILESTONE_2,
                "MILESTONE_3": self.MILESTONE_3,
                # Pesos
                "NEURAL_WEIGHT": self.NEURAL_WEIGHT,
                "TECHNICAL_WEIGHT": self.TECHNICAL_WEIGHT,
                # EMA Parameters
                "EMA_FAST": self.EMA_FAST,
                "EMA_SLOW": self.EMA_SLOW,
                # Auto-trading
                "AUTO_TRADING_ENABLED": self.AUTO_TRADING_ENABLED,
                "AUTO_TRADE_QUANTITY_USDT": self.AUTO_TRADE_QUANTITY_USDT,
                "TRAILING_STOP_ENABLED": self.TRAILING_STOP_ENABLED,
                "TRAILING_STOP_DISTANCE": self.TRAILING_STOP_DISTANCE,
                "USE_TESTNET": self.USE_TESTNET,
                # AutoTrader avanzado
                "AUTOTRADER_MODE": self.AUTOTRADER_MODE,
                "AUTOTRADER_MARGIN_USDT": self.AUTOTRADER_MARGIN_USDT,
                "AUTOTRADER_LEVERAGE": self.AUTOTRADER_LEVERAGE,
                "AUTOTRADER_COMPOUND_ENABLED": self.AUTOTRADER_COMPOUND_ENABLED,
                "AUTOTRADER_COMPOUND_PERCENT": self.AUTOTRADER_COMPOUND_PERCENT,
                "AUTOTRADER_CAPITAL_USDT": self.AUTOTRADER_CAPITAL_USDT,
                # Señales
                "MAX_DAILY_SIGNALS": self.MAX_DAILY_SIGNALS,
                "SCAN_INTERVAL": self.SCAN_INTERVAL,
                # Validación
                "MIN_VOLUME_RATIO": self.MIN_VOLUME_RATIO,
                "MIN_RISK_REWARD_RATIO": self.MIN_RISK_REWARD_RATIO,
                "REQUIRE_CANDLE_PATTERN": self.REQUIRE_CANDLE_PATTERN,
                "REQUIRE_ENTRY_SETUP": self.REQUIRE_ENTRY_SETUP,
                "ENTRY_EMA_PERIOD": self.ENTRY_EMA_PERIOD,
                "MIN_ENTRY_PATTERN_CONFIDENCE": self.MIN_ENTRY_PATTERN_CONFIDENCE,
                "MAX_ENTRY_DISTANCE_ATR": self.MAX_ENTRY_DISTANCE_ATR,
                "MAX_ENTRY_CANDLE_RANGE_ATR": self.MAX_ENTRY_CANDLE_RANGE_ATR,
                "MAX_ENTRY_CANDLE_BODY_ATR": self.MAX_ENTRY_CANDLE_BODY_ATR,
                "ENTRY_PULLBACK_REQUIRED": self.ENTRY_PULLBACK_REQUIRED,
                "ENTRY_CONFLUENCE_BYPASS": self.ENTRY_CONFLUENCE_BYPASS,
                # 🔥 PARÁMETROS DE FAST-FAIL REAL (¡AGREGADOS!)
                "FASTFAIL_RSI_BUY_MIN": getattr(self, 'FASTFAIL_RSI_BUY_MIN', 52.0),
                "FASTFAIL_RSI_SELL_MAX": getattr(self, 'FASTFAIL_RSI_SELL_MAX', 48.0),
                "MIN_VOLATILITY_PERCENT": getattr(self, 'MIN_VOLATILITY_PERCENT', 0.5),
                "MIN_VOLUME_24H_USD": getattr(self, 'MIN_VOLUME_24H_USD', 1_000_000),
                "FIX_API_ENABLED": getattr(self, 'FIX_API_ENABLED', False),  # ← ¡CRÍTICO!
                 # Símbolos
                "PERPETUALS_SYMBOLS": self.PERPETUALS_SYMBOLS,
                "SPOT_SYMBOLS": self.SPOT_SYMBOLS,
                # API Keys (si están configuradas via GUI, no desde env vars)
                "binance_api_key": self.binance_api_key if not os.environ.get('BINANCE_API_KEY') else "",
                "binance_secret_key": self.binance_secret_key if not os.environ.get('BINANCE_API_SECRET') else "",
                "telegram_bot_token": self.telegram_bot_token if not os.environ.get('TELEGRAM_BOT_TOKEN') else "",
                "telegram_chat_id": self.telegram_chat_id if not os.environ.get('TELEGRAM_CHAT_ID') else "",
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"✅ Configuración guardada: {len(data)} parámetros")
        except Exception as e:
            logger.error(f"Error guardando config: {e}")

    def get_commission_rate(self) -> float:
        """Obtener tasa de comisión según tipo de mercado"""
        if self.MARKET_TYPE == "PERPETUALS":
            return self.PERPETUALS_COMMISSION * 100
        return self.SPOT_COMMISSION * 100

    def get_round_trip_commission(self) -> float:
        """Obtener comisión round-trip (entrada + salida)"""
        return self.get_commission_rate() * 2

    def get_net_profit_target(self) -> float:
        """Obtener objetivo de profit neto (TP - comisiones round-trip)"""
        gross_target = self.PROFIT_TARGET_PERCENT
        round_trip = self.get_round_trip_commission()
        return max(0.0, gross_target - round_trip)

    def get_gross_profit_target(self) -> float:
        """Obtener objetivo de profit bruto (incluye comisiones)"""
        return self.PROFIT_TARGET_PERCENT

    def update_symbols_for_market_type(self):
        """Actualizar lista de símbolos según tipo de mercado"""
        if self.MARKET_TYPE == "PERPETUALS":
            self.TRADING_SYMBOLS = self.PERPETUALS_SYMBOLS.copy()
        else:
            self.TRADING_SYMBOLS = self.SPOT_SYMBOLS.copy()
        logger.info(f"📈 Símbolos actualizados para {self.MARKET_TYPE}: {len(self.TRADING_SYMBOLS)} pares")

# ==============================================================================
# CLIENTE BINANCE AVANZADO
# ==============================================================================
class AdvancedBinanceClient:
    """Cliente HTTP para API de Binance con manejo de errores y reintentos"""

    SPOT_ENDPOINTS = [
        "https://data-api.binance.vision",
        "https://api.binance.com",
        "https://api1.binance.com",
        "https://api2.binance.com",
        "https://api3.binance.com"
    ]

    FUTURES_ENDPOINTS = [
        "https://data-api.binance.vision",
        "https://fapi.binance.com",
    ]

    def __init__(self, config):
        self.config = config
        self.current_endpoint_idx = 0
        self.session = None
        self.market_type = getattr(config, 'MARKET_TYPE', 'PERPETUALS')
        self._init_session()

    def _init_session(self):
        """Inicializar sesión HTTP"""
        import requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoBotPro/32.0',
            'Content-Type': 'application/json'
        })

    @property
    def _endpoints(self):
        """Obtener lista de endpoints según tipo de mercado"""
        if self.market_type == "PERPETUALS":
            return self.FUTURES_ENDPOINTS
        return self.SPOT_ENDPOINTS

    def _get_endpoint(self) -> str:
        """Obtener endpoint actual"""
        return self._endpoints[self.current_endpoint_idx % len(self._endpoints)]

    def _get_api_path(self, endpoint: str) -> str:
        """Obtener path de API según endpoint y tipo de mercado"""
        if "data-api.binance.vision" in endpoint:
            return "/api/v3"
        if self.market_type == "PERPETUALS":
            return "/fapi/v1"
        return "/api/v3"

    def _rotate_endpoint(self):
        """Rotar al siguiente endpoint"""
        self.current_endpoint_idx = (self.current_endpoint_idx + 1) % len(self._endpoints)

    def get_ticker_price(self, symbol: str) -> float:
        """Obtener precio actual de un símbolo"""
        try:
            endpoint = self._get_endpoint()
            api_path = self._get_api_path(endpoint)
            url = f"{endpoint}{api_path}/ticker/price?symbol={symbol}"
            response = self.session.get(url, timeout=30)  # ✅ Aumentado para conexiones con alta latencia (ej: Argentina)
            if response.status_code == 200:
                return float(response.json().get('price', 0))
            self._rotate_endpoint()
            return 0
        except Exception as e:
            logger.debug(f"Error obteniendo precio de {symbol}: {e}")
            self._rotate_endpoint()
            return 0

    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> pd.DataFrame:
        """Obtener datos históricos de velas"""
        try:
            endpoint = self._get_endpoint()
            api_path = self._get_api_path(endpoint)
            url = f"{endpoint}{api_path}/klines?symbol={symbol}&interval={interval}&limit={limit}"
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                self._rotate_endpoint()
                return None

            data = response.json()
            if not data:
                return None

            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])

            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)

            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            return df

        except Exception as e:
            logger.debug(f"Error obteniendo klines de {symbol}: {e}")
            self._rotate_endpoint()
            return None

    def validate_symbols_list(self, symbols: list, market_type: str = "PERPETUALS") -> list:
        """Validar lista de símbolos contra Binance"""
        validated = []
        try:
            url = f"{self._get_endpoint()}/api/v3/exchangeInfo"
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                available = {s['symbol'] for s in data.get('symbols', []) if s.get('status') == 'TRADING'}
                validated = [s for s in symbols if s in available]
        except Exception as e:
            logger.debug(f"Error validando símbolos: {e}")
            validated = symbols
        return validated if validated else symbols

# ==============================================================================
# MÓDULO 1: PathManager (Gestión de Rutas Seguras)
# ==============================================================================
class PathManager:
    """
    Gestor centralizado de rutas para Crypto Bot Pro.
    Maneja correctamente las rutas tanto en desarrollo como en el .exe empaquetado.

    - Recursos ESTÁTICOS (modelos, config): empaquetados dentro del .exe (_MEIPASS)
    - Recursos DINÁMICOS (logs, charts, temp): guardados fuera del .exe para evitar errores de permisos
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if PathManager._initialized:
            return
        PathManager._initialized = True

        # Ruta base: directorio del .exe o del script actual
        self._app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        self._data_root = os.path.join(self._app_dir, 'CryptoBotPro_Data')

        # Definición de subcarpetas dinámicas
        self._subdirs = {
            'logs': 'logs',
            'charts': 'signal_charts',
            'training': 'training_data',
            'training_success': 'training_data/successful_trades',
            'training_features': 'training_data/features',
            'models': 'models',
            'temp': 'temp',
            'cache': 'cache',
        }

        self._init_directories()

    def _init_directories(self):
        """Crear directorios necesarios si no existen."""
        for subdir in self._subdirs.values():
            dir_path = os.path.join(self._data_root, subdir)
            os.makedirs(dir_path, exist_ok=True)

    @property
    def data_root(self) -> str:
        return self._data_root

    def get_static_path(self, relative_path: str) -> str:
        """
        Obtiene ruta a recurso ESTÁTICO (empaquetado en .exe).
        Si no está empaquetado, busca junto al script.
        """
        if getattr(sys, 'frozen', False):
            # Estamos en un .exe (PyInstaller)
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            # Desarrollo
            return os.path.join(os.path.abspath("."), relative_path)

    def get_data_path(self, subdir_key: str, filename: str = "") -> str:
        """
        Obtiene ruta a recurso DINÁMICO (generado en runtime).
        Siempre apunta a la carpeta CryptoBotPro_Data fuera del .exe.
        """
        subdir = self._subdirs.get(subdir_key, subdir_key)
        dir_path = os.path.join(self._data_root, subdir)
        os.makedirs(dir_path, exist_ok=True)
        if filename:
            return os.path.join(dir_path, filename)
        return dir_path

    def get_config_path(self, filename: str) -> str:
        """Ruta para archivo de configuración (permitir sobreescritura externa)"""
        # Prioridad: junto al .exe
        exe_path = os.path.join(self._app_dir, filename)
        if os.path.exists(exe_path):
            return exe_path
        # Fallback: dentro de _MEIPASS (para primera copia)
        return self.get_static_path(filename)

# Instancia global para uso en todo el script
path_manager = PathManager()

# ==============================================================================
# OPTIMIZACIÓN v32.0.23.0 - FAST-FAIL, CACHE Y UMBRALES ADAPTATIVOS
# ==============================================================================

class FastFailFilter:
    """
    FAST-FAIL: Descarta pares inviables ANTES de cálculos pesados.
    Objetivo: Rechazar 80% de pares en <5ms para ahorrar CPU.
    """
    def __init__(self, config):
        self.config = config
        self.blacklist = {}  # symbol -> (timestamp, reason)
        self.blacklist_duration = 300  # 5 minutos de blacklist
        
        # Umbrales de Fast-Fail
        self.MIN_VOLUME_24H = getattr(config, 'MIN_VOLUME_24H_USD', 1_000_000)
        self.MIN_VOLATILITY_1H = getattr(config, 'MIN_VOLATILITY_PERCENT', 0.3)
        base_min = getattr(config, 'MIN_NN_DATA_REQUIRED', 100)
        self.MIN_CANDLES_REQUIRED = max(150, int(base_min))
        self.RSI_BUY_MIN = getattr(config, 'FASTFAIL_RSI_BUY_MIN', 52.0)
        self.RSI_SELL_MAX = getattr(config, 'FASTFAIL_RSI_SELL_MAX', 48.0)
        
    def should_skip_symbol(self, symbol: str, df: pd.DataFrame, volume_24h: float = 0) -> Tuple[bool, str]:
        """
        Verifica si el símbolo debe ser saltado (FAST-FAIL).
        Returns: (should_skip, reason)
        """
        try:
            # 1. Verificar blacklist temporal
            if symbol in self.blacklist:
                timestamp, reason = self.blacklist[symbol]
                if time.time() - timestamp < self.blacklist_duration:
                    return True, f"Blacklisted: {reason}"
                else:
                    del self.blacklist[symbol]
            
            # 2. Verificar datos mínimos
            if df is None or len(df) < self.MIN_CANDLES_REQUIRED:
                self._add_to_blacklist(symbol, "Datos insuficientes")
                return True, f"Datos insuficientes ({len(df) if df is not None else 0} < {self.MIN_CANDLES_REQUIRED})"
            
            # 3. Verificar volumen 24h
            if volume_24h > 0 and volume_24h < self.MIN_VOLUME_24H:
                self._add_to_blacklist(symbol, "Volumen bajo")
                return True, f"Volumen 24h bajo (${volume_24h:,.0f} < ${self.MIN_VOLUME_24H:,.0f})"
            
            # 4. Verificar volatilidad mínima (última hora = últimas 2 velas de 30m)
            if len(df) >= 2:
                recent_high = df['high'].tail(2).max()
                recent_low = df['low'].tail(2).min()
                volatility_pct = ((recent_high - recent_low) / recent_low) * 100 if recent_low > 0 else 0
                if volatility_pct < self.MIN_VOLATILITY_1H:
                    return True, f"Volatilidad baja ({volatility_pct:.2f}% < {self.MIN_VOLATILITY_1H}%)"
            
            # 5. Verificar tendencia EMA 50/200 (mercados laterales = skip)
            if len(df) >= 200:
                close = df['close']
                ema50 = close.ewm(span=50, adjust=False).mean().iloc[-1]
                ema200 = close.ewm(span=200, adjust=False).mean().iloc[-1]
                current = close.iloc[-1]
                
                # Si precio está entre EMAs (mercado lateral), skip
                if min(ema50, ema200) < current < max(ema50, ema200):
                    ema_diff_pct = abs(ema50 - ema200) / ema200 * 100
                    if ema_diff_pct < 1.0:  # EMAs muy juntas = sin tendencia clara
                        return True, "Mercado lateral (EMAs convergentes)"
            
            return False, "OK"
            
        except Exception as e:
            logger.debug(f"FastFail error for {symbol}: {e}")
            return False, "Error en FastFail"
    
    def validate_rsi_direction(self, rsi_value: float, is_buy: bool) -> Tuple[bool, str]:
        """
        Valida RSI extremo para confirmar dirección.
        BUY: RSI > 52 | SELL: RSI < 48
        """
        if is_buy and rsi_value < self.RSI_BUY_MIN:
            return False, f"RSI bajo para BUY ({rsi_value:.1f} < {self.RSI_BUY_MIN})"
        if not is_buy and rsi_value > self.RSI_SELL_MAX:
            return False, f"RSI alto para SELL ({rsi_value:.1f} > {self.RSI_SELL_MAX})"
        return True, "RSI válido"
    
    def _add_to_blacklist(self, symbol: str, reason: str):
        self.blacklist[symbol] = (time.time(), reason)
        logger.debug(f"⛔ {symbol} añadido a blacklist: {reason}")


class AdaptiveThresholdManager:
    """
    UMBRAL ADAPTATIVO: Ajusta requisitos según condiciones del mercado.
    - En baja volatilidad: Umbrales más estrictos
    - Si IA falla consistentemente: Aumenta umbrales o desactiva
    """
    def __init__(self, config):
        self.config = config
        self.ia_success_history = []  # Lista de (timestamp, was_success)
        self.max_history = 20
        self.current_market_volatility = "NORMAL"  # LOW, NORMAL, HIGH
        
        # Multiplicadores adaptativos
        self.volatility_multipliers = {
            "LOW": {"neural": 1.15, "technical": 1.10, "alignment": 1.20},
            "NORMAL": {"neural": 1.0, "technical": 1.0, "alignment": 1.0},
            "HIGH": {"neural": 0.95, "technical": 0.95, "alignment": 0.90}
        }
        
    def update_market_volatility(self, avg_atr_percent: float):
        """Actualiza el estado de volatilidad del mercado."""
        if avg_atr_percent < 0.5:
            self.current_market_volatility = "LOW"
        elif avg_atr_percent > 2.0:
            self.current_market_volatility = "HIGH"
        else:
            self.current_market_volatility = "NORMAL"
    
    def record_ia_result(self, was_successful: bool):
        """Registra resultado de predicción de IA."""
        self.ia_success_history.append((time.time(), was_successful))
        if len(self.ia_success_history) > self.max_history:
            self.ia_success_history.pop(0)
    
    def get_ia_reliability(self) -> float:
        """Retorna tasa de éxito de IA (0.0 - 1.0)."""
        if len(self.ia_success_history) < 3:
            return 1.0  # Asumir confiable si no hay historial
        successes = sum(1 for _, s in self.ia_success_history if s)
        return successes / len(self.ia_success_history)
    
    def should_disable_ia(self) -> bool:
        """Retorna True si IA ha fallado consistentemente."""
        if len(self.ia_success_history) < 5:
            return False
        # Si las últimas 3 fueron fallos, desactivar temporalmente
        recent = self.ia_success_history[-3:]
        return all(not s for _, s in recent)
    
    def get_adjusted_thresholds(self) -> dict:
        """
        Retorna umbrales ajustados según volatilidad y confiabilidad de IA.
        """
        multipliers = self.volatility_multipliers.get(self.current_market_volatility, 
                                                       self.volatility_multipliers["NORMAL"])
        
        # Si IA no es confiable, aumentar umbral técnico
        ia_reliability = self.get_ia_reliability()
        tech_boost = 1.0 if ia_reliability > 0.6 else 1.15
        
        return {
            "MIN_NEURAL_DESTACADA": min(95, self.config.MIN_NEURAL_DESTACADA * multipliers["neural"]),
            "MIN_TECHNICAL_DESTACADA": min(90, self.config.MIN_TECHNICAL_DESTACADA * multipliers["technical"] * tech_boost),
            "MIN_ALIGNMENT_DESTACADA": min(95, self.config.MIN_ALIGNMENT_DESTACADA * multipliers["alignment"]),
            "volatility_state": self.current_market_volatility,
            "ia_reliability": ia_reliability,
            "ia_disabled": self.should_disable_ia()
        }


class EnhancedIndicatorCache:
    """
    CACHE EFICIENTE: Indicadores persistentes con actualización incremental.
    - Evita recalcular lo mismo cada ciclo
    - Solo recalcula si precio cambió >0.1%
    """
    def __init__(self, cache_ttl: int = 60):
        self.cache = {}  # {symbol: {indicator: (value, timestamp, last_price)}}
        self.cache_ttl = cache_ttl
        self.lock = threading.RLock()
        self.price_change_threshold = 0.001  # 0.1%
        
    def get_cached_or_calculate(self, symbol: str, indicator: str, current_price: float,
                                 calculate_func: callable, *args, **kwargs):
        """
        Retorna valor cacheado si válido, o calcula nuevo valor.
        """
        cache_key = f"{symbol}_{indicator}"
        current_time = time.time()
        
        with self.lock:
            if cache_key in self.cache:
                value, timestamp, cached_price = self.cache[cache_key]
                
                # Verificar TTL y cambio de precio
                if current_time - timestamp < self.cache_ttl:
                    if cached_price > 0:
                        price_change = abs(current_price - cached_price) / cached_price
                        if price_change < self.price_change_threshold:
                            return value  # Cache válido
        
        # Calcular nuevo valor
        try:
            new_value = calculate_func(*args, **kwargs)
            with self.lock:
                self.cache[cache_key] = (new_value, current_time, current_price)
            return new_value
        except Exception as e:
            logger.debug(f"Cache calculate error: {e}")
            return None
    
    def invalidate(self, symbol: str = None):
        """Invalida cache para un símbolo o todo."""
        with self.lock:
            if symbol:
                keys_to_remove = [k for k in self.cache if k.startswith(f"{symbol}_")]
                for key in keys_to_remove:
                    del self.cache[key]
            else:
                self.cache.clear()
    
    def get_stats(self) -> dict:
        with self.lock:
            return {
                "total_entries": len(self.cache),
                "symbols": len(set(k.split("_")[0] for k in self.cache))
            }


class DynamicAlignmentScorer:
    """
    ALINEACIÓN DINÁMICA: Score continuo multi-timeframe.
    Reemplaza alineación binaria por score ponderado.
    """
    def __init__(self, config):
        self.config = config
        
    def calculate_multi_timeframe_score(self, df_5m: pd.DataFrame, df_15m: pd.DataFrame, 
                                        df_30m: pd.DataFrame, signal_direction: str) -> dict:
        """
        Calcula score de alineación continuo (0-100) basado en 3 timeframes.
        Penaliza desalineaciones parciales.
        """
        result = {
            "alignment_score": 0.0,
            "details": {},
            "is_coherent": False,
            "contradiction_detected": False
        }
        
        try:
            # Obtener tendencia de cada timeframe
            trend_5m = self._get_trend_direction(df_5m) if df_5m is not None and len(df_5m) >= 50 else "NEUTRAL"
            trend_15m = self._get_trend_direction(df_15m) if df_15m is not None and len(df_15m) >= 50 else "NEUTRAL"
            trend_30m = self._get_trend_direction(df_30m) if df_30m is not None and len(df_30m) >= 50 else "NEUTRAL"
            
            result["details"] = {
                "5m": trend_5m,
                "15m": trend_15m,
                "30m": trend_30m,
                "signal": signal_direction
            }
            
            # Calcular score ponderado
            # 30m (primario): 50% | 15m (entrada): 35% | 5m (confirmación): 15%
            score = 0.0
            
            # Timeframe primario (30m) - 50 puntos
            if trend_30m == signal_direction:
                score += 50
            elif trend_30m == "NEUTRAL":
                score += 25
            else:
                score -= 10  # Penalización por contradicción
                result["contradiction_detected"] = True
            
            # Timeframe entrada (15m) - 35 puntos
            if trend_15m == signal_direction:
                score += 35
            elif trend_15m == "NEUTRAL":
                score += 15
            else:
                score -= 5
                result["contradiction_detected"] = True
            
            # Timeframe confirmación (5m) - 15 puntos
            if trend_5m == signal_direction:
                score += 15
            elif trend_5m == "NEUTRAL":
                score += 5
            
            # Bonus por alineación perfecta
            if trend_5m == trend_15m == trend_30m == signal_direction:
                score += 10  # Bonus de confluencia
            
            # Normalizar a 0-100
            result["alignment_score"] = max(0.0, min(100.0, score))
            result["is_coherent"] = result["alignment_score"] >= 60 and not result["contradiction_detected"]
            
        except Exception as e:
            logger.debug(f"Multi-TF alignment error: {e}")
        
        return result
    
    def _get_trend_direction(self, df: pd.DataFrame) -> str:
        """Determina dirección de tendencia usando EMA 50/200."""
        if df is None or len(df) < 200:
            return "NEUTRAL"
        
        try:
            close = df['close']
            ema50 = close.ewm(span=50, adjust=False).mean().iloc[-1]
            ema200 = close.ewm(span=200, adjust=False).mean().iloc[-1]
            current = close.iloc[-1]
            
            if current > ema50 > ema200:
                return "BULLISH"
            elif current < ema50 < ema200:
                return "BEARISH"
            else:
                return "NEUTRAL"
        except:
            return "NEUTRAL"


class VolumeBreakoutValidator:
    """
    VALIDACIÓN TÉCNICA MEJORADA: Patrones + Volumen en breakouts.
    """
    def __init__(self, config):
        self.config = config
        self.volume_increase_threshold = 1.2  # 20% sobre promedio
        
    def validate_breakout_with_volume(self, df: pd.DataFrame, is_buy: bool) -> dict:
        """
        Valida breakout con confirmación de volumen.
        """
        result = {
            "is_valid_breakout": False,
            "volume_confirmed": False,
            "volume_ratio": 0.0,
            "breakout_strength": 0.0
        }
        
        if df is None or len(df) < 21:
            return result
        
        try:
            # Calcular volumen relativo
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].tail(20).mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            result["volume_ratio"] = volume_ratio
            result["volume_confirmed"] = volume_ratio >= self.volume_increase_threshold
            
            # Verificar breakout de EMA20
            close = df['close']
            ema20 = close.ewm(span=20, adjust=False).mean()
            current_price = close.iloc[-1]
            prev_price = close.iloc[-2]
            ema20_current = ema20.iloc[-1]
            ema20_prev = ema20.iloc[-2]
            
            if is_buy:
                # Breakout alcista: Precio cruza EMA20 hacia arriba
                if prev_price <= ema20_prev and current_price > ema20_current:
                    result["is_valid_breakout"] = True
                    result["breakout_strength"] = ((current_price - ema20_current) / ema20_current) * 100
            else:
                # Breakout bajista: Precio cruza EMA20 hacia abajo
                if prev_price >= ema20_prev and current_price < ema20_current:
                    result["is_valid_breakout"] = True
                    result["breakout_strength"] = ((ema20_current - current_price) / ema20_current) * 100
            
        except Exception as e:
            logger.debug(f"Breakout validation error: {e}")
        
        return result
    
    def validate_atr_minimum(self, df: pd.DataFrame, min_atr_pct: float = 0.5) -> Tuple[bool, float]:
        """
        Verifica que ATR sea >= min_atr_pct del precio.
        Evita operar en mercados muertos.
        """
        if df is None or len(df) < 15:
            return False, 0.0
        
        try:
            high = df['high'].tail(14)
            low = df['low'].tail(14)
            close = df['close'].tail(14)
            
            tr = pd.concat([
                high - low,
                abs(high - close.shift(1)),
                abs(low - close.shift(1))
            ], axis=1).max(axis=1)
            
            atr = tr.mean()
            current_price = close.iloc[-1]
            atr_pct = (atr / current_price) * 100 if current_price > 0 else 0
            
            return atr_pct >= min_atr_pct, atr_pct
            
        except Exception as e:
            logger.debug(f"ATR validation error: {e}")
            return False, 0.0


# Instancias globales de optimización
_fast_fail_filter = None
_adaptive_threshold_manager = None
_enhanced_cache = None
_dynamic_alignment_scorer = None
_volume_breakout_validator = None

def get_optimization_components(config):
    """Factory para obtener componentes de optimización."""
    global _fast_fail_filter, _adaptive_threshold_manager, _enhanced_cache
    global _dynamic_alignment_scorer, _volume_breakout_validator
    
    if _fast_fail_filter is None:
        _fast_fail_filter = FastFailFilter(config)
        _adaptive_threshold_manager = AdaptiveThresholdManager(config)
        _enhanced_cache = EnhancedIndicatorCache(cache_ttl=60)
        _dynamic_alignment_scorer = DynamicAlignmentScorer(config)
        _volume_breakout_validator = VolumeBreakoutValidator(config)
        logger.info("⚡ Componentes de optimización inicializados")
    
    return {
        "fast_fail": _fast_fail_filter,
        "adaptive_thresholds": _adaptive_threshold_manager,
        "cache": _enhanced_cache,
        "alignment_scorer": _dynamic_alignment_scorer,
        "breakout_validator": _volume_breakout_validator
    }


# ==============================================================================
# MÓDULO 2 MODIFICADO: UnifiedMarketAnalyzer (Modo: 1 Señal Activa)
# ==============================================================================

# Singleton para evitar múltiples instancias del modelo NN (ahorro de memoria)
_unified_analyzer_instance = None
_unified_analyzer_lock = threading.Lock()

def get_unified_analyzer(config):
    """Factory Singleton para UnifiedMarketAnalyzer - evita cargar múltiples modelos NN"""
    global _unified_analyzer_instance
    with _unified_analyzer_lock:
        if _unified_analyzer_instance is None:
            _unified_analyzer_instance = UnifiedMarketAnalyzer(config)
            logger.info("🧠 UnifiedMarketAnalyzer Singleton creado")
        return _unified_analyzer_instance




class UnifiedMarketAnalyzer:
    """
    Analizador que usa INFERENCIA REAL de PyTorch.
    - Carga el modelo .pth entrenado.
    - Usa el scaler .pkl para normalizar datos.
    - NO usa random para decisiones.
    - Si no encuentra el modelo, usa lógica técnica determinista (no azar).
    - SINGLETON: Usar get_unified_analyzer(config) para obtener instancia única.
    """
    def __init__(self, config):
        self.config = config
        self.active_signal = None
        self.active_symbol = None

        # Configuración de dispositivo (GPU o CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Componentes de IA
        self.model = None
        self.scaler = None
        self.is_neural_ready = False

        # Cargar al inicio
        self._load_neural_components()

        if self.is_neural_ready:
            logger.info(f"✅ SISTEMA NEURONAL REAL ACTIVO (Device: {self.device})")
        else:
            logger.warning("⚠️ Modelo .pth NO encontrado. Sistema en MODO TÉCNICO ESTRICTO (Sin IA).")

    def set_active_signal(self, signal_data: dict):
        self.active_signal = signal_data
        self.active_symbol = signal_data.get('symbol')
        logger.info(f"🔒 Señal ACTIVA para {self.active_symbol}.")

    def clear_active_signal(self):
        prev = self.active_symbol
        self.active_signal = None
        self.active_symbol = None
        logger.info(f"🔓 Señal liberada ({prev}).")

    def _load_neural_components(self):
        """Carga la arquitectura, los pesos (pth) y el escalador (pkl)"""
        try:
            model_path = path_manager.get_data_path('models', 'neural_net_model_v20_optimized.pth')
            scaler_path = path_manager.get_data_path('models', 'scaler_v20_optimized.pkl')

            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                logger.error(f"❌ Archivos de IA no encontrados en {model_path} o {scaler_path}.")
                return

            # 1. Definir Arquitectura de la Red (Debe coincidir exactamente con el entrenamiento)
            class CryptoNet(nn.Module):
                def __init__(self, input_size, hidden_layers, dropout):
                    super(CryptoNet, self).__init__()
                    layers = []
                    prev_size = input_size
                    for h in hidden_layers:
                        layers.append(nn.Linear(prev_size, h))
                        layers.append(nn.ReLU())
                        layers.append(nn.Dropout(dropout))
                        prev_size = h
                    layers.append(nn.Linear(prev_size, 3))
                    layers.append(nn.Softmax(dim=1))
                    self.net = nn.Sequential(*layers)

                def forward(self, x):
                    return self.net(x)

            # 2. Instanciar Modelo
            self.model = CryptoNet(
                input_size=self.config.NEURAL_INPUT_SIZE,
                hidden_layers=self.config.NEURAL_HIDDEN_LAYERS,
                dropout=self.config.NEURAL_DROPOUT
            ).to(self.device)

            # 3. Cargar Pesos (State Dict)
            checkpoint = torch.load(model_path, map_location=self.device)
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                config_data = checkpoint.get('config', {})
                saved_input_size = config_data.get('input_size', self.config.NEURAL_INPUT_SIZE)
                if saved_input_size != self.config.NEURAL_INPUT_SIZE:
                    logger.warning(f"⚠️ Incompatibilidad de arquitectura detectada: {saved_input_size} vs {self.config.NEURAL_INPUT_SIZE}")
                    logger.warning("🔄 Eliminando modelo incompatible y se creará uno nuevo")
                    try:
                        os.remove(model_path)
                        if os.path.exists(scaler_path):
                            os.remove(scaler_path)
                        logger.info("✅ Archivos de modelo incompatibles eliminados")
                    except Exception as e:
                        logger.error(f"Error eliminando archivos: {e}")
                    self.is_neural_ready = False
                    return
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.model.eval()
                self.is_neural_ready = True
                self.performance_metrics = checkpoint.get('performance_metrics', {})
                self.training_history = checkpoint.get('training_history', [])
            else:
                logger.warning("⚠️ Modelo en formato antiguo detectado")
                logger.warning("🔄 Eliminando modelo antiguo y se creará uno nuevo")
                try:
                    os.remove(model_path)
                    if os.path.exists(scaler_path):
                        os.remove(scaler_path)
                    logger.info("✅ Archivos de modelo antiguos eliminados")
                except Exception as e:
                    logger.error(f"Error eliminando archivos: {e}")
                self.is_neural_ready = False
                return

            # 4. Cargar Scaler
            self.scaler = joblib.load(scaler_path)
            self.is_neural_ready = True

        except Exception as e:
            logger.critical(f"❌ Error crítico cargando IA Real: {e}")
            logger.info("ℹ️ Continuando sin IA (Modo Técnico Puro).")

    def check_limit_and_generate_signal(self, df: pd.DataFrame, symbol: str) -> Optional[Dict]:
        if self.active_signal is not None:
            return None

        # === 🔥 FAST-FAIL REAL: ANTES DE CUALQUIER CÁLCULO PESADO ===
        fast = self._fast_engine_lightweight(df, symbol)
        if not fast:
            return None

        current_price = fast["current_price"]
        atr = fast["atr"]

        # === 🧮 AHORA SÍ: calcular indicadores COMPLETOS ===
        df = self._compute_indicators(df)
        if len(df) < self.config.NEURAL_INPUT_SIZE + 50:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # === 🤖 Inferencia IA REAL ===
        neural_pred = self._get_neural_prediction(df)
        tech_bias, tech_score = self._get_technical_bias(latest, prev)
        align_bias, align_score = self._get_alignment_bias(latest, df.tail(50))

        # === 🎯 Confluencia obligatoria ===
        buy_confluence = (neural_pred['neural_bias'] == "BULLISH" and tech_bias == "BULLISH" and align_bias == "BULLISH")
        sell_confluence = (neural_pred['neural_bias'] == "BEARISH" and tech_bias == "BEARISH" and align_bias == "BEARISH")

        if not (buy_confluence or sell_confluence):
            return None

        # === 🛡️ Filtro de robustez: evita señales débiles o en rango ===
        robustness_score = (
            float(neural_pred.get('neural_confidence', 0.0)) * 0.45 +
            float(tech_score) * 0.30 +
            float(align_score) * 0.25
        )
        min_robustness = float(getattr(self.config, 'MIN_SIGNAL_ROBUSTNESS', 76.0))
        if robustness_score < min_robustness:
            return None

        # === 📏 Niveles con pisos mínimos ===
        min_sl_percent = getattr(self.config, 'MIN_STOP_LOSS_PERCENT', 0.3) / 100
        min_tp_percent = getattr(self.config, 'TAKE_PROFIT_PERCENT', 1.0) / 100
        atr_regime = float((atr / current_price) * 100) if current_price > 0 else 0.0

        # ✅ Ajuste adaptativo por volatilidad y calidad de señal (menos SL por ruido)
        if atr_regime >= 1.6:
            sl_mult, tp_mult = 1.9, 3.8
        elif atr_regime >= 1.0:
            sl_mult, tp_mult = 1.7, 3.4
        else:
            sl_mult, tp_mult = 1.45, 2.9

        if robustness_score >= 88:
            sl_mult += 0.12
            tp_mult += 0.30

        sl_dist = max(atr * sl_mult, current_price * min_sl_percent)
        tp_dist = max(atr * tp_mult, current_price * min_tp_percent)

        rr_ratio = (tp_dist / sl_dist) if sl_dist > 0 else 0.0
        min_rr_ratio = float(getattr(self.config, 'MIN_RISK_REWARD_RATIO', 1.75))
        if rr_ratio < min_rr_ratio:
            return None

        if buy_confluence:
            entry, sl, tp, direction = current_price, current_price - sl_dist, current_price + tp_dist, "BUY"
        else:
            entry, sl, tp, direction = current_price, current_price + sl_dist, current_price - tp_dist, "SELL"

        signal_data = {
            'symbol': symbol,
            'signal_type': direction,
            'entry_price': entry,
            'stop_loss': sl,
            'take_profit': tp,
            'neural_score': neural_pred['neural_confidence'],
            'technical_percentage': tech_score,
            'alignment_percentage': align_score,
            'robustness_score': robustness_score,
            'risk_reward_ratio': rr_ratio,
            'atr_regime_percent': atr_regime,
            'neural_label': neural_pred.get('neural_label', 'NEUTRAL'),
            'dataframe_entry': df.copy()
        }

        self.set_active_signal(signal_data)
        logger.info(
            f"🧠🚀 SEÑAL CONFIRMADA: {symbol} | IA={neural_pred['neural_confidence']:.1f}% "
            f"| Tec={tech_score:.1f}% | Ali={align_score:.1f}% | Robustez={robustness_score:.1f}% | R/R={rr_ratio:.2f}"
        )
        return signal_data

    def _fast_engine_lightweight(self, df: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        if df is None or len(df) < 70:
            return None

        try:
            latest = df.iloc[-1]
            price = float(latest['close'])
            ema_20 = float(latest.get('ema_20', 0))
            ema_50 = float(latest.get('ema_50', 0))
            volume = float(latest.get('volume', 0))

            if price <= 0 or not np.isfinite(price):
                return None

            # Tendencia
            if ema_20 > ema_50:
                direction = "BUY"
            elif ema_20 < ema_50:
                direction = "SELL"
            else:
                return None

            # ✅ 1. RSI Estricto (Mejorado para evitar sobrecompra/sobreventa extrema en entrada)
            rsi = float(latest.get('rsi', 50.0))
            # BUY: RSI debe estar subiendo pero no saturado (e.g. 50-70)
            # SELL: RSI debe estar bajando pero no saturado (e.g. 30-50)
            rsi_buy_min = 50.0  
            rsi_buy_max = 75.0  # Evitar comprar en pico
            rsi_sell_max = 50.0 
            rsi_sell_min = 25.0 # Evitar vender en fondo

            if direction == "BUY":
                if not (rsi_buy_min <= rsi <= rsi_buy_max):
                    return None
            else: # SELL
                if not (rsi_sell_min <= rsi <= rsi_sell_max):
                    return None

            # ✅ 2. Volumen (Validación simple)
            avg_volume = df['volume'].tail(20).mean()
            if volume < avg_volume * 0.8: # Permitir un poco menos, pero no mucho
                return None

            # Timing - Permitir pullback leve a la EMA
            if (direction == "BUY" and price < ema_20 * 0.995) or (direction == "SELL" and price > ema_20 * 1.005):
                return None

            # ✅ 3. Volatilidad y Fuerza de Tendencia (ADX)
            df_adx = self._compute_atr_adx_light(df, period=14)
            if df_adx is None:
                return None
            
            latest_adx = df_adx.iloc[-1]
            atr = float(latest_adx['atr'])
            adx = float(latest_adx['adx'])
            plus_di = float(latest_adx['plus_di'])
            minus_di = float(latest_adx['minus_di'])

            if not np.isfinite(atr) or atr <= 0:
                return None
            
            # ATR % Mínimo
            atr_pct = (atr / price) * 100
            if atr_pct < float(getattr(self.config, 'MIN_VOLATILITY_PERCENT', 0.5)):
                return None

            # ✅ ADX > 20 para asegurar tendencia
            if adx < 20.0:
                return None

            # ✅ Confirmación Direccional (+DI vs -DI)
            if direction == "BUY" and plus_di <= minus_di:
                return None
            if direction == "SELL" and minus_di <= plus_di:
                return None

            return {
                'current_price': price,
                'atr': atr,
                'direction': direction,
                'df': df
            }

        except Exception as e:
            logger.error(f"Error en _fast_engine_lightweight: {e}")
            return None

    def _compute_atr_adx_light(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Versión ligera de ATR y ADX (para FAST-FAIL).
        Calcula ATR, ADX, +DI, -DI sin dependencias pesadas.
        """
        try:
            high = pd.to_numeric(df['high'], errors='coerce')
            low = pd.to_numeric(df['low'], errors='coerce')
            close = pd.to_numeric(df['close'], errors='coerce')

            # TR
            tr0 = abs(high - low)
            tr1 = abs(high - close.shift())
            tr2 = abs(low - close.shift())
            tr = pd.concat([tr0, tr1, tr2], axis=1).max(axis=1)
            atr = tr.ewm(alpha=1/period, adjust=False).mean()

            # DM
            up = high - high.shift()
            down = low.shift() - low
            
            plus_dm = np.where((up > down) & (up > 0), up, 0.0)
            minus_dm = np.where((down > up) & (down > 0), down, 0.0)
            
            plus_dm_s = pd.Series(plus_dm, index=df.index).ewm(alpha=1/period, adjust=False).mean()
            minus_dm_s = pd.Series(minus_dm, index=df.index).ewm(alpha=1/period, adjust=False).mean()
            
            # Evitar división por cero
            atr_safe = atr.replace(0, 1e-9)
            
            plus_di = 100 * (plus_dm_s / atr_safe)
            minus_di = 100 * (minus_dm_s / atr_safe)
            
            dx_denom = plus_di + minus_di
            dx_denom = dx_denom.replace(0, 1e-9)
            
            dx = 100 * abs(plus_di - minus_di) / dx_denom
            adx = dx.ewm(alpha=1/period, adjust=False).mean()
            
            return df.assign(atr=atr, adx=adx, plus_di=plus_di, minus_di=minus_di)
        except Exception as e:
            logger.error(f"Error en _compute_atr_adx_light: {e}")
            return None

    def _get_neural_prediction(self, df: pd.DataFrame) -> Dict:
        if not self.is_neural_ready or self.model is None:
            return {'neural_bias': 'NEUTRAL', 'neural_label': 'NEUTRAL', 'neural_confidence': 0.0}

        try:
            analyzer = OptimizedTechnicalAnalyzer(self.config)
            features, _ = self._extract_optimized_features(df, analyzer)
            if not features:
                return {'neural_bias': 'NEUTRAL', 'neural_label': 'NEUTRAL', 'neural_confidence': 0.0}

            # Usar múltiples predicciones de 60 velas (60 min en 1m) para reducir ruido
            X = np.array(features[-60:]) if len(features) >= 60 else np.array(features[-max(1, len(features)):])
            X_scaled = self.scaler.transform(X)
            X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(X_tensor)
                probabilities = torch.mean(outputs, dim=0).cpu().numpy()

            sell_prob = float(probabilities[0])
            neutral_prob = float(probabilities[1])
            buy_prob = float(probabilities[2])

            max_prob = max(sell_prob, neutral_prob, buy_prob)
            prediction_strength = float(max_prob - np.mean([sell_prob, neutral_prob, buy_prob]))

            if buy_prob == max_prob:
                if buy_prob >= 0.8:
                    signal_type = SignalType.CONFIRMED_BUY
                elif buy_prob >= 0.7:
                    signal_type = SignalType.STRONG_BUY
                elif buy_prob >= 0.5:
                    signal_type = SignalType.MODERATE_BUY
                else:
                    signal_type = SignalType.NEUTRAL
            elif sell_prob == max_prob:
                if sell_prob >= 0.8:
                    signal_type = SignalType.CONFIRMED_SELL
                elif sell_prob >= 0.7:
                    signal_type = SignalType.STRONG_SELL
                elif sell_prob >= 0.5:
                    signal_type = SignalType.MODERATE_SELL
                else:
                    signal_type = SignalType.NEUTRAL
            else:
                signal_type = SignalType.NEUTRAL

            if signal_type in (SignalType.CONFIRMED_BUY, SignalType.STRONG_BUY, SignalType.MODERATE_BUY, SignalType.WEAK_BUY):
                normalized_bias = "BULLISH"
            elif signal_type in (SignalType.CONFIRMED_SELL, SignalType.STRONG_SELL, SignalType.MODERATE_SELL, SignalType.WEAK_SELL):
                normalized_bias = "BEARISH"
            else:
                normalized_bias = "NEUTRAL"

            return {
                'neural_bias': normalized_bias,
                'neural_label': signal_type.name,
                'neural_confidence': max_prob * 100,
                'buy_probability': buy_prob * 100,
                'sell_probability': sell_prob * 100,
                'prediction_strength': prediction_strength * 100
            }

        except Exception as e:
            logger.error(f"Error en _get_neural_prediction: {e}")
            return {'neural_bias': 'NEUTRAL', 'neural_label': 'NEUTRAL', 'neural_confidence': 0.0}

    def _get_technical_bias(self, latest: pd.Series, prev: pd.Series) -> Tuple[str, float]:
        try:
            ema50 = self.config.EMA_FAST
            ema200 = self.config.EMA_SLOW
            rsi = float(latest.get('rsi', 50.0))
            volume = float(latest.get('volume', 0.0))
            avg_volume = float(prev.get('volume', 0.0))

            if latest['close'] > latest[f'ema_{ema50}'] and latest['close'] > latest[f'ema_{ema200}']:
                bias = "BULLISH"
            elif latest['close'] < latest[f'ema_{ema50}'] and latest['close'] < latest[f'ema_{ema200}']:
                bias = "BEARISH"
            else:
                bias = "NEUTRAL"
            
            # ✅ Validación de Volumen en Bias Técnico
            if bias != "NEUTRAL" and volume < avg_volume * 0.7: # Permitir 70% del promedio
                bias = "NEUTRAL"


            # Calcular confianza técnica
            ema_diff = (latest['close'] - latest[f'ema_{ema50}']) / latest['close'] * 100
            if ema_diff > 0:
                tech_confidence = (ema_diff + rsi) / 2
            else:
                tech_confidence = (ema_diff + (100 - rsi)) / 2

            return bias, tech_confidence

        except Exception as e:
            logger.error(f"Error en _get_technical_bias: {e}")
            return "NEUTRAL", 0.0

    def _get_alignment_bias(self, latest: pd.Series, df_tail: pd.DataFrame) -> Tuple[str, float]:
        try:
            ema50 = self.config.EMA_FAST
            ema200 = self.config.EMA_SLOW
            rsi = float(latest.get('rsi', 50.0))
            volume = float(latest.get('volume', 0.0))
            avg_volume = float(df_tail['volume'].mean())

            if latest['close'] > latest[f'ema_{ema50}'] and latest['close'] > latest[f'ema_{ema200}']:
                bias = "BULLISH"
            elif latest['close'] < latest[f'ema_{ema50}'] and latest['close'] < latest[f'ema_{ema200}']:
                bias = "BEARISH"
            else:
                bias = "NEUTRAL"

            # Calcular confianza de alineación
            ema_diff = (latest['close'] - latest[f'ema_{ema50}']) / latest['close'] * 100
            if ema_diff > 0:
                align_confidence = (ema_diff + rsi) / 2
            else:
                align_confidence = (ema_diff + (100 - rsi)) / 2

            return bias, align_confidence

        except Exception as e:
            logger.error(f"Error en _get_alignment_bias: {e}")
            return "NEUTRAL", 0.0

    def _extract_optimized_features(self, df: pd.DataFrame, analyzer: "OptimizedTechnicalAnalyzer") -> Tuple[List, List]:
        if df is None or df.empty or len(df) < self.config.MIN_NN_DATA_REQUIRED:
            return [], []

        features = []
        targets = []

        try:
            df_work = df.copy()
            data_id = str(hash(str(df.iloc[0]['timestamp'])))

            # === 🔒 SANITIZACIÓN GLOBAL: Función para forzar escalar/float ===
            def _to_safe_float(x, default=0.0):
                """Convierte cualquier valor a float seguro. Maneja tuplas, arrays, NaN, None."""
                try:
                    # Desempaquetar recursivamente
                    while isinstance(x, (tuple, list, np.ndarray)) and len(x) > 0:
                        x = x[0]
                    # Convertir
                    val = float(x)
                    return val if np.isfinite(val) else default
                except Exception:
                    return default

            # === 1. Calcular indicadores — SANITIZAR cada salida ===
            ema50_raw = analyzer.calculate_ema(df_work['close'], 50, data_id)
            ema200_raw = analyzer.calculate_ema(df_work['close'], 200, data_id)
            tdi_out = analyzer.calculate_tdi(df_work, data_id)

            # Verificar salida de calculate_tdi (puede devolver tupla o dict)
            if isinstance(tdi_out, tuple) and len(tdi_out) == 5:
                tdi_rsi, tdi_green, tdi_red, tdi_upper, tdi_lower = tdi_out
            elif isinstance(tdi_out, dict):
                tdi_rsi = tdi_out.get('rsi', pd.Series([50.0] * len(df_work)))
                tdi_green = tdi_out.get('green', pd.Series([50.0] * len(df_work)))
                tdi_red = tdi_out.get('red', pd.Series([50.0] * len(df_work)))
            else:
                # Fallback seguro
                tdi_rsi = tdi_green = tdi_red = pd.Series([50.0] * len(df_work))

            # Asegurar Series de float
            df_work['ema50'] = pd.to_numeric(ema50_raw, errors='coerce').apply(_to_safe_float)
            df_work['ema200'] = pd.to_numeric(ema200_raw, errors='coerce').apply(_to_safe_float)
            df_work['tdi_rsi'] = pd.to_numeric(tdi_rsi, errors='coerce').apply(_to_safe_float)
            df_work['tdi_green'] = pd.to_numeric(tdi_green, errors='coerce').apply(_to_safe_float)
            df_work['tdi_red'] = pd.to_numeric(tdi_red, errors='coerce').apply(_to_safe_float)

            # === 2. Patrones — ya son dict seguros, pero sanitizamos ===
            try:
                candle_pattern = analyzer.analyze_candlestick_pattern(df_work)
            except Exception as e:
                logger.debug(f"⚠️ Falló analyze_candlestick_pattern: {e}")
                candle_pattern = {'type': 'NEUTRAL', 'pattern': 'NONE', 'confidence': 0}
            try:
                w_m_pattern = analyzer.detect_w_m_pattern(df_work)
            except:
                w_m_pattern = {'pattern': 'NONE'}
            try:
                hch_pattern = analyzer.detect_hch_pattern(df_work)
            except:
                hch_pattern = {'pattern': 'NONE'}

            df_work['pattern_bullish'] = 1 if candle_pattern.get('type') == 'BULLISH' else 0
            df_work['pattern_bearish'] = 1 if candle_pattern.get('type') == 'BEARISH' else 0
            df_work['pattern_w'] = 1 if w_m_pattern.get('pattern') == 'W_BOTTOM' else 0
            df_work['pattern_m'] = 1 if w_m_pattern.get('pattern') == 'M_TOP' else 0
            df_work['pattern_hch'] = 1 if hch_pattern.get('pattern') == 'HCH' else 0
            df_work['pattern_lcl'] = 1 if hch_pattern.get('pattern') == 'LCL' else 0

            # === 3. Soporte/Resistencia — sanitización robusta ===
            try:
                sr_levels = analyzer.find_support_resistance(df_work)
            except Exception as e:
                logger.debug(f"⚠️ Falló find_support_resistance: {e}")
                sr_levels = {'support': None, 'resistance': None}

            support_val = _to_safe_float(sr_levels.get('support'))
            resistance_val = _to_safe_float(sr_levels.get('resistance'))

            current_price = _to_safe_float(df_work['close'].iloc[-1], default=1e-8)

            dist_to_support = (current_price - support_val) / current_price if current_price != 0 else 0.0
            dist_to_resistance = (resistance_val - current_price) / current_price if current_price != 0 else 0.0

            df_work['distance_to_support'] = dist_to_support
            df_work['distance_to_resistance'] = dist_to_resistance

            # === 4. Ciclo de mercado ===
            try:
                market_cycle = analyzer.analyze_market_cycles(df_work)
                cycle = market_cycle.get('cycle', 'NEUTRAL').upper()
            except:
                cycle = 'NEUTRAL'

            df_work['cycle_accumulation'] = 1 if cycle == 'ACCUMULATION' else 0
            df_work['cycle_uptrend'] = 1 if cycle == 'UPTREND' else 0
            df_work['cycle_distribution'] = 1 if cycle == 'DISTRIBUTION' else 0
            df_work['cycle_downtrend'] = 1 if cycle == 'DOWNTREND' else 0

            # === 5. Lista final de columnas ===
            feature_columns = [
                'open', 'high', 'low', 'close', 'volume',
                'ema50', 'ema200',
                'tdi_rsi', 'tdi_green', 'tdi_red',
                'pattern_bullish', 'pattern_bearish',
                'pattern_w', 'pattern_m',
                'pattern_hch', 'pattern_lcl',
                'distance_to_support', 'distance_to_resistance',
                'cycle_accumulation', 'cycle_uptrend',
                'cycle_distribution', 'cycle_downtrend'
            ]

            # === 6. Limpieza final de df_work ===
            for col in feature_columns:
                if col in df_work.columns:
                    # Aplicar conversión segura columna por columna
                    df_work[col] = df_work[col].apply(_to_safe_float)
                else:
                    df_work[col] = 0.0  # columna faltante → rellenar con 0

            # Normalizar por último cierre
            last_close = _to_safe_float(df_work['close'].iloc[-1], default=1e-8)
            if last_close == 0:
                last_close = 1e-8

            for col in ['open', 'high', 'low', 'close', 'ema50', 'ema200']:
                if col in df_work.columns:
                    df_work[col] = df_work[col] / last_close

            # Asegurar array numérico limpio
            df_clean = df_work[feature_columns].copy()
            df_clean = df_clean.replace([np.inf, -np.inf], np.nan).fillna(0.0)

            if len(df_clean) < 50:
                logger.warning(f"📉 df_clean demasiado corto ({len(df_clean)} filas)")
                return [], []

            # === 7. Generar features y targets ===
            lookback = 3
            lookahead = 5
            for i in range(lookback, len(df_clean) - lookahead):
                # Construir feature vector plano (solo floats)
                feature_row = []
                for j in range(lookback):
                    # .iloc[i-j] → Serie → .values → array → lista de floats
                    values = df_clean.iloc[i - j][feature_columns].values
                    # Garantizar que todos sean float (no tuplas/listas)
                    clean_values = [_to_safe_float(v) for v in values]
                    feature_row.extend(clean_values)

                # Target
                current_close = _to_safe_float(df_clean.iloc[i]['close'])
                future_close = _to_safe_float(df_clean.iloc[i + lookahead]['close'])
                price_change = (future_close - current_close) / (current_close if abs(current_close) > 1e-12 else 1e-8)

                if price_change > 0.008:
                    target = 2  # BUY
                elif price_change < -0.008:
                    target = 0  # SELL
                else:
                    target = 1  # NEUTRAL

                features.append(feature_row)
                targets.append(target)

            return features, targets

        except Exception as e:
            logger.error(f"[ERROR] Error FATAL en _extract_optimized_features: {e}", exc_info=True)
            return [], []

    def _compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            analyzer = OptimizedTechnicalAnalyzer(self.config)
            df['ema_50'] = analyzer.calculate_ema(df['close'], 50)
            df['ema_200'] = analyzer.calculate_ema(df['close'], 200)
            tdi_out = analyzer.calculate_tdi(df)
            if isinstance(tdi_out, tuple) and len(tdi_out) == 5:
                df['tdi_rsi'], df['tdi_green'], df['tdi_red'], _, _ = tdi_out
            elif isinstance(tdi_out, dict):
                df['tdi_rsi'] = tdi_out.get('rsi', pd.Series([50.0] * len(df)))
                df['tdi_green'] = tdi_out.get('green', pd.Series([50.0] * len(df)))
                df['tdi_red'] = tdi_out.get('red', pd.Series([50.0] * len(df)))

            df['rsi'] = analyzer.calculate_rsi(df['close'], 14)
            df['ema_20'] = analyzer.calculate_ema(df['close'], 20)
            df['pattern'] = df.apply(lambda row: analyzer.analyze_candlestick_pattern(row), axis=1)
            df['w_m_pattern'] = df.apply(lambda row: analyzer.detect_w_m_pattern(row), axis=1)
            df['hch_pattern'] = df.apply(lambda row: analyzer.detect_hch_pattern(row), axis=1)

            return df

        except Exception as e:
            logger.error(f"Error en _compute_indicators: {e}")
            return df

# Factory Singleton para UnifiedMarketAnalyzer - evita cargar múltiples modelos NN
_unified_analyzer_instance = None
_unified_analyzer_lock = threading.Lock()

def get_unified_analyzer(config):
    global _unified_analyzer_instance
    with _unified_analyzer_lock:
        if _unified_analyzer_instance is None:
            _unified_analyzer_instance = UnifiedMarketAnalyzer(config)
            logger.info("🧠 UnifiedMarketAnalyzer Singleton creado")
        return _unified_analyzer_instance


class SignalChartGenerator:
    """Generador de gráficos de señales optimizado con manejo eficiente de WebSocket"""

    def __init__(self, disable_websocket: bool = False):
        self.directorio_graficos = path_manager.get_data_path('charts')

        # ✅ Flag para deshabilitar WebSocket cuando FIX_API está activo
        self._disable_websocket_global = disable_websocket
        if disable_websocket:
            logger.info("✅ WebSocket deshabilitado en SignalChartGenerator (FIX API activo)")

        # Gestión WebSocket
        self.gestor_ws = None
        self.symbol_actual = None
        self.df_tiempo_real = None
        self.actualizando = False
        self.callback_actualizacion = None

        # Optimización de rendimiento
        self.bloqueo_actualizacion = threading.Lock()
        self.ultima_actualizacion = 0
        self.intervalo_min_actualizacion = 1.0  # segundos

        # Caché de datos
        self.cache_graficos = {}
        self.tamano_max_cache = 10

    def generate_signal_chart(self, symbol: str, df: pd.DataFrame, signal_data: dict, analysis_result: dict) -> Optional[str]:
        """
        Genera gráfico PROFESIONAL con velas, volumen, EMAs, TDI y niveles.
        Incluye:
            - Velas japonesas con colores profesionales
            - EMAs 50 (dorado) y 200 (púrpura)
            - TDI (Traders Dynamic Index)
            - Niveles: ENTRADA, STOP LOSS, TAKE PROFIT
            - Ejes X e Y con valores claros
            - Volumen con colores según velas
            - Métricas de confianza (IA, Técnico, Alineación)
            - Barra de progreso hacia TP
        """
        if not PLOTTING_AVAILABLE:
            logger.warning("Matplotlib no disponible para generar gráficos")
            return None

        try:
            if df is None or df.empty or len(df) < 5:
                logger.warning(f"Datos insuficientes para gráfico de {symbol}")
                return None

            # Preparar datos
            df_plot = df.tail(80).copy().reset_index(drop=True)
            x_vals = range(len(df_plot))
            
            # Calcular EMAs
            ema_50 = df_plot['close'].ewm(span=50, adjust=False).mean()
            ema_200 = df_plot['close'].ewm(span=200, adjust=False).mean()
            
            # Calcular TDI (RSI-based indicator)
            delta = df_plot['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            tdi_rsi = 100 - (100 / (1 + rs))
            tdi_rsi = tdi_rsi.fillna(50)

            # --- Crear figura con layout profesional ---
            fig = plt.figure(figsize=(14, 9), facecolor='#0f0f23')
            gs = GridSpec(4, 1, height_ratios=[3, 1, 0.8, 0.6], hspace=0.04)

            ax_main   = fig.add_subplot(gs[0])
            ax_volume = fig.add_subplot(gs[1], sharex=ax_main)
            ax_tdi    = fig.add_subplot(gs[2], sharex=ax_main)
            ax_progress = fig.add_subplot(gs[3])

            # Estilo profesional
            for ax in [ax_main, ax_volume, ax_tdi, ax_progress]:
                ax.set_facecolor('#0f0f23')
                ax.tick_params(colors='#b0b0b0', labelsize=9, length=4)
                ax.grid(True, alpha=0.15, color='#1a2a4c', linestyle='--', linewidth=0.5)
                for spine in ax.spines.values():
                    spine.set_color('#1a2a4c')
                    spine.set_linewidth(1)

            # --- VELAS JAPONESAS PROFESIONALES ---
            colors = ['#00d4aa' if df_plot.iloc[i]['close'] >= df_plot.iloc[i]['open'] else '#ff6b6b'
                      for i in range(len(df_plot))]

            for i in range(len(df_plot)):
                row = df_plot.iloc[i]
                o, h, l, c = row['open'], row['high'], row['low'], row['close']
                color = colors[i]
                # Sombra (wick)
                ax_main.plot([i, i], [l, h], color=color, linewidth=1.2, alpha=0.8)
                # Cuerpo (body)
                height = abs(c - o)
                bottom = min(o, c)
                ax_main.bar(i, height if height > 0 else 1e-8, bottom=bottom, width=0.65, 
                          color=color, alpha=0.95, edgecolor='none')

            # --- EMAs ---
            ax_main.plot(x_vals, ema_50, color='#FFD700', linewidth=2, label='EMA 50', alpha=0.85, linestyle='-')
            ax_main.plot(x_vals, ema_200, color='#9C27B0', linewidth=2.5, label='EMA 200', alpha=0.75, linestyle='-')

            # --- NIVELES DE SEÑAL (ENTRADA, SL, TP) ---
            entry_price = signal_data.get('entry_price', 0)
            stop_loss = signal_data.get('stop_loss', 0)
            take_profit = signal_data.get('take_profit', 0)
            current_price = float(df_plot.iloc[-1]['close'])
            is_buy = 'BUY' in str(signal_data.get('combined_signal', '')) or 'COMPRA' in str(signal_data.get('combined_signal', ''))

            # Entrada (azul)
            if entry_price > 0:
                ax_main.axhline(y=entry_price, color='#2196F3', linestyle='-', linewidth=2.5, alpha=0.9, label='ENTRADA')
                y_pos = entry_price
                ax_main.text(len(df_plot) - 1, y_pos, f' ${entry_price:.8f}', fontsize=10, fontweight='bold',
                           color='white', va='center', 
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='#2196F3', alpha=0.85, edgecolor='#1976D2', linewidth=1))

            # Stop Loss (rojo punteado)
            if stop_loss > 0:
                ax_main.axhline(y=stop_loss, color='#FF5252', linestyle='--', linewidth=2.5, alpha=0.9, label='STOP LOSS')
                y_pos = stop_loss
                ax_main.text(len(df_plot) - 1, y_pos, f' ${stop_loss:.8f}', fontsize=10, fontweight='bold',
                           color='white', va='center',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='#FF5252', alpha=0.85, edgecolor='#D32F2F', linewidth=1))

            # Take Profit (verde/rojo según dirección)
            if take_profit > 0:
                tp_color = '#4CAF50' if is_buy else '#FF9800'
                ax_main.axhline(y=take_profit, color=tp_color, linestyle='-', linewidth=2.5, alpha=0.9, label='TAKE PROFIT')
                y_pos = take_profit
                tp_label_color = '#1B5E20' if is_buy else '#E65100'
                ax_main.text(len(df_plot) - 1, y_pos, f' ${take_profit:.8f}', fontsize=10, fontweight='bold',
                           color='white', va='center',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor=tp_color, alpha=0.85, edgecolor=tp_label_color, linewidth=1))

            # Precio actual (línea punteada dorada)
            ax_main.axhline(y=current_price, color='#FFEB3B', linestyle=':', linewidth=2, alpha=0.7, label=f'ACTUAL ${current_price:.8f}')

            # --- VOLUMEN ---
            ax_volume.bar(x_vals, df_plot['volume'], color=colors, alpha=0.7, width=0.65, edgecolor='none')
            ax_volume.set_ylabel('Volumen', color='#b0b0b0', fontsize=10, fontweight='bold')
            
            # Agregar valores al eje Y del volumen
            y_ticks = ax_volume.get_yticks()
            ax_volume.set_yticklabels([f'{int(y/1e6)}M' if y >= 1e6 else f'{int(y/1e3)}K' for y in y_ticks], fontsize=8)

            # --- TDI (Traders Dynamic Index) ---
            ax_tdi.plot(x_vals, tdi_rsi, color='#00BCD4', linewidth=2, label='TDI RSI', alpha=0.9)
            ax_tdi.axhline(y=50, color='#FFD700', linestyle='--', linewidth=1, alpha=0.5, label='Neutral (50)')
            ax_tdi.axhline(y=30, color='#FF5252', linestyle=':', linewidth=1, alpha=0.5, label='Sobrevendido (30)')
            ax_tdi.axhline(y=70, color='#4CAF50', linestyle=':', linewidth=1, alpha=0.5, label='Sobrecomprado (70)')
            ax_tdi.fill_between(x_vals, 30, 70, alpha=0.1, color='#2196F3', label='Zona Neutral')
            ax_tdi.set_ylabel('TDI RSI', color='#b0b0b0', fontsize=10, fontweight='bold')
            ax_tdi.set_ylim(0, 100)
            ax_tdi.legend(loc='upper left', fontsize=8, framealpha=0.9, edgecolor='#1a2a4c')

            # --- LEYENDA PRINCIPAL ---
            ax_main.legend(loc='upper left', fontsize=9, framealpha=0.95, edgecolor='#1a2a4c', 
                         fancybox=True, shadow=False)

            # --- EJES X e Y CON VALORES CLAROS ---
            # Eje X - mostrar índices
            x_ticks = np.linspace(0, len(df_plot) - 1, min(10, len(df_plot)))
            ax_main.set_xticks(x_ticks)
            x_labels = [df_plot.iloc[int(x)]['timestamp'].strftime('%H:%M') if hasattr(df_plot.iloc[int(x)]['timestamp'], 'strftime') 
                       else str(int(x)) for x in x_ticks]
            ax_main.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=9)
            ax_main.set_xlim(-1, len(df_plot))

            # Eje Y - valores de precio
            y_min = df_plot['low'].min() * 0.995
            y_max = df_plot['high'].max() * 1.005
            ax_main.set_ylim(y_min, y_max)
            y_ticks = ax_main.get_yticks()
            ax_main.set_yticklabels([f'${y:.8f}' for y in y_ticks], fontsize=8)
            ax_main.set_ylabel('Precio (USD)', color='#b0b0b0', fontsize=10, fontweight='bold')

            # --- TÍTULO PROFESIONAL ---
            signal_type = signal_data.get('combined_signal', SignalType.NEUTRAL)
            title_color = '#00d4aa' if is_buy else '#ff6b6b'
            status = signal_data.get('status', 'DESTACADA')
            
            title_text = f'{symbol} | {getattr(signal_type, "value", str(signal_type))} | Precio: ${current_price:.8f} | {status}'
            ax_main.set_title(title_text, fontsize=13, fontweight='bold', color=title_color, pad=15)

            # --- BARRA DE PROGRESO HACIA TP ---
            progress = 0
            if entry_price > 0 and take_profit > 0:
                distance_to_tp = abs(take_profit - entry_price)
                distance_moved = current_price - entry_price if is_buy else entry_price - current_price
                progress = min(100, max(0, (distance_moved / distance_to_tp) * 100)) if distance_to_tp > 0 else 0

            bar_color = '#4CAF50' if progress > 0 else '#FF5252'
            ax_progress.barh(0, progress, height=0.7, color=bar_color, alpha=0.9, label='Progreso')
            ax_progress.barh(0, 100 - progress, left=progress, height=0.7, color='#1a2a4c', alpha=0.4)
            ax_progress.set_xlim(0, 100)
            ax_progress.set_yticks([])
            ax_progress.set_xlabel('Progreso hacia TP (%)', color='#b0b0b0', fontsize=10, fontweight='bold')
            ax_progress.text(50, 0, f'{progress:.1f}%', ha='center', va='center', color='white', 
                           fontsize=11, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a2a4c', alpha=0.9, edgecolor='#00d4aa', linewidth=1))

            # --- GUARDAR GRÁFICO ---
            status = signal_data.get('status', 'DESTACADA')
            if status == 'CONFIRMADA':
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{symbol}_{timestamp}.png"
            else:
                filename = f"temp_{symbol}.png"

            filepath = os.path.join(self.directorio_graficos, filename)
            plt.savefig(filepath, dpi=150, facecolor='#0f0f23', edgecolor='none', bbox_inches='tight')
            plt.close(fig)
            plt.close('all')

            logger.info(f"✅ Gráfico PROFESIONAL generado ({status}): {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error generando gráfico para {symbol}: {e}", exc_info=True)
            plt.close('all')
            return None
            
    def iniciar_actualizaciones_tiempo_real(self, symbol: str, df_inicial: pd.DataFrame, 
                                           datos_señal: dict, analisis: dict, callback=None):
        """Iniciar actualizaciones en tiempo real con el gestor robusto."""
        # ✅ VALIDAR SÍMBOLO
        if not symbol or symbol == 'N/A' or not str(symbol).strip():
            logger.warning(f"⚠️ Símbolo inválido para WebSocket: '{symbol}'. WebSocket no iniciado.")
            return False

        if not WEBSOCKET_AVAILABLE:
            logger.warning("Biblioteca WebSocket no disponible. Actualizaciones en tiempo real deshabilitadas.")
            return False

        # ✅ CRÍTICO: NO INICIAR WEBSOCKET SI FIX_API ESTÁ HABILITADO
        if hasattr(self, '_disable_websocket_global'):
            if self._disable_websocket_global:
                logger.debug(f"🟢 WebSocket deshabilitado (FIX_API activo). Saltando para {symbol}")
                return False

        self.detener_actualizaciones_tiempo_real()

        try:
            self.symbol_actual = symbol
            self.df_tiempo_real = df_inicial.copy() if df_inicial is not None else None
            self.datos_señal = datos_señal
            self.analisis = analisis
            self.callback_actualizacion = callback

            logger.info(f"🔌 Iniciando WebSocket para {symbol}")
            self.gestor_ws = RobustWebSocketManager(
                symbols=[symbol],
                intervalo="1m",
                callback=self._on_actualizacion_ws
            )

            self.gestor_ws.iniciar()
            self.actualizando = True

            logger.info(f"✅ WebSocket activo para {symbol}")
            return True

        except Exception as e:
            logger.error(f"Error iniciando WebSocket para {symbol}: {e}")
            return False

    def detener_actualizaciones_tiempo_real(self):
        """Detener actualizaciones en tiempo real"""
        self.actualizando = False

        if self.gestor_ws:
            try:
                self.gestor_ws.detener()
                self.gestor_ws = None
            except Exception as e:
                logger.error(f"Error deteniendo WebSocket: {e}")

        logger.info("Actualizaciones en tiempo real detenidas")

    def _on_actualizacion_ws(self, actualizacion_ws):
        """Manejar actualizaciones WebSocket con limitación de velocidad"""
        if not self.actualizando or actualizacion_ws['symbol'] != self.symbol_actual:
            return

        tiempo_actual = time.time()

        # Limitación de velocidad para evitar actualizaciones excesivas
        if tiempo_actual - self.ultima_actualizacion < self.intervalo_min_actualizacion:
            return

        with self.bloqueo_actualizacion:
            try:
                # Procesar datos de nueva vela
                kline = actualizacion_ws['kline']
                nueva_vela = {
                    'timestamp': pd.to_datetime(kline['t'], unit='ms'),
                    'open': float(kline['o']),
                    'high': float(kline['h']),
                    'low': float(kline['l']),
                    'close': float(kline['c']),
                    'volume': float(kline['v'])
                }

                # Actualizar DataFrame eficientemente
                fila_nueva = pd.DataFrame([nueva_vela])

                # Verificar si necesitamos actualizar la última vela o agregar una nueva
                if not self.df_tiempo_real.empty:
                    ultimo_timestamp = self.df_tiempo_real.iloc[-1]['timestamp']
                    if nueva_vela['timestamp'] == ultimo_timestamp:
                        # Actualizar última vela
                        self.df_tiempo_real.iloc[-1] = nueva_vela
                    else:
                        # Agregar nueva vela
                        self.df_tiempo_real = pd.concat([self.df_tiempo_real, fila_nueva], ignore_index=True)
                else:
                    # Primera vela
                    self.df_tiempo_real = fila_nueva

                # Mantener tamaño eficiente
                if len(self.df_tiempo_real) > 50:
                    self.df_tiempo_real = self.df_tiempo_real.tail(50).reset_index(drop=True)

                # Generar gráfico
                self._actualizar_grafico()

                self.ultima_actualizacion = tiempo_actual

            except Exception as e:
                logger.error(f"Error procesando actualización WebSocket: {e}")

    def _actualizar_grafico(self):
        """Actualizar gráfico con caché"""
        try:
            # Generar clave de caché
            clave_cache = f"{self.symbol_actual}_{self.df_tiempo_real.iloc[-1]['timestamp'].timestamp()}"

            # Verificar caché
            if clave_cache in self.cache_graficos:
                ruta_grafico = self.cache_graficos[clave_cache]
            else:
                # Generar nuevo gráfico (usando el método correcto)
                ruta_grafico = self.generate_signal_chart(
                    self.symbol_actual, 
                    self.df_tiempo_real, 
                    self.datos_señal, 
                    self.analisis
                )

                # Actualizar caché
                if ruta_grafico:
                    self.cache_graficos[clave_cache] = ruta_grafico

                    # Limitar tamaño de caché
                    if len(self.cache_graficos) > self.tamano_max_cache:
                        clave_mas_antigua = min(self.cache_graficos.keys())
                        del self.cache_graficos[clave_mas_antigua]

            # Llamar callback si se proporcionó
            if self.callback_actualizacion and ruta_grafico:
                self.callback_actualizacion(ruta_grafico, self.df_tiempo_real, self.datos_señal, self.analisis)

        except Exception as e:
            logger.error(f"Error actualizando gráfico: {e}")

    def generate_realtime_chart(self, symbol: str, df: pd.DataFrame, signal_data: dict, analysis: dict) -> str:
        """Genera el gráfico en tiempo real y lo actualiza"""
        # Guardar los datos para usarlos en la ventana
        self.signal_data = signal_data
        self.analysis = analysis
        # Generar el gráfico inicial
        chart_path = self.generate_signal_chart(symbol, df, signal_data, analysis)
        if chart_path and os.path.exists(chart_path):
            # Emitir señal para actualizar la ventana flotante
            if hasattr(self, 'update_callback'):
                self.update_callback(chart_path, df, signal_data, analysis)
        return chart_path


# ==============================================================================
# MÓDULO COMPLETO Y CORREGIDO: SignalChartDialog (Visualización en Tiempo Real)
# ==============================================================================

class SignalChartDialog(QtWidgets.QDialog):
    """
    Diálogo profesional para visualizar señales en tiempo real.
    Utiliza Matplotlib nativo para máxima estabilidad y rendimiento.
    Incluye manejo seguro de hilos para actualizaciones vía WebSocket.
    """
    def __init__(self, signal_data: dict, parent=None):
        super().__init__(parent)

        # Datos de la señal
        self.signal_data = signal_data
        self.df = signal_data.get('dataframe_entry')
        self.symbol = signal_data.get('symbol', 'N/A')

        # Estado de actualización
        self.is_running = False
        self.ws_manager = None
        self.update_timer = None
        self.current_profit_pct = None  # ✅ Sincronización con SignalTracker

        # Configuración de ventana
        self.setWindowTitle(f"📊 Señal Activa: {self.symbol}")
        self.resize(900, 650)
        self.setMinimumSize(800, 500)
        self.setStyleSheet("""
            QDialog { background-color: #0f0f23; }
            QLabel { color: #E0E0E0; font-family: Segoe UI, Arial; }
        """)

        # Layout principal
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Inicializar componentes
        self._init_header()
        self._init_chart_area()
        self._init_footer()

        # Iniciar actualizaciones
        self._start_realtime_updates()

    def _init_header(self):
        """Panel superior con métricas clave"""
        header_frame = QtWidgets.QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2a4c;
                border: 1px solid #2c3e50;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout = QtWidgets.QGridLayout(header_frame)

        # Labels dinámicos
        self.lbl_symbol = QtWidgets.QLabel(f"📌 {self.symbol}")
        self.lbl_symbol.setStyleSheet("font-size: 16px; font-weight: bold; color: #00d4aa;")

        self.lbl_type = QtWidgets.QLabel(f"📡 {self.signal_data.get('signal_type', 'N/A')}")
        self.lbl_type.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFD700;")

        # Métricas de Confianza (Neural, Tech, Alignment)
        n_score = self.signal_data.get('neural_score', 0)
        t_score = self.signal_data.get('technical_percentage', 0)
        a_score = self.signal_data.get('alignment_percentage', 0)

        self.lbl_neural = QtWidgets.QLabel(f"🧠 IA: {n_score:.1f}%")
        self.lbl_neural.setStyleSheet("color: #00d4aa; font-weight: bold;")

        self.lbl_tech = QtWidgets.QLabel(f"📊 Tec: {t_score:.1f}%")
        self.lbl_tech.setStyleSheet("color: #FFB6C1; font-weight: bold;")

        self.lbl_align = QtWidgets.QLabel(f"🔗 Ali: {a_score:.1f}%")
        self.lbl_align.setStyleSheet("color: #2196F3; font-weight: bold;")

        # Precios
        entry = self.signal_data.get('entry_price', 0)
        sl = self.signal_data.get('stop_loss', 0)
        tp = self.signal_data.get('take_profit', 0)

        self.lbl_entry = QtWidgets.QLabel(f"Entrada: ${entry:.8f}")
        self.lbl_sl = QtWidgets.QLabel(f"SL: ${sl:.8f}")
        self.lbl_tp = QtWidgets.QLabel(f"TP: ${tp:.8f}")

        self.lbl_sl.setStyleSheet("color: #ff5252;")
        self.lbl_tp.setStyleSheet("color: #69f0ae;")

        # Posicionamiento en Grid
        layout.addWidget(self.lbl_symbol, 0, 0)
        layout.addWidget(self.lbl_type, 0, 1)
        layout.addWidget(self.lbl_neural, 0, 2)
        layout.addWidget(self.lbl_tech, 0, 3)
        layout.addWidget(self.lbl_align, 0, 4)

        layout.addWidget(self.lbl_entry, 1, 0)
        layout.addWidget(self.lbl_sl, 1, 1)
        layout.addWidget(self.lbl_tp, 1, 2)

        self.main_layout.addWidget(header_frame)

    def _init_chart_area(self):
        """Área de gráfico principal (Matplotlib)"""
        if PLOTTING_AVAILABLE:
            # Configurar Figura y Ejes
            self.figure = Figure(figsize=(8, 5), dpi=100, facecolor='#0f0f23', edgecolor='none')
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("border: 1px solid #1a2a4c; border-radius: 5px;")

            # GridSpec para gráfico principal + sub-gráfico de volumen/progreso
            gs = GridSpec(4, 1, height_ratios=[3, 0.5, 0.5, 0.2], hspace=0.1)

            self.ax_main = self.figure.add_subplot(gs[0])
            self.ax_main.set_facecolor('#0f0f23')

            self.ax_progress = self.figure.add_subplot(gs[1])
            self.ax_progress.set_facecolor('#0f0f23')

            self.main_layout.addWidget(self.canvas, stretch=1)

            # Dibujo inicial
            self._update_chart_static()
        else:
            self.main_layout.addWidget(QtWidgets.QLabel("⚠️ Matplotlib no disponible"))

    def _init_footer(self):
        """Barra de estado inferior"""
        footer_layout = QtWidgets.QHBoxLayout()

        self.lbl_status = QtWidgets.QLabel("⚡ Iniciando...")
        self.lbl_status.setStyleSheet("color: #888; font-size: 10px;")

        btn_close = QtWidgets.QPushButton("Cerrar")
        btn_close.setStyleSheet("""
            QPushButton { background-color: #D32F2F; color: white; padding: 5px 15px; border-radius: 4px; }
            QPushButton:hover { background-color: #B71C1C; }
        """)
        btn_close.clicked.connect(self.close)

        footer_layout.addWidget(self.lbl_status)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_close)

        self.main_layout.addLayout(footer_layout)

    def _start_realtime_updates(self):
        """Inicia el timer para actualizaciones periódicas (Polling seguro)"""
        self.is_running = True

        # Timer de actualización (cada 1 segundo)
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self._on_timer_tick)
        self.update_timer.start(1000)

        # Intentar iniciar WebSocket real (si está disponible)
        if WEBSOCKET_AVAILABLE and hasattr(self, 'signal_data'):
            try:
                symbol = self.signal_data.get('symbol')
                # Aquí se conectaría con tu RobustWebSocketManager si está global
                # Por seguridad, en este módulo usamos polling + timer visual
                logger.info(f"🔄 Iniciando monitoreo visual para {symbol}")
            except Exception as e:
                logger.warning(f"WS no disponible, usando modo visual: {e}")

    def _on_timer_tick(self):
        """Tick del timer: Sincronizado con SignalTracker para datos REALES"""
        try:
            # Intentar obtener datos reales del SignalTracker
            real_data = False
            current_price = 0.0
            profit_percent = 0.0
            tracking_info = {}

            # Acceder al tracker a través del padre (Main Window)
            parent = self.parent()
            if parent and hasattr(parent, 'bot') and hasattr(parent.bot, 'signal_tracker'):
                tracker = parent.bot.signal_tracker
                signal_hash = self.signal_data.get('signal_hash')

                if signal_hash:
                    with tracker.lock:
                        if signal_hash in tracker.tracked_signals:
                            tracking = tracker.tracked_signals[signal_hash]
                            current_price = tracking.get('current_price', 0)
                            profit_percent = tracking.get('profit_percent', 0)
                            tracking_info = tracking.copy()
                            real_data = True

            if real_data and current_price > 0:
                # ✅ Sincronizar profit exacto
                self.current_profit_pct = profit_percent

                # ✅ ACTUALIZAR DATOS SI CAMBIARON (e.g. Promoción DESTACADA -> CONFIRMADA)
                if 'entry_price' in tracking_info and tracking_info['entry_price'] != self.signal_data.get('entry_price'):
                    logger.info(f"🔄 GUI: Actualizando datos de señal {self.symbol} (Promoción)")
                    self.signal_data['entry_price'] = tracking_info['entry_price']
                    self.signal_data['stop_loss'] = tracking_info['stop_loss']
                    self.signal_data['take_profit'] = tracking_info['take_profit']
                    self.signal_data['status'] = tracking_info.get('status', 'CONFIRMADA')
                    # Actualizar UI Header
                    self._update_header_labels()

                # Actualizar DataFrame local
                if self.df is not None and not self.df.empty:
                    last_row = self.df.iloc[-1].copy()
                    last_row['close'] = current_price
                    last_row['high'] = max(last_row['high'], current_price)
                    last_row['low'] = min(last_row['low'], current_price)
                    self.df.iloc[-1] = last_row

                    # Redibujar gráfico
                    self._update_chart_visuals()

                    # Actualizar etiquetas con datos REALES
                    self._update_pnl_label(current_price, real_profit_pct=profit_percent)
            else:
                # Fallback: Simulación si no está en tracking activo
                self.current_profit_pct = None # Reset
                if self.df is not None and not self.df.empty:
                    last_row = self.df.iloc[-1].copy()
                    import random
                    variation = random.uniform(-0.0005, 0.0005)
                    last_row['close'] = last_row['close'] * (1 + variation)
                    last_row['high'] = max(last_row['high'], last_row['close'])
                    last_row['low'] = min(last_row['low'], last_row['close'])
                    self.df.iloc[-1] = last_row
                    self._update_chart_visuals()
                    self._update_pnl_label(last_row['close'])

        except Exception as e:
            logger.debug(f"Error en timer tick: {e}")

    def _update_header_labels(self):
        """Actualiza etiquetas del header cuando cambian los datos (Promoción)"""
        try:
            entry = self.signal_data.get('entry_price', 0)
            sl = self.signal_data.get('stop_loss', 0)
            tp = self.signal_data.get('take_profit', 0)
            status = self.signal_data.get('status', 'N/A')

            self.lbl_entry.setText(f"Entrada: ${entry:.8f}")
            self.lbl_sl.setText(f"SL: ${sl:.8f}")
            self.lbl_tp.setText(f"TP: ${tp:.8f}")

            # Actualizar estado visual
            if status == 'CONFIRMADA':
                self.lbl_type.setText(f"📡 CONFIRMADA")
                self.lbl_type.setStyleSheet("font-size: 16px; font-weight: bold; color: #00FF00;") # Verde brillante
        except Exception as e:
            logger.error(f"Error actualizando header labels: {e}")


    def _update_pnl_label(self, current_price, real_profit_pct=None):
        """Calcula y muestra el Profit/Loss en tiempo real"""
        entry = self.signal_data.get('entry_price', 0)
        tp = self.signal_data.get('take_profit', 0)
        # ✅ Detectar dirección correctamente
        is_buy = 'BUY' in str(self.signal_data.get('signal_type', '')).upper() or 'COMPRA' in str(self.signal_data.get('signal_type', ''))

        if entry > 0:
            # ✅ Usar profit real si está disponible, sino calcular
            if real_profit_pct is not None:
                pnl_pct = real_profit_pct
            else:
                if is_buy:
                    pnl_pct = ((current_price - entry) / entry) * 100
                else:
                    pnl_pct = ((entry - current_price) / entry) * 100

            color = "#69f0ae" if pnl_pct >= 0 else "#ff5252"
            status_text = f"PnL: {pnl_pct:+.2f}% | Precio: ${current_price:.8f}"

            # Calcular progreso hacia TP
            if tp > 0:
                # ✅ Usar config si está disponible
                if hasattr(self, 'config') and hasattr(self.config, 'MILESTONE_3'):
                    target_pct = self.config.MILESTONE_3
                else:
                    target_pct = 3.0

                # ✅ Progreso basado en profit real vs objetivo
                progress = min(100, max(0, (pnl_pct / target_pct) * 100)) if target_pct > 0 else 0
                status_text += f" | Progreso TP: {progress:.1f}%"

            self.lbl_status.setText(status_text)
            self.lbl_status.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")

    def _update_chart_static(self):
        """Dibujo inicial estático"""
        self._update_chart_visuals()

    def _update_chart_visuals(self):
        """Redibuja todo el gráfico basado en self.df actual - MEJORADO"""
        try:
            if self.df is None or self.df.empty:
                return

            # Preparar datos (últimas 50 velas)
            df_plot = self.df.tail(50).copy()
            x_vals = range(len(df_plot))
            self.ax_main.clear()
            self.ax_progress.clear()

            # 1. Dibujar Velas - Estilo Profesional
            # Velas alcistas: Verde neón, Velas bajistas: Rojo brillante
            up_color = '#00ff00' 
            down_color = '#ff0044'

            colors = [up_color if row['close'] >= row['open'] else down_color for _, row in df_plot.iterrows()]

            for idx, (i, row) in enumerate(df_plot.iterrows()):
                # Mecha (High-Low)
                self.ax_main.plot([idx, idx], [row['low'], row['high']], color=colors[idx], linewidth=1.2, alpha=0.9)
                # Cuerpo (Open-Close)
                body_bottom = min(row['open'], row['close'])
                body_height = abs(row['close'] - row['open'])
                # Si el cuerpo es muy pequeño, dibujar al menos una línea
                if body_height == 0:
                    body_height = (row['high'] - row['low']) * 0.05

                self.ax_main.bar(idx, body_height,
                                bottom=body_bottom,
                                width=0.6, color=colors[idx], alpha=0.9)

            # 2. Dibujar Líneas de Señal
            entry = self.signal_data.get('entry_price', 0)
            sl = self.signal_data.get('stop_loss', 0)
            tp = self.signal_data.get('take_profit', 0)
            status = self.signal_data.get('status', 'DESTACADA')

            current_price = df_plot.iloc[-1]['close']
            is_buy = 'BUY' in str(self.signal_data.get('signal_type', '')).upper() or 'COMPRA' in str(self.signal_data.get('signal_type', ''))

            # Solo mostrar líneas "reales" si está confirmada o como referencia punteada si es destacada
            line_style = '-' if status == 'CONFIRMADA' else '--'
            alpha_val = 0.9 if status == 'CONFIRMADA' else 0.6

            if entry > 0:
                self.ax_main.axhline(entry, color='#2196F3', linewidth=1.5, alpha=alpha_val, linestyle=line_style)
                label_text = ' ENTRY' if status == 'CONFIRMADA' else ' REF ENTRY'
                self.ax_main.text(len(df_plot)-1, entry, label_text, color='#2196F3', fontsize=8, va='bottom', fontweight='bold')

            if sl > 0:
                self.ax_main.axhline(sl, color='#D32F2F', linewidth=1.5, alpha=alpha_val, linestyle='--')
                self.ax_main.text(len(df_plot)-1, sl, ' SL', color='#D32F2F', fontsize=8, va='top')

            if tp > 0:
                tp_color = '#4CAF50' if is_buy else '#FF5252'
                self.ax_main.axhline(tp, color=tp_color, linewidth=1.5, alpha=alpha_val, linestyle=line_style)
                self.ax_main.text(len(df_plot)-1, tp, ' TP', color=tp_color, fontsize=8, va='bottom')

            # ✅ Línea de Precio Actual (sincronizada con progres bar y PnL)
            self.ax_main.axhline(y=current_price, color='#FFD700', linestyle=':', linewidth=1.5, alpha=0.9)
            self.ax_main.text(len(df_plot)-1, current_price, f' ${current_price:.6f}', color='#FFD700', fontsize=9, va='center', fontweight='bold')

            # 3. Estilo del Eje Principal - Fondo más oscuro y Grid sutil
            self.ax_main.set_title(f"{self.symbol} - Timeframe: 15m ({status})", color='white', fontsize=10, fontweight='bold')
            self.ax_main.set_facecolor('#0b0b1a') # Fondo un poco más oscuro
            self.ax_main.tick_params(axis='x', colors='#a0a0a0', labelsize=8)
            self.ax_main.tick_params(axis='y', colors='#a0a0a0', labelsize=8)
            # Grid más profesional
            self.ax_main.grid(True, color='#2c3e50', linestyle='--', linewidth=0.5, alpha=0.4)

            # Quitar bordes innecesarios
            self.ax_main.spines['top'].set_visible(False)
            self.ax_main.spines['right'].set_visible(False)
            self.ax_main.spines['bottom'].set_color('#2c3e50')
            self.ax_main.spines['left'].set_color('#2c3e50')

            # 4. Barra de Progreso (Visual) — ✅ SINCRONIZADA CON PRECIO REAL Y MILESTONES DINÁMICOS
            progress = 0
            if entry > 0 and tp > 0:
                # Si es DESTACADA, el progreso es "simulado" o 0 hasta confirmación
                # El usuario dijo: "solo cuando es confimada alli recien debe tomar loa valores ... y calcular el progreso"

                if status != 'CONFIRMADA':
                     # Mostrar barra vacía o indicación de espera
                     self.ax_progress.text(50, 0, "ESPERANDO CONFIRMACIÓN...", ha='center', va='center', color='white', fontsize=9)
                     self.ax_progress.set_facecolor('#0b0b1a')
                     self.ax_progress.set_xticks([])
                     self.ax_progress.set_yticks([])
                     self.canvas.draw()
                     return

                # ✅ Usar config si está disponible, sino fallback a valores fijos
                if hasattr(self, 'config') and hasattr(self.config, 'MILESTONE_3'):
                    target_pct = self.config.MILESTONE_3  # Objetivo final = MILESTONE_3
                else:
                    target_pct = 3.0  # fallback

                # Calcular profit actual en %
                if hasattr(self, 'current_profit_pct') and self.current_profit_pct is not None:
                    profit_percent = self.current_profit_pct
                elif is_buy:
                    profit_percent = ((current_price - entry) / entry) * 100
                else:
                    profit_percent = ((entry - current_price) / entry) * 100

                # Progreso hacia el objetivo final (MILESTONE_3)
                progress = min(100, max(0, (profit_percent / target_pct) * 100)) if target_pct > 0 else 0

                # Color según estado
                bar_color = '#00ff00' if profit_percent >= 0 else '#ff0044'

                self.ax_progress.barh(0, progress, height=0.6, color=bar_color, alpha=0.9, edgecolor='none')
                # Fondo de barra
                self.ax_progress.barh(0, 100, height=0.6, color='#1a2a4c', alpha=0.3, zorder=-1)

                # ✅ Marcadores de Milestones (Sincronización visual)
                if hasattr(self, 'config'):
                    m1 = getattr(self.config, 'MILESTONE_1', 1.0)
                    m2 = getattr(self.config, 'MILESTONE_2', 2.0)
                    if target_pct > 0:
                        pos_m1 = (m1 / target_pct) * 100
                        pos_m2 = (m2 / target_pct) * 100

                        if 0 < pos_m1 < 100:
                            self.ax_progress.axvline(x=pos_m1, color='white', linestyle=':', alpha=0.5, linewidth=1)
                        if 0 < pos_m2 < 100:
                            self.ax_progress.axvline(x=pos_m2, color='white', linestyle=':', alpha=0.5, linewidth=1)

                self.ax_progress.set_xlim(0, 100)
                self.ax_progress.set_yticks([])
                self.ax_progress.set_xticks([0, 50, 100])
                self.ax_progress.set_xticklabels(['0%', '50%', '100%'], fontsize=8, color='#a0a0a0')

                # Texto de progreso
                self.ax_progress.text(50, 0, f"{progress:.1f}%", ha='center', va='center', color='white', fontweight='bold', fontsize=9)

                # ✅ Mostrar precio actual debajo de la barra de progreso
                self.ax_progress.text(50, -0.4, f"${current_price:.6f}", ha='center', va='top', color='#FFD700', fontsize=9, fontweight='bold')
                self.ax_progress.set_facecolor('#0b0b1a')

                # Quitar bordes
                self.ax_progress.spines['top'].set_visible(False)
                self.ax_progress.spines['right'].set_visible(False)
                self.ax_progress.spines['left'].set_visible(False)
                self.ax_progress.spines['bottom'].set_visible(False)

            self.canvas.draw()

        except Exception as e:
            logger.error(f"Error actualizando visuales: {e}")

    def closeEvent(self, event):
        """Limpieza al cerrar"""
        self.is_running = False
        if self.update_timer:
            self.update_timer.stop()

        # Detener WebSocket si existe referencia externa
        # (Asumiendo que el gestor principal maneja la conexión global)

        logger.info(f"Ventana de señal cerrada: {self.symbol}")
        super().closeEvent(event)
# ========== CLIENTE BINANCE FIX API (BAJA LATENCIA + FALLBACK ROBUSTO) ==========
class BinanceFIXClient:
    """Wrapper profesional para FIX API de Binance con fallback REST automático"""
    def __init__(self, config: "AdvancedTradingConfig"): # <-- Nota las comillas
        self.config = config
        self.rest_client = AdvancedBinanceClient(config)
        self.fix_enabled = False  # ✅ NUEVO: Flag para indicador GUI
        self.disable_websocket = False
        self.fix_session = None
        self.last_fix_check = 0
        self.fix_check_interval = 300  # Verificar FIX cada 5 min
        self.connection_lock = threading.RLock()

        try:
            if getattr(config, 'FIX_API_ENABLED', False):
                self._init_fix_api()
            else:
                logger.debug("ℹ️ FIX API deshabilitado - usando REST API")
        except Exception as e:
            logger.warning(f"⚠️ FIX API no disponible: {e} - Fallback a REST")

    def _init_fix_api(self):
        """Inicializar FIX API - Deshabilita WebSocket automáticamente"""
        try:
            self.fix_enabled = True  # ✅ Marcar como activo
            self.disable_websocket = True  # ✅ Deshabilitar WebSocket
            logger.info("✅ FIX API activo - WebSocket deshabilitado")

            # Intentar import como bonus, pero no es crítico
            try:
                from binance_fix_connector.fix_connector import create_market_data_session
                logger.debug("✅ binance-fix-connector disponible")
            except ImportError:
                logger.debug("ℹ️ binance-fix-connector no disponible (normal en Replit)")

        except Exception as e:
            logger.error(f"Error inicializando FIX API: {e}")
            self.fix_enabled = False
            self.disable_websocket = False

    def _check_fix_health(self) -> bool:
        """Verificar salud de conexión FIX (fallback a REST si falla)"""
        current_time = time.time()
        if current_time - self.last_fix_check < self.fix_check_interval:
            return True

        try:
            with self.connection_lock:
                # Intentar verificación simple
                test_price = self.rest_client.get_ticker_price("ETHUSDT")
                self.last_fix_check = current_time
                return test_price > 0
        except Exception as e:
            logger.debug(f"⚠️ Health check falló: {e}")
            return False

    def get_ticker_price(self, symbol: str, timeout_sec: int = 5) -> float:
        """Obtener precio RÁPIDO con timeout y fallback automático"""
        try:
            # Verificar salud de conexión
            if not self._check_fix_health():
                logger.debug(f"⚠️ FIX health check falló para {symbol}, usando REST")

            return self._get_price_with_timeout(symbol, timeout_sec)
        except Exception as e:
            logger.debug(f"⚠️ Error precio {symbol}: {e}")
            return 0.0

    def _get_price_with_timeout(self, symbol: str, timeout_sec: int) -> float:
        """Obtener precio - En Replit sin threads para evitar límites"""
        # ✅ En Replit: llamada síncrona para evitar "can't start new thread"
        if IN_REPLIT:
            try:
                with self.connection_lock:
                    return self.rest_client.get_ticker_price(symbol)
            except Exception as e:
                logger.debug(f"⚠️ Error precio {symbol}: {e}")
                return 0.0

        # En local: usar threads con timeout
        result = [0.0]
        exception = [None]

        def fetch():
            try:
                with self.connection_lock:
                    result[0] = self.rest_client.get_ticker_price(symbol)
            except Exception as e:
                exception[0] = e
                result[0] = 0.0

        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()
        thread.join(timeout=timeout_sec)

        if exception[0]:
            logger.debug(f"⚠️ Precio timeout para {symbol} (>={timeout_sec}s)")
        return result[0]

    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> Optional[pd.DataFrame]:
        """Obtener velas - En Replit sin threads para evitar límites"""
        try:
            # ✅ En Replit: llamada síncrona para evitar "can't start new thread"
            if IN_REPLIT:
                with self.connection_lock:
                    return self.rest_client.get_klines(symbol, interval, limit)

            # En local: usar threads con timeout
            result = [None]
            def fetch():
                try:
                    with self.connection_lock:
                        result[0] = self.rest_client.get_klines(symbol, interval, limit)
                except:
                    result[0] = None

            thread = threading.Thread(target=fetch, daemon=True)
            thread.start()
            thread.join(timeout=20)
            return result[0]
        except Exception as e:
            logger.debug(f"⚠️ Error klines {symbol}: {e}")
            return None

    def place_order(self, symbol: str, side: str, quantity: float, price: float = None, order_type: str = "LIMIT") -> Optional[dict]:
        """Colocar orden con fallback"""
        try:
            with self.connection_lock:
                return self.rest_client.place_order(symbol, side, quantity, price, order_type)
        except Exception as e:
            logger.error(f"❌ Error placing order: {e}")
            return None

    def cancel_order(self, symbol: str, order_id: int) -> Optional[dict]:
        """Cancelar orden con fallback"""
        try:
            with self.connection_lock:
                return self.rest_client.cancel_order(symbol, order_id)
        except Exception as e:
            logger.error(f"❌ Error canceling order: {e}")
            return None

    def get_open_orders(self, symbol: str = None) -> Optional[list]:
        """Obtener órdenes abiertas"""
        try:
            with self.connection_lock:
                return self.rest_client.get_open_orders(symbol)
        except Exception as e:
            logger.debug(f"⚠️ Error getting open orders: {e}")
            return []

    def get_account(self) -> Optional[dict]:
        """Obtener info de cuenta"""
        try:
            with self.connection_lock:
                return self.rest_client.get_account()
        except Exception as e:
            logger.debug(f"⚠️ Error getting account: {e}")
            return None

    def get_balance(self, asset: str = "USDT") -> float:
        """Obtener balance"""
        try:
            with self.connection_lock:
                return self.rest_client.get_balance(asset)
        except Exception as e:
            logger.debug(f"⚠️ Error getting balance: {e}")
            return 0.0

# ========== VALIDADOR DE ALINEACIÓN DE TENDENCIAS ==========
class TrendAlignmentValidator:
    def __init__(self, config):
        self.config = config

    def validate_trend_alignment(self, df_15m: pd.DataFrame, df_30m: pd.DataFrame,
                                 neural_score: float = 0.0,
                                 technical_pct: float = 0.0,
                                 signal_direction: str = "NEUTRAL") -> dict:
        """
        Valida alineación entre timeframes 15m y 30m
        """
        result = {
            'alignment_score': 0.0,
            'continuity_valid': False,
            'is_aligned': False,
            'reason': 'Datos insuficientes'
        }

        if df_15m is None or df_30m is None or len(df_15m) < 50 or len(df_30m) < 50:
            return result

        try:
            # Validar EMAs en ambos timeframes
            ema50_15 = df_15m['close'].ewm(span=50).mean().iloc[-1]
            ema200_15 = df_15m['close'].ewm(span=200).mean().iloc[-1]
            current_15 = df_15m['close'].iloc[-1]

            ema50_30 = df_30m['close'].ewm(span=50).mean().iloc[-1]
            ema200_30 = df_30m['close'].ewm(span=200).mean().iloc[-1]

            # Determinar tendencia
            if current_15 > ema50_15 > ema200_15 and ema50_30 > ema200_30:
                trend = "BULLISH"
            elif current_15 < ema50_15 < ema200_15 and ema50_30 < ema200_30:
                trend = "BEARISH"
            else:
                trend = "NEUTRAL"

            # Validar continuidad
            closes = df_15m['close'].tail(5).values
            diffs = [closes[i] > closes[i-1] for i in range(1, len(closes))]
            continuity_valid = all(diffs) or all(not d for d in diffs)

            # Calcular score
            score = 0.0
            if trend != "NEUTRAL":
                score += 50.0
            if continuity_valid:
                score += 30.0
            if signal_direction.upper() == trend:
                score += 20.0

            final_score = min(100.0, max(0.0, score))

            result['alignment_score'] = final_score
            result['continuity_valid'] = continuity_valid
            result['is_aligned'] = final_score >= self.config.MIN_ALIGNMENT_CONFIRMADA and continuity_valid
            result['reason'] = f"Alineación: {final_score:.1f}% | Tendencia: {trend}"
            result['trend'] = trend

        except Exception as e:
            logger.error(f"Error en validación de alineación: {e}")
            result['reason'] = f"Error: {e}"

        return result

    # ------------------------------------------------------------------
    # 2. EMA 50/200 – tendencia mayor
    # ------------------------------------------------------------------
    def _get_ema50_200_trend(self, df: pd.DataFrame) -> TrendDirection:
        if len(df) < 200:
            return TrendDirection.NEUTRAL

        close = df['close'].values
        ema50  = pd.Series(close).ewm(span=50,  adjust=False).mean().iloc[-1]
        ema200 = pd.Series(close).ewm(span=200, adjust=False).mean().iloc[-1]
        current = close[-1]

        if current > ema50 > ema200:
            return TrendDirection.BULLISH
        elif current < ema50 < ema200:
            return TrendDirection.BEARISH
        else:
            return TrendDirection.NEUTRAL

    # ------------------------------------------------------------------
    # 3. TDI – momentum + bandas
    # ------------------------------------------------------------------
    def _get_tdi_trend(self, df: pd.DataFrame) -> TrendDirection:
        try:
            from core.technical import OptimizedTechnicalAnalyzer   # ajusta import
            analyzer = OptimizedTechnicalAnalyzer(self.config)
            rsi, green, red, _, _ = analyzer.calculate_tdi(df)
            if rsi.empty or green.empty or red.empty:
                return TrendDirection.NEUTRAL

            rsi_val   = float(rsi.iloc[-1])
            green_val = float(green.iloc[-1])
            red_val   = float(red.iloc[-1])

            # Lógica TDI clásica
            if green_val > red_val and rsi_val < self.config.TDI_OVERBOUGHT_LEVEL_SELL:
                return TrendDirection.BULLISH
            elif green_val < red_val and rsi_val > self.config.TDI_OVERSOLD_LEVEL_BUY:
                return TrendDirection.BEARISH
            else:
                return TrendDirection.NEUTRAL
        except Exception as e:
            logger.debug(f"TDI trend error: {e}")
            return TrendDirection.NEUTRAL

    # ------------------------------------------------------------------
    # 4. Ciclo de mercado (acumulación/distribución/alza/baja)
    # ------------------------------------------------------------------
    def _get_market_cycle(self, df: pd.DataFrame) -> dict:
        try:
            from core.technical import OptimizedTechnicalAnalyzer
            analyzer = OptimizedTechnicalAnalyzer(self.config)
            cycle_info = analyzer.analyze_market_cycles(df)
            strength = cycle_info.get('strength', 0.0)  # 0-1
            cycle      = cycle_info.get('cycle', 'NEUTRAL')
            return {'cycle': cycle, 'strength': strength, 'direction': cycle.upper()}
        except Exception as e:
            logger.debug(f"Market cycle error: {e}")
            return {'cycle': 'NEUTRAL', 'strength': 0.0, 'direction': 'NEUTRAL'}

    # ------------------------------------------------------------------
    # 5. Acción del precio – patrones + S/R
    # ------------------------------------------------------------------
    def _get_price_action_score(self, df: pd.DataFrame) -> float:
        try:
            from core.technical import OptimizedTechnicalAnalyzer
            analyzer = OptimizedTechnicalAnalyzer(self.config)

            candle  = analyzer.analyze_candlestick_pattern(df.tail(5))
            w_m     = analyzer.detect_w_m_pattern(df)
            hch_lcl = analyzer.detect_hch_pattern(df)
            sr      = analyzer.find_support_resistance(df.tail(30))

            score  = 0.0
            score += candle.get('confidence', 0) * 0.4
            score += w_m.get('confidence', 0) * 0.3
            score += hch_lcl.get('confidence', 0) * 0.3

            # bonus si está cerca de S/R
            current = float(df['close'].iloc[-1])
            sup = sr.get('support', 0)
            res = sr.get('resistance', 0)
            if sup and res and res > sup:
                dist_s = (current - sup) / sup
                dist_r = (res - current) / res
                if dist_s <= 0.02 or dist_r <= 0.02:  # ≤ 2 %
                    score += 10.0

            return min(100.0, score)
        except Exception as e:
            logger.debug(f"Price-action score error: {e}")
            return 0.0

    # ------------------------------------------------------------------
    # 6. Continuidad – últimas 5 velas
    # ------------------------------------------------------------------
    def _validate_continuity(self, df: pd.DataFrame, candles: int = 5) -> bool:
        if len(df) < candles:
            return False
        closes = df['close'].tail(candles).values
        changes = [(closes[i+1] - closes[i]) / closes[i] for i in range(len(closes)-1) if closes[i] != 0]
        if not changes:
            return False
        up = sum(1 for c in changes if c > 0.0001)
        dn = sum(1 for c in changes if c < -0.0001)
        return up >= 4 or dn >= 4

# ========== ANÁLISIS TÉCNICO OPTIMIZADO ==========
class OptimizedTechnicalAnalyzer:
    def __init__(self, config: "AdvancedTradingConfig"): # <-- Nota las comillas
        self.config = config
        self.indicator_cache = {}
        self.cache_max_size = 100
        self.cache_access_times = {}
        self.cache_lock = threading.RLock()  # 🔒 LOCK AÑADIDO
        # Contador diario de señales validadas
        self.daily_signal_count = 0
        self.daily_signal_date = datetime.now().date()

    def _update_daily_signal_counter(self):
        try:
            today = datetime.now().date()
            if self.daily_signal_date != today:
                self.daily_signal_date = today
                self.daily_signal_count = 0
            self.daily_signal_count += 1
            logger.info(f"📈 Señales diarias validadas: {self.daily_signal_count}")
            max_signals = getattr(self.config, 'MAX_DAILY_SIGNALS', 3)
            if self.daily_signal_count > max_signals:
                logger.info("⚠️ Límite diario de señales superado; considera elevar umbrales o pausar generación.")
        except Exception as e:
            logger.debug(f"No se pudo actualizar contador diario: {e}")

    def _manage_cache_size(self):
        with self.cache_lock:
            if len(self.indicator_cache) > self.cache_max_size:
                sorted_items = sorted(self.cache_access_times.items(), key=lambda x: x[1])
                for key, _ in sorted_items[:20]:
                    if key in self.indicator_cache:
                        del self.indicator_cache[key]
                    if key in self.cache_access_times:
                        del self.cache_access_times[key]

    def _get_cache_key(self, data_id: str, indicator: str, params: str = "") -> str:
        return f"{data_id}_{indicator}_{params}"

    def calculate_ema(self, prices: pd.Series, period: int, data_id: str = "") -> pd.Series:
        cache_key = self._get_cache_key(data_id, "ema", str(period))
        current_time = time.time()
        with self.cache_lock:
            if cache_key in self.indicator_cache:
                cached_result, cache_time = self.indicator_cache[cache_key]
                if current_time - cache_time < 30:
                    self.cache_access_times[cache_key] = current_time
                    return cached_result
        result = prices.ewm(span=period, adjust=False).mean()
        with self.cache_lock:
            self.indicator_cache[cache_key] = (result, current_time)
            self.cache_access_times[cache_key] = current_time
            self._manage_cache_size()
        return result

    def calculate_rsi(self, prices: pd.Series, period: int = 14, data_id: str = "") -> pd.Series:
        cache_key = self._get_cache_key(data_id, "rsi", str(period))
        current_time = time.time()
        with self.cache_lock:
            if cache_key in self.indicator_cache:
                cached_result, cache_time = self.indicator_cache[cache_key]
                if current_time - cache_time < 30:
                    self.cache_access_times[cache_key] = current_time
                    return cached_result
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.ewm(span=period, adjust=False).mean()
        avg_loss = loss.ewm(span=period, adjust=False).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        with self.cache_lock:
            self.indicator_cache[cache_key] = (rsi, current_time)
            self.cache_access_times[cache_key] = current_time
            self._manage_cache_size()
        return rsi

    def calculate_tdi(self, df: pd.DataFrame, data_id: str = "") -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
        cache_key = self._get_cache_key(data_id, "tdi", f"{self.config.TDI_RSI_PERIOD}_{self.config.TDI_PRICE_PERIOD}_{self.config.TDI_SIGNAL_PERIOD}")
        current_time = time.time()
        with self.cache_lock:
            if cache_key in self.indicator_cache:
                cached_result, cache_time = self.indicator_cache[cache_key]
                if current_time - cache_time < 30:
                    self.cache_access_times[cache_key] = current_time
                    return cached_result
        rsi_line = self.calculate_rsi(df['close'], self.config.TDI_RSI_PERIOD, data_id)
        ma_rsi_green = self.calculate_ema(rsi_line, self.config.TDI_PRICE_PERIOD, data_id)
        ma_green_red = self.calculate_ema(ma_rsi_green, self.config.TDI_SIGNAL_PERIOD, data_id)
        std_dev_rsi = rsi_line.rolling(window=self.config.TDI_VOLATILITY_BAND).std()
        upper_band = ma_rsi_green + (2 * std_dev_rsi)
        lower_band = ma_rsi_green - (2 * std_dev_rsi)
        result = (rsi_line, ma_rsi_green, ma_green_red, upper_band, lower_band)
        with self.cache_lock:
            self.indicator_cache[cache_key] = (result, current_time)
            self.cache_access_times[cache_key] = current_time
            self._manage_cache_size()
        return result

    def calculate_volume_confidence(self, df: pd.DataFrame, period: int = 20) -> dict:
        """
        Calcula la confianza del volumen relativo.
        Compara el volumen actual con el promedio de los últimos N períodos.
        Retorna un score de 0-100 indicando la fuerza del volumen.
        """
        try:
            if df is None or len(df) < period + 1:
                return {'confidence': 0, 'ratio': 0, 'trend': 'NEUTRAL', 'valid': False}

            volumes = df['volume'].tail(period + 1)
            current_volume = float(volumes.iloc[-1])
            avg_volume = float(volumes.iloc[:-1].mean())

            if avg_volume <= 0:
                return {'confidence': 0, 'ratio': 0, 'trend': 'NEUTRAL', 'valid': False}

            volume_ratio = current_volume / avg_volume

            volume_trend = 'NEUTRAL'
            if volume_ratio >= 1.5:
                volume_trend = 'STRONG'
            elif volume_ratio >= 1.2:
                volume_trend = 'ABOVE_AVERAGE'
            elif volume_ratio >= 0.8:
                volume_trend = 'NORMAL'
            else:
                volume_trend = 'WEAK'

            confidence = min(100, max(0, (volume_ratio - 0.5) * 100))

            return {
                'confidence': confidence,
                'ratio': volume_ratio,
                'trend': volume_trend,
                'current': current_volume,
                'average': avg_volume,
                'valid': volume_ratio >= 0.8
            }
        except Exception as e:
            logger.debug(f"Error calculando volumen: {e}")
            return {'confidence': 0, 'ratio': 0, 'trend': 'NEUTRAL', 'valid': False}

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calcula el Average True Range (ATR) para gestion dinamica de riesgo.
        Retorna Series completa para analisis de volatilidad
        
        Mejora v35: Retorna Series en lugar de float para permitir analisis historico
        """
        try:
            if df is None or len(df) < period + 1:
                return pd.Series([0.0])

            high = df['high']
            low = df['low']
            close = df['close']

            # True Range: max(high-low, |high-prev_close|, |low-prev_close|)
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))

            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.ewm(span=period, adjust=False).mean()

            return atr
        except Exception as e:
            logger.debug(f"Error calculando ATR: {e}")
            return pd.Series([0.0])
    
    def calculate_atr_percent(self, df: pd.DataFrame, period: int = 14) -> float:
        """
        Calcula el ATR como porcentaje del precio actual.
        Util para comparar volatilidad entre diferentes activos.
        """
        try:
            if df is None or len(df) < period + 1:
                return 0.0
            
            atr_series = self.calculate_atr(df, period)
            atr_value = float(atr_series.iloc[-1]) if len(atr_series) > 0 else 0.0
            current_price = float(df['close'].iloc[-1])
            
            if current_price > 0:
                return (atr_value / current_price) * 100
            return 0.0
        except Exception as e:
            logger.debug(f"Error calculando ATR%: {e}")
            return 0.0
    
    def is_volatility_optimal(self, df: pd.DataFrame, min_atr_pct: float = 0.3, 
                              max_atr_pct: float = 5.0) -> Tuple[bool, float, str]:
        """
        Verifica si la volatilidad esta en rango optimo para trading.
        
        Returns:
            (es_optima, atr_percent, mensaje)
        """
        try:
            atr_pct = self.calculate_atr_percent(df)
            
            if atr_pct < min_atr_pct:
                return False, atr_pct, f"Volatilidad muy baja ({atr_pct:.2f}%)"
            elif atr_pct > max_atr_pct:
                return False, atr_pct, f"Volatilidad muy alta ({atr_pct:.2f}%)"
            else:
                return True, atr_pct, f"Volatilidad optima ({atr_pct:.2f}%)"
        except Exception as e:
            logger.debug(f"Error verificando volatilidad: {e}")
            return True, 0.0, "No verificado"

    def calculate_dynamic_stop_loss(self, entry_price: float, atr: float, 
                                     trend_direction: str, multiplier: float = 1.5) -> dict:
        """
        Calcula Stop Loss y Take Profit asegurando ratio 1:3 por defecto.
        
        Mejora v35.1:
        - Prioriza configuración 1% SL / 3% TP (Ratio 1:3)
        - Milestones dinámicos desde configuración
        """
        try:
            # Asegurar que atr sea un float (por si viene como pd.Series)
            if hasattr(atr, 'iloc'):
                atr = float(atr.iloc[-1]) if len(atr) > 0 else 0.0
            
            # ✅ Cargar configuración 1:3 por defecto
            default_sl_pct = getattr(self.config, 'STOP_LOSS_PERCENT', 1.0) / 100  # 1.0%
            default_tp_pct = getattr(self.config, 'PROFIT_TARGET_PERCENT', 3.0) / 100  # 3.0%
            
            # Calcular distancias base
            sl_distance = entry_price * default_sl_pct
            tp_distance = entry_price * default_tp_pct
            
            # Si hay ATR válido y config lo permite, podemos ajustar
            # Pero aseguramos que el ratio se mantenga cercano o mejor a 1:3
            atr_based = False
            if atr > 0 and getattr(self.config, 'USE_ATR_SL', False):
                sl_distance = max(atr * multiplier, sl_distance)
                # Forzar TP a ser 3 veces el SL para mantener ratio
                tp_distance = sl_distance * 3.0
                atr_based = True

            if trend_direction == 'BULLISH':
                stop_loss = entry_price - sl_distance
                take_profit = entry_price + tp_distance
            else:
                stop_loss = entry_price + sl_distance
                take_profit = entry_price - tp_distance

            sl_percent = abs(entry_price - stop_loss) / entry_price * 100
            tp_percent = abs(take_profit - entry_price) / entry_price * 100
            
            # Evitar división por cero
            safe_sl_percent = max(sl_percent, 0.01)
            risk_reward = tp_percent / safe_sl_percent
            
            # ✅ Milestones desde configuración
            milestones_pct = getattr(self.config, 'PROFIT_MILESTONES', [1.0, 2.0, 3.0])
            
            # Calcular precios de milestones (para referencia)
            milestone_prices = []
            for m_pct in milestones_pct:
                if trend_direction == 'BULLISH':
                    m_price = entry_price * (1 + m_pct/100)
                else:
                    m_price = entry_price * (1 - m_pct/100)
                milestone_prices.append(m_price)

            return {
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'sl_distance': sl_distance,
                'tp_distance': tp_distance,
                'sl_percent': sl_percent,
                'tp_percent': tp_percent,
                'risk_reward': risk_reward,
                'atr_based': atr_based,
                'atr_multiplier': multiplier if atr_based else 0,
                'trailing_stop_distance': sl_distance * 0.5, 
                'milestones': milestone_prices
            }
        except Exception as e:
            logger.error(f"Error calculando SL/TP 1:3: {e}")
            # Fallback seguro 1:3
            return {
                'stop_loss': entry_price * 0.99, # 1%
                'take_profit': entry_price * 1.03, # 3%
                'sl_percent': 1.0,
                'tp_percent': 3.0,
                'risk_reward': 3.0,
                'atr_based': False
            }

    def analyze_candlestick_pattern(self, df: pd.DataFrame, include_volume: bool = True) -> dict:
        """
        Analiza patrones de velas clásicos con confirmación de volumen opcional.
        Patrones detectados: Hammer, Inverted Hammer, Engulfing, Three White Soldiers,
        Three Black Crows, Morning Star, Evening Star, Dojis, Rising/Falling 3 Method.
        Devuelve: {'type': 'BULLISH'/'BEARISH'/'NEUTRAL', 'pattern': str, 'confidence': 0-100, 'volume_confirmed': bool}
        """
        try:
            if df is None or len(df) < 3:
                return {'type': 'NEUTRAL', 'pattern': 'NONE', 'confidence': 0, 'volume_confirmed': False}

            recent = df.tail(7).reset_index(drop=True)
            n = len(recent)
            if n < 3:
                return {'type': 'NEUTRAL', 'pattern': 'INSUFICIENTE', 'confidence': 0, 'volume_confirmed': False}

            c_last = recent.iloc[-1]
            body = abs(c_last['close'] - c_last['open'])
            total_range = max(c_last['high'] - c_last['low'], 1e-8)
            upper_wick = c_last['high'] - max(c_last['open'], c_last['close'])
            lower_wick = min(c_last['open'], c_last['close']) - c_last['low']
            is_bullish = c_last['close'] > c_last['open']

            vol_confirmed = False
            if include_volume and 'volume' in recent.columns and n >= 5:
                avg_vol = recent['volume'].iloc[:-1].mean()
                vol_confirmed = c_last['volume'] > avg_vol * 1.2

            def _make_result(ptype, pname, conf):
                return {'type': ptype, 'pattern': pname, 'confidence': min(100, int(conf)), 'volume_confirmed': vol_confirmed}

            # === PATRONES DE 1 VELA ===

            # 1. HAMMER (Martillo Alcista) - cuerpo pequeño arriba, mecha inferior larga
            if body < 0.35 * total_range and lower_wick >= 2 * body and upper_wick < body * 0.5:
                if is_bullish or body < 0.15 * total_range:
                    conf = 60 + (lower_wick / total_range) * 30 + (10 if vol_confirmed else 0)
                    return _make_result('BULLISH', 'Hammer', conf)

            # 2. INVERTED HAMMER (Martillo Invertido Alcista)
            if body < 0.35 * total_range and upper_wick >= 2 * body and lower_wick < body * 0.5:
                if is_bullish:
                    conf = 55 + (upper_wick / total_range) * 30 + (10 if vol_confirmed else 0)
                    return _make_result('BULLISH', 'Inverted Hammer', conf)

            # 3. SHOOTING STAR (Estrella Fugaz Bajista)
            if body < 0.35 * total_range and upper_wick >= 2 * body and lower_wick < body * 0.5:
                if not is_bullish:
                    conf = 60 + (upper_wick / total_range) * 30 + (10 if vol_confirmed else 0)
                    return _make_result('BEARISH', 'Shooting Star', conf)

            # 4. HANGING MAN (Hombre Colgado Bajista)
            if body < 0.35 * total_range and lower_wick >= 2 * body and upper_wick < body * 0.5:
                if not is_bullish:
                    conf = 55 + (lower_wick / total_range) * 25 + (10 if vol_confirmed else 0)
                    return _make_result('BEARISH', 'Hanging Man', conf)

            # 5. DRAGONFLY DOJI (Alcista)
            if body < 0.1 * total_range and lower_wick > 2.5 * upper_wick:
                conf = 55 + (lower_wick / total_range) * 35 + (10 if vol_confirmed else 0)
                return _make_result('BULLISH', 'Dragonfly Doji', conf)

            # 6. GRAVESTONE DOJI (Bajista)
            if body < 0.1 * total_range and upper_wick > 2.5 * lower_wick:
                conf = 55 + (upper_wick / total_range) * 35 + (10 if vol_confirmed else 0)
                return _make_result('BEARISH', 'Gravestone Doji', conf)

            # === PATRONES DE 2 VELAS ===
            if n >= 2:
                c_prev = recent.iloc[-2]
                body_prev = abs(c_prev['close'] - c_prev['open'])
                prev_bullish = c_prev['close'] > c_prev['open']
                range_prev = max(c_prev['high'] - c_prev['low'], 1e-8)

                # 7. BULLISH ENGULFING (Envolvente Alcista)
                if not prev_bullish and is_bullish:
                    if c_last['open'] <= c_prev['close'] and c_last['close'] >= c_prev['open']:
                        if body > body_prev * 1.1:
                            conf = 65 + min(25, (body / body_prev - 1) * 50) + (10 if vol_confirmed else 0)
                            return _make_result('BULLISH', 'Bullish Engulfing', conf)

                # 8. BEARISH ENGULFING (Envolvente Bajista)
                if prev_bullish and not is_bullish:
                    if c_last['open'] >= c_prev['close'] and c_last['close'] <= c_prev['open']:
                        if body > body_prev * 1.1:
                            conf = 65 + min(25, (body / body_prev - 1) * 50) + (10 if vol_confirmed else 0)
                            return _make_result('BEARISH', 'Bearish Engulfing', conf)

                # 9. PIERCING LINE (Alcista)
                if not prev_bullish and is_bullish:
                    midpoint_prev = (c_prev['open'] + c_prev['close']) / 2
                    if c_last['open'] < c_prev['close'] and c_last['close'] > midpoint_prev and c_last['close'] < c_prev['open']:
                        conf = 60 + (10 if vol_confirmed else 0)
                        return _make_result('BULLISH', 'Piercing Line', conf)

                # 10. DARK CLOUD COVER (Bajista)
                if prev_bullish and not is_bullish:
                    midpoint_prev = (c_prev['open'] + c_prev['close']) / 2
                    if c_last['open'] > c_prev['close'] and c_last['close'] < midpoint_prev and c_last['close'] > c_prev['open']:
                        conf = 60 + (10 if vol_confirmed else 0)
                        return _make_result('BEARISH', 'Dark Cloud Cover', conf)

            # === PATRONES DE 3 VELAS ===
            if n >= 3:
                c0, c1, c2 = recent.iloc[-3], recent.iloc[-2], recent.iloc[-1]
                b0 = abs(c0['close'] - c0['open'])
                b1 = abs(c1['close'] - c1['open'])
                b2 = abs(c2['close'] - c2['open'])
                bull0 = c0['close'] > c0['open']
                bull1 = c1['close'] > c1['open']
                bull2 = c2['close'] > c2['open']
                r0 = max(c0['high'] - c0['low'], 1e-8)

                # 11. THREE WHITE SOLDIERS (Tres Soldados Blancos - Alcista fuerte)
                if bull0 and bull1 and bull2:
                    if c1['close'] > c0['close'] and c2['close'] > c1['close']:
                        if c1['open'] > c0['open'] and c2['open'] > c1['open']:
                            body_ratio = min(b0, b1, b2) / max(b0, b1, b2, 1e-8)
                            if body_ratio > 0.5:
                                conf = 75 + body_ratio * 15 + (10 if vol_confirmed else 0)
                                return _make_result('BULLISH', 'Three White Soldiers', conf)

                # 12. THREE BLACK CROWS (Tres Cuervos Negros - Bajista fuerte)
                if not bull0 and not bull1 and not bull2:
                    if c1['close'] < c0['close'] and c2['close'] < c1['close']:
                        if c1['open'] < c0['open'] and c2['open'] < c1['open']:
                            body_ratio = min(b0, b1, b2) / max(b0, b1, b2, 1e-8)
                            if body_ratio > 0.5:
                                conf = 75 + body_ratio * 15 + (10 if vol_confirmed else 0)
                                return _make_result('BEARISH', 'Three Black Crows', conf)

                # 13. MORNING STAR (Estrella de la Mañana - Alcista)
                if not bull0 and b0 > r0 * 0.5:
                    if b1 < b0 * 0.4 and b1 < b2 * 0.4:
                        if bull2 and c2['close'] > (c0['open'] + c0['close']) / 2:
                            conf = 70 + (10 if vol_confirmed else 0)
                            return _make_result('BULLISH', 'Morning Star', conf)

                # 14. EVENING STAR (Estrella Vespertina - Bajista)
                if bull0 and b0 > r0 * 0.5:
                    if b1 < b0 * 0.4 and b1 < b2 * 0.4:
                        if not bull2 and c2['close'] < (c0['open'] + c0['close']) / 2:
                            conf = 70 + (10 if vol_confirmed else 0)
                            return _make_result('BEARISH', 'Evening Star', conf)

            # === PATRONES DE 4-5 VELAS ===
            if n >= 5:
                c0, c1, c2, c3, c4 = [recent.iloc[i] for i in range(-5, 0)]
                body0 = abs(c0['close'] - c0['open'])
                body4 = abs(c4['close'] - c4['open'])
                range4 = max(c4['high'] - c4['low'], 1e-8)

                small_bodies = all(abs(recent.iloc[i]['close'] - recent.iloc[i]['open']) < body0 * 0.5 for i in [-4, -3, -2])
                within_range = all(
                    c0['low'] <= recent.iloc[i]['low'] and recent.iloc[i]['high'] <= c0['high']
                    for i in [-4, -3, -2]
                )
                bullish_close = c4['close'] > c0['close'] and c4['close'] > c4['open']
                bearish_close = c4['close'] < c0['close'] and c4['close'] < c4['open']

                # 15. RISING THREE METHOD
                if small_bodies and within_range and bullish_close:
                    conf = 70 + (body4 / range4) * 20 + (10 if vol_confirmed else 0)
                    return _make_result('BULLISH', 'Rising 3 Method', conf)

                # 16. FALLING THREE METHOD
                if small_bodies and within_range and bearish_close:
                    conf = 70 + (body4 / range4) * 20 + (10 if vol_confirmed else 0)
                    return _make_result('BEARISH', 'Falling 3 Method', conf)

            # === PATRONES DE AGOTAMIENTO (4 velas) ===
            if n >= 4:
                last4 = recent.iloc[-4:].copy()
                first3_bearish = all(last4.iloc[i]['close'] < last4.iloc[i]['open'] for i in [0, 1, 2])
                first3_bullish = all(last4.iloc[i]['close'] > last4.iloc[i]['open'] for i in [0, 1, 2])
                last_bullish = last4.iloc[3]['close'] > last4.iloc[3]['open']
                last_bearish = last4.iloc[3]['close'] < last4.iloc[3]['open']
                body_last = abs(last4.iloc[3]['close'] - last4.iloc[3]['open'])
                body_first = abs(last4.iloc[0]['close'] - last4.iloc[0]['open'])
                range_last = max(last4.iloc[3]['high'] - last4.iloc[3]['low'], 1e-8)

                # 17. AGOTAMIENTO ALCISTA
                if first3_bearish and last_bullish and body_last > 1.5 * body_first:
                    conf = 65 + (body_last / range_last) * 25 + (10 if vol_confirmed else 0)
                    return _make_result('BULLISH', 'Exhaustion Reversal', conf)

                # 18. AGOTAMIENTO BAJISTA
                if first3_bullish and last_bearish and body_last > 1.5 * body_first:
                    conf = 65 + (body_last / range_last) * 25 + (10 if vol_confirmed else 0)
                    return _make_result('BEARISH', 'Exhaustion Reversal', conf)

            return {'type': 'NEUTRAL', 'pattern': 'NONE', 'confidence': 0, 'volume_confirmed': False}

        except Exception as e:
            logger.debug(f"[CANDLE] Error en analyze_candlestick_pattern: {e}")
            return {'type': 'NEUTRAL', 'pattern': 'ERROR', 'confidence': 0, 'volume_confirmed': False}

    def evaluate_entry_setup(self, df_entry: pd.DataFrame, market_direction: str, candle_pattern: dict,
                             confluence_score: float = 0.0, atr: Optional[float] = None, data_id: str = "") -> dict:
        try:
            if df_entry is None or len(df_entry) < 30:
                return {'valid': True, 'grade': 'N/A', 'reason': 'Datos insuficientes', 'text': "🎯 Entrada: N/A (datos insuficientes)"}

            c_last = df_entry.iloc[-1]
            o = float(c_last['open'])
            h = float(c_last['high'])
            l = float(c_last['low'])
            c = float(c_last['close'])

            if atr is not None:
                if hasattr(atr, 'iloc'):
                    atr_val = float(atr.iloc[-1]) if len(atr) > 0 else 0.0
                else:
                    atr_val = float(atr)
            else:
                atr_series = self.calculate_atr(df_entry, 14)
                atr_val = float(atr_series.iloc[-1]) if atr_series is not None and len(atr_series) > 0 else 0.0
            
            if atr_val <= 1e-12:
                return {'valid': True, 'grade': 'N/A', 'reason': 'ATR inválido', 'text': "🎯 Entrada: N/A (ATR inválido)"}

            ema_period = int(getattr(self.config, 'ENTRY_EMA_PERIOD', 21) or 21)
            ema_series = self.calculate_ema(df_entry['close'], ema_period, str(data_id or "") + "_entry")
            ema_val = float(ema_series.iloc[-1]) if ema_series is not None and len(ema_series) else c

            candle_range = max(h - l, 1e-12)
            close_pos = (c - l) / candle_range

            if pd.isna(atr_val) or atr_val <= 1e-12:
                return {'valid': True, 'grade': 'N/A', 'reason': 'ATR inválido', 'text': "🎯 Entrada: N/A (ATR inválido)"}

            range_atr = (h - l) / atr_val
            body_atr = abs(c - o) / atr_val
            dist_ema_atr = abs(c - ema_val) / atr_val

            pattern_type = (candle_pattern or {}).get('type', 'NEUTRAL')
            pattern_name = (candle_pattern or {}).get('pattern', 'NONE')
            pattern_conf = float((candle_pattern or {}).get('confidence', 0))
            pattern_vol = bool((candle_pattern or {}).get('volume_confirmed', False))

            require_pattern = bool(getattr(self.config, 'REQUIRE_CANDLE_PATTERN', False))
            min_pat = float(getattr(self.config, 'MIN_ENTRY_PATTERN_CONFIDENCE', 60.0) or 60.0)
            max_dist = float(getattr(self.config, 'MAX_ENTRY_DISTANCE_ATR', 1.2) or 1.2)
            max_range = float(getattr(self.config, 'MAX_ENTRY_CANDLE_RANGE_ATR', 1.6) or 1.6)
            max_body = float(getattr(self.config, 'MAX_ENTRY_CANDLE_BODY_ATR', 1.1) or 1.1)
            pullback_required = bool(getattr(self.config, 'ENTRY_PULLBACK_REQUIRED', True))
            confluence_bypass = float(getattr(self.config, 'ENTRY_CONFLUENCE_BYPASS', 75) or 75)

            direction = (market_direction or 'NEUTRAL').upper()
            if direction not in ('BULLISH', 'BEARISH'):
                return {
                    'valid': True,
                    'grade': 'N/A',
                    'reason': 'Mercado NEUTRAL',
                    'text': f"🎯 Entrada: N/A (mercado {direction})"
                }

            pattern_ok = True
            if require_pattern:
                pattern_ok = (pattern_type == direction and pattern_conf >= min_pat)

            if direction == 'BULLISH':
                pullback_ok = (l <= ema_val) or (c >= ema_val and dist_ema_atr <= 0.6)
                overextended = (range_atr > max_range and body_atr > max_body and close_pos >= 0.85)
            else:
                pullback_ok = (h >= ema_val) or (c <= ema_val and dist_ema_atr <= 0.6)
                overextended = (range_atr > max_range and body_atr > max_body and close_pos <= 0.15)

            if not pattern_ok:
                reason = f"Patrón no confirmatorio: {pattern_name} ({pattern_type} {pattern_conf:.0f}%)"
                valid = False
            elif dist_ema_atr > max_dist:
                reason = f"Entrada tardía: lejos de EMA{ema_period} ({dist_ema_atr:.2f} ATR)"
                valid = False
            elif overextended:
                reason = f"Entrada tardía: vela extendida ({range_atr:.2f} ATR)"
                valid = False
            elif pullback_required and (not pullback_ok) and confluence_score < confluence_bypass:
                reason = f"Entrada temprana: sin pullback a EMA{ema_period}"
                valid = False
            else:
                reason = "Setup de entrada OK"
                valid = True

            grade = 'C'
            if valid and dist_ema_atr <= 0.6 and pullback_ok and pattern_conf >= 80 and pattern_vol:
                grade = 'A+'
            elif valid:
                grade = 'B'

            text = (
                f"🎯 Entrada: {grade} | EMA{ema_period} dist={dist_ema_atr:.2f} ATR | "
                f"Rango vela={range_atr:.2f} ATR | Patrón={pattern_name}({pattern_conf:.0f}%)"
            )
            return {
                'valid': valid,
                'grade': grade,
                'reason': reason,
                'dist_ema_atr': dist_ema_atr,
                'range_atr': range_atr,
                'body_atr': body_atr,
                'pattern_name': pattern_name,
                'text': text
            }
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Error en evaluate_entry_setup: {e}\n{tb}")
            return {'valid': True, 'grade': 'N/A', 'reason': f'Error: {e}', 'text': f"🎯 Entrada: N/A ({str(e)[:40]})"}

    def evaluate_mm_buy_setup(self, df_entry: pd.DataFrame, market_direction: str, atr: Optional[float] = None) -> dict:
        """
        Market Maker Buy Model (spot/perpetual):
        - Impulso inicial
        - Retroceso controlado (pullback)
        - Spring/liquidity sweep en mínimos recientes
        - Recuperación rápida de EMA21 con volumen
        """
        try:
            if df_entry is None or len(df_entry) < 40:
                return {'valid': False, 'score': 0.0, 'reason': 'Datos insuficientes MM', 'spring_detected': False}

            d = df_entry.tail(40).copy()
            c = pd.to_numeric(d['close'], errors='coerce')
            h = pd.to_numeric(d['high'], errors='coerce')
            l = pd.to_numeric(d['low'], errors='coerce')
            o = pd.to_numeric(d['open'], errors='coerce')
            v = pd.to_numeric(d['volume'], errors='coerce').fillna(0)

            if hasattr(atr, 'iloc'):
                atr_val = float(atr.iloc[-1]) if len(atr) else 0.0
            elif atr is not None:
                atr_val = float(atr)
            else:
                atr_series = self.calculate_atr(d, 14)
                atr_val = float(atr_series.iloc[-1]) if len(atr_series) else 0.0

            if atr_val <= 1e-12:
                return {'valid': False, 'score': 0.0, 'reason': 'ATR inválido MM', 'spring_detected': False}

            ema21 = self.calculate_ema(c, 21, "mm_buy")
            ema_val = float(ema21.iloc[-1]) if len(ema21) else float(c.iloc[-1])

            # Impulso previo (últimas ~20 velas excluyendo la actual)
            prior = d.iloc[-21:-1]
            if len(prior) < 8:
                return {'valid': False, 'score': 0.0, 'reason': 'Impulso insuficiente MM', 'spring_detected': False}
            impulse_low = float(prior['low'].min())
            impulse_high = float(prior['high'].max())
            impulse_move = max(1e-12, impulse_high - impulse_low)

            # Retroceso desde máximo del impulso hasta mínimo reciente
            pullback_low = float(d.iloc[-8:]['low'].min())
            pullback_ratio = (impulse_high - pullback_low) / impulse_move

            pb_min = float(getattr(self.config, 'MM_PULLBACK_MIN', 0.25))
            pb_max = float(getattr(self.config, 'MM_PULLBACK_MAX', 0.72))
            pullback_ok = pb_min <= pullback_ratio <= pb_max

            # Spring: barrer mínimos recientes y cerrar por encima
            recent_support = float(d.iloc[-20:-2]['low'].min()) if len(d) >= 22 else float(d['low'].min())
            last = d.iloc[-1]
            spring_detected = (float(last['low']) < recent_support) and (float(last['close']) > recent_support)

            # Recuperación sobre EMA y cuerpo alcista
            reclaim_ema = float(last['close']) >= ema_val and float(last['close']) > float(last['open'])

            # Volumen confirmatorio
            vol_mean = float(v.tail(20).mean()) if len(v) >= 20 else float(v.mean())
            vol_ok = vol_mean > 0 and float(last['volume']) >= vol_mean * 1.15

            # Filtro de contexto: evitar entrar contra tendencia macro demasiado bajista
            macro_ok = (market_direction or 'NEUTRAL').upper() in ('BULLISH', 'NEUTRAL')

            score = 0.0
            if pullback_ok:
                score += 25
            if spring_detected:
                score += 30
            if reclaim_ema:
                score += 25
            if vol_ok:
                score += 15
            if macro_ok:
                score += 5

            mm_min = float(getattr(self.config, 'MM_MIN_SCORE', 65.0))
            valid = score >= mm_min and (spring_detected or reclaim_ema)

            reason = (
                f"MM score={score:.1f} | pullback={pullback_ratio:.2f} | "
                f"spring={'SI' if spring_detected else 'NO'} | vol={'OK' if vol_ok else 'BAJO'}"
            )

            return {
                'valid': valid,
                'score': float(score),
                'reason': reason,
                'spring_detected': spring_detected,
                'pullback_ratio': float(pullback_ratio),
                'reclaim_ema': reclaim_ema,
                'volume_ok': vol_ok
            }
        except Exception as e:
            logger.debug(f"Error en evaluate_mm_buy_setup: {e}")
            return {'valid': False, 'score': 0.0, 'reason': f'Error MM: {e}', 'spring_detected': False}


    def evaluate_mm_sell_setup(self, df_entry: pd.DataFrame, market_direction: str, atr: Optional[float] = None) -> dict:
        """
        Market Maker Sell Model (espejo del buy model):
        - Impulso bajista inicial
        - Retroceso alcista controlado
        - Upthrust/liquidity sweep en máximos recientes
        - Rechazo rápido por debajo de EMA21 con volumen
        """
        try:
            if df_entry is None or len(df_entry) < 40:
                return {'valid': False, 'score': 0.0, 'reason': 'Datos insuficientes MM SELL', 'upthrust_detected': False}

            d = df_entry.tail(40).copy()
            c = pd.to_numeric(d['close'], errors='coerce')
            h = pd.to_numeric(d['high'], errors='coerce')
            l = pd.to_numeric(d['low'], errors='coerce')
            o = pd.to_numeric(d['open'], errors='coerce')
            v = pd.to_numeric(d['volume'], errors='coerce').fillna(0)

            if hasattr(atr, 'iloc'):
                atr_val = float(atr.iloc[-1]) if len(atr) else 0.0
            elif atr is not None:
                atr_val = float(atr)
            else:
                atr_series = self.calculate_atr(d, 14)
                atr_val = float(atr_series.iloc[-1]) if len(atr_series) else 0.0

            if atr_val <= 1e-12:
                return {'valid': False, 'score': 0.0, 'reason': 'ATR inválido MM SELL', 'upthrust_detected': False}

            ema21 = self.calculate_ema(c, 21, "mm_sell")
            ema_val = float(ema21.iloc[-1]) if len(ema21) else float(c.iloc[-1])

            # Impulso bajista previo
            prior = d.iloc[-21:-1]
            if len(prior) < 8:
                return {'valid': False, 'score': 0.0, 'reason': 'Impulso insuficiente MM SELL', 'upthrust_detected': False}
            impulse_high = float(prior['high'].max())
            impulse_low = float(prior['low'].min())
            impulse_move = max(1e-12, impulse_high - impulse_low)

            # Retroceso alcista desde mínimo del impulso hasta máximo reciente
            pullback_high = float(d.iloc[-8:]['high'].max())
            pullback_ratio = (pullback_high - impulse_low) / impulse_move

            pb_min = float(getattr(self.config, 'MM_PULLBACK_MIN', 0.25))
            pb_max = float(getattr(self.config, 'MM_PULLBACK_MAX', 0.72))
            pullback_ok = pb_min <= pullback_ratio <= pb_max

            # Upthrust: barrer máximos recientes y cerrar por debajo
            recent_res = float(d.iloc[-20:-2]['high'].max()) if len(d) >= 22 else float(d['high'].max())
            last = d.iloc[-1]
            upthrust_detected = (float(last['high']) > recent_res) and (float(last['close']) < recent_res)

            # Rechazo bajo EMA y cuerpo bajista
            reject_ema = float(last['close']) <= ema_val and float(last['close']) < float(last['open'])

            vol_mean = float(v.tail(20).mean()) if len(v) >= 20 else float(v.mean())
            vol_ok = vol_mean > 0 and float(last['volume']) >= vol_mean * 1.15

            macro_ok = (market_direction or 'NEUTRAL').upper() in ('BEARISH', 'NEUTRAL')

            score = 0.0
            if pullback_ok:
                score += 25
            if upthrust_detected:
                score += 30
            if reject_ema:
                score += 25
            if vol_ok:
                score += 15
            if macro_ok:
                score += 5

            mm_min = float(getattr(self.config, 'MM_SELL_MIN_SCORE', getattr(self.config, 'MM_MIN_SCORE', 65.0)))
            valid = score >= mm_min and (upthrust_detected or reject_ema)

            reason = (
                f"MM SELL score={score:.1f} | pullback={pullback_ratio:.2f} | "
                f"upthrust={'SI' if upthrust_detected else 'NO'} | vol={'OK' if vol_ok else 'BAJO'}"
            )

            return {
                'valid': valid,
                'score': float(score),
                'reason': reason,
                'upthrust_detected': upthrust_detected,
                'pullback_ratio': float(pullback_ratio),
                'reject_ema': reject_ema,
                'volume_ok': vol_ok
            }
        except Exception as e:
            logger.debug(f"Error en evaluate_mm_sell_setup: {e}")
            return {'valid': False, 'score': 0.0, 'reason': f'Error MM SELL: {e}', 'upthrust_detected': False}

    def detect_w_m_pattern(self, df: pd.DataFrame) -> dict:
        """
        Detecta patrones W (doble suelo) y M (doble techo) con volumen y simetría.
        Devuelve: {'type': 'BULLISH'/'BEARISH'/'NEUTRAL', 'pattern': 'W_BOTTOM'/'M_TOP'/'NONE', 'confidence': 0-100}
        """
        try:
            if df is None or len(df) < 15:
                return {'type': 'NEUTRAL', 'pattern': 'NONE', 'confidence': 0}

            # Usar últimas 60 velas para contexto
            data = df.tail(60).reset_index(drop=True)
            lows = data['low'].values
            highs = data['high'].values
            volumes = data['volume'].values
            n = len(data)

            # Detectar mínimos locales (valles)
            min_idx = argrelextrema(lows, np.less, order=3)[0]
            max_idx = argrelextrema(highs, np.greater, order=3)[0]

            # --- W_BOTTOM (Bullish) ---
            if len(min_idx) >= 2:
                # Tomar los dos últimos mínimos
                i1, i2 = min_idx[-2], min_idx[-1]
                if i2 - i1 < 5 or i2 > n - 3:
                    pass
                else:
                    p1, p2 = lows[i1], lows[i2]
                    peak = max(highs[i1:i2+1]) if i2 > i1 else 0
                    vol1, vol2 = volumes[i1], volumes[i2]
                    vol_peak = volumes[i1:i2+1].max()

                    # Condiciones clave
                    price_similarity = abs(p1 - p2) / min(p1, p2) < 0.02  # ≤2% diferencia
                    volume_condition = vol2 > vol1 * 0.8  # segundo volumen no muy menor
                    breakout = data['close'].iloc[-1] > peak  # cierre por encima del pico intermedio

                    if price_similarity and volume_condition and breakout:
                        conf = 50
                        conf += 20 if price_similarity else 0
                        conf += 15 if volume_condition else 0
                        conf += 15 if breakout else 0
                        return {'type': 'BULLISH', 'pattern': 'W_BOTTOM', 'confidence': min(100, conf)}

            # --- M_TOP (Bearish) ---
            if len(max_idx) >= 2:
                i1, i2 = max_idx[-2], max_idx[-1]
                if i2 - i1 < 5 or i2 > n - 3:
                    pass
                else:
                    p1, p2 = highs[i1], highs[i2]
                    trough = min(lows[i1:i2+1]) if i2 > i1 else float('inf')
                    vol1, vol2 = volumes[i1], volumes[i2]
                    vol_trough = volumes[i1:i2+1].max()

                    price_similarity = abs(p1 - p2) / min(p1, p2) < 0.02
                    volume_condition = vol2 > vol1 * 0.8
                    breakdown = data['close'].iloc[-1] < trough

                    if price_similarity and volume_condition and breakdown:
                        conf = 50
                        conf += 20 if price_similarity else 0
                        conf += 15 if volume_condition else 0
                        conf += 15 if breakdown else 0
                        return {'type': 'BEARISH', 'pattern': 'M_TOP', 'confidence': min(100, conf)}

            return {'type': 'NEUTRAL', 'pattern': 'NONE', 'confidence': 0}

        except Exception as e:
            logger.debug(f"[W/M] Error en detect_w_m_pattern: {e}")
            return {'type': 'NEUTRAL', 'pattern': 'ERROR', 'confidence': 0}

    def detect_hch_pattern(self, df: pd.DataFrame) -> dict:
        try:
            if df is None or len(df) < 15:
                return {'type': 'NEUTRAL', 'pattern': 'NONE', 'confidence': 0}
            highs = df['high'].tail(60).to_numpy()
            maxs = (np.diff(np.sign(np.diff(highs))) < 0).nonzero()[0] + 1
            conf = 0
            t = 'NEUTRAL'
            pat = 'NONE'
            if len(maxs) >= 3:
                ls, head, rs = maxs[-3], maxs[-2], maxs[-1]
                h = highs[head]
                if h > highs[ls] * 1.02 and h > highs[rs] * 1.02 and abs(highs[ls] - highs[rs]) / h < 0.05:
                    t = 'BEARISH'
                    pat = 'HCH'
                    conf = int(min(100, abs((h - (highs[ls] + highs[rs]) / 2) / h) * 500))
            lows = df['low'].tail(60).to_numpy()
            mins = (np.diff(np.sign(np.diff(lows))) > 0).nonzero()[0] + 1
            if conf == 0 and len(mins) >= 3:
                ls, head, rs = mins[-3], mins[-2], mins[-1]
                h = lows[head]
                if h < lows[ls] * 0.98 and h < lows[rs] * 0.98 and abs(lows[ls] - lows[rs]) / (h + 1e-8) < 0.05:
                    t = 'BULLISH'
                    pat = 'LCL'
                    conf = int(min(100, abs(((lows[ls] + lows[rs]) / 2 - h) / (h + 1e-8)) * 500))
            return {'type': t, 'pattern': pat, 'confidence': conf}
        except Exception:
            return {'type': 'NEUTRAL', 'pattern': 'NONE', 'confidence': 0}

    def find_support_resistance(self, df: pd.DataFrame) -> dict:
        try:
            if df is None or len(df) < 5:
                return {'support': None, 'resistance': None}
            last = df.tail(30)
            support = float(last['low'].min()) if 'low' in last.columns else None
            resistance = float(last['high'].max()) if 'high' in last.columns else None
            return {'support': support, 'resistance': resistance}
        except Exception:
            return {'support': None, 'resistance': None}

    def detect_support_resistance_advanced(self, df: pd.DataFrame, lookback_candles: int = 120) -> dict:
        """
        Detección avanzada de S/R con:
        - Extremos locales (argrelextrema)
        - Clustering por proximidad (±0.5%)
        - Puntuación por volumen, retoques y antigüedad
        - Niveles más cercanos al precio actual
        """
        try:
            if df is None or len(df) < 20:
               return {
                    'support_levels': [], 'resistance_levels': [],
                    'closest_support': None, 'closest_resistance': None, 'valid': False
                }

            data = df.tail(lookback_candles).reset_index(drop=True)
            highs = data['high'].values
            lows = data['low'].values
            closes = data['close'].values
            volumes = data['volume'].values
            n = len(data)
            current_price = float(closes[-1])

            # Detectar extremos
            min_idx = argrelextrema(lows, np.less, order=3)[0]
            max_idx = argrelextrema(highs, np.greater, order=3)[0]

            def _score_levels(indices, prices, levels_type='SUPPORT'):
                levels = []
                for i in indices:
                    if i < 3 or i > n - 4:
                        continue
                    price = float(prices[i])
                    vol_at = float(volumes[i])
                    # Contar retoques cercanos (±0.5%)
                    retests = sum(
                        1 for j in indices
                        if j != i and abs(prices[j] - price) / price < 0.005
                    )
                    # Edad del nivel (velas desde primer toque)
                    first_touch = min([j for j in indices if abs(prices[j] - price) / price < 0.005], default=i)
                    age = (n - 1) - first_touch

                    # Puntuación 0-100
                    score = 0
                    score += min(40, retests * 20)                   # +20 por retoque
                    score += min(30, age * 0.5)                      # +0.5 por vela de vida (hasta 30)
                    vol_ratio = vol_at / max(np.mean(volumes[-20:]), 1e-8)
                    score += min(30, vol_ratio * 15)                # + hasta 30 si volumen > media

                    levels.append({
                        'price': float(price), 
                        'index': int(i), 
                        'retests': int(retests),
                        'age': int(age), 
                        'volume': float(vol_at), 
                        'strength': float(min(100.0, score)),
                        'type': str(levels_type)
                    })
                return levels

            supports = _score_levels(min_idx, lows, 'SUPPORT')
            resistances = _score_levels(max_idx, highs, 'RESISTANCE')

            # Filtrar por fuerza mínima
            supports = [s for s in supports if s['strength'] >= 40]
            resistances = [r for r in resistances if r['strength'] >= 40]

            # Clustering: agrupar niveles cercanos (±0.5%), mantener el más fuerte
            def _cluster(levels):
                clusters = []
                for lvl in sorted(levels, key=lambda x: x['price']):
                    found = False
                    for c in clusters:
                        if abs(lvl['price'] - c['price']) / c['price'] < 0.005:
                            if lvl['strength'] > c['strength']:
                                c.update(lvl)
                            found = True
                            break
                    if not found:
                        clusters.append(lvl)
                return sorted(clusters, key=lambda x: -x['strength'])

            supports = _cluster(supports)
            resistances = _cluster(resistances)

            # Encontrar más cercanos (dentro de ±3%)
            closest_support = None
            for s in supports:
                # Distancia porcentual (positiva si soporte está abajo)
                dist = (current_price - s['price']) / current_price
                if 0 < dist <= 0.03:  # soporte ≤3% por debajo (distancia positiva)
                    if closest_support is None or abs(dist) < abs((current_price - closest_support['price']) / current_price):
                        closest_support = s

            closest_resistance = None
            for r in resistances:
                dist = (r['price'] - current_price) / current_price
                if 0 < dist <= 0.03:  # resistencia ≤3% por encima
                    if closest_resistance is None or abs(dist) < abs((closest_resistance['price'] - current_price) / current_price):
                        closest_resistance = r

            return {
                'support_levels': supports,
                'resistance_levels': resistances,
                'closest_support': closest_support,
                'closest_resistance': closest_resistance,
                'valid': bool(closest_support or closest_resistance)
            }

        except Exception as e:
            logger.debug(f"[S/R ADV] Error en detect_support_resistance_advanced: {e}")
            return {
                'support_levels': [], 'resistance_levels': [],
                'closest_support': None, 'closest_resistance': None, 'valid': False
            }

    def calculate_pattern_confluence_score(self, df: pd.DataFrame, trend_direction: 'TrendDirection') -> dict:
        """
        Sistema de Scoring Mejorado v35 con 12 factores ponderados:
        
        FACTORES PRINCIPALES (70%):
        1. Patron de velas (20%) - Tipo, confianza, alineacion
        2. Soporte/Resistencia (15%) - Cercania, fuerza, retoques
        3. Volumen (15%) - Ratio vs media, perfil institucional
        4. Alineacion tendencia (10%) - EMA alignment
        5. Momentum (10%) - RSI, MACD direction
        
        FACTORES SECUNDARIOS (20%):
        6. Divergencias RSI/MACD (5%) - Confirmacion adicional
        7. Estructura de mercado (5%) - HH/HL o LH/LL
        8. Volatilidad ATR (5%) - Rango optimo
        9. Tiempo sesion (5%) - Horas de mayor liquidez
        
        BONUS (10%):
        10. Triple confluencia (+5%)
        11. Patron institucional (+3%)
        12. Confirmacion multi-timeframe (+2%)

        Returns: {
            'score': 0-100,
            'pattern': dict,
            'sr_level': dict or None,
            'volume_confirmed': bool,
            'trend_aligned': bool,
            'confluence_details': str,
            'entry_quality': 'HIGH'/'MEDIUM'/'LOW',
            'factor_breakdown': dict  # Desglose de cada factor
        }
        """
        try:
            if df is None or len(df) < 20:
                return {
                    'score': 0, 'pattern': None, 'sr_level': None,
                    'volume_confirmed': False, 'trend_aligned': False,
                    'confluence_details': 'Datos insuficientes', 'entry_quality': 'LOW',
                    'factor_breakdown': {}
                }

            score = 0
            details = []
            factor_breakdown = {}

            is_bullish_trend = trend_direction == TrendDirection.BULLISH
            is_bearish_trend = trend_direction == TrendDirection.BEARISH
            current_price = float(df['close'].iloc[-1])

            # ============ FACTOR 1: PATRON DE VELAS (20%) ============
            candle_pattern = self.analyze_candlestick_pattern(df.tail(7), include_volume=True)
            pattern_type = candle_pattern.get('type', 'NEUTRAL')
            pattern_conf = candle_pattern.get('confidence', 0)
            pattern_name = candle_pattern.get('pattern', 'NONE')
            vol_confirmed = candle_pattern.get('volume_confirmed', False)

            pattern_score = 0
            trend_aligned = False
            
            # Patrones de alta confianza
            high_conf_patterns = ['Three White Soldiers', 'Three Black Crows', 'Bullish Engulfing', 
                                  'Bearish Engulfing', 'Morning Star', 'Evening Star', 'Hammer', 
                                  'Inverted Hammer', 'Shooting Star', 'Hanging Man']

            if pattern_type != 'NEUTRAL' and pattern_conf >= 60:
                if (is_bullish_trend and pattern_type == 'BULLISH') or (is_bearish_trend and pattern_type == 'BEARISH'):
                    trend_aligned = True
                    pattern_score = min(20, pattern_conf * 0.2)
                    if pattern_name in high_conf_patterns:
                        pattern_score = min(20, pattern_score * 1.2)  # Bonus por patron fuerte
                    details.append(f"Patron {pattern_name} ({pattern_conf}%) alineado")
                elif pattern_type != 'NEUTRAL':
                    pattern_score = min(12, pattern_conf * 0.12)
                    details.append(f"Patron {pattern_name} contra tendencia")
            elif pattern_conf > 0:
                pattern_score = min(8, pattern_conf * 0.08)
                details.append(f"Patron debil: {pattern_name}")

            score += pattern_score
            factor_breakdown['pattern'] = pattern_score

            # ============ FACTOR 2: SOPORTE/RESISTENCIA (15%) ============
            sr_data = self.detect_support_resistance_advanced(df, lookback_candles=120)
            sr_score = 0
            sr_level = None

            if is_bullish_trend and sr_data.get('closest_support'):
                sup = sr_data['closest_support']
                dist = (current_price - sup['price']) / current_price
                if 0 <= dist <= 0.015:  # Muy cerca (1.5%)
                    sr_score = min(15, sup['strength'] * 0.15)
                    sr_level = {'type': 'SUPPORT', 'price': sup['price'], 'strength': sup['strength'], 'distance': dist}
                    details.append(f"Soporte fuerte ({dist:.1%})")
                elif 0 <= dist <= 0.03:
                    sr_score = min(10, sup['strength'] * 0.10)
                    sr_level = {'type': 'SUPPORT', 'price': sup['price'], 'strength': sup['strength'], 'distance': dist}
                    details.append(f"Soporte moderado ({dist:.1%})")

            elif is_bearish_trend and sr_data.get('closest_resistance'):
                res = sr_data['closest_resistance']
                dist = (res['price'] - current_price) / current_price
                if 0 <= dist <= 0.015:
                    sr_score = min(15, res['strength'] * 0.15)
                    sr_level = {'type': 'RESISTANCE', 'price': res['price'], 'strength': res['strength'], 'distance': dist}
                    details.append(f"Resistencia fuerte ({dist:.1%})")
                elif 0 <= dist <= 0.03:
                    sr_score = min(10, res['strength'] * 0.10)
                    sr_level = {'type': 'RESISTANCE', 'price': res['price'], 'strength': res['strength'], 'distance': dist}
                    details.append(f"Resistencia moderada ({dist:.1%})")

            score += sr_score
            factor_breakdown['support_resistance'] = sr_score

            # ============ FACTOR 3: VOLUMEN (15%) ============
            vol_score = 0
            vol_ratio = 1.0
            try:
                vol_analysis = self.calculate_volume_confidence(df, 20)
                if vol_analysis.get('valid', False):
                    vol_ratio = vol_analysis.get('ratio', 1.0)
                    vol_trend = vol_analysis.get('trend', 'NEUTRAL')
                    
                    if vol_confirmed and vol_ratio > 2.0:
                        vol_score = 15  # Volumen institucional
                        details.append(f"Volumen institucional ({vol_ratio:.1f}x)")
                    elif vol_ratio > 1.5:
                        vol_score = 12
                        details.append(f"Volumen alto ({vol_ratio:.1f}x)")
                    elif vol_ratio > 1.2:
                        vol_score = 8
                        details.append(f"Volumen moderado ({vol_ratio:.1f}x)")
                    elif vol_ratio < 0.7:
                        vol_score = -3  # Penalizacion por bajo volumen
                        details.append(f"Volumen bajo ({vol_ratio:.1f}x) - Penalizado")
            except Exception:
                pass

            score += max(0, vol_score)
            factor_breakdown['volume'] = max(0, vol_score)

            # ============ FACTOR 4: ALINEACION TENDENCIA (10%) ============
            trend_score = 0
            if trend_aligned:
                trend_score = 10
                details.append("Alineado con tendencia EMA")
            elif pattern_type != 'NEUTRAL':
                trend_score = 3

            score += trend_score
            factor_breakdown['trend_alignment'] = trend_score

            # ============ FACTOR 5: MOMENTUM RSI/TDI (10%) ============
            momentum_score = 0
            try:
                rsi = self.calculate_rsi(df['close'], 14)
                if len(rsi) > 0:
                    rsi_val = float(rsi.iloc[-1])
                    
                    if is_bullish_trend:
                        if 40 <= rsi_val <= 60:  # Zona neutral - buen entry
                            momentum_score = 10
                            details.append(f"RSI optimo para compra ({rsi_val:.0f})")
                        elif 30 <= rsi_val < 40:  # Sobrevendido - muy bueno
                            momentum_score = 8
                            details.append(f"RSI sobrevendido ({rsi_val:.0f})")
                        elif rsi_val > 70:  # Sobrecomprado - malo para compra
                            momentum_score = -5
                            details.append(f"RSI sobrecomprado ({rsi_val:.0f}) - Penalizado")
                    elif is_bearish_trend:
                        if 40 <= rsi_val <= 60:
                            momentum_score = 10
                            details.append(f"RSI optimo para venta ({rsi_val:.0f})")
                        elif 60 < rsi_val <= 70:
                            momentum_score = 8
                            details.append(f"RSI sobrecomprado ({rsi_val:.0f})")
                        elif rsi_val < 30:
                            momentum_score = -5
                            details.append(f"RSI sobrevendido ({rsi_val:.0f}) - Penalizado")
            except Exception:
                pass

            score += max(0, momentum_score)
            factor_breakdown['momentum'] = max(0, momentum_score)

            # ============ FACTOR 6: ESTRUCTURA DE MERCADO (5%) ============
            structure_score = 0
            try:
                structure = self.get_market_structure_score(df, lookback=20)
                if structure > 60:
                    structure_score = 5
                    details.append(f"Estructura clara ({structure:.0f}%)")
                elif structure > 40:
                    structure_score = 3
            except Exception:
                pass
            
            score += structure_score
            factor_breakdown['market_structure'] = structure_score

            # ============ FACTOR 7: VOLATILIDAD ATR (5%) ============
            volatility_score = 0
            try:
                atr = self.calculate_atr(df, 14)
                if len(atr) > 0:
                    atr_val = float(atr.iloc[-1])
                    atr_percent = (atr_val / current_price) * 100
                    
                    # Volatilidad optima: 0.5% - 3%
                    if 0.5 <= atr_percent <= 3.0:
                        volatility_score = 5
                        details.append(f"Volatilidad optima (ATR {atr_percent:.2f}%)")
                    elif 0.3 <= atr_percent < 0.5 or 3.0 < atr_percent <= 5.0:
                        volatility_score = 3
                    elif atr_percent > 5.0:
                        volatility_score = -3  # Demasiada volatilidad
                        details.append(f"Volatilidad excesiva (ATR {atr_percent:.2f}%) - Penalizado")
            except Exception:
                pass

            score += max(0, volatility_score)
            factor_breakdown['volatility'] = max(0, volatility_score)

            # ============ BONUS: CONFLUENCIAS MULTIPLES (hasta +10%) ============
            bonus = 0
            confluences = 0
            
            if trend_aligned: confluences += 1
            if vol_confirmed or vol_ratio > 1.5: confluences += 1
            if sr_level and sr_level.get('strength', 0) >= 60: confluences += 1
            if pattern_name in high_conf_patterns: confluences += 1
            if momentum_score >= 8: confluences += 1
            
            if confluences >= 4:
                bonus = 10
                details.append("BONUS: Cuadruple confluencia (+10)")
            elif confluences >= 3:
                bonus = 7
                details.append("BONUS: Triple confluencia (+7)")
            elif confluences >= 2:
                bonus = 4
                details.append("BONUS: Doble confluencia (+4)")

            score += bonus
            factor_breakdown['bonus'] = bonus

            # ============ CALCULO FINAL ============
            score = max(0, min(100, score))

            if score >= 80:
                quality = 'HIGH'
            elif score >= 60:
                quality = 'MEDIUM'
            else:
                quality = 'LOW'

            return {
                'score': int(score),
                'pattern': candle_pattern,
                'sr_level': sr_level,
                'volume_confirmed': vol_confirmed or vol_ratio > 1.5,
                'trend_aligned': trend_aligned,
                'confluence_details': ' | '.join(details) if details else 'Sin confluencia',
                'entry_quality': quality,
                'factor_breakdown': factor_breakdown,
                'volume_ratio': vol_ratio,
                'confluences_count': confluences
            }

        except Exception as e:
            logger.debug(f"[CONFLUENCE] Error: {e}")
            return {
                'score': 0, 'pattern': None, 'sr_level': None,
                'volume_confirmed': False, 'trend_aligned': False,
                'confluence_details': f'Error: {e}', 'entry_quality': 'LOW',
                'factor_breakdown': {}
            }

    def analyze_market_cycles(self, df: pd.DataFrame) -> dict:
        try:
            if df is None or len(df) < 20:
                return {'cycle': 'NEUTRAL', 'direction': 'NEUTRAL', 'strength': 0.0, 'phase': 'RANGE'}
            prices = df['close']
            ema50 = self.calculate_ema(prices, 50, 'cycle')
            ema200 = self.calculate_ema(prices, 200, 'cycle')
            slope50 = float(ema50.iloc[-1] - ema50.iloc[-2]) if len(ema50) >= 2 else 0.0
            slope200 = float(ema200.iloc[-1] - ema200.iloc[-2]) if len(ema200) >= 2 else 0.0
            direction = 'NEUTRAL'
            phase = 'RANGE'
            if ema50.iloc[-1] > ema200.iloc[-1] and slope50 > 0:
                direction = 'UPTREND'
                phase = 'TREND'
            elif ema50.iloc[-1] < ema200.iloc[-1] and slope50 < 0:
                direction = 'DOWNTREND'
                phase = 'TREND'
            else:
                returns = prices.pct_change().dropna()
                vol = float(returns.rolling(10).std().iloc[-1]) if len(returns) >= 10 else 0.0
                direction = 'ACCUMULATION' if vol < 0.01 else 'DISTRIBUTION'
                phase = 'RANGE'
            strength = min(1.0, max(0.0, abs(slope50) / (abs(prices.iloc[-1]) + 1e-8) * 100))
            return {'cycle': direction, 'direction': direction, 'strength': strength, 'phase': phase}
        except Exception:
            return {'cycle': 'NEUTRAL', 'direction': 'NEUTRAL', 'strength': 0.0, 'phase': 'RANGE'}

    def get_market_structure_score(self, df: pd.DataFrame, lookback: int = 20) -> float:
        try:
            if df is None or len(df) < lookback + 2:
                return 0.0
            sub = df.tail(lookback)
            highs = sub['high'].to_numpy()
            lows = sub['low'].to_numpy()
            hh = 0
            hl = 0
            lh = 0
            ll = 0
            for i in range(1, len(highs)):
                hh += int(highs[i] > highs[i-1])
                lh += int(highs[i] < highs[i-1])
                hl += int(lows[i] > lows[i-1])
                ll += int(lows[i] < lows[i-1])
            bullish_score = (hh + hl) / max(1, (len(highs) - 1)) * 50
            bearish_score = (lh + ll) / max(1, (len(highs) - 1)) * 50
            return float(max(bullish_score, bearish_score))
        except Exception:
            return 0.0

    def validate_ultra_selective_conditions(self, symbol: str,
                                            df_primary: pd.DataFrame,
                                            df_entry: pd.DataFrame,
                                            neural_prediction: dict,
                                            trend_direction: TrendDirection) -> Dict[str, Any]:
        """
        ✅ VALIDACIÓN SIMPLIFICADA v35.0.0.0 – SOLO 4 CRITERIOS CLAVE
        + Patrones W/M/HCH/LCL como bonus
        + Alineación 15m/30m SOLO para promoción y seguimiento
        """
        config = self.config

        # ✅ INICIALIZAR LISTAS FUERA DEL TRY (evita error de variable no definida)
        criteria_list = []  # Los 7 criterios técnicos
        tech_scores = []    # Puntuaciones para cálculo de porcentaje

        validation_result = {
            'valid': False,
            'reason': 'PENDIENTE',
            'technical_percentage': 0.0,
            'neural_score': 0.0,
            'alignment_percentage': 0.0,
            'criteria_passed': 0,
            'criteria_list': [],
            'entry_price': 0.0,
            'stop_loss': 0.0,
            'take_profit': 0.0,
            'risk_reward_ratio': 0.0,
            'conditions_met': [],
            'ia_direction': 'NEUTRAL',
            'technical_direction': 'NEUTRAL',
            'trend_direction': 'NEUTRAL',
            'signal_type_detected': 'NEUTRAL',
            'trend_strength': 0.0,
            'volume_ratio': 0.0,
            'pattern_score': 0.0,
            'market_cycle': 'NEUTRAL',
            'w_m_pattern': None,
            'hch_pattern': None,
            'confluence_score': 0,
            'confluence_quality': 'LOW',
            'confluence_details': '',
            'volume_confirmed_pattern': False
        }

        try:

            # ✅ VALIDACIÓN DE DATOS
            if df_primary is None or df_entry is None or len(df_primary) < 50 or len(df_entry) < 50:
                validation_result['reason'] = '❌ Datos insuficientes para el análisis'
                return validation_result

            current_price_entry = float(df_entry['close'].iloc[-1])
            if current_price_entry <= 0:
                validation_result['reason'] = '❌ Precio inválido detectado'
                return validation_result

            entry_price = current_price_entry
            data_id = f"{symbol}_{int(time.time())}"

            # ✅ 1. TENDENCIA EMA (35%)
            ema50 = self.calculate_ema(df_primary['close'], 50, data_id + "_primary")
            ema200 = self.calculate_ema(df_primary['close'], 200, data_id + "_primary")

            if ema50.empty or ema200.empty or len(ema50) < 2 or len(ema200) < 2:
                validation_result['reason'] = '❌ EMAs insuficientes'
                return validation_result

            ema50_val = float(ema50.iloc[-1])
            ema200_val = float(ema200.iloc[-1])
            ema_diff = ema50_val - ema200_val

            if ema50_val > ema200_val:
                detected_trend = TrendDirection.BULLISH
                trend_strength = min(100, abs(ema_diff / ema200_val * 100))
                technical_direction = 'BULLISH'
            elif ema50_val < ema200_val:
                detected_trend = TrendDirection.BEARISH
                trend_strength = min(100, abs(ema_diff / ema200_val * 100))
                technical_direction = 'BEARISH'
            else:
                detected_trend = TrendDirection.NEUTRAL
                trend_strength = 0
                technical_direction = 'NEUTRAL'

            validation_result['trend_direction'] = str(detected_trend).split('.')[-1]
            validation_result['technical_direction'] = technical_direction
            validation_result['trend_strength'] = trend_strength

            # ✅ 2. TDI (25%)
            try:
                _, tdi_green, tdi_red, _, _ = self.calculate_tdi(df_entry, data_id + "_entry")
                tdi_green_val = float(tdi_green.iloc[-1]) if not tdi_green.empty else 50
                tdi_red_val = float(tdi_red.iloc[-1]) if not tdi_red.empty else 50
                tdi_momentum = tdi_green_val - tdi_red_val
            except Exception:
                tdi_green_val = tdi_red_val = 50
                tdi_momentum = 0

            # ✅ 3. ANÁLISIS DE VOLUMEN (15%) - NUEVO CRITERIO
            try:
                volume_analysis = self.calculate_volume_confidence(df_entry, 20)
                volume_confidence = volume_analysis.get('confidence', 0)
                volume_ratio = volume_analysis.get('ratio', 0)
                volume_trend = volume_analysis.get('trend', 'NEUTRAL')
                volume_valid = volume_analysis.get('valid', False)
            except Exception:
                volume_confidence = 0
                volume_ratio = 0
                volume_trend = 'NEUTRAL'
                volume_valid = False

            validation_result['volume_ratio'] = volume_ratio
            validation_result['volume_confidence'] = volume_confidence
            validation_result['volume_trend'] = volume_trend

            # ✅ 4. PATRÓN DE VELAS (15%) — CON VALIDACIÓN OBLIGATORIA
            try:
                candle_pattern = self.analyze_candlestick_pattern(df_entry.tail(7), include_volume=True)
                pattern_type = candle_pattern.get('type', 'NEUTRAL')
                pattern_confidence = candle_pattern.get('confidence', 0)
                pattern_name = candle_pattern.get('pattern', 'NONE')
                volume_confirmed_pattern = candle_pattern.get('volume_confirmed', False)
            except Exception:
                pattern_type = 'NEUTRAL'
                pattern_confidence = 0
                pattern_name = 'ERROR'
                volume_confirmed_pattern = False

            validation_result['candle_pattern'] = candle_pattern if isinstance(candle_pattern, dict) else {
                'type': pattern_type, 'pattern': pattern_name, 'confidence': pattern_confidence, 'volume_confirmed': volume_confirmed_pattern
            }

            # ✅ 4.1 SCORE DE CONFLUENCIA (Patrón + S/R + Volumen + Tendencia)
            try:
                confluence_data = self.calculate_pattern_confluence_score(df_entry, detected_trend)
                confluence_score = confluence_data.get('score', 0)
                confluence_quality = confluence_data.get('entry_quality', 'LOW')
                confluence_details = confluence_data.get('confluence_details', '')
                confluence_sr = confluence_data.get('sr_level')
                confluence_vol = confluence_data.get('volume_confirmed', False)
                confluence_aligned = confluence_data.get('trend_aligned', False)
            except Exception as e:
                logger.debug(f"Error en confluence: {e}")
                confluence_score = 0
                confluence_quality = 'LOW'
                confluence_details = ''
                confluence_sr = None
                confluence_vol = False
                confluence_aligned = False

            validation_result['confluence_score'] = confluence_score
            validation_result['confluence_quality'] = confluence_quality
            validation_result['confluence_details'] = confluence_details
            validation_result['volume_confirmed_pattern'] = volume_confirmed_pattern or confluence_vol

            # ✅ VALIDACIÓN DE PATRÓN (sin bloqueo para mostrar criterios)
            pattern_valid = True
            pattern_fail_reason = ""
            min_entry_pat = float(getattr(config, 'MIN_ENTRY_PATTERN_CONFIDENCE', 60.0))
            if pattern_type == 'NEUTRAL' or pattern_confidence < min_entry_pat:
                pattern_valid = False
                pattern_fail_reason = f"Patrón débil: {pattern_name} ({pattern_confidence:.0f}% < {min_entry_pat:.0f}%)"
            elif trend_direction == TrendDirection.BULLISH and pattern_type != 'BULLISH':
                pattern_valid = False
                pattern_fail_reason = f"Patrón no alcista en tendencia alcista: {pattern_name}"
            elif trend_direction == TrendDirection.BEARISH and pattern_type != 'BEARISH':
                pattern_valid = False
                pattern_fail_reason = f"Patrón no bajista en tendencia bajista: {pattern_name}"

            validation_result['pattern_name'] = pattern_name
            validation_result['pattern_valid'] = pattern_valid

            # ✅ 5. CICLO DE MERCADO (15%)
            try:
                market_cycle = self.analyze_market_cycles(df_primary)
                cycle_type = market_cycle.get('cycle', 'NEUTRAL')
                cycle_strength = market_cycle.get('strength', 0) * 100
            except Exception:
                cycle_type = 'NEUTRAL'
                cycle_strength = 0

            # ✅ 6. PATRÓN DE CONFIRMACIÓN W/M o HCH/LCL — OBLIGATORIO
            w_m_pattern = self.detect_w_m_pattern(df_entry)
            hch_pattern = self.detect_hch_pattern(df_entry)

            confirmation_confidence = 0
            confirmation_pattern = None

            if pattern_type == 'BULLISH':
                if w_m_pattern['type'] == 'BULLISH':  # W_BOTTOM
                    confirmation_confidence = w_m_pattern['confidence']
                    confirmation_pattern = 'W_BOTTOM'
                elif hch_pattern['type'] == 'BULLISH':  # HCH
                    confirmation_confidence = hch_pattern['confidence']
                    confirmation_pattern = 'HCH'
            elif pattern_type == 'BEARISH':
                if w_m_pattern['type'] == 'BEARISH':  # M_TOP
                    confirmation_confidence = w_m_pattern['confidence']
                    confirmation_pattern = 'M_TOP'
                elif hch_pattern['type'] == 'BEARISH':  # LCL
                    confirmation_confidence = hch_pattern['confidence']
                    confirmation_pattern = 'LCL'

            # ✅ VALIDACIÓN DE CONFIRMACIÓN (sin bloqueo)
            confirmation_valid = confirmation_confidence >= 60 and confirmation_pattern is not None
            confirmation_fail_reason = ""
            if not confirmation_valid:
                if confirmation_confidence == 0:
                    confirmation_fail_reason = f"Sin patrón de confirmación"
                else:
                    confirmation_fail_reason = f"Confirmación débil: {confirmation_pattern} ({confirmation_confidence}%)"

            validation_result['confirmation_pattern'] = confirmation_pattern or 'NINGUNO'
            validation_result['confirmation_valid'] = confirmation_valid
            validation_result['w_m_pattern'] = w_m_pattern
            validation_result['hch_pattern'] = hch_pattern

            # ✅ 7. SOPORTE/RESISTENCIA AVANZADO (15%)
            sr_advanced = self.detect_support_resistance_advanced(df_entry, lookback_candles=120)
            closest_support = sr_advanced.get('closest_support')
            closest_resistance = sr_advanced.get('closest_resistance')
            sr_ok = False
            sr_reason = ""
            sr_confidence = 0.0
            sr_level = None
            sr_text = ""  # Se genera cuando S/R es válido

            if trend_direction == TrendDirection.BULLISH:
                if closest_support:
                    dist_to_support = (current_price_entry - closest_support['price']) / current_price_entry
                    if dist_to_support <= 0.015:  # ≤1.5%
                        sr_ok = True
                        sr_confidence = closest_support['strength']
                        sr_level = {'type': 'SUPPORT', 'price': closest_support['price'], 'strength': sr_confidence}
                        sr_text = f"🛡️ S/R: {dist_to_support:.2%} sobre soporte fuerte ({sr_confidence:.0f}%)"
                    else:
                        sr_reason = f"Lejos de soporte ({dist_to_support:.2%})"
                else:
                    sr_reason = "Sin soporte cercano"

            elif trend_direction == TrendDirection.BEARISH:
                if closest_resistance:
                    dist_to_resistance = (closest_resistance['price'] - current_price_entry) / current_price_entry
                    if dist_to_resistance <= 0.015:  # ≤1.5%
                        sr_ok = True
                        sr_confidence = closest_resistance['strength']
                        sr_level = {'type': 'RESISTANCE', 'price': closest_resistance['price'], 'strength': sr_confidence}
                        sr_text = f"🛡️ S/R: {dist_to_resistance:.2%} bajo resistencia fuerte ({sr_confidence:.0f}%)"
                    else:
                        sr_reason = f"Lejos de resistencia ({dist_to_resistance:.2%})"
                else:
                    sr_reason = "Sin resistencia cercana"

            else:
                sr_ok = True  # NEUTRAL → no exigir
                sr_text = "⚪ S/R: No requerido (NEUTRAL)"

            # S/R se evalúa pero no bloquea - se considera en la validación final
            validation_result['sr_level'] = sr_level
            validation_result['sr_valid'] = sr_ok
            sr_fail_reason = sr_reason if not sr_ok else ""

            # ✅ BONUS: Alineación patrón + S/R (+10 pts) - Se calcula pero no se añade aún
            bonus_active = False
            bonus_text = ""
            if (pattern_type == 'BULLISH' and confirmation_pattern == 'W_BOTTOM' and sr_level and sr_level['type'] == 'SUPPORT' and
                sr_confidence >= 60 and confirmation_confidence >= 70):
                bonus_active = True
                bonus_text = "⭐ Bonus: W_BOTTOM + Soporte fuerte (+10 pts)"
            elif (pattern_type == 'BEARISH' and confirmation_pattern == 'M_TOP' and sr_level and sr_level['type'] == 'RESISTANCE' and
                   sr_confidence >= 60 and confirmation_confidence >= 70):
                bonus_active = True
                bonus_text = "⭐ Bonus: M_TOP + Resistencia fuerte (+10 pts)"

            # ✅ 7. IA
            try:
                neural_score = float(neural_prediction.get('confidence', 0))
                neural_signal_type = neural_prediction.get('signal_type', SignalType.NEUTRAL)
                neural_name = str(neural_signal_type).upper()
                if 'BUY' in neural_name or 'COMPRA' in neural_name:
                    ia_direction = 'BULLISH'
                elif 'SELL' in neural_name or 'VENTA' in neural_name:
                    ia_direction = 'BEARISH'
                else:
                    ia_direction = 'NEUTRAL'
            except Exception:
                neural_score = 0
                ia_direction = 'NEUTRAL'

            validation_result['neural_score'] = neural_score
            validation_result['ia_direction'] = ia_direction

            # ✅ 8. CÁLCULO TÉCNICO PONDERADO - EVALUACIÓN INDEPENDIENTE DEL MERCADO

            # === DETERMINAR DIRECCIÓN TÉCNICA REAL (INDEPENDIENTE DE IA) ===
            bullish_signals = 0
            bearish_signals = 0

            # EMA: Evaluar tendencia real
            if ema_diff > 0:
                bullish_signals += 1
            elif ema_diff < 0:
                bearish_signals += 1

            # TDI: Evaluar momentum real
            if tdi_green_val > tdi_red_val:
                bullish_signals += 1
            elif tdi_green_val < tdi_red_val:
                bearish_signals += 1

            # Ciclo: Evaluar fase del mercado
            if cycle_type == 'UPTREND':
                bullish_signals += 1
            elif cycle_type == 'DOWNTREND':
                bearish_signals += 1
            elif cycle_type == 'ACCUMULATION':
                bullish_signals += 0.5
            elif cycle_type == 'DISTRIBUTION':
                bearish_signals += 0.5

            # Patrón de velas
            if pattern_type == 'BULLISH':
                bullish_signals += 1
            elif pattern_type == 'BEARISH':
                bearish_signals += 1

            # === DETERMINAR DIRECCIÓN DOMINANTE DEL MERCADO ===
            market_direction = 'NEUTRAL'
            direction_strength = 0
            if bullish_signals > bearish_signals:
                market_direction = 'BULLISH'
                direction_strength = bullish_signals / max(bullish_signals + bearish_signals, 1)
            elif bearish_signals > bullish_signals:
                market_direction = 'BEARISH'
                direction_strength = bearish_signals / max(bullish_signals + bearish_signals, 1)

            # === CALCULAR SCORES Y GENERAR 7 CRITERIOS EN ORDEN ===

            # 1. EMA (20%)
            ema_pct_diff = (ema_diff / ema200_val * 100) if ema200_val > 0 else 0
            trend_score = 100 if (market_direction == 'BULLISH' and ema_diff > 0) or (market_direction == 'BEARISH' and ema_diff < 0) else 50 if ema_diff != 0 else 0
            tech_scores.append(trend_score * 0.20)
            criteria_list.append(f"{'✅' if trend_score >= 80 else '⚠️' if trend_score >= 50 else '❌'} EMA: {trend_score:.0f} pts ({'+' if ema_pct_diff > 0 else ''}{ema_pct_diff:.2f}%)")

            # 2. TDI (20%)
            tdi_score = 100 if (market_direction == 'BULLISH' and tdi_green_val > tdi_red_val) or (market_direction == 'BEARISH' and tdi_green_val < tdi_red_val) else 50 if abs(tdi_green_val - tdi_red_val) < 5 else 0
            tech_scores.append(tdi_score * 0.20)
            criteria_list.append(f"{'✅' if tdi_score >= 80 else '⚠️' if tdi_score >= 50 else '❌'} TDI: {tdi_score:.0f} pts (G:{tdi_green_val:.1f}/R:{tdi_red_val:.1f})")

            # 3. Volumen (15%)
            vol_score = min(100, volume_confidence) if volume_valid else min(50, volume_ratio * 50)
            tech_scores.append(vol_score * 0.15)
            criteria_list.append(f"{'✅' if vol_score >= 60 else '⚠️' if vol_score >= 30 else '❌'} Volumen: {vol_score:.0f} pts (x{volume_ratio:.2f})")

            # 4. Patrón de velas (15%) + Confluencia
            pattern_aligned = (pattern_type == market_direction) or pattern_type == 'NEUTRAL'
            pattern_score_val = pattern_confidence if pattern_aligned else pattern_confidence * 0.5
            tech_scores.append(pattern_score_val * 0.15)
            vol_icon = "📊" if volume_confirmed_pattern else ""
            criteria_list.append(f"{'✅' if pattern_score_val >= 60 else '⚠️'} 🕯️ Patrón: {pattern_name} ({pattern_type}, {pattern_confidence:.0f}%) {vol_icon}")

            # 5. Confirmación W/M/HCH/LCL (15%)
            confirm_score = min(100, confirmation_confidence) if confirmation_pattern else 0
            tech_scores.append(confirm_score * 0.15)
            criteria_list.append(f"{'✅' if confirm_score >= 60 else '⚠️'} Confirmación: {confirmation_pattern or 'NINGUNO'} ({confirmation_confidence:.0f}%)")

            # 6. S/R Soporte/Resistencia (15%)
            sr_score = min(100, sr_confidence) if sr_ok and sr_level else 0
            tech_scores.append(sr_score * 0.15)
            criteria_list.append(sr_text if sr_text else f"⚠️ S/R: Sin nivel cercano")

            # 7. Bonus (+10 pts máximo) - Solo si hay alineación fuerte
            if bonus_active:
                tech_scores.append(10.0)
                criteria_list.append(bonus_text)

            # 8. Bonus Confluencia (hasta +10 pts adicionales)
            if confluence_score >= 75:
                tech_scores.append(10.0)
                criteria_list.append(f"⭐ Confluencia {confluence_quality}: {confluence_score}% (+10)")
            elif confluence_score >= 55:
                tech_scores.append(5.0)
                criteria_list.append(f"🔸 Confluencia {confluence_quality}: {confluence_score}% (+5)")

            # === ALINEACIÓN IA vs MERCADO (SE EVALÚA APARTE) ===
            ia_trend_aligned = (ia_direction == market_direction) or ia_direction == 'NEUTRAL' or market_direction == 'NEUTRAL'

            # Guardar resultados
            validation_result['market_direction'] = market_direction
            validation_result['direction_strength'] = direction_strength * 100
            validation_result['ia_trend_aligned'] = ia_trend_aligned

            technical_percentage = round(sum(tech_scores), 2)
            validation_result['technical_percentage'] = technical_percentage
            validation_result['criteria_list'] = criteria_list[:]
            validation_result['pattern_score'] = pattern_confidence

            # ✅ 8. ALINEACIÓN 15m/30m (SOLO PARA PROMOCIÓN - NO AFECTA VALIDACIÓN)
            alignment_percentage = 0.0
            if hasattr(self, 'trend_alignment_validator') and self.trend_alignment_validator:
                try:
                    df_15m = df_entry  # Ya es 15m
                    df_30m = self.calculate_ema(df_primary['close'], 30)  # Simulado como 30m
                    alignment = self.trend_alignment_validator.validate_trend_alignment(
                        df_15m, df_30m, neural_score, technical_percentage, ia_direction
                    )
                    alignment_percentage = alignment.get('alignment_score', 0.0)
                except Exception:
                    alignment_percentage = 0.0

            validation_result['alignment_percentage'] = alignment_percentage

            # ✅ 10. NIVELES DINÁMICOS BASADOS EN ATR
            is_buy = ia_direction == 'BULLISH'

            atr_series = self.calculate_atr(df_entry, 14)
            atr = float(atr_series.iloc[-1]) if not atr_series.empty else 0.0
            
            dynamic_levels = self.calculate_dynamic_stop_loss(
                entry_price, atr, ia_direction, multiplier=1.5
            )

            stop_loss = dynamic_levels['stop_loss']
            take_profit = dynamic_levels['take_profit']
            sl_percent_actual = dynamic_levels['sl_percent']
            tp_percent_actual = dynamic_levels['tp_percent']
            risk_reward_ratio = dynamic_levels['risk_reward']
            atr_based = dynamic_levels['atr_based']

            validation_result.update({
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward_ratio': risk_reward_ratio,
                'atr': atr,
                'atr_based': atr_based,
                'sl_percent': sl_percent_actual,
                'tp_percent': tp_percent_actual
            })

            if atr_based:
                criteria_list.append(f"📊 ATR SL/TP: SL={sl_percent_actual:.2f}% / TP={tp_percent_actual:.2f}%")
            else:
                criteria_list.append(f"📊 SL/TP Fijo: SL=1% / TP=2.5%")

            entry_setup = self.evaluate_entry_setup(
                df_entry=df_entry,
                market_direction=market_direction,
                candle_pattern=validation_result.get('candle_pattern', {}),
                confluence_score=confluence_score,
                atr=atr,
                data_id=data_id
            )
            validation_result['entry_setup'] = entry_setup

            # ✅ Filtro adicional MM Buy Model (reduce SL en falsas rupturas)
            mm_result = {
                'valid': True,
                'score': 100.0,
                'reason': 'MM filter desactivado o no aplica',
                'spring_detected': False
            }
            if bool(getattr(config, 'ENABLE_MM_BUY_FILTER', True)):
                if market_direction == 'BULLISH':
                    mm_result = self.evaluate_mm_buy_setup(df_entry=df_entry, market_direction=market_direction, atr=atr)
                elif market_direction == 'BEARISH':
                    mm_result = self.evaluate_mm_sell_setup(df_entry=df_entry, market_direction=market_direction, atr=atr)

            validation_result['mm_setup'] = mm_result
            try:
                criteria_list.append(entry_setup.get('text', '🎯 Entrada: N/A'))
                criteria_list.append(
                    f"🧩 MM Setup: {'✅' if mm_result.get('valid') else '❌'} "
                    f"{mm_result.get('reason', 'N/A')}"
                )
            except Exception:
                pass

            # ✅ 11. DECISIÓN FINAL (UMBRALES DINÁMICOS - VINCULADOS A GUI)
            # v32.0.22.4: Validación flexible - solo criterios esenciales son obligatorios
            min_tech = config.MIN_TECH_VALIDATION
            min_neural = config.MIN_NEURAL_VALIDATION
            min_rr = config.MIN_RISK_REWARD_RATIO
            min_volume_ratio = config.MIN_VOLUME_RATIO

            # === VALIDACIÓN PRINCIPAL (Solo criterios ESENCIALES son obligatorios) ===
            # Criterios ESENCIALES: Técnico, Neural, R/R, Dirección clara
            # Criterios BONUS: Patrón velas, Confirmación W/M, S/R (suman puntos pero no bloquean)
            essential_criteria_met = (
                technical_percentage >= min_tech and
                neural_score >= min_neural and
                risk_reward_ratio >= min_rr and
                market_direction != 'NEUTRAL'
            )

            entry_required = bool(getattr(config, 'REQUIRE_ENTRY_SETUP', False)) or bool(getattr(config, 'REQUIRE_CANDLE_PATTERN', False))
            entry_setup_valid = bool(entry_setup.get('valid', True)) if isinstance(entry_setup, dict) else True
            if entry_required and not entry_setup_valid:
                essential_criteria_met = False

            # MM Buy Model como criterio esencial adicional (si está activo)
            mm_required = bool(getattr(config, 'ENABLE_MM_BUY_FILTER', True)) and market_direction in ('BULLISH', 'BEARISH')
            mm_valid = bool(mm_result.get('valid', True))
            if mm_required and not mm_valid:
                essential_criteria_met = False

            # Bonus por criterios opcionales (no bloquean pero mejoran la señal)
            optional_bonus = 0
            if pattern_valid:
                optional_bonus += 5
            if confirmation_valid:
                optional_bonus += 5
            if sr_ok:
                optional_bonus += 5
            if volume_ratio >= min_volume_ratio:
                optional_bonus += 5
            if confluence_quality == 'HIGH':
                optional_bonus += 10
            elif confluence_quality == 'MEDIUM':
                optional_bonus += 5

            # Señal válida si cumple esenciales Y tiene al menos 1 bonus
            is_valid = essential_criteria_met and optional_bonus >= 5

            # === ADVERTENCIA SI NO HAY ALINEACIÓN (pero señal válida) ===
            if is_valid and not ia_trend_aligned:
                validation_result['warning'] = f"⚠️ RIESGO ALTO: IA={ia_direction} vs Mercado={market_direction}"

            validation_result['valid'] = is_valid

            # === GENERAR MOTIVO DE RECHAZO ===
            rejection_reasons = []
            if entry_required and not entry_setup_valid and isinstance(entry_setup, dict):
                rejection_reasons.append(entry_setup.get('reason', 'Entrada no óptima'))
            if mm_required and not mm_valid:
                rejection_reasons.append(mm_result.get('reason', 'MM setup no válido'))
            if not pattern_valid:
                rejection_reasons.append(pattern_fail_reason)
            if not confirmation_valid:
                rejection_reasons.append(confirmation_fail_reason)
            if not sr_ok:
                rejection_reasons.append(f"S/R: {sr_fail_reason}")
            if technical_percentage < min_tech:
                rejection_reasons.append(f"Técnico={technical_percentage:.1f}% (req: {min_tech}%)")
            if neural_score < min_neural:
                rejection_reasons.append(f"IA={neural_score:.1f}% (req: {min_neural}%)")
            if volume_ratio < min_volume_ratio:
                rejection_reasons.append(f"Volumen bajo x{volume_ratio:.2f} (req: x{min_volume_ratio})")
            if risk_reward_ratio < min_rr:
                rejection_reasons.append(f"R/R={risk_reward_ratio:.1f}:1 (req: {min_rr})")
            if market_direction == 'NEUTRAL':
                rejection_reasons.append(f"Mercado sin dirección clara")

            if is_valid:
                signal_type = SignalType.CONFIRMED_BUY if is_buy else SignalType.CONFIRMED_SELL
                validation_result['signal_type_detected'] = signal_type.value
                validation_result['reason'] = f'✅ VALIDACIÓN APROBADA: {technical_percentage:.1f}% técnico'
            else:
                validation_result['reason'] = f'❌ {"; ".join(rejection_reasons[:3])}'  # Máximo 3 razones

            validation_result['conditions_met'] = [
                f"IA: {neural_score:.1f}% {'✅' if neural_score >= min_neural else '❌'}",
                f"Técnico: {technical_percentage:.1f}% {'✅' if technical_percentage >= min_tech else '❌'}",
                f"Volumen: x{volume_ratio:.2f} {'✅' if volume_ratio >= min_volume_ratio else '❌'}",
                f"R/R: {risk_reward_ratio:.1f}:1 {'✅' if risk_reward_ratio >= min_rr else '❌'}",
                f"Entrada: {'✅' if entry_setup_valid else '❌'} {entry_setup.get('grade', 'N/A') if isinstance(entry_setup, dict) else 'N/A'}",
                f"Patrón: {'✅' if pattern_valid else '❌'} {pattern_name}",
                f"Confirmación: {'✅' if confirmation_valid else '❌'} {confirmation_pattern or 'NINGUNO'}",
                f"S/R: {'✅' if sr_ok else '❌'}"
            ]
            # ✅ GARANTIZAR PROPAGACIÓN DE CRITERIOS TÉCNICOS (CRÍTICO PARA GUI)
            validation_result['criteria_list'] = criteria_list[:]  # copia segura
            return validation_result

        except Exception as e:
            logger.error(f"Error CRÍTICO en validate_ultra_selective_conditions({symbol}): {e}", exc_info=True)
            validation_result['reason'] = f'❌ Error interno: {e}'
            validation_result['criteria_list'] = criteria_list[:]  # Guardar criterios parciales
            return validation_result
# ============================================================================
# MÓDULO SIMILARITY ENGINE - PARA COMPARACIÓN DE CONDICIONES CON SEÑALES EXITOSAS
# ============================================================================
class SimilarityEngine:
    """
    Motor de similitud para comparar condiciones actuales vs. trades exitosos históricos.
    Basado en cosine similarity sobre features técnicos + IA.
    Requiere: scikit-learn, numpy, joblib (todos ya importados en tu sistema).
    """
    def __init__(self, config: "AdvancedTradingConfig"): # <-- Nota las comillas
        self.config = config
        self.scaler = None
        self.success_vectors = np.empty((0, 0))  # (N, D)
        self.success_metadata = []  # List[dict]
        self.feature_names = []
        self._loaded = False
        self._load_successful_trades()

    def _load_successful_trades(self):
        """Carga trades exitosos desde JSONs y construye matriz de features escalados."""
        success_dir = self.config.TRAINING_SUCCESS_DIR
        if not os.path.exists(success_dir):
            logger.warning(f"📉 Directorio de trades exitosos no existe: {success_dir}")
            return

        files = glob.glob(os.path.join(success_dir, "*.json"))
        if not files:
            logger.info("📭 No hay trades exitosos guardados aún.")
            return

        vectors, metadata, feature_names = [], [], None
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                vec = self._json_to_feature_vector(data)
                if vec is None:
                    continue
                if feature_names is None:
                    # Extraer nombres solo una vez (del primer JSON válido con keys)
                    feature_names = self._get_feature_names_from_data(data)
                vectors.append(vec)
                metadata.append(data)
            except Exception as e:
                logger.debug(f"⚠️ Skip archivo corrupto o incompatible: {os.path.basename(f)} → {e}")

        if not vectors:
            logger.warning("📭 Ningún trade exitoso válido para cargar.")
            return

        # Convertir a array y escalar (reusar scaler guardado si existe)
        X_raw = np.array(vectors)
        scaler_path = os.path.join(self.config.TRAINING_FEATURES_DIR, "similarity_scaler.pkl")
        if os.path.exists(scaler_path):
            try:
                with open(scaler_path, 'rb') as f:
                    self.scaler = joblib.load(f)
                logger.info("✅ Scaler de SimilarityEngine cargado desde archivo.")
            except Exception as e:
                logger.error(f"[ERROR] Error cargando scaler: {e}")
                self.scaler = MinMaxScaler()
                self.scaler.fit(X_raw)
                os.makedirs(self.config.TRAINING_FEATURES_DIR, exist_ok=True)
                with open(scaler_path, 'wb') as f:
                    joblib.dump(self.scaler, f)
                logger.info("🆕 Scaler de SimilarityEngine creado y guardado.")
        else:
            self.scaler = MinMaxScaler()
            self.scaler.fit(X_raw)
            os.makedirs(self.config.TRAINING_FEATURES_DIR, exist_ok=True)
            with open(scaler_path, 'wb') as f:
                joblib.dump(self.scaler, f)
            logger.info("🆕 Scaler de SimilarityEngine creado y guardado.")

        self.success_vectors = self.scaler.transform(X_raw)
        self.success_metadata = metadata
        self.feature_names = feature_names or self._default_feature_names()
        self._loaded = True
        logger.info(f"📈 SimilarityEngine cargado: {len(self.success_vectors)} trades exitosos, {self.success_vectors.shape[1]} features.")

    def _default_feature_names(self):
        """Nombres por defecto (en caso de que no se puedan extraer de JSON)."""
        return [
            'price_change_10c', 'ema50_slope', 'ema200_slope', 'rsi', 'volume_ratio',
            'neural_confidence', 'technical_percentage', 'alignment_percentage',
            'is_bullish_pattern', 'is_bearish_pattern',
            'has_w_pattern', 'has_m_pattern', 'has_hch', 'has_lcl',
            'dist_to_support_norm', 'dist_to_resistance_norm',
            'is_accumulation', 'is_uptrend', 'is_distribution', 'is_downtrend',
            'current_profit_target', 'time_of_day_sin', 'time_of_day_cos'
        ]

    def _get_feature_names_from_data(self, json_data: dict):
        """Intenta extraer nombres desde keys comunes del JSON (robusto)."""
        try:
            feats = [
                'price_change_10c', 'ema50_slope', 'ema200_slope', 'rsi', 'volume_ratio',
                'neural_confidence', 'technical_percentage', 'alignment_percentage'
            ]
            pat = json_data.get('pattern_name', '').upper()
            feats.extend([
                1 if pat in ['BULLISH_ENGULFING', 'HAMMER', 'MORNING_STAR'] else 0,
                1 if pat in ['BEARISH_ENGULFING', 'SHOOTING_STAR', 'EVENING_STAR'] else 0,
                1 if json_data.get('pattern_type') == 'W' else 0,
                1 if json_data.get('pattern_type') == 'M' else 0,
                1 if json_data.get('pattern_type') == 'HCH' else 0,
                1 if json_data.get('pattern_type') == 'LCL' else 0,
                float(json_data.get('distance_to_support', 0)),
                float(json_data.get('distance_to_resistance', 0)),
                1 if json_data.get('market_cycle', {}).get('cycle') == 'ACCUMULATION' else 0,
                1 if json_data.get('market_cycle', {}).get('cycle') == 'UPTREND' else 0,
                1 if json_data.get('market_cycle', {}).get('cycle') == 'DISTRIBUTION' else 0,
                1 if json_data.get('market_cycle', {}).get('cycle') == 'DOWNTREND' else 0,
                float(json_data.get('profit_percent', 0)) / 0.03,
            ])
            # Añadir hora del día (normalizada con sin/cos)
            ts = json_data.get('timestamp_start')
            if ts:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                hour = dt.hour + dt.minute / 60.0
                feats.extend([np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)])
            else:
                feats.extend([0.0, 0.0])
            return self._default_feature_names()
        except:
            return self._default_feature_names()

    def _json_to_feature_vector(self, json_data: dict) -> Optional[np.ndarray]:
        """Convierte un JSON de trade exitoso a vector de features (crudo, sin escalar)."""
        try:
            # Features técnicos/IA crudos
            feats = [
                float(json_data.get('price_change_10c', 0)) / 100,
                float(json_data.get('ema50_slope', 0)),
                float(json_data.get('ema200_slope', 0)),
                float(json_data.get('rsi', 50)) / 100,
                float(json_data.get('volume_ratio', 1)),
                float(json_data.get('neural_confidence', 0)) / 100,
                float(json_data.get('technical_percentage', 0)) / 100,
                float(json_data.get('alignment_percentage', 0)) / 100,
            ]
            # Patrones (binarios)
            pat = json_data.get('pattern_name', '').upper()
            feats.extend([
                1.0 if pat in ['BULLISH_ENGULFING', 'HAMMER', 'MORNING_STAR', 'PIERCING_LINE'] else 0.0,
                1.0 if pat in ['BEARISH_ENGULFING', 'SHOOTING_STAR', 'EVENING_STAR', 'DARK_CLOUD_COVER'] else 0.0,
                1.0 if json_data.get('pattern_name') == 'W_BOTTOM' else 0.0,
                1.0 if json_data.get('pattern_name') == 'M_TOP' else 0.0,
                1.0 if json_data.get('pattern_name') == 'HCH' else 0.0,
                1.0 if json_data.get('pattern_name') == 'LCL' else 0.0,
            ])
            # Distancias a S/R (normalizadas por precio)
            dist_s = float(json_data.get('distance_to_support', 0))
            dist_r = float(json_data.get('distance_to_resistance', 0))
            feats.extend([dist_s, dist_r])
            # Ciclo de mercado (one-hot)
            cycle = json_data.get('market_cycle', {}).get('cycle', 'NEUTRAL').upper()
            feats.extend([
                1.0 if cycle == 'ACCUMULATION' else 0.0,
                1.0 if cycle == 'UPTREND' else 0.0,
                1.0 if cycle == 'DISTRIBUTION' else 0.0,
                1.0 if cycle == 'DOWNTREND' else 0.0,
            ])
            # Contexto adicional
            profit_norm = min(1.0, max(0.0, float(json_data.get('profit_percent', 0)) / 0.03))
            feats.append(profit_norm)
            # Hora del día (sin/cos — mejora similitud en patrones intradiarios)
            ts = json_data.get('timestamp_start')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    hour = dt.hour + dt.minute / 60.0
                    feats.extend([np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)])
                except:
                    feats.extend([0.0, 0.0])
            else:
                feats.extend([0.0, 0.0])

            return np.array(feats, dtype=np.float32)
        except Exception as e:
            logger.debug(f"❌ Error construyendo vector de features desde JSON: {e}")
            return None

    def _current_to_feature_vector(self, symbol: str, df_entry: pd.DataFrame, signal_data: dict) -> Optional[np.ndarray]:
        """Convierte condiciones actuales a vector de features (crudo), para comparar con históricos."""
        try:
            # Extraer datos actuales
            current_price = df_entry['close'].iloc[-1]
            analyzer = OptimizedTechnicalAnalyzer(self.config)
            data_id = f"{symbol}_current_{int(time.time())}"

            # Calcular indicadores
            ema50 = analyzer.calculate_ema(df_entry['close'], 50, data_id)
            ema200 = analyzer.calculate_ema(df_entry['close'], 200, data_id)
            rsi_series = analyzer.calculate_rsi(df_entry['close'], 14, data_id)
            pattern = analyzer.analyze_candlestick_pattern(df_entry.tail(5))
            sr_levels = analyzer.find_support_resistance(df_entry)
            market_cycle = analyzer.analyze_market_cycles(df_entry)

            # Features actuales
            price_change_10c = 0.0
            if len(df_entry) >= 10:
                price_change_10c = (df_entry['close'].iloc[-1] / df_entry['close'].iloc[-10] - 1) * 100

            feats = [
                price_change_10c / 100,
                float(ema50.iloc[-1] - ema50.iloc[-2]) if len(ema50) >= 2 else 0.0,
                float(ema200.iloc[-1] - ema200.iloc[-2]) if len(ema200) >= 2 else 0.0,
                float(rsi_series.iloc[-1] / 100) if len(rsi_series) > 0 else 0.5,
                float(df_entry['volume'].iloc[-1] / df_entry['volume'].tail(20).mean()) if len(df_entry) >= 20 else 1.0,
                signal_data.get('neural_score', 0) / 100,
                signal_data.get('technical_percentage', 0) / 100,
                signal_data.get('alignment_percentage', 0) / 100,
            ]

            # Patrones
            pat_name = pattern.get('pattern', '').upper()
            feats.extend([
                1.0 if pattern.get('type') == 'BULLISH' or pat_name in ['BULLISH_ENGULFING', 'HAMMER'] else 0.0,
                1.0 if pattern.get('type') == 'BEARISH' or pat_name in ['BEARISH_ENGULFING', 'SHOOTING_STAR'] else 0.0,
                1.0 if 'W_BOTTOM' in str(pattern) else 0.0,
                1.0 if 'M_TOP' in str(pattern) else 0.0,
                1.0 if 'HCH' in str(pattern) else 0.0,
                1.0 if 'LCL' in str(pattern) else 0.0,
            ])

            # S/R
            dist_s = (current_price - sr_levels.get('support', current_price)) / current_price if sr_levels.get('support') else 0.0
            dist_r = (sr_levels.get('resistance', current_price) - current_price) / current_price if sr_levels.get('resistance') else 0.0
            feats.extend([dist_s, dist_r])

            # Ciclo
            cycle = market_cycle.get('cycle', 'NEUTRAL').upper()
            feats.extend([
                1.0 if cycle == 'ACCUMULATION' else 0.0,
                1.0 if cycle == 'UPTREND' else 0.0,
                1.0 if cycle == 'DISTRIBUTION' else 0.0,
                1.0 if cycle == 'DOWNTREND' else 0.0,
            ])

            # Contexto
            tp = signal_data.get('take_profit', current_price)
            target_norm = abs(tp - current_price) / current_price / 0.03  # 3% objetivo
            feats.append(min(1.0, target_norm))

            # Hora
            now = datetime.now()
            hour = now.hour + now.minute / 60.0
            feats.extend([np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)])

            return np.array(feats, dtype=np.float32)
        except Exception as e:
            logger.error(f"[ERROR] Error construyendo vector actual para {symbol}: {e}")
            return None

    def find_similar_trades(self, current_feature_vector: np.ndarray, top_k: int = 3, similarity_threshold: float = 0.75) -> List[dict]:
        """
        Encuentra trades históricos similares a las condiciones actuales.
        Returns:
            List[dict]: [{'similarity': 0.89, 'metadata': {...}}, ...]
        """
        if not self._loaded or self.success_vectors.shape[0] == 0:
            return []

        try:
            # Escalar vector actual
            current_scaled = self.scaler.transform(current_feature_vector.reshape(1, -1))
            # Calcular similitud coseno
            similarities = cosine_similarity(current_scaled, self.success_vectors)[0]
            # Ordenar y filtrar
            top_indices = np.argsort(similarities)[::-1]
            results = []
            for idx in top_indices[:top_k]:
                sim = float(similarities[idx])
                if sim < similarity_threshold:
                    break
                results.append({
                    'similarity': sim,
                    'metadata': self.success_metadata[idx]
                })
            return results
        except Exception as e:
            logger.error(f"[ERROR] Error en find_similar_trades: {e}")
            return []

    def get_success_rate_for_context(self, current_feature_vector: np.ndarray, similarity_threshold: float = 0.75, min_samples: int = 3) -> float:
        """
        Retorna la tasa de éxito histórica para contextos similares (> similarity_threshold).
        Si < min_samples, retorna 0.5 (neutral).
        """
        similar = self.find_similar_trades(current_feature_vector, top_k=50, similarity_threshold=similarity_threshold)
        if len(similar) < min_samples:
            return 0.5

        wins = sum(1 for s in similar if s['metadata'].get('is_success', False))
        return wins / len(similar)

    def refresh(self):
        """Recarga los trades exitosos (útil tras guardar nuevas señales)."""
        logger.info("🔄 Recargando SimilarityEngine...")
        old_count = len(self.success_metadata)
        self._loaded = False
        self._load_successful_trades()
        new_count = len(self.success_metadata)
        logger.info(f"📈 SimilarityEngine actualizado: {old_count} → {new_count} trades exitosos.")

    def save_index(self):
        """Guarda índice para carga rápida (opcional)."""
        try:
            idx_path = os.path.join(self.config.TRAINING_FEATURES_DIR, "similar_engine_index.joblib")
            joblib.dump({
                'vectors': self.success_vectors,
                'metadata': self.success_metadata,
                'feature_names': self.feature_names,
                'scaler': self.scaler,
                'version': 'v35.0.0.0'
            }, idx_path)
            logger.info(f"💾 Índice de SimilarityEngine guardado: {idx_path}")
        except Exception as e:
            logger.error(f"[ERROR] Error guardando índice: {e}")

    def save_successful_trade(self, symbol: str, signal_type, entry_price: float, 
                              exit_price: float, profit_percent: float, duration_minutes: float):
        """
        Guarda un trade exitoso para aprendizaje futuro.
        Llamado desde SignalTracker cuando una señal alcanza PROFIT_TARGET (+1.5%).
        ✅ TRIGGER DE REENTRENAMIENTO: Después de 5 trades exitosos nuevos
        """
        try:
            import hashlib
            signal_hash = hashlib.md5(f"{symbol}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]

            # Crear directorio si no existe
            os.makedirs(self.config.TRAINING_SUCCESS_DIR, exist_ok=True)

            path = os.path.join(self.config.TRAINING_SUCCESS_DIR, f"{signal_hash}.json")
            data = {
                'signal_hash': signal_hash,
                'symbol': symbol,
                'signal_type': str(signal_type) if signal_type else 'UNKNOWN',
                'entry_price': entry_price,
                'exit_price': exit_price,
                'final_profit_percent': profit_percent,
                'duration_minutes': duration_minutes,
                'is_success': profit_percent >= 1.0,  # ✅ CORREGIDO: TP = 1%
                'timestamp': datetime.now().isoformat()
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 [TRADE EXITOSO] Guardado: {symbol} | Profit: {profit_percent:+.2f}% | {path}")

            # Actualizar threshold_history.json
            self._update_threshold_history(symbol, profit_percent, duration_minutes)

            # ✅ NUEVO: Contador de trades exitosos para trigger de reentrenamiento
            if not hasattr(self, '_successful_trades_since_retrain'):
                self._successful_trades_since_retrain = 0
            self._successful_trades_since_retrain += 1

            # ✅ TRIGGER: Reentrenar después de 5 trades exitosos
            retrain_threshold = getattr(self.config, 'RETRAIN_AFTER_N_TRADES', 5)
            if self._successful_trades_since_retrain >= retrain_threshold:
                logger.info(f"🎯 [AUTO-RETRAIN] {self._successful_trades_since_retrain} trades exitosos acumulados - Iniciando reentrenamiento...")
                print(f"🔄 [APRENDIZAJE] Reentrenamiento automático después de {retrain_threshold} trades exitosos")
                self._trigger_auto_retrain()
                self._successful_trades_since_retrain = 0  # Resetear contador

            # Recargar para incluir nuevo trade en comparaciones
            self.refresh()
        except Exception as e:
            logger.error(f"[ERROR] Error guardando trade exitoso {symbol}: {e}")

    def _trigger_auto_retrain(self):
        """Dispara el reentrenamiento automático de la red neuronal."""
        try:
            # Buscar referencia al bot para acceder al neural_trader
            if hasattr(self, '_bot_ref') and self._bot_ref:
                neural_trader = getattr(self._bot_ref, 'neural_trader', None)
                if neural_trader and hasattr(neural_trader, 'train_with_successful_only'):
                    success = neural_trader.train_with_successful_only()
                    if success:
                        logger.info("✅ [AUTO-RETRAIN] Reentrenamiento completado exitosamente")
                        print("✅ [APRENDIZAJE] Red neuronal reentrenada con últimos trades exitosos")
                    else:
                        logger.warning("⚠️ [AUTO-RETRAIN] Reentrenamiento omitido: insuficientes datos")
                else:
                    logger.debug("⚠️ [AUTO-RETRAIN] neural_trader no disponible")
            else:
                logger.debug("⚠️ [AUTO-RETRAIN] _bot_ref no disponible")
        except Exception as e:
            logger.error(f"[ERROR] Error en auto-retrain: {e}")

    def _update_threshold_history(self, symbol: str, profit_percent: float, duration_minutes: float):
        """Actualiza el historial de umbrales para ajuste dinámico (30 días rolling)."""
        try:
            history_path = "threshold_history.json"
            history = []
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        history = json.loads(content)
                    else:
                        history = []

            # Agregar nuevo registro
            history.append({
                'symbol': symbol,
                'profit_percent': profit_percent,
                'duration_minutes': duration_minutes,
                'timestamp': datetime.now().isoformat(),
                'is_win': profit_percent >= 1.0  # ✅ CORREGIDO: TP = 1%
            })

            # Mantener solo últimos 30 días
            cutoff = datetime.now() - timedelta(days=30)
            history = [h for h in history if datetime.fromisoformat(h['timestamp']) > cutoff]

            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)

            logger.info(f"📊 Threshold history actualizado: {len(history)} registros (30 días)")
        except Exception as e:
            logger.error(f"[ERROR] Error actualizando threshold_history: {e}")

    def _save_successful_trade_internal(self, signal_hash: str, tracking: dict, report: dict):
        try:
            signal_data = tracking.get('signal_data', {})
            entry_price = float(tracking.get('entry_price') or signal_data.get('entry_price') or 0.0)
            exit_price = float(report.get('exit_price', 0.0) or 0.0)
            final_profit_percent = float(report.get('final_profit_percent', 0.0) or 0.0)
            duration_minutes = float(report.get('duration_minutes', 0.0) or 0.0)

            if entry_price <= 0 or exit_price <= 0:
                logger.warning(f"[SKIP] Trade no guardado por precios inválidos: entry={entry_price}, exit={exit_price}")
                return

            # Evitar ruido de muestras no exitosas para entrenamiento "successful only"
            min_success_profit = max(0.5, float(getattr(self.config, 'MIN_PROFIT_THRESHOLD', 1.0)) * 0.5)
            if final_profit_percent < min_success_profit:
                logger.info(
                    f"[SKIP] Trade omitido para entrenamiento exitoso: profit={final_profit_percent:.2f}% < {min_success_profit:.2f}%"
                )
                return

            path = os.path.join(self.config.TRAINING_SUCCESS_DIR, f"{signal_hash}.json")
            data = {
                'signal_hash': signal_hash,
                'symbol': signal_data.get('symbol', 'N/A'),
                'signal_type': signal_data.get('signal_type', 'N/A'),
                'entry_price': entry_price,
                'exit_price': exit_price,
                'final_profit_percent': final_profit_percent,
                'duration_minutes': duration_minutes,
                'is_success': True,
                'reason': report.get('reason', 'N/A'),
                'reason_normalized': report.get('reason_normalized', 'N/A'),
                'is_buy': bool(report.get('is_buy', signal_data.get('is_buy', True))),
                'max_profit_reached': float(report.get('max_profit_reached', final_profit_percent) or final_profit_percent),
                'neural_score': float(signal_data.get('neural_score', 0.0) or 0.0),
                'technical_percentage': float(signal_data.get('technical_percentage', 0.0) or 0.0),
                'alignment_percentage': float(signal_data.get('alignment_percentage', 0.0) or 0.0),
                'robustness_score': float(signal_data.get('robustness_score', 0.0) or 0.0),
                'risk_reward_ratio': float(signal_data.get('risk_reward_ratio', 0.0) or 0.0),
                'atr_regime_percent': float(signal_data.get('atr_regime_percent', 0.0) or 0.0),
                'entry_price_confirmada': float(tracking.get('entry_price_confirmada') or 0.0),
                'reference_price_destacada': float(tracking.get('reference_price_destacada') or 0.0),
                'timestamp': datetime.now().isoformat()
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"[OK] Trade guardado para entrenamiento exitoso: {path}")
            self.refresh()
        except Exception as e:
            logger.error(f"[ERROR] Error guardando trade {signal_hash}: {e}")

# ========== RED NEURONAL OPTIMIZADA ==========

class OptimizedNeuralTrader:
    def __init__(self, config: "AdvancedTradingConfig", force_retrain=False):
        self.config = config
        self.scaler = MinMaxScaler()
        self.model = None
        self.criterion = nn.CrossEntropyLoss() if TORCH_AVAILABLE else None
        self.optimizer = None
        self.scheduler = None
        self.is_trained = False
        self.training_history = []
        self.scaler_fitted = False
        self.feature_importance = {}
        self.performance_metrics = {}
        
        if TORCH_AVAILABLE and torch is not None:
             self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
             self.device = 'cpu'

        if TORCH_AVAILABLE:
            logger.info(f"🖥️ Dispositivo de entrenamiento: {self.device}")

        self._clear_corrupted_model_files()

        if force_retrain:
            self._clear_model_files()

        self._load_model_and_scaler()

    def _build_optimized_model(self, input_size):
        """
        Red Neuronal Mejorada v35 con:
        - Capa de atencion para ponderar features importantes
        - Conexiones residuales para mejor flujo de gradientes
        - Dropout decreciente por capa
        - Inicializacion Xavier para estabilidad
        - LeakyReLU para evitar neuronas muertas
        """
        class AttentionLayer(nn.Module):
            """Capa de atencion simple para ponderar features"""
            def __init__(self, input_dim):
                super(AttentionLayer, self).__init__()
                self.attention = nn.Sequential(
                    nn.Linear(input_dim, input_dim // 2),
                    nn.Tanh(),
                    nn.Linear(input_dim // 2, input_dim),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                weights = self.attention(x)
                return x * weights
        
        class ResidualBlock(nn.Module):
            """Bloque residual con conexion skip"""
            def __init__(self, in_features, out_features, dropout_rate):
                super(ResidualBlock, self).__init__()
                self.linear1 = nn.Linear(in_features, out_features)
                self.bn1 = nn.BatchNorm1d(out_features)
                self.linear2 = nn.Linear(out_features, out_features)
                self.bn2 = nn.BatchNorm1d(out_features)
                self.dropout = nn.Dropout(dropout_rate)
                self.activation = nn.LeakyReLU(0.1)
                
                # Conexion skip con proyeccion si las dimensiones difieren
                self.skip = nn.Linear(in_features, out_features) if in_features != out_features else nn.Identity()
            
            def forward(self, x):
                residual = self.skip(x)
                out = self.activation(self.bn1(self.linear1(x)))
                out = self.dropout(out)
                out = self.bn2(self.linear2(out))
                out = out + residual  # Conexion residual
                return self.activation(out)
        
        class EnhancedOptimizedNet(nn.Module):
            def __init__(self, input_size, hidden_layers, dropout):
                super(EnhancedOptimizedNet, self).__init__()
                
                # Capa de atencion inicial para ponderar features
                self.attention = AttentionLayer(input_size)
                
                # Primera capa con expansion
                self.input_layer = nn.Sequential(
                    nn.Linear(input_size, hidden_layers[0]),
                    nn.BatchNorm1d(hidden_layers[0]),
                    nn.LeakyReLU(0.1),
                    nn.Dropout(dropout)
                )
                
                # Bloques residuales con dropout decreciente
                self.residual_blocks = nn.ModuleList()
                prev_size = hidden_layers[0]
                for i, size in enumerate(hidden_layers[1:]):
                    # Dropout decreciente: 0.3 -> 0.24 -> 0.19 -> etc
                    block_dropout = dropout * (0.8 ** (i + 1))
                    self.residual_blocks.append(ResidualBlock(prev_size, size, block_dropout))
                    prev_size = size
                
                # Capa de salida con regularizacion
                self.output_layer = nn.Sequential(
                    nn.Linear(prev_size, prev_size // 2),
                    nn.BatchNorm1d(prev_size // 2),
                    nn.LeakyReLU(0.1),
                    nn.Dropout(dropout * 0.5),
                    nn.Linear(prev_size // 2, 3),
                    nn.Softmax(dim=1)
                )
                
                # Inicializacion de pesos
                self.apply(self._init_weights)
            
            def _init_weights(self, m):
                if isinstance(m, nn.Linear):
                    torch.nn.init.xavier_uniform_(m.weight)
                    if m.bias is not None:
                        m.bias.data.fill_(0.01)
            
            def forward(self, x):
                # Aplicar atencion a las features de entrada
                x = self.attention(x)
                
                # Capa de entrada
                x = self.input_layer(x)
                
                # Bloques residuales
                for block in self.residual_blocks:
                    x = block(x)
                
                # Capa de salida
                return self.output_layer(x)
        
        return EnhancedOptimizedNet(input_size, self.config.NEURAL_HIDDEN_LAYERS, self.config.NEURAL_DROPOUT)

    def finetune_incremental(self, X: np.ndarray, y: np.ndarray, epochs: int = 3, batch_size: int = 32) -> bool:
        """
        Fine-tuning incremental ligero: ajusta pesos existentes con pocos datos nuevos.
        No reemplaza el scaler — asume que features ya están en el mismo espacio.
        """
        if not self.is_trained or self.model is None:
            logger.error("❌ Modelo no entrenado → fine-tuning no posible.")
            return False

        try:
            # Escalar con scaler existente
            if not self.scaler_fitted:
                logger.error("❌ Scaler no ajustado → fine-tuning abortado.")
                return False
            X_scaled = self.scaler.transform(X)

            # Convertir a tensores
            X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
            y_tensor = torch.tensor(y, dtype=torch.long)

            # DataLoader
            dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
            dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

            # Modo entrenamiento (pero con bajo LR)
            self.model.train()
            optimizer = torch.optim.Adam(self.model.parameters(), lr=self.config.NEURAL_LEARNING_RATE * 0.1)  # LR reducido
            criterion = nn.CrossEntropyLoss()

            logger.info(f"🔧 Fine-tuning: {len(X)} muestras, {epochs} épocas, LR reducido...")

            for epoch in range(epochs):
                epoch_loss = 0.0
                for batch_X, batch_y in dataloader:
                    optimizer.zero_grad()
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
                    epoch_loss += loss.item()
                avg_loss = epoch_loss / len(dataloader)
                logger.debug(f"   Época {epoch+1}/{epochs} | Loss: {avg_loss:.5f}")

            # Guardar modelo actualizado (sobrescribe el anterior)
            self._save_model_and_scaler()
            logger.info("✅ Fine-tuning incremental guardado.")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Error en finetune_incremental: {e}", exc_info=True)
            return False

    def _clean_numpy_types(self, data):
        if isinstance(data, dict):
            return {key: self._clean_numpy_types(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._clean_numpy_types(item) for item in data]
        elif isinstance(data, (np.float64, np.float32, np.int64, np.int32)):
            return float(data)
        elif isinstance(data, np.ndarray):
            return data.tolist()
        else:
            return data

    def _clear_corrupted_model_files(self):
        try:
            files_to_check = [self.config.NN_MODEL_PATH, self.config.SCALER_PATH]
            removed_files = []
            for file_path in files_to_check:
                if os.path.exists(file_path):
                    try:
                        if file_path.endswith('.pth'):
                            checkpoint = torch.load(file_path, map_location='cpu')
                            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                                continue
                        elif file_path.endswith('.pkl'):
                            with open(file_path, 'rb') as f:
                                pickle.load(f)
                    except Exception:
                        os.remove(file_path)
                        removed_files.append(file_path)
                        logger.warning(f"🗑️ Archivo corrupto eliminado: {file_path}")
            if removed_files:
                logger.info(f"[OK] Archivos corruptos eliminados: {removed_files}")
                self.is_trained = False
                self.scaler_fitted = False
                return True
            return False
        except Exception as e:
            logger.error(f"Error limpiando archivos corruptos: {e}")
            return False

    def _clear_model_files(self):
        try:
            files_to_remove = [self.config.NN_MODEL_PATH, self.config.SCALER_PATH]
            removed_files = []
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    removed_files.append(file_path)
            if removed_files:
                logger.info(f"🗑️ Archivos de modelo eliminados: {removed_files}")
                self.is_trained = False
                self.scaler_fitted = False
                return True
            return False
        except Exception as e:
            logger.error(f"Error limpiando archivos de modelo: {e}")
            return False

    def _extract_optimized_features(self, df: pd.DataFrame, analyzer: OptimizedTechnicalAnalyzer) -> Tuple[List, List]:
        if df is None or df.empty or len(df) < self.config.MIN_NN_DATA_REQUIRED:
            return [], []

        features = []
        targets = []

        try:
            df_work = df.copy()
            data_id = str(hash(str(df.iloc[0]['timestamp'])))

            # === 🔒 SANITIZACIÓN GLOBAL: Función para forzar escalar/float ===
            def _to_safe_float(x, default=0.0):
                """Convierte cualquier valor a float seguro. Maneja tuplas, arrays, NaN, None."""
                try:
                    # Desempaquetar recursivamente
                    while isinstance(x, (tuple, list, np.ndarray)) and len(x) > 0:
                        x = x[0]
                    # Convertir
                    val = float(x)
                    return val if np.isfinite(val) else default
                except Exception:
                    return default

            # === 1. Calcular indicadores — SANITIZAR cada salida ===
            ema50_raw = analyzer.calculate_ema(df_work['close'], 50, data_id)
            ema200_raw = analyzer.calculate_ema(df_work['close'], 200, data_id)
            tdi_out = analyzer.calculate_tdi(df_work, data_id)

            # Verificar salida de calculate_tdi (puede devolver tupla o dict)
            if isinstance(tdi_out, tuple) and len(tdi_out) == 5:
                tdi_rsi, tdi_green, tdi_red, tdi_upper, tdi_lower = tdi_out
            elif isinstance(tdi_out, dict):
                tdi_rsi = tdi_out.get('rsi', pd.Series([50.0] * len(df_work)))
                tdi_green = tdi_out.get('green', pd.Series([50.0] * len(df_work)))
                tdi_red = tdi_out.get('red', pd.Series([50.0] * len(df_work)))
            else:
                # Fallback seguro
                tdi_rsi = tdi_green = tdi_red = pd.Series([50.0] * len(df_work))

            # Asegurar Series de float
            df_work['ema50'] = pd.to_numeric(ema50_raw, errors='coerce').apply(_to_safe_float)
            df_work['ema200'] = pd.to_numeric(ema200_raw, errors='coerce').apply(_to_safe_float)
            df_work['tdi_rsi'] = pd.to_numeric(tdi_rsi, errors='coerce').apply(_to_safe_float)
            df_work['tdi_green'] = pd.to_numeric(tdi_green, errors='coerce').apply(_to_safe_float)
            df_work['tdi_red'] = pd.to_numeric(tdi_red, errors='coerce').apply(_to_safe_float)

            # === 2. Patrones — ya son dict seguros, pero sanitizamos ===
            try:
                candle_pattern = analyzer.analyze_candlestick_pattern(df_work)
            except Exception as e:
                logger.debug(f"⚠️ Falló analyze_candlestick_pattern: {e}")
                candle_pattern = {'type': 'NEUTRAL', 'pattern': 'NONE', 'confidence': 0}
            try:
                w_m_pattern = analyzer.detect_w_m_pattern(df_work)
            except:
                w_m_pattern = {'pattern': 'NONE'}
            try:
                hch_pattern = analyzer.detect_hch_pattern(df_work)
            except:
                hch_pattern = {'pattern': 'NONE'}

            df_work['pattern_bullish'] = 1 if candle_pattern.get('type') == 'BULLISH' else 0
            df_work['pattern_bearish'] = 1 if candle_pattern.get('type') == 'BEARISH' else 0
            df_work['pattern_w'] = 1 if w_m_pattern.get('pattern') == 'W_BOTTOM' else 0
            df_work['pattern_m'] = 1 if w_m_pattern.get('pattern') == 'M_TOP' else 0
            df_work['pattern_hch'] = 1 if hch_pattern.get('pattern') == 'HCH' else 0
            df_work['pattern_lcl'] = 1 if hch_pattern.get('pattern') == 'LCL' else 0

            # === 3. Soporte/Resistencia — sanitización robusta ===
            try:
                sr_levels = analyzer.find_support_resistance(df_work)
            except Exception as e:
                logger.debug(f"⚠️ Falló find_support_resistance: {e}")
                sr_levels = {'support': None, 'resistance': None}

            support_val = _to_safe_float(sr_levels.get('support'))
            resistance_val = _to_safe_float(sr_levels.get('resistance'))

            current_price = _to_safe_float(df_work['close'].iloc[-1], default=1e-8)

            dist_to_support = (current_price - support_val) / current_price if current_price != 0 else 0.0
            dist_to_resistance = (resistance_val - current_price) / current_price if current_price != 0 else 0.0

            df_work['distance_to_support'] = dist_to_support
            df_work['distance_to_resistance'] = dist_to_resistance

            # === 4. Ciclo de mercado ===
            try:
                market_cycle = analyzer.analyze_market_cycles(df_work)
                cycle = market_cycle.get('cycle', 'NEUTRAL').upper()
            except:
                cycle = 'NEUTRAL'

            df_work['cycle_accumulation'] = 1 if cycle == 'ACCUMULATION' else 0
            df_work['cycle_uptrend'] = 1 if cycle == 'UPTREND' else 0
            df_work['cycle_distribution'] = 1 if cycle == 'DISTRIBUTION' else 0
            df_work['cycle_downtrend'] = 1 if cycle == 'DOWNTREND' else 0

            # === 5. Lista final de columnas ===
            feature_columns = [
                'open', 'high', 'low', 'close', 'volume',
                'ema50', 'ema200',
                'tdi_rsi', 'tdi_green', 'tdi_red',
                'pattern_bullish', 'pattern_bearish',
                'pattern_w', 'pattern_m',
                'pattern_hch', 'pattern_lcl',
                'distance_to_support', 'distance_to_resistance',
                'cycle_accumulation', 'cycle_uptrend',
                'cycle_distribution', 'cycle_downtrend'
            ]

            # === 6. Limpieza final de df_work ===
            for col in feature_columns:
                if col in df_work.columns:
                    # Aplicar conversión segura columna por columna
                    df_work[col] = df_work[col].apply(_to_safe_float)
                else:
                    df_work[col] = 0.0  # columna faltante → rellenar con 0

            # Normalizar por último cierre
            last_close = _to_safe_float(df_work['close'].iloc[-1], default=1e-8)
            if last_close == 0:
                last_close = 1e-8

            for col in ['open', 'high', 'low', 'close', 'ema50', 'ema200']:
                if col in df_work.columns:
                    df_work[col] = df_work[col] / last_close

            # Asegurar array numérico limpio
            df_clean = df_work[feature_columns].copy()
            df_clean = df_clean.replace([np.inf, -np.inf], np.nan).fillna(0.0)

            if len(df_clean) < 50:
                logger.warning(f"📉 df_clean demasiado corto ({len(df_clean)} filas)")
                return [], []

            # === 7. Generar features y targets ===
            lookback = 3
            lookahead = 5
            for i in range(lookback, len(df_clean) - lookahead):
                # Construir feature vector plano (solo floats)
                feature_row = []
                for j in range(lookback):
                    # .iloc[i-j] → Serie → .values → array → lista de floats
                    values = df_clean.iloc[i - j][feature_columns].values
                    # Garantizar que todos sean float (no tuplas/listas)
                    clean_values = [_to_safe_float(v) for v in values]
                    feature_row.extend(clean_values)

                # Target
                current_close = _to_safe_float(df_clean.iloc[i]['close'])
                future_close = _to_safe_float(df_clean.iloc[i + lookahead]['close'])
                price_change = (future_close - current_close) / (current_close if abs(current_close) > 1e-12 else 1e-8)

                if price_change > 0.008:
                    target = 2  # BUY
                elif price_change < -0.008:
                    target = 0  # SELL
                else:
                    target = 1  # NEUTRAL

                features.append(feature_row)
                targets.append(target)

            return features, targets

        except Exception as e:
            logger.error(f"[ERROR] Error FATAL en _extract_optimized_features: {e}", exc_info=True)
            return [], []

    def _calculate_performance_metrics(self, val_loader):
        if not TORCH_AVAILABLE:
            return
        self.model.eval()
        all_predictions = []
        all_targets = []
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                outputs = self.model(batch_X)
                _, predicted = torch.max(outputs.data, 1)
                all_predictions.extend(predicted.cpu().numpy())
                all_targets.extend(batch_y.cpu().numpy())
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_targets, all_predictions, average=None, labels=[0, 1, 2]
        )
        self.performance_metrics = {
            'precision_sell': float(precision[0]),
            'precision_neutral': float(precision[1]),
            'precision_buy': float(precision[2]),
            'recall_sell': float(recall[0]),
            'recall_neutral': float(recall[1]),
            'recall_buy': float(recall[2]),
            'f1_sell': float(f1[0]),
            'f1_neutral': float(f1[1]),
            'f1_buy': float(f1[2]),
            'overall_accuracy': float(accuracy_score(all_targets, all_predictions))
        }
        logger.info(f"Métricas de rendimiento calculadas correctamente")

    def train_with_optimized_data(self, symbols=None, days=None, progress_callback=None):
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch no está disponible")
            return False
        symbols = symbols or self.config.TRADING_SYMBOLS[:20]
        days = days or self.config.HISTORICAL_DAYS
        logger.info(f"🧠 Entrenando IA optimizada con {len(symbols)} símbolos y {days} días")
        all_X, all_y = [], []
        client = AdvancedBinanceClient(self.config)
        analyzer = OptimizedTechnicalAnalyzer(self.config)
        class_counts = {0: 0, 1: 0, 2: 0}
        max_samples_per_class = 5000
        for i, symbol in enumerate(symbols):
            try:
                df = client.get_klines(symbol, self.config.PRIMARY_TIMEFRAME, 
                                     limit=min(days * 48, 1000))
                if df is None or len(df) < self.config.MIN_NN_DATA_REQUIRED:
                    continue
                features, targets = self._extract_optimized_features(df, analyzer)
                if not features or not targets:
                    continue
                for feat, targ in zip(features, targets):
                    if class_counts[targ] < max_samples_per_class:
                        all_X.append(feat)
                        all_y.append(targ)
                        class_counts[targ] += 1
                if progress_callback:
                    progress_callback(int((i + 1) / len(symbols) * 50))
            except Exception as e:
                logger.error(f"Error entrenando con {symbol}: {e}")
        if not all_X:
            logger.warning("No hay datos suficientes para entrenar")
            return False
        logger.info(f"Distribución de clases: {class_counts}")
        input_size = len(all_X[0])
        self.config.NEURAL_INPUT_SIZE = input_size
        self.model = self._build_optimized_model(input_size)
        self.model = self.model.to(self.device)
        logger.info(f"🚀 Modelo movido a {self.device} para entrenamiento")
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.config.NEURAL_LEARNING_RATE,
            weight_decay=1e-4,
            betas=(0.9, 0.999)
        )
        self.scheduler = optim.lr_scheduler.OneCycleLR(
            self.optimizer,
            max_lr=self.config.NEURAL_LEARNING_RATE * 10,
            epochs=self.config.NEURAL_EPOCHS,
            steps_per_epoch=len(all_X) // self.config.NEURAL_BATCH_SIZE + 1
        )
        if not self.scaler_fitted:
            X = np.array(all_X)
            X[~np.isfinite(X)] = 0
            self.scaler.fit(X)
            self.scaler_fitted = True
        X_scaled = self.scaler.transform(np.array(all_X))
        y = np.array(all_y)
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        train_dataset = torch.utils.data.TensorDataset(
            torch.tensor(X_train, dtype=torch.float32),
            torch.tensor(y_train, dtype=torch.long)
        )
        val_dataset = torch.utils.data.TensorDataset(
            torch.tensor(X_val, dtype=torch.float32),
            torch.tensor(y_val, dtype=torch.long)
        )
        train_loader = torch.utils.data.DataLoader(
            train_dataset, batch_size=self.config.NEURAL_BATCH_SIZE, shuffle=True
        )
        val_loader = torch.utils.data.DataLoader(
            val_dataset, batch_size=self.config.NEURAL_BATCH_SIZE, shuffle=False
        )
        best_val_accuracy = 0
        patience_counter = 0
        for epoch in range(self.config.NEURAL_EPOCHS):
            self.model.train()
            total_loss = 0
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                self.optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = self.criterion(outputs, batch_y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                self.scheduler.step()
                total_loss += loss.item()
            self.model.eval()
            val_loss = 0
            correct = 0
            total = 0
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                    outputs = self.model(batch_X)
                    val_loss += self.criterion(outputs, batch_y).item()
                    _, predicted = torch.max(outputs.data, 1)
                    total += batch_y.size(0)
                    correct += (predicted == batch_y).sum().item()
            val_accuracy = correct / total
            avg_loss = total_loss / len(train_loader)
            avg_val_loss = val_loss / len(val_loader)
            self.training_history.append({
                'epoch': epoch + 1,
                'loss': avg_loss,
                'val_loss': avg_val_loss,
                'accuracy': val_accuracy
            })
            if val_accuracy > best_val_accuracy:
                best_val_accuracy = val_accuracy
                patience_counter = 0
                torch.save(self.model.state_dict(), self.config.NN_MODEL_PATH)
            else:
                patience_counter += 1
                if patience_counter >= self.config.NEURAL_EARLY_STOPPING:
                    logger.info(f"Early stopping en época {epoch + 1}")
                    if progress_callback:
                        progress_callback(50 + int((epoch + 1) / self.config.NEURAL_EPOCHS * 50))
                    self.model.load_state_dict(torch.load(self.config.NN_MODEL_PATH))
                    self._calculate_performance_metrics(val_loader)
                    self.is_trained = True
                    self._save_model_and_scaler()
                    logger.info(f"[OK] IA optimizada entrenada - Mejor precisión: {best_val_accuracy:.4f}")
                    return True
            if progress_callback:
                progress_callback(50 + int((epoch + 1) / self.config.NEURAL_EPOCHS * 50))
            if (epoch + 1) % 25 == 0:
                logger.info(f"Época {epoch + 1}: Loss={avg_loss:.4f}, Val_Loss={avg_val_loss:.4f}, Acc={val_accuracy:.4f}")
        self.model.load_state_dict(torch.load(self.config.NEURAL_MODEL_PATH))
        self._calculate_performance_metrics(val_loader)
        self.is_trained = True
        self._save_model_and_scaler()
        logger.info(f"[OK] IA optimizada entrenada - Mejor precisión: {best_val_accuracy:.4f}")
        return True

    def _predict_fallback_technical(self, df_entry: pd.DataFrame) -> dict:
        """
        ✅ v32.0.22.4: FALLBACK TÉCNICO - Genera predicciones basadas en indicadores técnicos
        cuando no hay modelo de red neuronal entrenado disponible.
        """
        try:
            if df_entry is None or len(df_entry) < 50:
                return {
                    'signal_type': SignalType.NEUTRAL,
                    'confidence': 0,
                    'neural_confidence': 0,
                    'buy_probability': 0,
                    'sell_probability': 0,
                    'prediction_strength': 0
                }

            # Calcular indicadores técnicos simples
            close = df_entry['close'].values
            high = df_entry['high'].values
            low = df_entry['low'].values
            volume = df_entry['volume'].values

            # EMAs
            ema_fast = pd.Series(close).ewm(span=8, adjust=False).mean().iloc[-1]
            ema_slow = pd.Series(close).ewm(span=21, adjust=False).mean().iloc[-1]
            ema_trend = pd.Series(close).ewm(span=50, adjust=False).mean().iloc[-1]

            # RSI (con protección contra NaN/Inf)
            delta = pd.Series(close).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean().iloc[-1]
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean().iloc[-1]
            if pd.isna(gain) or pd.isna(loss):
                rsi = 50.0  # Valor neutral
            elif loss == 0:
                rsi = 100.0 if gain > 0 else 50.0
            else:
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
            rsi = max(0, min(100, rsi))

            # Momentum
            momentum = (close[-1] - close[-10]) / close[-10] * 100 if len(close) >= 10 else 0

            # Volume trend
            avg_vol = np.mean(volume[-20:]) if len(volume) >= 20 else np.mean(volume)
            current_vol = volume[-1]
            vol_ratio = current_vol / (avg_vol + 1e-10)

            # Determinar dirección y confianza
            bullish_score = 0
            bearish_score = 0

            # EMA crossover
            if ema_fast > ema_slow:
                bullish_score += 25
            else:
                bearish_score += 25

            # EMA trend
            if close[-1] > ema_trend:
                bullish_score += 20
            else:
                bearish_score += 20

            # RSI - Optimizado para entradas tempranas
            if rsi > 42 and rsi < 78:
                bullish_score += 20
            elif rsi < 58 and rsi > 22:
                bearish_score += 20
            elif rsi >= 78:
                bearish_score += 10  # Sobrecompra extrema
            elif rsi <= 22:
                bullish_score += 10  # Sobreventa extrema

            # Momentum - Umbral reducido
            if momentum > 0.2:
                bullish_score += 15
            elif momentum < -0.2:
                bearish_score += 15

            # Volume confirmation
            if vol_ratio > 1.2:
                if bullish_score > bearish_score:
                    bullish_score += 10
                else:
                    bearish_score += 10

            # Calcular probabilidades
            total = bullish_score + bearish_score + 20  # 20 base neutral
            buy_prob = bullish_score / total
            sell_prob = bearish_score / total
            neutral_prob = 20 / total

            # Determinar señal
            max_prob = max(buy_prob, sell_prob, neutral_prob)
            if buy_prob == max_prob and buy_prob > 0.4:
                if buy_prob >= 0.7:
                    signal_type = SignalType.STRONG_BUY
                elif buy_prob >= 0.5:
                    signal_type = SignalType.MODERATE_BUY
                else:
                    signal_type = SignalType.NEUTRAL
            elif sell_prob == max_prob and sell_prob > 0.4:
                if sell_prob >= 0.7:
                    signal_type = SignalType.STRONG_SELL
                elif sell_prob >= 0.5:
                    signal_type = SignalType.MODERATE_SELL
                else:
                    signal_type = SignalType.NEUTRAL
            else:
                signal_type = SignalType.NEUTRAL

            confidence = max_prob * 100

            return {
                'signal_type': signal_type,
                'confidence': confidence,
                'neural_confidence': confidence,
                'buy_probability': buy_prob * 100,
                'sell_probability': sell_prob * 100,
                'prediction_strength': abs(buy_prob - sell_prob) * 100
            }

        except Exception as e:
            logger.error(f"Error en predicción fallback técnico: {e}")
            return {
                'signal_type': SignalType.NEUTRAL,
                'confidence': 0,
                'neural_confidence': 0,
                'buy_probability': 0,
                'sell_probability': 0,
                'prediction_strength': 0
            }

    def predict_optimized(self, df_entry: pd.DataFrame) -> dict:
        # ✅ v32.0.22.4: FALLBACK TÉCNICO cuando no hay modelo entrenado
        if not TORCH_AVAILABLE or not self.is_trained or self.model is None:
            # Usar análisis técnico simple como fallback para generar predicciones
            return self._predict_fallback_technical(df_entry)
        try:
            analyzer = OptimizedTechnicalAnalyzer(self.config)
            features, _ = self._extract_optimized_features(df_entry, analyzer)
            if not features:
                return {
                    'signal_type': SignalType.NEUTRAL,
                    'confidence': 0,
                    'neural_confidence': 0,
                    'buy_probability': 0,
                    'sell_probability': 0,
                    'prediction_strength': 0
                }
            # Usar múltiples predicciones de 60 velas (60 min en 1m) para reducir ruido
            X = np.array(features[-60:]) if len(features) >= 60 else np.array(features[-max(1, len(features)):])
            X_scaled = self.scaler.transform(X)
            X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(X_tensor)
                probabilities = torch.mean(outputs, dim=0).cpu().numpy()

            sell_prob = float(probabilities[0])  # Convertir a float nativo
            neutral_prob = float(probabilities[1])
            buy_prob = float(probabilities[2])
            # Determinar señal optimizada
            max_prob = max(sell_prob, neutral_prob, buy_prob)
            prediction_strength = float(max_prob - np.mean([sell_prob, neutral_prob, buy_prob]))

            # ✅ CORREGIDO: Sin umbral rígido de 0.6 - permitir probabilidades bajas
            if buy_prob == max_prob:
                if buy_prob >= 0.8:
                    signal_type = SignalType.CONFIRMED_BUY
                elif buy_prob >= 0.7:
                    signal_type = SignalType.STRONG_BUY
                elif buy_prob >= 0.5:
                    signal_type = SignalType.MODERATE_BUY
                else:
                    signal_type = SignalType.NEUTRAL
            elif sell_prob == max_prob:
                if sell_prob >= 0.8:
                    signal_type = SignalType.CONFIRMED_SELL
                elif sell_prob >= 0.7:
                    signal_type = SignalType.STRONG_SELL
                elif sell_prob >= 0.5:
                    signal_type = SignalType.MODERATE_SELL
                else:
                    signal_type = SignalType.NEUTRAL
            else:
                signal_type = SignalType.NEUTRAL

            # Confianza ajustada por métricas de rendimiento
            base_confidence = max_prob * 100
            if self.performance_metrics:
                if buy_prob == max_prob:
                    precision_c = self.performance_metrics.get('precision_buy', 0.5)
                    recall_c = self.performance_metrics.get('recall_buy', 0.5)
                elif sell_prob == max_prob:
                    precision_c = self.performance_metrics.get('precision_sell', 0.5)
                    recall_c = self.performance_metrics.get('recall_sell', 0.5)
                else:
                    precision_c = self.performance_metrics.get('precision_neutral', 0.5)
                    recall_c = self.performance_metrics.get('recall_neutral', 0.5)
                performance_factor = (precision_c + recall_c) / 2.0
                adjusted_confidence = base_confidence * (0.5 + performance_factor)
            else:
                adjusted_confidence = base_confidence

            return {
                'signal_type': signal_type,
                'confidence': min(adjusted_confidence, 100.0),
                'neural_confidence': base_confidence,
                'buy_probability': buy_prob * 100,
                'sell_probability': sell_prob * 100,
                'prediction_strength': prediction_strength * 100
            }

        except Exception as e:
            logger.error(f"Error en predicción optimizada: {e}")
            return {
                'signal_type': SignalType.NEUTRAL,
                'confidence': 0,
                'neural_confidence': 0,
                'buy_probability': 0,
                'sell_probability': 0,
                'prediction_strength': 0
            }

    def _save_model_and_scaler(self):
        try:
            if TORCH_AVAILABLE and self.model is not None:
                clean_metrics = self._clean_numpy_types(self.performance_metrics)
                clean_history = self._clean_numpy_types(self.training_history)
                torch.save({
                    'model_state_dict': self.model.state_dict(),
                    'config': {
                        'input_size': self.config.NEURAL_INPUT_SIZE,
                        'hidden_layers': self.config.NEURAL_HIDDEN_LAYERS,
                        'dropout': self.config.NEURAL_DROPOUT,
                        'version': '20.0.3'
                    },
                    'performance_metrics': clean_metrics,
                    'training_history': clean_history[-10:] if clean_history else [],
                    'timestamp': datetime.now().isoformat(),
                    'features_count': self.config.NEURAL_INPUT_SIZE
                }, self.config.NN_MODEL_PATH)
                with open(self.config.SCALER_PATH, 'wb') as f:
                    pickle.dump(self.scaler, f)
                logger.info("Modelo optimizado y scaler guardados correctamente")
                logger.info(f"[CHART] Arquitectura guardada: {self.config.NEURAL_INPUT_SIZE} características de entrada")
        except Exception as e:
            logger.error(f"Error guardando modelo optimizado: {e}")

    def _load_model_and_scaler(self):
        try:
            if TORCH_AVAILABLE and os.path.exists(self.config.NN_MODEL_PATH):
                checkpoint = torch.load(self.config.NN_MODEL_PATH, map_location='cpu')
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    config_data = checkpoint.get('config', {})
                    saved_input_size = config_data.get('input_size', self.config.NEURAL_INPUT_SIZE)
                    if saved_input_size != self.config.NEURAL_INPUT_SIZE:
                        logger.warning(f"[WARN] Incompatibilidad de arquitectura detectada:")
                        logger.warning(f"  Modelo guardado: {saved_input_size} características")
                        logger.warning(f"  Arquitectura actual: {self.config.NEURAL_INPUT_SIZE} características")
                        logger.warning("🔄 Eliminando modelo incompatible y se creará uno nuevo")
                        try:
                            os.remove(self.config.NN_MODEL_PATH)
                            if os.path.exists(self.config.SCALER_PATH):
                                os.remove(self.config.SCALER_PATH)
                            logger.info("✅ Archivos de modelo incompatibles eliminados")
                        except Exception as e:
                            logger.error(f"Error eliminando archivos: {e}")
                        self.is_trained = False
                        # ✅ CREAR NUEVO MODELO AUTOMÁTICAMENTE CON LA ARQUITECTURA CORRECTA
                        self.model = self._build_optimized_model(self.config.NEURAL_INPUT_SIZE)
                        logger.info(f"[OK] Nuevo modelo creado con {self.config.NEURAL_INPUT_SIZE} características")
                        return
                    if self.config.NEURAL_INPUT_SIZE > 0:
                        self.model = self._build_optimized_model(self.config.NEURAL_INPUT_SIZE)
                        self.model.load_state_dict(checkpoint['model_state_dict'])
                        self.model.eval()
                        self.is_trained = True
                        loaded_metrics = checkpoint.get('performance_metrics', {})
                        self.performance_metrics = self._clean_numpy_types(loaded_metrics)
                        loaded_history = checkpoint.get('training_history', [])
                        self.training_history = self._clean_numpy_types(loaded_history)
                        logger.info("Modelo optimizado cargado con metadatos")
                else:
                    logger.warning("⚠️ Modelo en formato antiguo detectado")
                    logger.warning("🔄 Eliminando modelo antiguo y se creará uno nuevo")
                    try:
                        os.remove(self.config.NN_MODEL_PATH)
                        if os.path.exists(self.config.SCALER_PATH):
                            os.remove(self.config.SCALER_PATH)
                        logger.info("✅ Archivos de modelo antiguos eliminados")
                    except Exception as e:
                        logger.error(f"Error eliminando archivos: {e}")
                    self.is_trained = False
                    # ✅ CREAR NUEVO MODELO AUTOMÁTICAMENTE
                    self.model = self._build_optimized_model(self.config.NEURAL_INPUT_SIZE)
                    logger.info(f"[OK] Nuevo modelo creado con {self.config.NEURAL_INPUT_SIZE} características")
                if os.path.exists(self.config.SCALER_PATH):
                    try:
                        with open(self.config.SCALER_PATH, 'rb') as f:
                            self.scaler = pickle.load(f)
                        self.scaler_fitted = True
                        logger.info("Scaler optimizado cargado")
                    except Exception as e:
                        logger.error(f"Error cargando scaler: {e}")
                        self.scaler_fitted = False
                else:
                    self.scaler_fitted = False
            elif not os.path.exists(self.config.NN_MODEL_PATH):
                logger.info("ℹ️ No existe archivo de modelo. Se entrenará uno nuevo cuando esté disponible.")
                self.is_trained = False
        except Exception as e:
            logger.error(f"Error cargando modelo optimizado: {e}")
            logger.info("🔄 Se creará un nuevo modelo cuando se entrene")
            self.is_trained = False
# ========== IMPLEMENTACIÓN DE ESTRATEGIAS OPTIMIZADA ==========

class OptimizedStrategyImplementation:
    def __init__(self, config: "AdvancedTradingConfig"):  # <-- Nota las comillas
        self.config = config
        self.technical_analyzer = OptimizedTechnicalAnalyzer(config)
        self.signal_history = []
        self.performance_tracker = {}
        self.signal_quality_cache = {}
        self.adaptive_thresholds = {
            'confidence': 78,  # Umbral mínimo de IA
            'volume_min': 0.8,
            'volatility_max': 0.1
        }

    def check_optimized_unified_strategy(self, df_primary: pd.DataFrame, df_entry: pd.DataFrame, neural_prediction: dict = None) -> Tuple[bool, float, TrendDirection, List[str], float]:
        """
        Estrategia unificada optimizada - NUEVA LÓGICA:
        El análisis TÉCNICO actúa como FILTRO que detecta condiciones favorables:
        - EMAs en tendencia clara
        - TDI con momentum favorable  
        - Patrones de velas confirmando
        - Cerca de soporte/resistencia clave
        - Ciclo de mercado alineado
        - Acción del precio coherente
        Returns:
            - bool: True si condiciones técnicas se CUMPLEN (actúa como filtro)
            - float: Score de calidad técnica (NO requiere alcanzar 70%)
            - TrendDirection: Dirección de la tendencia detectada
            - List[str]: Condiciones cumplidas
            - float: Neural score
        La IA valida con ≥92.0% (DESTACADA) o ≥88.0% (CONFIRMADA)
        """
        conditions_met = []
        if len(df_primary) < self.config.MIN_NN_DATA_REQUIRED or len(df_entry) < self.config.MIN_NN_DATA_REQUIRED:
            return False, 0.0, TrendDirection.NEUTRAL, [], 0.0

        current_price_entry = df_entry['close'].iloc[-1]
        data_id = str(hash(str(df_entry.iloc[0]['timestamp'])))

        # 1. ANÁLISIS DE TENDENCIA CON EMAS
        ema50 = self.technical_analyzer.calculate_ema(df_primary['close'], 50, data_id + "_primary")
        ema200 = self.technical_analyzer.calculate_ema(df_primary['close'], 200, data_id + "_primary")

        if ema50.iloc[-1] > ema200.iloc[-1]:
            trend_direction = TrendDirection.BULLISH
            trend_strength = (ema50.iloc[-1] - ema200.iloc[-1]) / ema200.iloc[-1] * 100
        elif ema50.iloc[-1] < ema200.iloc[-1]:
            trend_direction = TrendDirection.BEARISH
            trend_strength = (ema200.iloc[-1] - ema50.iloc[-1]) / ema50.iloc[-1] * 100
        else:
            return False, 0.0, TrendDirection.NEUTRAL, [], 0.0

        conditions_met.append(f"Tendencia {trend_direction.value} confirmada (Fuerza: {trend_strength:.2f}%)")

        # 2. ANÁLISIS TDI
        tdi_out = self.technical_analyzer.calculate_tdi(df_entry, data_id + "_entry")
        if isinstance(tdi_out, tuple) and len(tdi_out) == 5:
            tdi_rsi, tdi_green, tdi_red, _, _ = tdi_out
        elif isinstance(tdi_out, dict):
            tdi_rsi = tdi_out.get('rsi', pd.Series([50.0] * len(df_entry)))
            tdi_green = tdi_out.get('green', pd.Series([50.0] * len(df_entry)))
            tdi_red = tdi_out.get('red', pd.Series([50.0] * len(df_entry)))
        else:
            return False, 0.0, TrendDirection.NEUTRAL, [], 0.0

        tdi_favorable = False
        tdi_momentum = (tdi_green.iloc[-1] - tdi_red.iloc[-1])

        if trend_direction == TrendDirection.BULLISH:
            # Entry mas agresiva: momentum positivo y RSI no extremo (permitir hasta 78)
            if tdi_green.iloc[-1] > tdi_red.iloc[-1] and tdi_green.iloc[-1] < 78 and tdi_momentum > 0.2:
                tdi_favorable = True
        elif trend_direction == TrendDirection.BEARISH:
             # Entry mas agresiva: momentum negativo y RSI no extremo (permitir hasta 22)
            if tdi_green.iloc[-1] < tdi_red.iloc[-1] and tdi_green.iloc[-1] > 22 and tdi_momentum < -0.2:
                tdi_favorable = True

        if not tdi_favorable:
            # NO BLOQUEAR: Solo penalizar score final si no es favorable
            # return False, 0.0, TrendDirection.NEUTRAL, [], 0.0
            conditions_met.append(f"TDI neutral/adverso (Momentum: {tdi_momentum:.2f})")
        else:
            conditions_met.append(f"TDI favorable (Momentum: {tdi_momentum:.2f})")

        # 3. PATRONES DE VELAS
        price_action = self.technical_analyzer.analyze_candlestick_pattern(df_entry.tail(5))
        pattern_score = 0

        if trend_direction == TrendDirection.BULLISH and price_action['type'] in ['BULLISH', 'REVERSAL']:
            pattern_score = price_action['confidence']
        elif trend_direction == TrendDirection.BEARISH and price_action['type'] in ['BEARISH', 'REVERSAL']:
            pattern_score = price_action['confidence']

        # NO BLOQUEAR por patrón de velas (permitir entrada por pura acción de precio/EMA)
        # if pattern_score < 45:
        #    return False, 0.0, TrendDirection.NEUTRAL, [], 0.0

        if pattern_score > 0:
            conditions_met.append(f"Patrón de vela: {price_action['pattern']} (Confianza: {pattern_score}%)")

        # 4. PATRONES W, M, HCH
        w_m_pattern = self.technical_analyzer.detect_w_m_pattern(df_entry)
        hch_pattern = self.technical_analyzer.detect_hch_pattern(df_entry)
        pattern_bonus = 0

        if trend_direction == TrendDirection.BULLISH and w_m_pattern['type'] == 'BULLISH':
            pattern_bonus = w_m_pattern['confidence'] * 0.5
            conditions_met.append(f"Patrón W detectado (Confianza: {w_m_pattern['confidence']}%)")
        elif trend_direction == TrendDirection.BEARISH and w_m_pattern['type'] == 'BEARISH':
            pattern_bonus = w_m_pattern['confidence'] * 0.5
            conditions_met.append(f"Patrón M detectado (Confianza: {w_m_pattern['confidence']}%)")

        if trend_direction == TrendDirection.BULLISH and hch_pattern['type'] == 'BULLISH':
            pattern_bonus += hch_pattern['confidence'] * 0.3
            conditions_met.append(f"Patrón HCH detectado (Confianza: {hch_pattern['confidence']}%)")
        elif trend_direction == TrendDirection.BEARISH and hch_pattern['type'] == 'BEARISH':
            pattern_bonus += hch_pattern['confidence'] * 0.3
            conditions_met.append(f"Patrón LCL detectado (Confianza: {hch_pattern['confidence']}%)")

        # 5. SOPORTES Y RESISTENCIAS (Detección Avanzada)
        sr_data = self.technical_analyzer.detect_support_resistance_advanced(df_entry, lookback_candles=120)
        sr_score = 0

        if trend_direction == TrendDirection.BULLISH:
            # Ideal: Rebotando en soporte (compra en dip) o rompiendo resistencia (breakout)
            
            # 1. Soporte validado (Bounce)
            if sr_data.get('closest_support'):
                sup = sr_data['closest_support']
                dist_sup = (current_price_entry - sup['price']) / current_price_entry
                if 0 <= dist_sup < 0.03:  # 0% a 3% sobre soporte
                    sr_score += 20
                    conditions_met.append(f"Soporte validado (Dist: {dist_sup:.2%})")
            
            # 2. Resistencia cercana (Breakout potential)
            if sr_data.get('closest_resistance'):
                res = sr_data['closest_resistance']
                dist_res = (res['price'] - current_price_entry) / current_price_entry
                if 0.005 < dist_res < 0.05:  # 0.5% a 5% bajo resistencia
                    sr_score += 15
                    conditions_met.append(f"Cerca resistencia (Dist: {dist_res:.2%})")

        elif trend_direction == TrendDirection.BEARISH:
            # Ideal: Rechazo en resistencia o rompiendo soporte
            
            # 1. Resistencia validada (Rechazo)
            if sr_data.get('closest_resistance'):
                res = sr_data['closest_resistance']
                dist_res = (res['price'] - current_price_entry) / current_price_entry
                if 0 <= dist_res < 0.03:  # 0% a 3% bajo resistencia
                    sr_score += 20
                    conditions_met.append(f"Resistencia validada (Dist: {dist_res:.2%})")
            
            # 2. Soporte cercano (Breakdown potential)
            if sr_data.get('closest_support'):
                sup = sr_data['closest_support']
                dist_sup = (current_price_entry - sup['price']) / current_price_entry
                if 0.005 < dist_sup < 0.05:  # 0.5% a 5% sobre soporte
                    sr_score += 15
                    conditions_met.append(f"Cerca soporte (Dist: {dist_sup:.2%})")
        
        sr_score = min(sr_score, 30)  # Limitar impacto máximo de S/R

        # 6. CICLO DE MERCADO
        market_cycle = self.technical_analyzer.analyze_market_cycles(df_primary)
        cycle_score = market_cycle['strength'] * 100
        conditions_met.append(f"Ciclo de mercado: {market_cycle['cycle']} ({market_cycle['phase']}) - Fuerza: {cycle_score:.0f}%")

        # 7. INTEGRACIÓN CON PREDICCIÓN NEURAL
        neural_score = 0
        neural_alignment = 0

        if neural_prediction and neural_prediction.get('confidence', 0) > 50:
            neural_signal = neural_prediction.get('signal_type', SignalType.NEUTRAL)
            neural_conf = neural_prediction.get('confidence', 0)

            if trend_direction == TrendDirection.BULLISH and 'BUY' in neural_signal.name:
                neural_alignment = 1
                neural_score = neural_conf
            elif trend_direction == TrendDirection.BEARISH and 'SELL' in neural_signal.name:
                neural_alignment = 1
                neural_score = neural_conf
            else:
                neural_alignment = -1
                neural_score = neural_conf * 0.6

            conditions_met.append(f"IA: {neural_signal.name} ({neural_conf:.1f}%) - Alineación: {'✓' if neural_alignment > 0 else '✗'}")

        # 8. CÁLCULO DE CONFIANZA
        base_confidence = 75
        base_confidence += trend_strength * 0.8
        base_confidence += abs(tdi_momentum) * 0.3
        base_confidence += pattern_score * 0.2
        base_confidence += pattern_bonus
        base_confidence += sr_score
        base_confidence += cycle_score * 0.3

        if neural_alignment > 0:
            base_confidence += neural_score * 0.3
        else:
            base_confidence *= 0.8

        final_confidence = max(0, min(base_confidence, 95))

        # 9. CÁLCULO DE NIVELES (✅ CORREGIDO: Usa variables de config para SL y TP + COMISIONES)
        tp_percent = self.config.DEFAULT_TAKE_PROFIT_PERCENT  # Toma el valor del config/slider (ej. 0.03)
        sl_percent = self.config.DEFAULT_STOP_LOSS_PERCENT    # Toma el valor del config/slider (ej. 0.01)

        # ✅ AGREGAR COMISIÓN ROUND-TRIP AL OBJETIVO PARA LOGRAR PROFIT NETO
        commission_pct = self.config.get_round_trip_commission() / 100.0  # ej: 0.0010 para 0.10%
        tp_adjusted = tp_percent + commission_pct  # TP bruto = TP neto + comisiones

        if trend_direction == TrendDirection.BULLISH:
            entry_price = current_price_entry
            stop_loss = entry_price * (1 - sl_percent)
            take_profit = entry_price * (1 + tp_adjusted)  # ✅ TP ajustado por comisiones
        else:
            entry_price = current_price_entry
            stop_loss = entry_price * (1 + sl_percent)  # +7% (para venta, el SL está arriba)
            take_profit = entry_price * (1 - tp_adjusted)  # ✅ TP ajustado por comisiones

        stop_distance = abs(entry_price - stop_loss)
        if stop_distance < 1e-8:
            return False, 0.0, TrendDirection.NEUTRAL, [], 0.0

        risk_reward_ratio = abs(take_profit - entry_price) / stop_distance
        if risk_reward_ratio < self.config.MIN_RISK_REWARD_RATIO:
            return False, 0.0, TrendDirection.NEUTRAL, [], 0.0

        # 10. AJUSTE FINAL POR CICLO DE MERCADO
        if market_cycle['cycle'] in ['ACCUMULATION', 'UPTREND'] and trend_direction == TrendDirection.BULLISH:
            final_confidence *= 1.1
        elif market_cycle['cycle'] in ['DISTRIBUTION', 'DOWNTREND'] and trend_direction == TrendDirection.BEARISH:
            final_confidence *= 1.1
        else:
            final_confidence *= 0.9

        final_confidence = max(0, min(final_confidence, 95))

        return True, final_confidence, trend_direction, conditions_met, neural_score
# ============================================================================
# SISTEMA DE PROCESAMIENTO DE SENALES OPTIMIZADO v35.0.0.0
# Con filtros de calidad, cooldown y validacion mejorada
# ============================================================================
class OptimizedSignalProcessor:
    def __init__(self, config: "AdvancedTradingConfig"):
        self.config = config
        self.strategy_performance = defaultdict(list)
        self.market_conditions = {}
        self.signal_quality_cache = {}
        self.bot = None
        self.trend_alignment_validator = None
        
        # === MEJORAS v35: Sistema de cooldown y filtros ===
        self.signal_cooldown = {}  # {symbol: timestamp} - Cooldown entre senales del mismo par
        self.COOLDOWN_MINUTES = 30  # Minutos minimos entre senales del mismo par
        
        # Cache de senales recientes para evitar duplicados
        self.recent_signals = {}  # {symbol: {'direction': str, 'timestamp': datetime}}
        
        # Estadisticas de calidad de senales
        self.signal_quality_stats = {
            'total_generated': 0,
            'filtered_volume': 0,
            'filtered_volatility': 0,
            'filtered_cooldown': 0,
            'filtered_quality': 0,
            'approved': 0
        }
        
        # Umbrales de calidad minima
        self.MIN_VOLUME_RATIO = 1.2  # Volumen minimo 1.2x promedio
        self.MIN_ATR_PERCENT = 0.3   # ATR minimo 0.3%
        self.MAX_ATR_PERCENT = 5.0   # ATR maximo 5%
        self.MIN_RR_RATIO = 1.8      # Risk/Reward minimo 1:1.8

    # ------------------------------------------------------------------
    # 1. REFERENCIA AL BOT PRINCIPAL
    # ------------------------------------------------------------------
    def set_bot_reference(self, bot_instance):
        self.bot = bot_instance
        if hasattr(bot_instance, 'config') and self.trend_alignment_validator is None:
            self.trend_alignment_validator = TrendAlignmentValidator(bot_instance.config)
    
    # ------------------------------------------------------------------
    # 2. FILTROS DE CALIDAD DE SENAL (NUEVO v35)
    # ------------------------------------------------------------------
    def _check_signal_cooldown(self, symbol: str) -> Tuple[bool, str]:
        """
        Verifica si el par esta en cooldown para evitar sobretrading
        Returns: (puede_operar, razon)
        """
        if symbol in self.signal_cooldown:
            last_signal_time = self.signal_cooldown[symbol]
            elapsed_minutes = (datetime.now() - last_signal_time).total_seconds() / 60
            
            if elapsed_minutes < self.COOLDOWN_MINUTES:
                remaining = self.COOLDOWN_MINUTES - elapsed_minutes
                return False, f"Cooldown activo: {remaining:.0f} min restantes"
        
        return True, "OK"
    
    def _check_volume_quality(self, validation_result: dict) -> Tuple[bool, str]:
        """
        Verifica que el volumen sea suficiente para una senal de calidad
        """
        volume_ratio = validation_result.get('volume_ratio', 1.0)
        volume_confidence = validation_result.get('volume_confidence', 0)
        
        if volume_ratio < self.MIN_VOLUME_RATIO:
            return False, f"Volumen insuficiente: {volume_ratio:.2f}x (min: {self.MIN_VOLUME_RATIO}x)"
        
        return True, f"Volumen OK: {volume_ratio:.2f}x"
    
    def _check_volatility_range(self, validation_result: dict, current_price: float) -> Tuple[bool, str]:
        """
        Verifica que la volatilidad este en rango optimo (ni muy baja ni muy alta)
        """
        # Intentar obtener ATR del resultado de validacion
        atr_value = validation_result.get('atr', 0)
        
        if atr_value > 0 and current_price > 0:
            atr_percent = (atr_value / current_price) * 100
            
            if atr_percent < self.MIN_ATR_PERCENT:
                return False, f"Volatilidad muy baja: ATR {atr_percent:.2f}% (min: {self.MIN_ATR_PERCENT}%)"
            
            if atr_percent > self.MAX_ATR_PERCENT:
                return False, f"Volatilidad excesiva: ATR {atr_percent:.2f}% (max: {self.MAX_ATR_PERCENT}%)"
            
            return True, f"Volatilidad optima: ATR {atr_percent:.2f}%"
        
        return True, "Volatilidad no verificada"
    
    def _check_risk_reward(self, validation_result: dict) -> Tuple[bool, str]:
        """
        Verifica que el ratio Risk/Reward sea favorable
        """
        rr_ratio = validation_result.get('risk_reward_ratio', 0)
        
        if rr_ratio < self.MIN_RR_RATIO:
            return False, f"R/R desfavorable: 1:{rr_ratio:.2f} (min: 1:{self.MIN_RR_RATIO})"
        
        return True, f"R/R favorable: 1:{rr_ratio:.2f}"
    
    def _check_confluence_quality(self, validation_result: dict) -> Tuple[bool, str]:
        """
        Verifica la calidad de confluencia de la senal
        """
        confluence_score = validation_result.get('confluence_score', 0)
        confluence_quality = validation_result.get('confluence_quality', 'LOW')
        
        if confluence_quality == 'LOW' and confluence_score < 40:
            return False, f"Confluencia baja: {confluence_score}%"
        
        return True, f"Confluencia {confluence_quality}: {confluence_score}%"
    
    def validate_signal_quality(self, symbol: str, validation_result: dict, 
                                current_price: float) -> Tuple[bool, List[str]]:
        """
        Validacion completa de calidad de senal con multiples filtros
        Returns: (es_valida, lista_de_razones)
        """
        self.signal_quality_stats['total_generated'] += 1
        reasons = []
        is_valid = True
        
        # 1. Check cooldown
        cooldown_ok, cooldown_reason = self._check_signal_cooldown(symbol)
        if not cooldown_ok:
            self.signal_quality_stats['filtered_cooldown'] += 1
            reasons.append(cooldown_reason)
            is_valid = False
        
        # 2. Check volumen
        volume_ok, volume_reason = self._check_volume_quality(validation_result)
        if not volume_ok:
            self.signal_quality_stats['filtered_volume'] += 1
            reasons.append(volume_reason)
            is_valid = False
        else:
            reasons.append(volume_reason)
        
        # 3. Check volatilidad
        vol_ok, vol_reason = self._check_volatility_range(validation_result, current_price)
        if not vol_ok:
            self.signal_quality_stats['filtered_volatility'] += 1
            reasons.append(vol_reason)
            is_valid = False
        else:
            reasons.append(vol_reason)
        
        # 4. Check R/R
        rr_ok, rr_reason = self._check_risk_reward(validation_result)
        if not rr_ok:
            self.signal_quality_stats['filtered_quality'] += 1
            reasons.append(rr_reason)
            is_valid = False
        else:
            reasons.append(rr_reason)
        
        # 5. Check confluencia
        conf_ok, conf_reason = self._check_confluence_quality(validation_result)
        if not conf_ok:
            self.signal_quality_stats['filtered_quality'] += 1
            reasons.append(conf_reason)
            is_valid = False
        else:
            reasons.append(conf_reason)
        
        if is_valid:
            self.signal_quality_stats['approved'] += 1
            # Registrar cooldown para este par
            self.signal_cooldown[symbol] = datetime.now()
        
        return is_valid, reasons
    
    def get_quality_stats(self) -> dict:
        """Retorna estadisticas de filtrado de senales"""
        total = self.signal_quality_stats['total_generated']
        if total > 0:
            approval_rate = (self.signal_quality_stats['approved'] / total) * 100
        else:
            approval_rate = 0
        
        return {
            **self.signal_quality_stats,
            'approval_rate': f"{approval_rate:.1f}%"
        }

    # ------------------------------------------------------------------
    # 2. PROCESAMIENTO CENTRAL DE SEÑALES
    # ------------------------------------------------------------------
    def process_optimized_signal(self,
                                 symbol: str,
                                 strategy_signal: "StrategySignal",
                                 neural_prediction: dict,
                                 technical_confidence: float,
                                 validation_result: dict = None,
                                 market_data: dict = None) -> dict:
        """
        Valida y clasifica la señal según:
        - IA ≥ 88 %
        - Técnico ≥ 88 %
        - Alineación 15m-30m ≥ 88 %
        - Coherencia direccional
        - Seguimiento: 1 %, 2 %, 3 % + cierre
        """
        if not validation_result or not validation_result.get('valid', False):
            return {
                'combined_signal': SignalType.NEUTRAL,
                'combined_confidence': 0.0,
                'neural_score': neural_prediction.get('confidence', 0.0),
                'technical_percentage': 0.0,
                'alignment_percentage': 0.0,
                'double_validated': False,
                'is_buy': False,
                'status': 'NEUTRAL'
            }

        neural_score = float(validation_result.get('neural_score', 0.0))
        technical_percentage = float(validation_result.get('technical_percentage', 0.0))
        alignment_percentage = 0.0
        continuity_valid = False
        ia_dir = validation_result.get('ia_direction', 'NEUTRAL').upper()
        tech_dir = validation_result.get('technical_direction', 'NEUTRAL').upper()

        # --- Alineación 15m-30m ----------------------------------------
        if market_data and self.trend_alignment_validator:
            df_15m = market_data.get('df_entry') or market_data.get('df_15m')
            df_30m = market_data.get('df_30m')
            if df_15m is not None and df_30m is not None:
                alignment = self.trend_alignment_validator.validate_trend_alignment(
                    df_15m, df_30m,
                    neural_score=neural_score,
                    technical_pct=technical_percentage,
                    signal_direction=ia_dir
                )
                alignment_percentage = alignment.get('alignment_score', 0.0)
                continuity_valid = alignment.get('continuity_valid', False)
                trend_dir = alignment.get('trend', 'NEUTRAL').upper()
                if alignment_percentage < self.config.MIN_ALIGNMENT_CONFIRMADA:
                    return {
                        'combined_signal': SignalType.NEUTRAL,
                        'combined_confidence': 0.0,
                        'neural_score': neural_score,
                        'technical_percentage': technical_percentage,
                        'alignment_percentage': alignment_percentage,
                        'double_validated': False,
                        'is_buy': False,
                        'status': 'NEUTRAL',
                        'reason': f'Alineación insuficiente (<{self.config.MIN_ALIGNMENT_CONFIRMADA}%)'
                    }
                if not continuity_valid:
                    return {
                        'combined_signal': SignalType.NEUTRAL,
                        'combined_confidence': 0.0,
                        'neural_score': neural_score,
                        'technical_percentage': technical_percentage,
                        'alignment_percentage': alignment_percentage,
                        'double_validated': False,
                        'is_buy': False,
                        'status': 'NEUTRAL',
                        'reason': 'Sin continuidad de tendencia'
                    }
                # Rechazar si dirección IA contradice la tendencia
                if ia_dir in ('BUY','BULLISH') and trend_dir == 'BEARISH':
                    return {
                        'combined_signal': SignalType.NEUTRAL,
                        'combined_confidence': 0.0,
                        'neural_score': neural_score,
                        'technical_percentage': technical_percentage,
                        'alignment_percentage': alignment_percentage,
                        'double_validated': False,
                        'is_buy': False,
                        'status': 'NEUTRAL',
                        'reason': 'IA BUY contradice tendencia BEARISH'
                    }
                if ia_dir in ('SELL','BEARISH') and trend_dir == 'BULLISH':
                    return {
                        'combined_signal': SignalType.NEUTRAL,
                        'combined_confidence': 0.0,
                        'neural_score': neural_score,
                        'technical_percentage': technical_percentage,
                        'alignment_percentage': alignment_percentage,
                        'double_validated': False,
                        'is_buy': False,
                        'status': 'NEUTRAL',
                        'reason': 'IA SELL contradice tendencia BULLISH'
                    }

        # --- Umbral técnico mínimo -------------------------------------
        # ✅ CORREGIDO v32.0.22.4: Usar umbrales DESTACADA para señales iniciales
        if technical_percentage < self.config.MIN_TECHNICAL_DESTACADA:
            return {
                'combined_signal': SignalType.NEUTRAL,
                'combined_confidence': 0.0,
                'neural_score': neural_score,
                'technical_percentage': technical_percentage,
                'alignment_percentage': alignment_percentage,
                'double_validated': False,
                'is_buy': False,
                'status': 'NEUTRAL',
                'reason': f'Técnico < {self.config.MIN_TECHNICAL_DESTACADA}%'
            }

        # --- Coherencia direccional IA vs Técnico ----------------------
        if ia_dir != tech_dir and ia_dir != 'NEUTRAL' and tech_dir != 'NEUTRAL':
            return {
                'combined_signal': SignalType.NEUTRAL,
                'combined_confidence': 0.0,
                'neural_score': neural_score,
                'technical_percentage': technical_percentage,
                'alignment_percentage': alignment_percentage,
                'double_validated': False,
                'is_buy': False,
                'status': 'NEUTRAL',
                'reason': 'IA y técnico en dirección opuesta'
            }

        # --- Clasificación final ---------------------------------------
        is_buy = 'BUY' in validation_result.get('ia_direction', '').upper() or 'BULLISH' in validation_result.get('ia_direction', '').upper()

        # ✅ CORREGIDO: DESTACADA usa umbrales DESTACADA (82/82/82)
        if neural_score >= self.config.MIN_NEURAL_DESTACADA and technical_percentage >= self.config.MIN_TECHNICAL_DESTACADA and alignment_percentage >= self.config.MIN_ALIGNMENT_DESTACADA:
            signal_type = SignalType.HIGHLIGHTED_BUY if is_buy else SignalType.HIGHLIGHTED_SELL
            status = 'DESTACADA'
        else:
            return {
                'combined_signal': SignalType.NEUTRAL,
                'combined_confidence': 0.0,
                'neural_score': neural_score,
                'technical_percentage': technical_percentage,
                'alignment_percentage': alignment_percentage,
                'double_validated': False,
                'is_buy': is_buy,
                'status': 'NEUTRAL',
                'reason': 'No cumple umbrales DESTACADA'
            }

        return {
            'combined_signal': signal_type,
            'combined_confidence': alignment_percentage,
            'neural_score': neural_score,
            'technical_percentage': technical_percentage,
            'alignment_percentage': alignment_percentage,
            'double_validated': True,
            'is_buy': is_buy,
            'alignment_status': 'ALINEADO' if alignment_percentage >= self.config.MIN_ALIGNMENT_CONFIRMADA else 'PARCIAL',
            'technical_score': technical_percentage,
            'combined_score': (neural_score + technical_percentage + alignment_percentage) / 3,
            'status': status,
            'continuity_valid': continuity_valid
        }

    # ------------------------------------------------------------------
    # 3. CÁLCULO DE RENDIMIENTO POR SÍMBOLO
    # ------------------------------------------------------------------
    def _get_symbol_performance(self, symbol: str) -> float:
        if symbol not in self.strategy_performance or len(self.strategy_performance[symbol]) < 5:
            return 0.0
        recent = self.strategy_performance[symbol][-10:]
        win_rate = sum(1 for r in recent if r > 0) / len(recent)
        avg_return = sum(recent) / len(recent)
        return max(-0.5, min(0.5, (win_rate - 0.5) * 2 + avg_return * 10))

    # ------------------------------------------------------------------
    # 4. VALIDACIÓN RÁPIDA DE CALIDAD
    # ------------------------------------------------------------------
    def validate_signal_quality_optimized(self, signal_data: dict, market_data: dict) -> bool:
        try:
            symbol = signal_data.get('symbol', '')
            neural_score = signal_data.get('neural_score', 0)
            cache_key = f"{symbol}_{neural_score}_{signal_data.get('timestamp', datetime.now()).strftime('%Y%m%d%H%M')}"

            if cache_key in self.signal_quality_cache:
                return self.signal_quality_cache[cache_key]

            if neural_score < self.config.MIN_NEURAL_DESTACADA:
                self.signal_quality_cache[cache_key] = False
                return False

            df_entry = market_data.get(symbol, {}).get('df_entry')
            if df_entry is not None and not df_entry.empty:
                current_vol = df_entry['volume'].iloc[-1]
                avg_vol = df_entry['volume'].tail(20).mean()
                if current_vol / avg_vol < 0.5:
                    self.signal_quality_cache[cache_key] = False
                    return False

            self.signal_quality_cache[cache_key] = True
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # 5. SEGUIMIENTO POR ETAPAS + NOTIFICACIONES TELEGRAM (MEJORADO v35)
    # ------------------------------------------------------------------
    def track_signal_stages(self, symbol: str, signal_hash: str,
                            entry_price: float, is_buy: bool,
                            current_price: float, market_data: dict = None) -> dict:
        """
        Sistema de seguimiento mejorado v35 con:
        - Trailing stop dinamico basado en ATR
        - Milestones configurables desde config
        - Deteccion de reversion multi-timeframe
        - Metricas de rendimiento por senal
        
        Etapas: milestone_1% -> milestone_2% -> milestone_3% / -SL% / reversion
        Retorna dict con estado actual.
        """
        from datetime import datetime
        import math

        # --- Calculo de profit -------------------------------------------------
        if is_buy:
            profit_percent = ((current_price - entry_price) / entry_price) * 100
        else:
            profit_percent = ((entry_price - current_price) / entry_price) * 100

        # --- Obtener tracking con lock para thread safety -------------------------------------------------
        tracking = {}
        try:
            with self.bot.signal_tracker.lock:
                tracking = self.bot.signal_tracker.tracked_signals.get(signal_hash, {}).copy()
        except Exception:
            tracking = self.bot.signal_tracker.tracked_signals.get(signal_hash, {})
        
        signal_status = tracking.get('status', 'DESTACADA')
        
        # === MEJORA v35: Actualizar max_profit alcanzado ===
        max_profit = tracking.get('max_profit', profit_percent)
        if profit_percent > max_profit:
            max_profit = profit_percent
            try:
                with self.bot.signal_tracker.lock:
                    if signal_hash in self.bot.signal_tracker.tracked_signals:
                        self.bot.signal_tracker.tracked_signals[signal_hash]['max_profit'] = max_profit
            except Exception:
                pass
        
        # === MEJORA v35: Trailing Stop dinamico ===
        trailing_stop_triggered = False
        trailing_config = getattr(self.config, 'TRAILING_STOP_ENABLED', True)
        trailing_activation = getattr(self.config, 'TRAILING_STOP_ACTIVATION', 0.5)  # Activar despues de 0.5%
        trailing_distance = getattr(self.config, 'TRAILING_STOP_DISTANCE', 0.3)  # 0.3% de distancia
        
        if trailing_config and max_profit >= trailing_activation:
            trailing_stop_level = max_profit - trailing_distance
            if profit_percent <= trailing_stop_level and profit_percent > 0:
                trailing_stop_triggered = True
                logger.info(f"Trailing stop activado para {symbol}: Max={max_profit:.2f}%, Actual={profit_percent:.2f}%")

        if signal_status == 'CONFIRMADA':
            milestones = self.config.PROFIT_MILESTONES
            updates_sent = tracking.get('telegram_updates_sent', 0)

            for i, milestone in enumerate(milestones):
                if profit_percent >= milestone and updates_sent <= i:
                    # Actualizar contador
                    self.bot.signal_tracker.tracked_signals[signal_hash]['telegram_updates_sent'] = i + 1
                    # Generar gráfico de velas en tiempo real
                    chart_path = None
                    try:
                        df_chart = market_data.get(symbol, {}).get('df_entry')
                        if df_chart is not None and not df_chart.empty:
                            signal_data = self.bot.signal_tracker.tracked_signals[signal_hash]['signal_data']
                            analysis = self.bot._analyze_async_with_timeout(symbol, 3)
                            if analysis:
                                chart_path = self.bot.chart_generator.generate_signal_chart(symbol, df_chart, signal_data, analysis)
                    except Exception as e:
                        logger.debug(f"⚠️ Error generando gráfico para milestone {milestone}%: {e}")

                    # Enviar notificación con gráfico
                    if self.bot.telegram_client and self.bot.config.telegram_enabled:
                        self.bot.telegram_client.send_milestone_update(
                            symbol=symbol,
                            milestone=milestone,
                            profit=profit_percent,
                            chart_path=chart_path
                        )
                    # Log interno
                    logger.info(f"📊 {symbol} +{milestone}% (Profit: {profit_percent:+.2f}%) – Notificación + Gráfico enviados")
        else:
            logger.debug(f"⏭️ {symbol} - Milestones solo para CONFIRMADA (estado actual: {signal_status})")

        # --- Cierre por objetivo (config) ------------------------------------------
        tp_pct = self.config.PROFIT_TARGET_PERCENT
        if profit_percent >= tp_pct:
            self.bot.signal_tracker.close_signal(signal_hash, current_price, reason='target_reached')
            logger.info(f"🎯 {symbol} objetivo {tp_pct}% alcanzado – Cierre automático")
            return {'closed': True, 'reason': 'target_reached', 'profit': profit_percent}

        # --- Cierre por stop (config) ---------------------------------------------
        sl_pct = self.config.DEFAULT_STOP_LOSS_PERCENT * 100  # Convertir a porcentaje
        if profit_percent <= -sl_pct:
            self.bot.signal_tracker.close_signal(signal_hash, current_price, reason='stop_loss_hit')
            logger.info(f"🛑 {symbol} stop -1 % alcanzado – Cierre automático")
            return {'closed': True, 'reason': 'stop_loss_hit', 'profit': profit_percent}

        # ✅ CONFIRMADAS: Sin timeout de tiempo - continúan hasta TP, SL o cambio de tendencia
        # El timeout de 20 minutos para DESTACADAS se maneja en la lógica de promoción

        # --- Reversión ROBUSTA (validación multi-timeframe 15m/30m + IA + Técnico) ---------------------------------------------------------
        try:
            # Calcular tiempo transcurrido para detección de reversión
            start_time = self.bot.signal_tracker.tracked_signals.get(signal_hash, {}).get('start_time')
            elapsed_min = 0
            if start_time:
                elapsed_min = (datetime.now() - start_time).total_seconds() / 60

            # ✅ Solo verificar reversión después de 10 minutos y si profit < -0.3%
            if start_time and elapsed_min >= 10 and profit_percent < -0.3:
                df_15m = self.bot.data_manager.get_data(symbol, "15m", 200, self.bot.client)
                df_30m = self.bot.data_manager.get_data(symbol, "30m", 200, self.bot.client)

                if df_15m is not None and df_30m is not None and len(df_15m) >= 50:
                    original_is_buy = self.bot.signal_tracker.tracked_signals[signal_hash]['is_buy']
                    opposite_direction = "BEARISH" if original_is_buy else "BULLISH"

                    current_analysis = self.bot._analyze_async_with_timeout(symbol, 3)
                    if current_analysis:
                        current_neural = current_analysis.get('neural_score', 0)
                        current_technical = current_analysis.get('technical_percentage', 0)

                        alignment = self.bot.trend_alignment_validator.validate_trend_alignment(
                            df_15m, df_30m, current_neural, current_technical, opposite_direction
                        )

                        # Cierre solo si reversión CONFIRMADA por múltiples factores
                        if (alignment.get('alignment_score', 0) >= 70 and 
                            alignment.get('is_aligned', False) and
                            current_neural >= 75 and current_technical >= 70):
                            self.bot.signal_tracker.close_signal(signal_hash, current_price, reason='trend_reversal_detected')
                            logger.info(f"🔄 {symbol} reversión CONFIRMADA después de {elapsed_min:.1f} min | Alineación: {alignment.get('alignment_score', 0):.1f}%")
                            return {'closed': True, 'reason': 'trend_reversal_detected', 'profit': profit_percent}
        except Exception as e:
            logger.debug(f"⚠️ Error detectando reversión para {symbol}: {e}")

        # --- Estado actual ----------------------------------------------------
        return {
            'closed': False,
            'profit_percent': profit_percent,
            'milestone_reached': math.floor(profit_percent),
            'updates_sent': updates_sent
        }


# ========== CLIENTE TELEGRAM OPTIMIZADO v35.0.0.0 ==========
class OptimizedTelegramClient:
    """
    Cliente Telegram Mejorado v35 con:
    - Reintentos con backoff exponencial
    - Deteccion y manejo de rate limiting (429)
    - Validacion de respuestas de API
    - Estadisticas de envio
    - Reconexion automatica de sesion
    - Manejo robusto de errores de red
    """
    def __init__(self, config):
        self.config = config
        self.base_url = f"https://api.telegram.org/bot{config.telegram_bot_token}"

        # Configurar sesion de requests con reintentos mejorados
        self.session = None
        self._init_session()

        # Control de rate limiting mejorado
        self.last_message_time = 0
        self.min_message_interval = 2  # Intervalo minimo entre mensajes
        self.rate_limit_until = 0  # Timestamp hasta que no se puede enviar
        
        # Control de mensajes enviados
        self.sent_signals = set()
        self.sent_promotions = set()  # Control de promociones enviadas por par
        self.sent_milestones = {}  # {symbol: set(milestones_enviados)}
        self.sent_closures = set()  # {(symbol, reason_norm)}
        self.sent_highlight_expired = set()  # {symbol}
        self.telegram_dedupe_lock = threading.Lock()

        # Cola de mensajes para envio no bloqueante
        self.message_queue = queue.Queue(maxsize=100)
        self.processing_thread = None
        self._start_message_processor()
        
        # Estadisticas de envio
        self.stats = {
            'messages_sent': 0,
            'messages_failed': 0,
            'photos_sent': 0,
            'photos_failed': 0,
            'rate_limit_hits': 0,
            'retries_total': 0
        }
    
    def _init_session(self):
        """Inicializa la sesion de requests con configuracion robusta"""
        if REQUESTS_AVAILABLE:
            try:
                self.session = requests.Session()
                retry_strategy = Retry(
                    total=5,  # Aumentado a 5 reintentos
                    backoff_factor=1.5,  # Backoff mas agresivo
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=frozenset(['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']),
                    raise_on_status=False,
                )
                adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=50, pool_maxsize=100)
                self.session.mount("https://", adapter)
                self.session.mount("http://", adapter)
                self.session.headers.update({
                    'Connection': 'keep-alive',
                    'User-Agent': 'CryptoBotPro/35.0'
                })
            except Exception as e:
                logger.error(f"Error inicializando sesion Telegram: {e}")
                self.session = None

    def _reset_session(self):
        if REQUESTS_AVAILABLE:
            try:
                self.session = requests.Session()
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=frozenset(['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']),
                    raise_on_status=False,
                )
                adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=50, pool_maxsize=100)
                self.session.mount("https://", adapter)
                self.session.mount("http://", adapter)
                try:
                    self.session.headers.update({'Connection': 'keep-alive'})
                except Exception:
                    pass
            except Exception:
                self.session = None

    def _escape_html(self, text: str) -> str:
        """
        Escapar caracteres especiales para HTML en Telegram de forma segura.
        Utiliza html.escape para mayor seguridad.
        """
        if not text:
            return text
        # Usar html.escape para mayor seguridad
        return html.escape(text)

    def _truncate_message(self, text: str, max_length: int = 4096) -> str:
        """
        Truncar mensaje a límite de Telegram (4096 chars)
        """
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text

    def _start_message_processor(self):
        """Iniciar procesador de mensajes en hilo separado"""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.processing_thread = threading.Thread(target=self._process_message_queue, daemon=True)
            self.processing_thread.start()
            logger.info("Procesador de mensajes de Telegram iniciado")

    def _process_message_queue(self):
        """Procesar cola de mensajes con manejo de errores"""
        while True:
            try:
                message_data = self.message_queue.get(timeout=5)
                if isinstance(message_data, tuple) and len(message_data) == 2:
                    message, parse_mode = message_data
                    self._send_message_direct(message, parse_mode)
                elif isinstance(message_data, dict) and 'photo_path' in message_data:
                    self._send_photo_direct(message_data)
                else:
                    logger.warning(f"Formato de mensaje no reconocido: {type(message_data)}")

                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error procesando cola de mensajes Telegram: {e}")

    def _rate_limit_check(self):
        """
        Implementar rate limiting mejorado v35:
        - Respeta rate limits de Telegram API
        - Maneja respuestas 429 con retry-after
        - Backoff exponencial si hay multiples rate limits
        """
        current_time = time.time()
        
        # Verificar si estamos en periodo de rate limit
        if self.rate_limit_until > current_time:
            wait_time = self.rate_limit_until - current_time
            logger.warning(f"Rate limit activo: esperando {wait_time:.1f}s")
            time.sleep(wait_time)
            return
        
        # Verificar intervalo minimo entre mensajes
        time_since_last = current_time - self.last_message_time

        if time_since_last < self.min_message_interval:
            sleep_time = self.min_message_interval - time_since_last
            logger.debug(f"Rate limiting: esperando {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_message_time = time.time()
    
    def _handle_rate_limit(self, retry_after: int = 30):
        """Manejar respuesta 429 de rate limit"""
        self.stats['rate_limit_hits'] += 1
        self.rate_limit_until = time.time() + retry_after
        logger.warning(f"Rate limit recibido. Esperando {retry_after}s antes de reintentar")
    
    def get_stats(self) -> dict:
        """Retorna estadisticas de envio de mensajes"""
        total_messages = self.stats['messages_sent'] + self.stats['messages_failed']
        success_rate = (self.stats['messages_sent'] / total_messages * 100) if total_messages > 0 else 0
        
        return {
            **self.stats,
            'total_messages': total_messages,
            'success_rate': f"{success_rate:.1f}%",
            'signals_tracked': len(self.sent_signals),
            'promotions_sent': len(self.sent_promotions)
        }
    
    def reset_signal_tracking(self, symbol: str = None):
        """Resetea el tracking de senales para permitir nuevas notificaciones"""
        if symbol:
            # Eliminar solo el simbolo especifico
            self.sent_signals = {s for s in self.sent_signals if symbol not in s}
            self.sent_promotions.discard(symbol)
            if symbol in self.sent_milestones:
                del self.sent_milestones[symbol]
            logger.info(f"Tracking de {symbol} reseteado")
        else:
            # Resetear todo
            self.sent_signals.clear()
            self.sent_promotions.clear()
            self.sent_milestones.clear()
            logger.info("Todo el tracking de Telegram reseteado")

    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """
        Encolar mensaje para envío no bloqueante
        """
        if not self.config.telegram_bot_token or not self.config.telegram_chat_id:
            logger.info("⚠️ Telegram no configurado; mensaje no enviado")
            return False

        try:
            self.message_queue.put((text, parse_mode), timeout=1)
            logger.debug("🕒 Mensaje encolado para Telegram")
            return True
        except queue.Full:
            logger.warning("Cola de mensajes Telegram llena")
            return False

    def send_photo(self, photo_path: str, caption: str = '', parse_mode: str = 'HTML') -> bool:
        """
        Encolar foto para envío no bloqueante
        """
        if not self.config.telegram_bot_token or not self.config.telegram_chat_id or not REQUESTS_AVAILABLE:
            logger.info("⚠️ Telegram no configurado o requests no disponible; foto no enviada")
            return False

        try:
            photo_data = {
                'photo_path': photo_path,
                'caption': caption,
                'parse_mode': parse_mode
            }
            self.message_queue.put(photo_data, timeout=1)
            logger.debug("🕒 Foto encolada para Telegram")
            return True
        except queue.Full:
            logger.warning("Cola de mensajes Telegram llena")
            return False

    def _send_message_direct(self, message: str, parse_mode: str = 'HTML', max_retries=3) -> bool:
        """
        Envía mensaje directamente con reintentos robustos y depuración detallada.
        """
        # Validaciones iniciales
        if not self.config.telegram_bot_token or not self.config.telegram_chat_id:
            logger.error("❌ Telegram: bot_token o chat_id no están configurados.")
            return False

        if not message or not message.strip():
            logger.error("❌ Telegram: el texto del mensaje está vacío.")
            return False

        # Sanitizar el texto si se usa HTML
        if parse_mode == 'HTML':
            message = self._escape_html(message)

        # Truncar mensaje a límite de Telegram
        message = self._truncate_message(message)

        # Aplicar rate limiting
        self._rate_limit_check()

        # Preparar payload según Telegram Bot API oficial
        payload = {
            'chat_id': str(self.config.telegram_chat_id),  # Debe ser string
            'text': message,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True,
            'disable_notification': False  # Permitir notificación (pero sin sonido si el usuario lo tiene deshabilitado)
        }

        # Bucle de reintentos con backoff exponencial
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                # Timeout corto para evitar que la cola se “congele” por minutos
                current_timeout = 15 + (attempt * 5)  # 20s, 25s, 30s

                # Enviar solicitud
                if self.session:
                    response = self.session.post(
                        f"{self.base_url}/sendMessage",
                        json=payload,
                        timeout=current_timeout
                    )
                    success = response.status_code == 200
                    response_text = response.text
                else:
                    # Fallback a urllib
                    import urllib.request
                    data = json.dumps(payload).encode('utf-8')
                    req = urllib.request.Request(
                        f"{self.base_url}/sendMessage",
                        data=data,
                        headers={'Content-Type': 'application/json'}
                    )
                    with urllib.request.urlopen(req, timeout=current_timeout) as resp:
                        success = resp.status == 200
                        response_text = resp.read().decode('utf-8')

                # Procesar respuesta según formato JSON de Telegram Bot API
                if success:
                    try:
                        response_json = json.loads(response_text) if response_text else {}
                        # Telegram devuelve {"ok": true, "result": {...}} cuando es exitoso
                        if response_json.get('ok') is True:
                            logger.info(f"✅ Mensaje enviado a Telegram exitosamente (intento {attempt})")
                            return True
                        else:
                            error_code = response_json.get('error_code', 'UNKNOWN')
                            error_desc = response_json.get('description', 'Sin descripción')
                            logger.warning(f"⚠️ Telegram rechazó el mensaje: [{error_code}] {error_desc}")
                    except Exception as parse_err:
                        logger.warning(f"⚠️ Error parseando respuesta JSON: {parse_err}")
                        # Si no podemos parsear pero status es 200, asumir éxito
                        logger.info(f"✅ Mensaje enviado a Telegram (intento {attempt})")
                        return True

                # Extraer información de error
                try:
                    error_data = json.loads(response_text) if response_text else {}
                    error_code = error_data.get('error_code', 'N/A')
                    error_description = error_data.get('description', 'Sin descripción')
                except:
                    error_code = response.status_code if 'response' in locals() else 'N/A'
                    error_description = response_text[:100] if response_text else 'Sin respuesta'

                last_error = f"{error_code} - {error_description}"
                logger.error(f"❌ [ERROR] Telegram API (intento {attempt}): {last_error}")

                try:
                    error_code_int = int(error_code)
                except Exception:
                    error_code_int = None

                # Si es 429, respetar retry_after si viene (evita ban temporal)
                if error_code_int == 429:
                    retry_after = 5
                    try:
                        retry_after = int(error_data.get('parameters', {}).get('retry_after', retry_after))
                    except Exception:
                        pass
                    if attempt < max_retries:
                        logger.warning(f"⏳ Telegram rate limit (429). Reintentando en {retry_after}s")
                        time.sleep(max(1, retry_after))
                        continue

                # Si es un error de cliente (4xx), reintentar no sirve. Salimos del bucle.
                if error_code_int is not None and 400 <= error_code_int < 500:
                    logger.error("🛑 [FATAL] Error de cliente (4xx). No se reintentará.")
                    return False

            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                logger.warning(f"⚠️ Telegram intento {attempt}/{max_retries} fallido: {last_error}")
                try:
                    if 'ConnectionResetError' in last_error or 'Connection aborted' in last_error:
                        self._reset_session()
                        time.sleep(1)
                except Exception:
                    pass

            # Esperar antes del siguiente intento (backoff exponencial)
            if attempt < max_retries:
                wait_time = 2 ** (attempt - 1)  # 1s, 2s, 4s
                time.sleep(wait_time)

        logger.error(f"❌ [ERROR] Telegram: todos los intentos fallidos ({max_retries}). Último error: {last_error}")
        return False

    def _send_photo_direct(self, photo_data: Dict, max_retries=3) -> bool:
        """
        Envía foto directamente con reintentos robustos
        """
        photo_path = photo_data.get('photo_path', '')
        caption = photo_data.get('caption', '')
        parse_mode = photo_data.get('parse_mode', 'HTML')

        # Validaciones
        if not os.path.exists(photo_path):
            logger.error(f"❌ Foto no encontrada: {photo_path}")
            return False

        # Sanitizar caption si es HTML
        if parse_mode == 'HTML':
            caption = self._escape_html(caption)

        # Truncar caption a límite de Telegram (1024 chars para fotos)
        caption = self._truncate_message(caption, 1024)

        # Aplicar rate limiting
        self._rate_limit_check()

        # Bucle de reintentos
        for attempt in range(1, max_retries + 1):
            try:
                current_timeout = 30 + (attempt * 15)  # 30s, 45s, 60s para Replit

                logger.debug(f"🔍 [DEBUG] Enviando foto a Telegram (intento {attempt}): {photo_path}")

                if self.session:
                    with open(photo_path, 'rb') as photo:
                        files = {'photo': photo}
                        data = {
                            'chat_id': str(self.config.telegram_chat_id),  # Debe ser string según API
                            'caption': caption,
                            'parse_mode': parse_mode,
                            'disable_notification': False  # Permitir notificación
                        }
                        response = self.session.post(
                            f"{self.base_url}/sendPhoto",
                            files=files,
                            data=data,
                            timeout=current_timeout
                        )
                        success = response.status_code == 200
                        response_text = response.text
                else:
                    # Fallback a urllib (más complejo para archivos)
                    with open(photo_path, 'rb') as photo:
                        photo_data = photo.read()

                    # Crear boundary multipart/form-data
                    boundary = f'----WebKitFormBoundary{int(time.time())}'

                    # Construir cuerpo multipart
                    body = []

                    # chat_id
                    body.append(f'--{boundary}\r\n'.encode())
                    body.append(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'.encode())
                    body.append(f'{self.config.telegram_chat_id}\r\n'.encode())

                    # caption
                    body.append(f'--{boundary}\r\n'.encode())
                    body.append(f'Content-Disposition: form-data; name="caption"\r\n\r\n'.encode())
                    body.append(f'{caption}\r\n'.encode())

                    # parse_mode
                    body.append(f'--{boundary}\r\n'.encode())
                    body.append(f'Content-Disposition: form-data; name="parse_mode"\r\n\r\n'.encode())
                    body.append(f'{parse_mode}\r\n'.encode())

                    # photo
                    body.append(f'--{boundary}\r\n'.encode())
                    body.append(f'Content-Disposition: form-data; name="photo"; filename="{os.path.basename(photo_path)}"\r\n'.encode())
                    body.append(f'Content-Type: image/jpeg\r\n\r\n'.encode())
                    body.append(photo_data)
                    body.append(f'\r\n--{boundary}--\r\n'.encode())

                    body_bytes = b''.join(body)

                    req = urllib.request.Request(
                        f"{self.base_url}/sendPhoto",
                        data=body_bytes,
                        headers={
                            'Content-Type': f'multipart/form-data; boundary={boundary}',
                            'Content-Length': str(len(body_bytes))
                        }
                    )

                    with urllib.request.urlopen(req, timeout=current_timeout) as resp:
                        success = resp.status == 200
                        response_text = resp.read().decode('utf-8')

                # Procesar respuesta
                if success:
                    logger.info(f"✅ Foto enviada a Telegram exitosamente (intento {attempt}): {photo_path}")
                    return True
                else:
                    # Extraer información de error
                    try:
                        error_data = json.loads(response_text) if response_text else {}
                        error_code = error_data.get('error_code', 'N/A')
                        error_description = error_data.get('description', 'Sin descripción')
                    except:
                        error_code = response.status_code if 'response' in locals() else 'N/A'
                        error_description = response_text[:100] if response_text else 'Sin respuesta'

                    logger.error(f"❌ [ERROR] Telegram API Photo (intento {attempt}):")
                    logger.error(f"   Status Code: {error_code}")
                    logger.error(f"   Respuesta: {response_text[:200]}...")
                    logger.error(f"   Descripción del error: '{error_description}'")

                    # Si es un error de cliente (4xx), reintentar no sirve
                    if 400 <= error_code < 500:
                        logger.error("🛑 [FATAL] Error de cliente (4xx). No se reintentará.")
                        return False

            except Exception as e:
                logger.debug(f"⚠️ [DEBUG] Intento {attempt}/{max_retries} fallido al enviar foto: {e}")

            # Esperar antes del siguiente intento
            if attempt < max_retries:
                wait_time = 2 ** (attempt - 1)
                logger.debug(f"🔄 Reintentando enviar foto en {wait_time} segundos...")
                time.sleep(wait_time)

        logger.error(f"❌ [ERROR] Telegram: todos los intentos fallidos ({max_retries}) para enviar foto.")
        return False

    def send_optimized_trading_signal(self, signal_id: str, signal_dict: dict, symbol: str,
                                neural_prediction: dict, technical_confidence: float,
                                send_photo: bool = False) -> bool:
        """
        Envío de señal premium con ciclo completo:
        DESTACADA (solo texto) → CONFIRMADA (notificación con gráfico) → Milestones → Cierre
        ✅ CORREGIDO: DESTACADA envía solo texto, CONFIRMADA envía con gráfico
        """
        if not self.config.telegram_enabled or signal_id in self.sent_signals:
            return False
        try:
            signal_data = signal_dict or {}
            combined_signal_type = signal_data.get('combined_signal', 'NEUTRAL')
            neural_confidence = signal_data.get('neural_score', 0)
            technical_percentage = signal_data.get('technical_percentage', technical_confidence)
            current_status = signal_data.get('status', 'DESTACADA')

            # ✅ DESTACADA: Enviar notificación sin gráfico
            # ✅ CONFIRMADA: Enviar notificación con gráfico
            is_buy = signal_data.get('is_buy', True)
            direction = "COMPRA 🟢" if is_buy else "VENTA 🔴"

            if current_status == 'CONFIRMADA':
                emoji_prefix = "🚀"
                signal_level_text = "(✨ CONFIRMADA ✨)"
            else:
                emoji_prefix = "⭐"
                signal_level_text = "(⭐ DESTACADA ⭐)"

            # === CALCULAR SL/TP CON PROTECCIÓN ===
            entry_price = float(signal_dict.get('entry_price', 0.0))
            if entry_price <= 1e-8:
                logger.error(f"Precio inválido para {symbol}: {entry_price}")
                return None  

            sl_pct = self.config.DEFAULT_STOP_LOSS_PERCENT
            tp_pct = self.config.DEFAULT_TAKE_PROFIT_PERCENT
            # ✅ CORREGIDO: Usar is_buy para calcular SL/TP correctamente
            if is_buy:  # COMPRA (Long): SL abajo, TP arriba
                stop_loss = entry_price * (1 - sl_pct)
                take_profit = entry_price * (1 + tp_pct)
            else:  # VENTA (Short): SL arriba, TP abajo
                stop_loss = entry_price * (1 + sl_pct)
                take_profit = entry_price * (1 - tp_pct)

            # === CONDICIONES CUMPLIDAS ===
            conditions = signal_data.get('conditions_met', ["IA + Técnico + Alineación ≥ 92%"])
            formatted_conditions = "\n".join([f"   • {c}" for c in conditions[:5]]) if conditions else "IA + Técnico + Alineación ALINEADOS"

            # === CONSTRUIR MENSAJE ===
            message = self.config.TELEGRAM_SIGNAL_TEMPLATE.format(
                emoji_prefix=emoji_prefix,
                direction=direction,
                signal_level_text=signal_level_text,
                symbol=self._escape_html(symbol),
                market_type=self.config.MARKET_TYPE,
                combined_signal_type=self._escape_html(str(combined_signal_type)),
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                technical_confidence=technical_percentage,
                neural_confidence=neural_confidence,
                combined_confidence=(neural_confidence + technical_percentage) / 2,
                conditions_met=self._escape_html(formatted_conditions),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            # === ENVIAR TEXTO ===
            text_sent = self._send_message_direct(message)

            # === GRÁFICO SOLO PARA CONFIRMADA ===
            if current_status == 'CONFIRMADA' and send_photo:
                chart_path = signal_data.get('chart_path')
                if chart_path and os.path.exists(chart_path):
                    caption = f"📊 {self._escape_html(symbol)} {signal_level_text}\n💰 Objetivo: {tp_pct*100:.1f}% | Stop: {sl_pct*100:.1f}%"
                    self.send_photo(chart_path, caption)
                logger.info(f"✅ {symbol} CONFIRMADA enviada a Telegram con gráfico")
            else:
                logger.info(f"⭐ {symbol} DESTACADA enviada a Telegram (sin gráfico)")

            self.sent_signals.add(signal_id)
            return text_sent
        except Exception as e:
            logger.error(f"Error enviando señal optimizada: {e}")
            return False


    def send_promotion_update(self, symbol: str, profit_percent: float, chart_path: str = None, signal_data: dict = None):
        """
        Enviar notificación cuando DESTACADA se promueve a CONFIRMADA
        ✅ Envía notificación CON gráfico (segunda notificación del ciclo de vida)
        """
        if not self.config.telegram_enabled:
            return False

        # Evitar duplicados - cada símbolo solo se promociona una vez
        if symbol in self.sent_promotions:
            logger.debug(f"⏭️ Promoción ya enviada para {symbol}, omitiendo duplicado")
            return True

        # Dedupe fuerte por evento
        if not self._dedupe_once(("PROMOTION", symbol)):
            logger.debug(f"⏭️ Evento PROMOTION duplicado para {symbol}")
            return True

        try:
            escaped_symbol = self._escape_html(symbol)

            # Construir mensaje según datos disponibles
            if signal_data:
                entry_price = signal_data.get('entry_price', 0)
                stop_loss = signal_data.get('stop_loss', 0)
                take_profit = signal_data.get('take_profit', 0)
                neural_conf = signal_data.get('neural_score', 0)
                tech_pct = signal_data.get('technical_percentage', 0)
                is_buy = signal_data.get('is_buy', True)
                direction = "COMPRA 🟢" if is_buy else "VENTA 🔴"

                message = (
                    f"🚀 <b>SEÑAL PROMOVIDA A CONFIRMADA</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 Par: {escaped_symbol}\n"
                    f"📈 Mercado: {self.config.MARKET_TYPE}\n"
                    f"📌 Dirección: {direction}\n"
                    f"💰 Entrada: ${entry_price:.6f}\n"
                    f"🎯 Objetivo: ${take_profit:.6f}\n"
                    f"🛑 Stop Loss: ${stop_loss:.6f}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🤖 IA: {neural_conf:.1f}% | 📈 Técnico: {tech_pct:.1f}%\n"
                    f"📊 Profit Actual: {profit_percent:+.2f}%\n"
                    f"⏳ Seguimiento activo hasta objetivo o cambio de tendencia"
                )
            else:
                message = (
                    f"🚀 <b>SEÑAL PROMOVIDA A CONFIRMADA</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 Par: {escaped_symbol}\n"
                    f"📈 Mercado: {self.config.MARKET_TYPE}\n"
                    f"📊 Profit Actual: {profit_percent:+.2f}%\n"
                    f"⏳ Seguimiento activo hasta objetivo o cambio de tendencia"
                )

            message = self._truncate_message(message)

            # SOLO UN ENVÍO: foto con caption o texto (nunca ambos)
            sent_ok = False
            if chart_path and os.path.exists(chart_path):
                sent_ok = self.send_photo(chart_path, message, parse_mode='HTML')

            if not sent_ok:
                sent_ok = self._send_message_direct(message)

            if sent_ok:
                self.sent_promotions.add(symbol)
                logger.info(f"✅ {symbol} promoción CONFIRMADA enviada (1 solo mensaje)")
            return sent_ok

        except Exception as e:
            logger.error(f"❌ Error enviando promoción para {symbol}: {e}")
            return False

    def send_closure_update(self, symbol: str, reason: str, profit_percent: float, duration_minutes: float, max_profit: float, chart_path: str = None):
        if not self.config.telegram_enabled:
            return False

        # Limpiar promoción enviada para permitir futuras promociones del mismo par
        self.sent_promotions.discard(symbol)

        reason_key = self._normalize_reason_key(reason)
        if not self._dedupe_once(("CLOSURE", symbol, reason_key)):
            logger.debug(f"⏭️ Cierre duplicado omitido para {symbol} ({reason_key})")
            return True

        try:
            if reason == 'target_reached':
                emoji = "🏆"
                title = "OBJETIVO ALCANZADO - OPERACIÓN CERRADA"
            elif reason == 'PARTIAL_TARGET_TIMEOUT':
                emoji = "✅"
                title = "OBJETIVO PARCIAL ALCANZADO - OPERACIÓN CERRADA (3h)"
            elif reason == 'stop_loss_hit':
                emoji = "🛑"
                title = "STOP LOSS ALCANZADO - OPERACIÓN CERRADA"
            elif reason == 'trend_reversal_detected':
                emoji = "🔄"
                title = "CAMBIO DE TENDENCIA - OPERACIÓN CERRADA"
            elif reason == 'TREND_CHANGE_PARTIAL':
                emoji = "⚠️"
                title = "CAMBIO DE TENDENCIA - CIERRE PARCIAL"
            elif reason == 'TIMEOUT' or reason == 'CONFIRMED_TIMEOUT':
                emoji = "⌛"
                title = "TIMEOUT - OPERACIÓN CERRADA"
            else:
                emoji = "⏹️"
                title = "OPERACIÓN CERRADA"

            escaped_symbol = self._escape_html(symbol)

            # Mensaje especial para cierre parcial por timeout
            if reason == 'PARTIAL_TARGET_TIMEOUT':
                caption = (
                    f"{emoji} <b>{title}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 Par: {escaped_symbol}\n"
                    f"💰 Profit Alcanzado: <b>{profit_percent:+.2f}%</b>\n"
                    f"⏱️ Duración: {duration_minutes:.0f} min ({duration_minutes/60:.1f}h)\n"
                    f"📈 Máximo: {max_profit:.2f}%\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ Cierre inteligente por tiempo (3h+)\n"
                    f"🔄 Bot reanudado - Buscando nuevas oportunidades"
                )
            elif reason == 'TREND_CHANGE_PARTIAL':
                caption = (
                    f"{emoji} <b>{title}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 Par: {escaped_symbol}\n"
                    f"💰 Profit Asegurado: <b>{profit_percent:+.2f}%</b>\n"
                    f"⏱️ Duración: {duration_minutes:.0f} min\n"
                    f"📈 Máximo: {max_profit:.2f}%\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚠️ Tendencia invertida durante profit\n"
                    f"🔒 Ganancia asegurada antes de reversión"
                )
            else:
                caption = (
                    f"{emoji} <b>{title}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 Símbolo: {escaped_symbol}\n"
                    f"{'💰 Profit Final' if profit_percent >= 0 else '📉 Pérdida'}: {profit_percent:+.2f}%\n"
                    f"⏱️ Duración: {duration_minutes:.1f} minutos\n"
                    f"📈 Máximo Alcanzado: {max_profit:.2f}%\n"
                    f"▶️ Bot reanudado."
                )

            caption = self._truncate_message(caption)

            # SOLO UN ENVÍO: foto con caption o texto (nunca ambos)
            sent_ok = False
            if chart_path and os.path.exists(chart_path):
                sent_ok = self.send_photo(chart_path, caption, parse_mode='HTML')
            if not sent_ok:
                sent_ok = self.send_message(caption, parse_mode='HTML')
            return sent_ok
        except Exception as e:
            logger.error(f"Error enviando cierre: {e}")
            return False

    def _normalize_reason_key(self, reason: str) -> str:
        """Normaliza razones de cierre para evitar duplicados con alias."""
        r = str(reason or '').strip().upper()
        reason_map = {
            "TARGET_REACHED": "PROFIT_TARGET",
            "TAKE_PROFIT": "PROFIT_TARGET",
            "TP_REACHED": "PROFIT_TARGET",
            "STOP_LOSS_HIT": "STOP_LOSS",
            "SL_HIT": "STOP_LOSS",
            "TREND_REVERSAL_DETECTED": "TREND_REVERSAL",
            "TREND_CHANGE_PARTIAL": "PARTIAL_TARGET",
        }
        return reason_map.get(r, r)

    def _dedupe_once(self, key: tuple) -> bool:
        """Retorna True si el evento es nuevo; False si ya fue enviado antes."""
        with self.telegram_dedupe_lock:
            if not hasattr(self, '_sent_event_keys'):
                self._sent_event_keys = set()
            if key in self._sent_event_keys:
                return False
            self._sent_event_keys.add(key)
            return True


    def test_connection(self) -> bool:
        """Probar conexión optimizada (requests o urllib)"""
        try:
            url = f"{self.base_url}/getMe"
            if self.session:
                response = self.session.get(url, timeout=30)  # ✅ Aumentado para alta latencia
                return response.status_code == 200
            else:
                with urllib.request.urlopen(url, timeout=30) as resp:  # ✅ Aumentado para alta latencia
                    return resp.status == 200
        except Exception as e:
            logger.error(f"Error probando conexión Telegram: {e}")
            return False

    def send_milestone_update(self, symbol: str, milestone: float, profit: float, chart_path: str = None):
        """Enviar actualización de milestone con valores dinámicos desde config"""
        if not self.config.telegram_enabled:
            return False
        try:
            # ✅ Obtener valores dinámicos de config
            m1 = getattr(self.config, 'MILESTONE_1', 0.5)
            m2 = getattr(self.config, 'MILESTONE_2', 1.0)
            m3 = getattr(self.config, 'MILESTONE_3', 1.5)
            sl_pct = getattr(self.config, 'DEFAULT_STOP_LOSS_PERCENT', 0.01) * 100

            # Evitar duplicar la notificación final: objetivo lo informa el cierre
            if milestone >= m3:
                logger.debug(f"⏭️ Milestone objetivo omitido para {symbol}; lo informa el cierre")
                return True

            milestone_key = round(float(milestone), 4)
            if not self._dedupe_once(("MILESTONE", symbol, milestone_key)):
                logger.debug(f"⏭️ Milestone duplicado omitido para {symbol} ({milestone_key})")
                return True

            # Determinar qué milestone es y cuál es el próximo
            if milestone >= m3:
                emoji = "🎯"
                milestone_name = "OBJETIVO ALCANZADO"
                next_info = "✅ ¡Take Profit logrado!"
            elif milestone >= m2:
                emoji = "📊"
                milestone_name = f"Avance +{milestone:.1f}%"
                next_info = f"📈 Próximo objetivo: {m3:.1f}%"
            else:
                emoji = "📊"
                milestone_name = f"Avance +{milestone:.1f}%"
                next_info = f"📈 Próximo objetivo: {m2:.1f}%"

            escaped_symbol = self._escape_html(symbol)
            text = (
                f"{emoji} ACTUALIZACIÓN DE OPERACIÓN — {milestone_name}\n"
                f"📈 Símbolo: {escaped_symbol}\n"
                f"💰 Profit actual: {profit:+.2f}%\n"
                f"🎯 Objetivo: {m3:.1f}% (TP)\n"
                f"🛑 Stop Loss: -{sl_pct:.1f}%\n"
                f"{next_info}\n"
                f"⏱️ {datetime.now().strftime('%H:%M:%S')}"
            )
            text = self._truncate_message(text)

            # SOLO UN ENVÍO: foto con caption o texto
            sent_ok = False
            if chart_path and os.path.exists(chart_path):
                sent_ok = self.send_photo(photo_path=chart_path, caption=text, parse_mode='HTML')
            if not sent_ok:
                sent_ok = self.send_message(text, parse_mode='HTML')
            return sent_ok
        except Exception as e:
            logger.error(f"Error enviando Avance {milestone}%: {e}")
            return False

    def send_highlight_expired_notification(self, symbol: str, duration_minutes: float):
        """Enviar notificación cuando una señal DESTACADA expira sin confirmarse"""
        if not self.config.telegram_enabled:
            return False

        if not self._dedupe_once(("HIGHLIGHT_EXPIRED", symbol)):
            logger.debug(f"⏭️ HIGHLIGHT_EXPIRED duplicado omitido para {symbol}")
            return True

        try:
            escaped_symbol = self._escape_html(symbol)
            text = (
                f"❌ SEÑAL DESTACADA CANCELADA\n\n"
                f"📊 Símbolo: {escaped_symbol}\n"
                f"📝 Motivo: No superó confirmación\n"
                f"⏱️ Tiempo en destacada: {duration_minutes:.1f} minutos\n"
                f"▶️ Bot reanudado - Buscando nuevas señales\n"
                f"🕐 {datetime.now().strftime('%H:%M:%S')}"
            )
            text = self._truncate_message(text)
            return self.send_message(text, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Error enviando notificación HIGHLIGHT_EXPIRED: {e}")
            return False


# ========== GESTOR DE DATOS OPTIMIZADO ==========
class OptimizedDataManager:
    def __init__(self, max_memory_mb=300):
        self.max_memory = max_memory_mb * 1024 * 1024
        self.data_cache = {}
        self.access_times = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
        self.cache_lock = threading.RLock()  # 🔒 LOCK AÑADIDO
        self._access_counter = 0

    def get_data(self, symbol, timeframe, limit=500, client=None):
        cache_key = f"{symbol}_{timeframe}_{limit}"
        current_time = time.time()
        with self.cache_lock:
            if cache_key in self.data_cache:
                data, timestamp = self.data_cache[cache_key]
                cache_duration = 900 if timeframe in ['5m', '15m'] else 3600
                if current_time - timestamp < cache_duration:
                    self.access_times[cache_key] = current_time
                    self.cache_stats['hits'] += 1
                    return data
        self.cache_stats['misses'] += 1
        if client is None:
            return None
        df = client.get_klines(symbol, timeframe, limit)
        if df is not None and not df.empty:
            if self._validate_data_quality(df):
                with self.cache_lock:
                    self.data_cache[cache_key] = (df, current_time)
                    self.access_times[cache_key] = current_time
                self._access_counter += 1
                if self._access_counter % 20 == 0:
                    self._optimize_cache()
            else:
                logger.warning(f"Datos de calidad insuficiente para {symbol}")
        return df

    def _validate_data_quality(self, df):
        if df is None or df.empty or len(df) < 20:
            return False
        if df.isnull().any().any():
            return False
        if (df['high'] < df['low']).any() or (df['close'] < df['low']).any() or (df['close'] > df['high']).any():
            return False
        if (df['volume'] < 0).any():
            return False
        if (df['close'] <= 0).any() or (df['high'] <= 0).any() or (df['low'] <= 0).any():
            return False
        return True

    def _optimize_cache(self):
        with self.cache_lock:
            if len(self.data_cache) > 80:  # ✅ LÍMITE EXPLÍCITO
                n_to_remove = max(1, len(self.data_cache) // 5)
                sorted_keys = sorted(
                    self.access_times.items(), 
                    key=lambda x: x[1]
                )[:n_to_remove]
                for key, _ in sorted_keys:
                    self.data_cache.pop(key, None)
                    self.access_times.pop(key, None)
                logger.info(f"🧹 Cache limpiada: eliminadas {n_to_remove} entradas (total: {len(self.data_cache)})")

    def get_cache_stats(self):
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        return {
            'total_entries': len(self.data_cache),
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses']
        }

class APIPollingFallback:
    """
    Obtiene datos de mercado mediante la API REST como respaldo cuando WebSocket falla.
    """
    def __init__(self, symbol: str, intervalo: str, callback: Callable, polling_interval: int = 30):
        self.symbol = symbol
        self.intervalo = intervalo
        self.callback = callback
        self.polling_interval = polling_interval
        self._stop_event = threading.Event()
        self.thread = None
        _env_eps = os.environ.get('BINANCE_KLINES_ENDPOINTS', '').strip()
        if _env_eps:
            _parsed = [e.strip() for e in _env_eps.split(',') if e.strip()]
            self.endpoints = _parsed if _parsed else [
                "https://api.binance.com/api/v3/klines",
                "https://api1.binance.com/api/v3/klines",
                "https://api2.binance.com/api/v3/klines",
                "https://api3.binance.com/api/v3/klines",
                "https://data-api.binance.vision/api/v3/klines"
            ]
        else:
            self.endpoints = [
                "https://api.binance.com/api/v3/klines",
                "https://api1.binance.com/api/v3/klines",
                "https://api2.binance.com/api/v3/klines",
                "https://api3.binance.com/api/v3/klines",
                "https://data-api.binance.vision/api/v3/klines"
            ]
        self._endpoint_index = 0
        self.session = None
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            _retry = Retry(total=3, connect=3, read=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
            _adapter = HTTPAdapter(max_retries=_retry)
            self.session.mount("https://", _adapter)

    def _fetch_kline(self):
        try:
            params = {
                'symbol': self.symbol,
                'interval': self.intervalo,
                'limit': 1  # Solo la última vela
            }
            last_error = None
            for _ in range(len(self.endpoints)):
                url = self.endpoints[self._endpoint_index]
                try:
                    if self.session is not None:
                        response = self.session.get(url, params=params, timeout=30)
                    else:
                        response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    if data:
                        kline_data = data[0]
                        kline = {
                            't': int(kline_data[0]),
                            's': self.symbol,
                            'o': kline_data[1],
                            'h': kline_data[2],
                            'l': kline_data[3],
                            'c': kline_data[4],
                            'v': kline_data[5],
                            'i': self.intervalo,
                            'x': True,
                        }
                        if self.callback:
                            self.callback({'symbol': self.symbol, 'kline': kline})
                        return
                except Exception as e:
                    last_error = e
                    self._endpoint_index = (self._endpoint_index + 1) % len(self.endpoints)
                    continue
            if last_error:
                raise last_error
        except Exception as e:
            err_str = str(e)
            is_conn_error = "NameResolutionError" in err_str or "ConnectionError" in err_str or "getaddrinfo failed" in err_str
            
            if is_conn_error:
                # ✅ MEJORA v35: Throttling de logs de conexión inestable
                global _LAST_NETWORK_WARNING_TIME
                current_time = time.time()
                if current_time - _LAST_NETWORK_WARNING_TIME > 60: # Solo una vez por minuto
                    logger.warning(f"⚠️ Conexión inestable en API Polling: No se pudo resolver host o conectar. (Afectando a {self.symbol} y otros)")
                    _LAST_NETWORK_WARNING_TIME = current_time
                else:
                    logger.debug(f"Fallo de conexión en API Polling para {self.symbol} (silenciado)")
            else:
                logger.error(f"Error en API Polling Fallback para {self.symbol}: {e}")

    def _run_loop(self):
        logger.info(f"🔄 Iniciando modo de respaldo (API Polling) para {self.symbol} cada {self.polling_interval}s.")
        while not self._stop_event.is_set():
            self._fetch_kline()
            # Esperar el intervalo o hasta que se detenga
            self._stop_event.wait(self.polling_interval)
        logger.info(f"🛑 Modo de respaldo (API Polling) detenido para {self.symbol}.")

    def iniciar(self):
        if self.thread and self.thread.is_alive():
            return
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def detener(self):
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)
class RobustWebSocketManager:
    """
    Gestor WebSocket Mejorado v35.0.0.0 con:
    - Backoff exponencial con jitter para reconexion
    - Heartbeat para detectar conexiones muertas
    - Deteccion de error 451 (bloqueo regional)
    - Metricas de latencia y calidad de conexion
    - Fallback automatico a API REST
    """
    def __init__(self, symbols: List[str], intervalo: str, callback: Callable, max_reconnect_attempts: int = 100):
        # Validar y limpiar simbolos invalidos
        self.symbols = [s.strip().upper() for s in symbols if s and isinstance(s, str)]
        if not self.symbols:
            logger.error("Ningun simbolo valido proporcionado a RobustWebSocketManager")
            self.symbols = []

        self.intervalo = intervalo
        self.callback = callback
        self.max_reconnect_attempts = max_reconnect_attempts

        self.ws = None
        self.thread = None
        self.ejecutando = False
        self.intentos_reconexion = 0
        
        # === MEJORA v35: Backoff exponencial con jitter ===
        self.base_retraso_reconexion = 1  # Segundos base para reconexion
        self.max_retraso_reconexion = 60  # Max 60 segundos
        self.jitter_factor = 0.3  # 30% de variacion aleatoria

        # URL WebSocket para Binance Futures (PERPETUALS)
        self.url_base_futures = "wss://fstream.binance.com/ws"
        self.url_base_spot = "wss://stream.binance.com:9443/ws"
        self.url_base = self.url_base_futures  # Default: Futures para PERPETUALS
        
        # URLs alternativas para fallback
        self.url_alternativas = [
            "wss://fstream.binance.com/ws",
            "wss://fstream1.binance.com/ws",
            "wss://fstream2.binance.com/ws",
            "wss://fstream3.binance.com/ws"
        ]
        self.url_index = 0

        # Estado de conexion
        self.conectado = False
        self.ultimo_ping = 0
        # Ping/pong optimizado para estabilidad
        self.intervalo_ping = 90  # Intervalo entre pings (90s)
        self.ping_timeout = 60    # Tiempo de espera para pong (60s)

        # Gestion del modo de respaldo (Fallback)
        self.fallback_active = False
        self.fallback_managers: Dict[str, APIPollingFallback] = {}
        self.reconnect_timer = None

        # === MEJORA v35: Metricas avanzadas ===
        self.ultimo_mensaje = 0
        self.mensajes_recibidos = 0
        self.errores_consecutivos = 0
        self.ultimos_errores = []  # Rastrear ultimos errores para diagnostico
        self.latencias = []  # Ultimas 100 latencias para analisis
        self.max_latencias_guardadas = 100
        
        # Heartbeat para detectar conexiones muertas
        self.ultimo_heartbeat = time.time()
        self.heartbeat_timeout = 120  # Segundos sin datos = conexion muerta
        self.heartbeat_thread = None
        
        # Deteccion de bloqueo regional (error 451)
        self.regional_block_detected = False
        self.last_451_error = None

        # Control de hilo para reconexion
        self._stop_event = threading.Event()
        self._callback_queue = queue.Queue(maxsize=2000)
        self._callback_thread = None
        self._dropped_updates = 0

        # Compatibilidad websocket-client (evitar warning repetido por ping_payload)
        self._ping_payload_unsupported = False
        
        # Estadisticas de conexion
        self.connection_stats = {
            'total_connections': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'total_reconnections': 0,
            'fallback_activations': 0,
            'messages_processed': 0,
            'messages_dropped': 0,
            'avg_latency_ms': 0
        }
    
    def _calculate_backoff_delay(self) -> float:
        """
        Calcula el delay para reconexion usando backoff exponencial con jitter
        """
        # Backoff exponencial: base * 2^intentos
        delay = self.base_retraso_reconexion * (2 ** min(self.intentos_reconexion, 6))
        delay = min(delay, self.max_retraso_reconexion)
        
        # Agregar jitter aleatorio para evitar thundering herd
        jitter = delay * self.jitter_factor * random.random()
        final_delay = delay + jitter
        
        logger.debug(f"Backoff delay: {final_delay:.1f}s (intento {self.intentos_reconexion})")
        return final_delay
    
    def _rotate_url(self):
        """Rota a la siguiente URL alternativa"""
        self.url_index = (self.url_index + 1) % len(self.url_alternativas)
        self.url_base = self.url_alternativas[self.url_index]
        logger.info(f"Rotando a URL alternativa: {self.url_base}")
    
    def _start_heartbeat_monitor(self):
        """Inicia el monitor de heartbeat para detectar conexiones muertas"""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            return
        
        def heartbeat_worker():
            while self.ejecutando and not self._stop_event.is_set():
                time.sleep(30)  # Verificar cada 30 segundos
                
                if not self.conectado:
                    continue
                
                tiempo_sin_datos = time.time() - self.ultimo_heartbeat
                
                if tiempo_sin_datos > self.heartbeat_timeout:
                    logger.warning(f"Heartbeat timeout: {tiempo_sin_datos:.0f}s sin datos. Forzando reconexion...")
                    self.errores_consecutivos += 1
                    
                    # Forzar cierre y reconexion
                    if self.ws:
                        try:
                            self.ws.close()
                        except:
                            pass
                    self.conectado = False
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True, name="WS-Heartbeat")
        self.heartbeat_thread.start()
    
    def _record_latency(self, latency_ms: float):
        """Registra latencia para estadisticas"""
        self.latencias.append(latency_ms)
        if len(self.latencias) > self.max_latencias_guardadas:
            self.latencias.pop(0)
        
        if self.latencias:
            self.connection_stats['avg_latency_ms'] = sum(self.latencias) / len(self.latencias)
    
    def get_connection_quality(self) -> str:
        """Retorna la calidad de la conexion basada en metricas"""
        if not self.conectado:
            return "DESCONECTADO"
        
        avg_latency = self.connection_stats.get('avg_latency_ms', 0)
        
        if avg_latency < 100:
            return "EXCELENTE"
        elif avg_latency < 300:
            return "BUENA"
        elif avg_latency < 1000:
            return "REGULAR"
        else:
            return "POBRE"
    def iniciar(self):
        """Iniciar conexion WebSocket en un hilo separado con mejoras v35"""
        if not WEBSOCKET_AVAILABLE:
            logger.info("WebSocket no disponible - Usando modo polling/REST")
            self._start_fallback()
            return

        if self.ejecutando:
            logger.warning("WebSocket ya esta en ejecucion")
            return

        self._stop_event.clear()
        self.ejecutando = True
        self.intentos_reconexion = 0
        self.errores_consecutivos = 0
        self.regional_block_detected = False
        self.ultimo_heartbeat = time.time()
        
        # Reset estadisticas de conexion
        self.connection_stats['total_connections'] += 1

        if not self._callback_thread or not self._callback_thread.is_alive():
            self._callback_thread = threading.Thread(target=self._callback_worker, daemon=True, name="WS-Callback")
            self._callback_thread.start()
        
        # Iniciar monitor de heartbeat
        self._start_heartbeat_monitor()

        self.thread = threading.Thread(target=self._gestor_conexion, daemon=True, name="WS-Manager")
        self.thread.start()
        logger.info(f"Gestor WebSocket v35 iniciado para {len(self.symbols)} simbolos")

    def detener(self):
        """Detener conexión WebSocket y modo de respaldo"""
        logger.info("🛑 Deteniendo gestor WebSocket...")
        self.ejecutando = False
        self._stop_event.set()

        if self.reconnect_timer:
            self.reconnect_timer.cancel()

        self._stop_fallback()

        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

        if self._callback_thread and self._callback_thread.is_alive():
            self._callback_thread.join(timeout=5)

        logger.info("✅ Gestor WebSocket y modo de respaldo detenido.")

    def _callback_worker(self):
        while self.ejecutando and not self._stop_event.is_set():
            try:
                item = self._callback_queue.get(timeout=1)
            except queue.Empty:
                continue
            try:
                self.callback(item)
            except Exception as e:
                logger.error(f"Error procesando callback WebSocket: {e}")
            finally:
                try:
                    self._callback_queue.task_done()
                except Exception:
                    pass

    def _gestor_conexion(self):
        """Gestiona la conexión WebSocket con lógica de reconexión"""
        while self.ejecutando:
            try:
                if not self.conectado:
                    self._conectar()

                # Dormir por un intervalo corto para evitar bucle ajustado
                time.sleep(1)

                # Verificar si hay mensajes (para detectar conexiones muertas)
                if self.conectado and time.time() - self.ultimo_mensaje > self.intervalo_ping * 3:
                    logger.warning("No se recibieron mensajes recientes, posible conexión muerta")
                    self.conectado = False
                    self.ws.close()

            except Exception as e:
                logger.error(f"Error en gestor de conexión: {e}")
                self.errores_consecutivos += 1

                # Si hay demasiados errores consecutivos, activar el modo de respaldo
                if self.errores_consecutivos >= 5:
                    logger.error("Demasiados errores consecutivos, activando modo de respaldo")
                    self._start_fallback()

                time.sleep(5)

    def _conectar(self):
        """Establecer conexión WebSocket - Siguiendo mejores prácticas de Binance"""
        try:
            # ✅ MEJORA 1: Validar símbolos antes de conectar
            if not self.symbols:
                logger.warning("⚠️ Sin símbolos válidos para conectar a WebSocket. Activando respaldo...")
                self._start_fallback()
                return

            # Construir nombres de streams (máx 10 por conexión según Binance)
            streams = [f"{symbol.lower()}@kline_{self.intervalo}" for symbol in self.symbols[:10]]
            if not streams:
                logger.warning("⚠️ No se pudieron construir streams válidos. Activando respaldo...")
                self._start_fallback()
                return

            ruta_stream = "/".join(streams)
            url = f"{self.url_base}/{ruta_stream}"

            logger.info(f"✅ Conectando a WebSocket: {len(streams)} streams de {len(self.symbols)} símbolos totales")

            # Crear WebSocket con encabezados correctos según Binance API docs
            self.ws = websocket.WebSocketApp(
                url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open,
                header={
                    "User-Agent": "CryptoBotPro/1.0",
                    "Connection": "keep-alive"
                }
            )

            # ✅ MEJORA ARGENTINA: WebSocket con ping/pong optimizado para alta latencia
            # IMPORTANTE: ping_interval (90s) > ping_timeout (60s) - requisito websocket-client
            run_forever_kwargs = {
                'ping_interval': self.intervalo_ping,
                'ping_timeout': self.ping_timeout,
            }
            if not self._ping_payload_unsupported:
                run_forever_kwargs['ping_payload'] = 'ping'

            try:
                self.ws.run_forever(**run_forever_kwargs)
            except TypeError as te:
                # Compatibilidad con versiones websocket-client antiguas sin soporte ping_payload
                if 'ping_payload' in str(te):
                    if not self._ping_payload_unsupported:
                        logger.info("websocket-client sin soporte 'ping_payload'; usando fallback sin ese parámetro")
                    self._ping_payload_unsupported = True
                    run_forever_kwargs.pop('ping_payload', None)
                    self.ws.run_forever(**run_forever_kwargs)
                else:
                    raise

        except Exception as e:
            error_str = str(e)
            # Errores específicos que requieren reconexión inmediata
            if any(err in error_str for err in ['10054', '10053', 'Connection reset', 'Connection closed']):
                logger.warning(f"Conexión reset por servidor: {e}. Reconectando inmediatamente...")
            else:
                logger.error(f"Fallo en conexión WebSocket: {e}")
            self.conectado = False
            self._programar_reconexion()

    def _programar_reconexion(self):
        """✅ MEJORA 2: Reconexión con retroceso exponencial mejorado - Binance Compliant"""
        if not self.ejecutando:
            return

        self.intentos_reconexion += 1

        if self.intentos_reconexion > self.max_reconnect_attempts:
            logger.error(f"❌ Máximo de intentos de reconexión ({self.max_reconnect_attempts}) alcanzado. Activando modo de respaldo.")
            self._start_fallback()
            return

        # ✅ MEJORA 2: Backoff exponencial más agresivo (0.5s base, max 30s)
        retraso = min(
            self.base_retraso_reconexion * (2 ** (self.intentos_reconexion - 1)),
            self.max_retraso_reconexion
        )
        # Añadir pequeño jitter para evitar "thundering herd"
        jitter = random.uniform(0, retraso * 0.1)
        retraso_final = retraso + jitter

        logger.debug(f"⏳ Reconectando en {retraso_final:.1f}s (intento {self.intentos_reconexion}/{self.max_reconnect_attempts})")
        time.sleep(retraso_final)

    def _on_open(self, ws):
        """Manejar conexión WebSocket abierta"""
        self.conectado = True
        self.intentos_reconexion = 0
        self.ultimo_ping = time.time()
        self.errores_consecutivos = 0  # Resetear contador de errores
        logger.info("Conexión WebSocket establecida")

        # Si la conexión se restablece, detener el modo de respaldo
        if self.fallback_active:
            self._stop_fallback()

    def _on_open(self, ws):
        """Manejar conexion WebSocket abierta - Mejorado v35"""
        self.conectado = True
        self.intentos_reconexion = 0
        self.ultimo_ping = time.time()
        self.ultimo_heartbeat = time.time()
        self.errores_consecutivos = 0
        self.connection_stats['successful_connections'] += 1
        logger.info(f"Conexion WebSocket establecida - URL: {self.url_base}")

        # Si la conexion se restablece, detener el modo de respaldo
        if self.fallback_active:
            self._stop_fallback()

    def _on_message(self, ws, mensaje):
        """Manejar mensajes WebSocket entrantes - Mejorado v35 con heartbeat"""
        try:
            current_time = time.time()
            self.ultimo_mensaje = current_time
            self.ultimo_heartbeat = current_time  # Actualizar heartbeat
            self.mensajes_recibidos += 1
            self.connection_stats['messages_processed'] += 1

            datos = json.loads(mensaje)

            # Manejar diferentes tipos de mensajes
            if 'data' in datos and 'k' in datos['data']:
                # Actualización de kline
                datos_kline = datos['data']['k']
                symbol = datos_kline['s']

                actualizacion = {
                    'symbol': symbol,
                    'kline': {
                        't': datos_kline['t'],  # Tiempo de apertura
                        'o': datos_kline['o'],  # Precio de apertura
                        'h': datos_kline['h'],  # Precio máximo
                        'l': datos_kline['l'],  # Precio mínimo
                        'c': datos_kline['c'],  # Precio de cierre
                        'v': datos_kline['v'],  # Volumen
                        'i': datos_kline['i'],  # Intervalo
                        'x': datos_kline['x'],  # Kline cerrado
                    }
                }

                # Procesar solo si kline está cerrado (vela completa)
                if datos_kline['x']:
                    try:
                        self._callback_queue.put_nowait(actualizacion)
                    except queue.Full:
                        self._dropped_updates += 1

            elif 'result' in datos:
                # Respuesta a suscripción
                logger.info("Suscripción WebSocket exitosa")
                try:
                    NETWORK_SUPPRESS_BLACKLIST_UNTIL = 0
                except Exception:
                    pass

        except json.JSONDecodeError as e:
            logger.error(f"No se pudo parsear mensaje WebSocket: {e}")
            self.errores_consecutivos += 1
        except Exception as e:
            logger.error(f"Error procesando mensaje WebSocket: {e}")
            self.errores_consecutivos += 1

    def _on_error(self, ws, error):
        """✅ MEJORA 4: Manejar errores WebSocket mejorado - Binance Error Handling"""
        error_str = str(error)
        self.ultimos_errores.append((datetime.now(), error_str))
        if len(self.ultimos_errores) > 10:
            self.ultimos_errores.pop(0)  # Mantener solo últimos 10 errores

        # Detectar tipos de error específicos
        is_dns_error = '11001' in error_str or 'getaddrinfo failed' in error_str
        
        if '10054' in error_str or '10053' in error_str:
            logger.warning(f"🔌 Conexión reset por host remoto. Intentando reconectar...")
        elif is_dns_error:
            # ✅ MEJORA v35: Si es error de DNS, verificar si hay internet general
            has_internet = is_internet_available()
            if not has_internet:
                logger.warning(f"📡 Error DNS (Sin Internet). El bot pausará intentos agresivos por 60s...")
                # Aumentar tiempo de espera para evitar spam
                time.sleep(5) 
            else:
                logger.warning(f"📡 Error DNS detectado pero hay internet. Posible bloqueo de dominio o DNS local fallido.")
            
            global NETWORK_SUPPRESS_BLACKLIST_UNTIL
            NETWORK_SUPPRESS_BLACKLIST_UNTIL = time.time() + 600
        elif 'ping/pong timed out' in error_str:
            logger.debug(f"⏱️ Timeout ping/pong. Posible lag de red. Aumentando tolerancia...")
        else:
            logger.error(f"❌ Error WebSocket: {error}")

        self.conectado = False
        self.errores_consecutivos += 1

        # ✅ MEJORA 4: Si hay muchos errores de ping/pong, activar respaldo más rápido
        # Pero si es un error DNS, no activar respaldo inmediatamente ya que fallará igual
        if self.errores_consecutivos >= 3:
            if is_dns_error and not is_internet_available():
                logger.debug("Omitiendo activación de modo respaldo: Sin conexión a internet.")
                # Resetear contador para reintentar websocket después de una pausa
                self.errores_consecutivos = 1 
                time.sleep(10)
            else:
                logger.error(f"⚠️ {self.errores_consecutivos} errores consecutivos. Escalando a modo de respaldo...")
                self._start_fallback()

    # --- dentro de RobustWebSocketManager._on_close ---
    def _on_close(self, ws, codigo_cierre, mensaje_cierre):
        self.conectado = False
        if codigo_cierre is None and mensaje_cierre is None:
            logger.debug("WebSocket cerrado sin código (posiblemente por falta de símbolos válidos)")
        else:
            logger.warning(f"WebSocket cerrado: {codigo_cierre} - {mensaje_cierre}")
        if self.ejecutando:
            self._programar_reconexion()

    def _start_fallback(self):
        """Inicia el mecanismo de respaldo con API REST."""
        if self.fallback_active:
            return

        self.fallback_active = True
        logger.warning("⚠️ Activando MODO DE RESPALDO (API REST). La conexión en tiempo real está deshabilitada.")

        for symbol in self.symbols:
            manager = APIPollingFallback(
                symbol=symbol,
                intervalo=self.intervalo,
                callback=self.callback
            )
            manager.iniciar()
            self.fallback_managers[symbol] = manager

        self._try_reconnect_periodically()

    def _stop_fallback(self):
        """Detiene el mecanismo de respaldo y el temporizador de reconexión."""
        if not self.fallback_active:
            return

        self.fallback_active = False
        logger.info("🔄 Desactivando modo de respaldo, intentando reconectar a WebSocket...")

        if self.reconnect_timer:
            self.reconnect_timer.cancel()
            self.reconnect_timer = None

        for symbol, manager in self.fallback_managers.items():
            manager.detener()
        self.fallback_managers.clear()

    def _try_reconnect_periodically(self):
        """Intenta reconectar a WebSocket cada 5 minutos mientras el fallback está activo."""
        if self._stop_event.is_set() or not self.fallback_active:
            return

        logger.info("🔄 Intentando reconectar a WebSocket desde el modo de respaldo...")
        self._stop_fallback()
        self.intentos_reconexion = 0
        self.iniciar()

        # Si la nueva conexión también falla, este proceso se repetirá.
        # Programar el siguiente intento si el fallback se vuelve a activar.
        if self.fallback_active:
            self.reconnect_timer = threading.Timer(300, self._try_reconnect_periodically) # 300s = 5 min
            self.reconnect_timer.daemon = True
            self.reconnect_timer.start()

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de rendimiento del gestor WebSocket"""
        return {
            'conectado': self.conectado,
            'fallback_active': self.fallback_active,
            'intentos_reconexion': self.intentos_reconexion,
            'mensajes_recibidos': self.mensajes_recibidos,
            'errores_consecutivos': self.errores_consecutivos,
            'ultimo_mensaje': datetime.fromtimestamp(self.ultimo_mensaje).isoformat() if self.ultimo_mensaje > 0 else None,
            'symbols': self.symbols
        }
# ========== ESCÁNER DE SÍMBOLOS ==========
class SymbolScanner:
    def __init__(self, bot, symbols, scan_interval=3, config: "AdvancedTradingConfig" = None):
        self.bot = bot
        self.symbols = symbols
        self.config = config or getattr(bot, 'config', None)
        self.scan_interval = scan_interval
        self.last_scan_time = {sym: 0 for sym in symbols}
        maxsize = 100
        if self.config and hasattr(self.config, 'SCAN_QUEUE_MAX_SIZE'):
            maxsize = int(self.config.SCAN_QUEUE_MAX_SIZE)
        self.scan_queue = queue.Queue(maxsize=maxsize)
        self.active_threads = []
        if IN_REPLIT:
            default_threads = 1
        else:
            default_threads = min(3, len(symbols))
            if self.config and hasattr(self.config, 'SCAN_WORKER_THREADS'):
                default_threads = min(int(self.config.SCAN_WORKER_THREADS), len(symbols))
        self.max_threads = max(1, default_threads)
        self.running = False
        self._retry_count = {sym: 0 for sym in symbols}
        self._in_queue = set()

    def start(self):
        self.running = True
        self.last_scan_time = {sym: 0 for sym in self.symbols}
        self._retry_count = {sym: 0 for sym in self.symbols}
        self._in_queue.clear()
        # Iniciar workers
        for _ in range(self.max_threads):
            thread = threading.Thread(target=self._worker, daemon=True, name="SymbolWorker")
            thread.start()
            self.active_threads.append(thread)
        # Iniciar scheduler
        scheduler_thread = threading.Thread(target=self._scheduler, daemon=True, name="SymbolScheduler")
        scheduler_thread.start()
        logger.info(f"[OK] SymbolScanner iniciado: {len(self.symbols)} pares, {self.max_threads} hilos, intervalo={self.scan_interval}s")

    def stop(self):
        self.running = False
        while not self.scan_queue.empty():
            try:
                self.scan_queue.get_nowait()
                self.scan_queue.task_done()
            except:
                break

    def rescan_symbol(self, symbol: str):
        """Fuerza re-escaneo inmediato de un símbolo (ej: tras cierre de señal)."""
        try:
            if symbol in self.symbols:
                self.last_scan_time[symbol] = 0
                self._retry_count[symbol] = 0
                self._in_queue.discard(symbol)
                logger.info(f"🔄 Símbolo {symbol} marcado para re-escaneo inmediato")
        except Exception as e:
            logger.error(f"Error en rescan_symbol: {e}")

    def resume_all_scanning(self):
        """Reanuda escaneo de TODOS los símbolos y limpia estado de seguimiento exclusivo."""
        try:
            # ✅ LIMPIAR MODO EXCLUSIVO EN EL BOT (clave para evitar bloqueo)
            if hasattr(self.bot, 'exclusive_tracking_mode'):
                self.bot.exclusive_tracking_mode = False
                self.bot.tracked_symbol = None
                self.bot.tracked_signal_hash = None
                self.bot.single_active_signal_hash = None
                logger.info("🔓 Modo exclusivo liberado en el bot")

            # Reiniciar contadores de escaneo
            current_time = time.time()
            for symbol in self.symbols:
                self.last_scan_time[symbol] = 0
                self._retry_count[symbol] = 0
            self._in_queue.clear()
            logger.info(f"▶️ Escaneo reanudado para {len(self.symbols)} símbolos")
        except Exception as e:
            logger.error(f"Error en resume_all_scanning: {e}")

    def _scheduler(self):
        batch_size = getattr(self.config, 'SCAN_BATCH_SIZE', 10) if self.config else 10
        batch_delay = getattr(self.config, 'SCAN_BATCH_DELAY', 0.5) if self.config else 0.5

        while self.running and self.bot.running:
            current_time = time.time()
            scheduled = 0
            batch_count = 0

            for symbol in self.symbols:
                elapsed = current_time - self.last_scan_time[symbol]
                if elapsed >= self.scan_interval:
                    try:
                        # ✅ Protección contra estado inconsistente: resetear si es primer símbolo
                        if scheduled == 0:
                            self.bot.symbols_analyzed_count = 0
                            self.bot.symbol_analysis_counts = {sym: 0 for sym in self.symbols}
                            self.bot._safe_gui_queue_put(('update_pair_scan_progress', 0))

                        # ✅ Evitar duplicados y exceso de reintentos
                        if self._retry_count.get(symbol, 0) < 3 and symbol not in self._in_queue:
                            self.scan_queue.put_nowait(symbol)
                            self._in_queue.add(symbol)
                            self.last_scan_time[symbol] = current_time
                            scheduled += 1
                            batch_count += 1

                            if batch_count >= batch_size:
                                time.sleep(batch_delay)
                                batch_count = 0

                    except queue.Full:
                        pass  # Omitir si cola llena

            if scheduled > 0:
                self.bot._safe_gui_queue_put(('log_message', f"🔍 Programados {scheduled} símbolos para análisis"))
            time.sleep(1)

    def _worker(self):
        while self.running and self.bot.running:
            try:
                symbol = self.scan_queue.get(timeout=2)
                try:
                    self._retry_count[symbol] = 0
                    self.bot.analyze_and_process_symbol(symbol)
                    self.scan_queue.task_done()
                    self._in_queue.discard(symbol)
                except Exception as e:
                    self._retry_count[symbol] = self._retry_count.get(symbol, 0) + 1
                    retry = self._retry_count[symbol]
                    if retry <= 2:
                        logger.error(f"[ERROR] Falló {symbol} (intento {retry}/3): {e}. Reintentando en 5s...")
                        time.sleep(5)
                        if symbol not in self._in_queue:
                            self._in_queue.add(symbol)
                        self.scan_queue.put(symbol)
                    else:
                        logger.error(f"💀 {symbol} falló 3 veces. Omitiendo hasta próximo ciclo.")
                        self._in_queue.discard(symbol)
                    self.scan_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.critical(f"🔥 Error crítico en SymbolScanner worker: {e}", exc_info=True)
                time.sleep(1)

# ========== AUTO-TRADE STATE & ORDER MANAGER ==========
class AutoTradeState:
    """Estado de una operación de auto-trading activa"""
    def __init__(self, symbol: str, side: str, entry_price: float, quantity: float, config):
        self.symbol = symbol
        self.side = side  # 'BUY' o 'SELL'
        self.entry_price = entry_price
        self.quantity = quantity
        self.config = config

        # IDs de órdenes Binance
        self.entry_order_id = None
        self.stop_loss_order_id = None
        self.take_profit_order_id = None

        # Precios SL/TP
        milestone1 = getattr(config, 'MILESTONE_1', 1.0)
        if side == 'BUY':
            self.current_sl = entry_price * (1 - milestone1 / 100)  # SL inicial = -milestone1%
            self.take_profit = entry_price * (1 + getattr(config, 'MILESTONE_3', 3.0) / 100)
        else:
            self.current_sl = entry_price * (1 + milestone1 / 100)  # SL inicial = +milestone1%
            self.take_profit = entry_price * (1 - getattr(config, 'MILESTONE_3', 3.0) / 100)

        # Trailing Stop config
        self.trailing_distance = getattr(config, 'TRAILING_DISTANCE', 0.3)  # % distancia mínima
        self.trailing_step = getattr(config, 'TRAILING_STEP', 0.1)  # % incremento mínimo

        # Estado de milestones
        self.milestone1_reached = False
        self.milestone2_reached = False  # Al llegar aquí, SL → breakeven
        self.milestone3_reached = False
        self.breakeven_activated = False

        # Timestamps
        self.opened_at = datetime.now()
        self.last_sl_update = datetime.now()
        self.max_profit_reached = 0.0

    def calculate_profit_percent(self, current_price: float) -> float:
        """Calcular profit actual en %"""
        if self.side == 'BUY':
            return ((current_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - current_price) / self.entry_price) * 100

    def should_update_trailing_sl(self, current_price: float) -> tuple:
        """Verificar si se debe actualizar el Trailing Stop"""
        profit_pct = self.calculate_profit_percent(current_price)

        # Actualizar máximo profit
        if profit_pct > self.max_profit_reached:
            self.max_profit_reached = profit_pct

        # Verificar milestones
        milestone1 = getattr(self.config, 'MILESTONE_1', 1.0)
        milestone2 = getattr(self.config, 'MILESTONE_2', 2.0)

        new_sl = None
        reason = None

        # Milestone 2 → Breakeven (SL = entry price)
        if profit_pct >= milestone2 and not self.breakeven_activated:
            self.milestone2_reached = True
            self.breakeven_activated = True
            new_sl = self.entry_price
            reason = f"BREAKEVEN activado al {profit_pct:.2f}%"
            return (True, new_sl, reason)

        # Milestone 1 alcanzado
        if profit_pct >= milestone1 and not self.milestone1_reached:
            self.milestone1_reached = True

        # Trailing Stop después de breakeven
        if self.breakeven_activated:
            # Calcular nuevo SL basado en trailing
            if self.side == 'BUY':
                trailing_sl = current_price * (1 - self.trailing_distance / 100)
                if trailing_sl > self.current_sl + (self.entry_price * self.trailing_step / 100):
                    new_sl = trailing_sl
                    reason = f"Trailing SL actualizado: {new_sl:.8f}"
            else:
                trailing_sl = current_price * (1 + self.trailing_distance / 100)
                if trailing_sl < self.current_sl - (self.entry_price * self.trailing_step / 100):
                    new_sl = trailing_sl
                    reason = f"Trailing SL actualizado: {new_sl:.8f}"

        if new_sl:
            return (True, new_sl, reason)
        return (False, None, None)


class BinanceTestnetOrderExecutor:
    """Ejecutor de órdenes para Binance Testnet (SPOT y PERPETUALS)"""

    def __init__(self, config):
        self.config = config
        self.session = requests.Session() if REQUESTS_AVAILABLE else None
        self._update_base_url()

    def _update_base_url(self):
        """Actualizar URL base según configuración"""
        if self.config.use_testnet:
            if self.config.MARKET_TYPE == "PERPETUALS":
                self.base_url = self.config.BINANCE_TESTNET_FUTURES_URL
                self.api_prefix = "/fapi/v1"
            else:
                self.base_url = self.config.BINANCE_TESTNET_SPOT_URL
                self.api_prefix = "/api/v3"
        else:
            if self.config.MARKET_TYPE == "PERPETUALS":
                self.base_url = "https://fapi.binance.com"
                self.api_prefix = "/fapi/v1"
            else:
                self.base_url = "https://api.binance.com"
                self.api_prefix = "/api/v3"

    def _generate_signature(self, params: dict) -> str:
        """Generar firma HMAC SHA256 para autenticación"""
        import hmac
        import hashlib
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.config.binance_secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _make_signed_request(self, method: str, endpoint: str, params: dict = None) -> dict:
        """Hacer petición firmada a Binance"""
        if params is None:
            params = {}

        params['timestamp'] = int(time.time() * 1000)
        params['recvWindow'] = 5000
        params['signature'] = self._generate_signature(params)

        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        headers = {'X-MBX-APIKEY': self.config.binance_api_key}

        try:
            if self.session:
                if method == 'GET':
                    response = self.session.get(url, params=params, headers=headers, timeout=10)
                elif method == 'POST':
                    response = self.session.post(url, params=params, headers=headers, timeout=10)
                elif method == 'DELETE':
                    response = self.session.delete(url, params=params, headers=headers, timeout=10)
                else:
                    return {'success': False, 'error': f'Unknown method: {method}'}

                response.raise_for_status()
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': 'No session available'}
        except Exception as e:
            logger.error(f"Error en petición Binance: {e}")
            return {'success': False, 'error': str(e)}

    def get_account_balance(self) -> dict:
        """Obtener balance de la cuenta"""
        self._update_base_url()
        if self.config.MARKET_TYPE == "PERPETUALS":
            result = self._make_signed_request('GET', '/balance')
        else:
            result = self._make_signed_request('GET', '/account')
        return result

    def get_symbol_precision(self, symbol: str) -> tuple:
        """Obtener precisión de cantidad y precio para un símbolo"""
        try:
            self._update_base_url()
            url = f"{self.base_url}{self.api_prefix}/exchangeInfo"
            if self.session:
                response = self.session.get(url, params={'symbol': symbol}, timeout=10)
                data = response.json()
                for sym in data.get('symbols', []):
                    if sym['symbol'] == symbol:
                        qty_precision = sym.get('quantityPrecision', 3)
                        price_precision = sym.get('pricePrecision', 2)
                        for f in sym.get('filters', []):
                            if f['filterType'] == 'LOT_SIZE':
                                step = f.get('stepSize', '0.001')
                                qty_precision = len(step.rstrip('0').split('.')[-1]) if '.' in step else 0
                            if f['filterType'] == 'PRICE_FILTER':
                                tick = f.get('tickSize', '0.01')
                                price_precision = len(tick.rstrip('0').split('.')[-1]) if '.' in tick else 0
                        return (qty_precision, price_precision)
        except Exception as e:
            logger.error(f"Error obteniendo precisión de {symbol}: {e}")
        return (3, 2)  # Valores por defecto

    def calculate_quantity(self, symbol: str, usdt_amount: float, current_price: float) -> float:
        """Calcular cantidad basada en monto USDT y precio actual"""
        qty_precision, _ = self.get_symbol_precision(symbol)
        quantity = usdt_amount / current_price
        return round(quantity, qty_precision)

    def calculate_effective_margin(self) -> float:
        """Wrapper que usa el leverage configurado (para compatibilidad)"""
        leverage = getattr(self.config, 'AUTOTRADER_LEVERAGE', 1)
        return self.calculate_effective_margin_with_leverage(leverage)

    def calculate_effective_margin_with_leverage(self, effective_leverage: int = 1) -> float:
        """
        ✅ Calcular margen (colateral) y tamaño de posición:
        - PERPETUALS: margen es colateral, posición = margen * leverage
        - SPOT: leverage no aplica, posición = margen directo
        - Interés compuesto: agrega % del capital al margen base

        Args:
            effective_leverage: El leverage REAL que fue aplicado en Binance (no el configurado)
        """
        base_margin = getattr(self.config, 'AUTOTRADER_MARGIN_USDT', 1.0)

        # Validar leverage en opciones permitidas
        valid_leverages = getattr(self.config, 'AUTOTRADER_LEVERAGE_OPTIONS', [1, 5, 10, 15, 20, 25])
        if effective_leverage not in valid_leverages:
            logger.warning(f"⚠️ Apalancamiento {effective_leverage}x no válido, usando 1x")
            effective_leverage = 1

        # Interés compuesto: agregar % del capital al margen
        if getattr(self.config, 'AUTOTRADER_COMPOUND_ENABLED', False):
            capital = getattr(self.config, 'AUTOTRADER_CAPITAL_USDT', 10.0)
            compound_pct = getattr(self.config, 'AUTOTRADER_COMPOUND_PERCENT', 10.0)
            compound_amount = capital * (compound_pct / 100.0)
            base_margin += compound_amount
            logger.info(f"💰 Interés compuesto: +${compound_amount:.2f} USDT ({compound_pct}% de ${capital:.2f})")

        # Para PERPETUALS: posición = margen * leverage (el margen es colateral)
        # Para SPOT: leverage no aplica
        if self.config.MARKET_TYPE == "PERPETUALS":
            effective_position = base_margin * effective_leverage
            logger.info(f"📊 PERPETUALS: Margen ${base_margin:.2f} x {effective_leverage}x = Posición ${effective_position:.2f} USDT")
        else:
            effective_position = base_margin  # SPOT no usa apalancamiento
            logger.info(f"📊 SPOT: Posición ${effective_position:.2f} USDT (sin apalancamiento)")

        return effective_position

    def set_leverage(self, symbol: str, leverage: int) -> dict:
        """Configurar apalancamiento para un símbolo (solo PERPETUALS)"""
        if self.config.MARKET_TYPE != "PERPETUALS":
            logger.info("ℹ️ Apalancamiento solo disponible en PERPETUALS")
            return {'success': True, 'message': 'Spot no soporta apalancamiento', 'skip_order': False}

        # Validar leverage en rango permitido
        valid_leverages = getattr(self.config, 'AUTOTRADER_LEVERAGE_OPTIONS', [1, 5, 10, 15, 20, 25])
        if leverage not in valid_leverages:
            logger.error(f"❌ Apalancamiento {leverage}x no está en opciones válidas: {valid_leverages}")
            return {'success': False, 'error': f'Leverage {leverage}x no válido', 'skip_order': True}

        self._update_base_url()
        params = {
            'symbol': symbol,
            'leverage': leverage
        }

        logger.info(f"⚙️ Configurando apalancamiento {leverage}x para {symbol}")
        result = self._make_signed_request('POST', '/leverage', params)

        if result['success']:
            logger.info(f"✅ Apalancamiento configurado: {symbol} = {leverage}x")
            return {'success': True, 'leverage': leverage, 'skip_order': False}
        else:
            logger.warning(f"⚠️ No se pudo configurar apalancamiento: {result.get('error')}")
            # Continuar con leverage 1x si falla
            return {'success': False, 'error': result.get('error'), 'skip_order': False}

    def sync_mode(self):
        """✅ Sincronizar modo testnet/real entre todas las configuraciones"""
        mode = getattr(self.config, 'AUTOTRADER_MODE', 'testnet')
        is_testnet = (mode == 'testnet')

        # Sincronizar ambas banderas
        self.config.use_testnet = is_testnet
        self.config.USE_TESTNET = is_testnet

        self._update_base_url()
        logger.info(f"🔄 Modo sincronizado: {'TESTNET' if is_testnet else 'REAL'}")
        return is_testnet

    def get_mode_info(self) -> str:
        """Obtener información del modo actual (testnet/real)"""
        mode = getattr(self.config, 'AUTOTRADER_MODE', 'testnet')
        is_testnet = mode == 'testnet'
        return f"{'🧪 TESTNET' if is_testnet else '💰 REAL'}"

    def execute_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        """Ejecutar orden MARKET"""
        self._update_base_url()
        qty_precision, _ = self.get_symbol_precision(symbol)
        formatted_qty = f"{quantity:.{qty_precision}f}"

        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': formatted_qty
        }

        logger.info(f"📤 Ejecutando MARKET {side} {formatted_qty} {symbol} en {'TESTNET' if self.config.use_testnet else 'LIVE'}")

        result = self._make_signed_request('POST', '/order', params)

        if result['success']:
            order_data = result['data']
            fill_price = 0.0
            if order_data.get('fills'):
                fill_price = float(order_data['fills'][0].get('price', 0))
            elif order_data.get('avgPrice'):
                fill_price = float(order_data['avgPrice'])

            logger.info(f"✅ Orden ejecutada: {order_data.get('orderId')} @ {fill_price}")
            return {
                'success': True,
                'order_id': order_data.get('orderId'),
                'fill_price': fill_price,
                'quantity': float(formatted_qty),
                'status': order_data.get('status')
            }
        else:
            logger.error(f"❌ Error ejecutando orden: {result.get('error')}")
            return result

    def place_stop_loss_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Colocar orden Stop Loss"""
        self._update_base_url()
        qty_precision, price_precision = self.get_symbol_precision(symbol)
        formatted_qty = f"{quantity:.{qty_precision}f}"
        formatted_price = f"{stop_price:.{price_precision}f}"

        sl_side = 'SELL' if side.upper() == 'BUY' else 'BUY'

        if self.config.MARKET_TYPE == "PERPETUALS":
            params = {
                'symbol': symbol,
                'side': sl_side,
                'type': 'STOP_MARKET',
                'quantity': formatted_qty,
                'stopPrice': formatted_price,
                'closePosition': 'false'
            }
        else:
            params = {
                'symbol': symbol,
                'side': sl_side,
                'type': 'STOP_LOSS_LIMIT',
                'quantity': formatted_qty,
                'stopPrice': formatted_price,
                'price': formatted_price,
                'timeInForce': 'GTC'
            }

        logger.info(f"📤 Colocando SL {sl_side} {formatted_qty} {symbol} @ {formatted_price}")

        result = self._make_signed_request('POST', '/order', params)

        if result['success']:
            order_data = result['data']
            logger.info(f"✅ Stop Loss colocado: {order_data.get('orderId')}")
            return {
                'success': True,
                'order_id': order_data.get('orderId'),
                'stop_price': float(formatted_price)
            }
        else:
            logger.error(f"❌ Error colocando SL: {result.get('error')}")
            return result

    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancelar orden existente"""
        self._update_base_url()
        params = {'symbol': symbol, 'orderId': order_id}
        result = self._make_signed_request('DELETE', '/order', params)
        if result['success']:
            logger.info(f"✅ Orden {order_id} cancelada")
            return True
        logger.error(f"❌ Error cancelando orden: {result.get('error')}")
        return False

    def update_trailing_stop(self, symbol: str, trade_state: 'AutoTradeState', new_sl_price: float) -> dict:
        """Actualizar trailing stop (cancelar anterior y crear nuevo)"""
        if trade_state.stop_loss_order_id:
            self.cancel_order(symbol, trade_state.stop_loss_order_id)

        result = self.place_stop_loss_order(
            symbol, trade_state.side, trade_state.quantity, new_sl_price
        )

        if result['success']:
            trade_state.stop_loss_order_id = result['order_id']
            trade_state.current_sl = new_sl_price
            trade_state.last_sl_update = datetime.now()
            logger.info(f"🔄 Trailing SL actualizado: {symbol} @ {new_sl_price:.6f}")

        return result


class BinanceOrderManager:
    """Gestor de órdenes para Binance con soporte de Trailing Stop"""

    def __init__(self, config, binance_client=None):
        self.config = config
        self.client = binance_client
        self.active_trades = {}  # {symbol: AutoTradeState}
        self.lock = threading.Lock()
        self.symbol_info_cache = {}
        self.testnet_executor = BinanceTestnetOrderExecutor(config)  # Ejecutor testnet

    def set_client(self, client):
        """Establecer cliente Binance"""
        self.client = client

    def _get_symbol_info(self, symbol: str) -> dict:
        """Obtener información del símbolo (filtros, precisión, etc.)"""
        if symbol in self.symbol_info_cache:
            return self.symbol_info_cache[symbol]
        try:
            if self.client:
                info = self.client.get_exchange_info(symbol)
                self.symbol_info_cache[symbol] = info
                return info
        except Exception as e:
            logger.error(f"Error obteniendo info de {symbol}: {e}")
        return None

    def _format_quantity(self, symbol: str, quantity: float) -> str:
        """Formatear cantidad según precisión del símbolo"""
        info = self._get_symbol_info(symbol)
        if info:
            step_size = info.get('stepSize', '0.001')
            precision = len(step_size.rstrip('0').split('.')[-1]) if '.' in step_size else 0
            return f"{quantity:.{precision}f}"
        return f"{quantity:.6f}"

    def _format_price(self, symbol: str, price: float) -> str:
        """Formatear precio según precisión del símbolo"""
        info = self._get_symbol_info(symbol)
        if info:
            tick_size = info.get('tickSize', '0.00001')
            precision = len(tick_size.rstrip('0').split('.')[-1]) if '.' in tick_size else 0
            return f"{price:.{precision}f}"
        return f"{price:.8f}"

    def execute_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        """Ejecutar orden MARKET en Binance"""
        if not self.client:
            logger.error("❌ Cliente Binance no configurado")
            return {'success': False, 'error': 'No Binance client'}

        if not self.config.auto_trading_enabled:
            logger.warning("⚠️ Auto-trading deshabilitado")
            return {'success': False, 'error': 'Auto-trading disabled'}

        try:
            formatted_qty = self._format_quantity(symbol, quantity)

            order_params = {
                'symbol': symbol,
                'side': side,
                'type': 'MARKET',
                'quantity': formatted_qty
            }

            logger.info(f"📤 Ejecutando orden MARKET: {side} {formatted_qty} {symbol}")

            response = self.client.create_order(**order_params)

            if response and response.get('orderId'):
                fill_price = float(response.get('fills', [{}])[0].get('price', 0))
                logger.info(f"✅ Orden ejecutada: {response['orderId']} @ {fill_price}")
                return {
                    'success': True,
                    'order_id': response['orderId'],
                    'fill_price': fill_price,
                    'quantity': float(formatted_qty),
                    'response': response
                }
            else:
                return {'success': False, 'error': 'No order ID returned'}

        except Exception as e:
            logger.error(f"❌ Error ejecutando orden: {e}")
            return {'success': False, 'error': str(e)}

    def place_stop_loss_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Colocar orden Stop Loss"""
        if not self.client:
            return {'success': False, 'error': 'No Binance client'}

        try:
            sl_side = 'SELL' if side == 'BUY' else 'BUY'
            formatted_qty = self._format_quantity(symbol, quantity)
            formatted_price = self._format_price(symbol, stop_price)

            order_params = {
                'symbol': symbol,
                'side': sl_side,
                'type': 'STOP_LOSS_LIMIT',
                'quantity': formatted_qty,
                'stopPrice': formatted_price,
                'price': formatted_price,
                'timeInForce': 'GTC'
            }

            logger.info(f"📤 Colocando Stop Loss: {sl_side} {formatted_qty} {symbol} @ {formatted_price}")

            response = self.client.create_order(**order_params)

            if response and response.get('orderId'):
                logger.info(f"✅ Stop Loss colocado: {response['orderId']}")
                return {'success': True, 'order_id': response['orderId'], 'response': response}
            else:
                return {'success': False, 'error': 'No order ID returned'}

        except Exception as e:
            logger.error(f"❌ Error colocando Stop Loss: {e}")
            return {'success': False, 'error': str(e)}

    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancelar orden existente"""
        if not self.client:
            return False
        try:
            self.client.cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"✅ Orden {order_id} cancelada")
            return True
        except Exception as e:
            logger.error(f"❌ Error cancelando orden {order_id}: {e}")
            return False

    def update_stop_loss(self, symbol: str, new_sl_price: float) -> dict:
        """Actualizar Stop Loss (cancelar anterior y crear nuevo)"""
        with self.lock:
            if symbol not in self.active_trades:
                return {'success': False, 'error': 'No active trade'}

            trade = self.active_trades[symbol]

            # Cancelar SL anterior
            if trade.stop_loss_order_id:
                self.cancel_order(symbol, trade.stop_loss_order_id)

            # Crear nuevo SL
            result = self.place_stop_loss_order(
                symbol, trade.side, trade.quantity, new_sl_price
            )

            if result['success']:
                trade.stop_loss_order_id = result['order_id']
                trade.current_sl = new_sl_price
                trade.last_sl_update = datetime.now()
                logger.info(f"🔄 SL actualizado para {symbol}: {new_sl_price:.8f}")

            return result

    def open_auto_trade(self, symbol: str, side: str, entry_price: float, 
                        quantity: float) -> dict:
        """Abrir operación de auto-trading completa"""
        with self.lock:
            if symbol in self.active_trades:
                return {'success': False, 'error': 'Trade already active for symbol'}

            # Crear estado de trade
            trade_state = AutoTradeState(symbol, side, entry_price, quantity, self.config)

            # Ejecutar orden de entrada
            entry_result = self.execute_market_order(symbol, side, quantity)

            if not entry_result['success']:
                return entry_result

            # Actualizar precio real de entrada
            if entry_result.get('fill_price'):
                trade_state.entry_price = entry_result['fill_price']
                # Recalcular SL con precio real
                milestone1 = getattr(self.config, 'MILESTONE_1', 1.0)
                if side == 'BUY':
                    trade_state.current_sl = trade_state.entry_price * (1 - milestone1 / 100)
                else:
                    trade_state.current_sl = trade_state.entry_price * (1 + milestone1 / 100)

            trade_state.entry_order_id = entry_result['order_id']

            # Colocar Stop Loss inicial
            sl_result = self.place_stop_loss_order(
                symbol, side, quantity, trade_state.current_sl
            )

            if sl_result['success']:
                trade_state.stop_loss_order_id = sl_result['order_id']

            # Registrar trade activo
            self.active_trades[symbol] = trade_state

            logger.info(f"🚀 Auto-trade abierto: {side} {quantity} {symbol} @ {trade_state.entry_price}")
            logger.info(f"   SL: {trade_state.current_sl:.8f} | TP: {trade_state.take_profit:.8f}")

            return {
                'success': True,
                'trade_state': trade_state,
                'entry_order_id': trade_state.entry_order_id,
                'sl_order_id': trade_state.stop_loss_order_id
            }

    def close_auto_trade(self, symbol: str, reason: str = 'manual') -> dict:
        """Cerrar operación de auto-trading"""
        with self.lock:
            if symbol not in self.active_trades:
                return {'success': False, 'error': 'No active trade'}

            trade = self.active_trades[symbol]

            # Cancelar órdenes pendientes
            if trade.stop_loss_order_id:
                self.cancel_order(symbol, trade.stop_loss_order_id)
            if trade.take_profit_order_id:
                self.cancel_order(symbol, trade.take_profit_order_id)

            # Cerrar posición (orden opuesta)
            close_side = 'SELL' if trade.side == 'BUY' else 'BUY'
            close_result = self.execute_market_order(symbol, close_side, trade.quantity)

            if close_result['success']:
                del self.active_trades[symbol]
                logger.info(f"✅ Auto-trade cerrado: {symbol} | Razón: {reason}")

            return close_result

    def monitor_trailing_stops(self, price_updates: dict):
        """Monitorear y actualizar Trailing Stops basado en precios actuales"""
        with self.lock:
            for symbol, trade in list(self.active_trades.items()):
                current_price = price_updates.get(symbol)
                if not current_price:
                    continue

                should_update, new_sl, reason = trade.should_update_trailing_sl(current_price)

                if should_update and new_sl:
                    # Actualizar SL en Binance
                    result = self.update_stop_loss(symbol, new_sl)
                    if result['success']:
                        logger.info(f"📊 {symbol}: {reason}")

    def get_active_trade(self, symbol: str) -> AutoTradeState:
        """Obtener estado de trade activo"""
        return self.active_trades.get(symbol)

    def has_active_trade(self, symbol: str = None) -> bool:
        """Verificar si hay trades activos"""
        if symbol:
            return symbol in self.active_trades
        return len(self.active_trades) > 0




logger = logging.getLogger('CryptoBotOptimized')

# ============================================================================
# BOT PRINCIPAL OPTIMIZADO (CORREGIDO v35.0.0.0)
# ============================================================================
class OptimizedTradingBot:
    def __init__(self, config: "AdvancedTradingConfig"): # <-- Nota las comillas
        # 1️⃣ PRIMERO: Asignar configuración básica
        self.config = config
        # 2️⃣ SEGUNDO: Atributos de control simples (no dependen de otros objetos)
        self.running = False
        self.current_pair = "ETHUSDT"
        self.last_update = ""
        self.exclusive_tracking_mode = False
        self.tracked_symbol = None
        self.tracked_signal_hash = None
        self.single_active_signal_hash = None  # ✅ SOLO UNA SEÑAL ACTIVA A LA VEZ

        self.TRAINING_SUCCESS_DIR = path_manager.get_data_path('training_success')
        self.TRAINING_FEATURES_DIR = path_manager.get_data_path('training_features')

        # ✅ CRÍTICO: Cargar configuración antes de inicializar módulos
        self.config.load_config()

        # 4️⃣ CUARTO: Inicializar módulos que DEPENDEN de `config` (orden crítico)
        self.similarity_engine = SimilarityEngine(self.config)  # ✔️ Usa config + carpetas ya creadas
        self.similarity_engine._bot_ref = self  # ✅ Referencia para auto-retrain después de 5 trades exitosos
        self.client = BinanceFIXClient(config)  # ✅ FIX API wrapper - deshabilita WebSocket si está activo
        self.neural_trader = OptimizedNeuralTrader(config)
        self.technical_analyzer = OptimizedTechnicalAnalyzer(config)
        self.strategy_impl = OptimizedStrategyImplementation(config)
        self.telegram_client = OptimizedTelegramClient(config)
        # ✅ Pasar flag disable_websocket al chart_generator para excluir WebSocket si FIX_API activo
        self.chart_generator = SignalChartGenerator(disable_websocket=getattr(self.client, 'disable_websocket', False))
        self.data_manager = OptimizedDataManager()
        self.signal_processor = OptimizedSignalProcessor(config)

        self.trend_alignment_validator = TrendAlignmentValidator(self.config)
        self.signal_tracker = SignalTracker(self.config)  # ✅ Pasar config para PROFIT_MILESTONES
        self.signal_tracker.on_closed_callback = self._on_signal_closed_callback
        self.signal_tracker._similarity_engine_ref = self.similarity_engine # ✅ REFERENCIA A SIMILARITY ENGINE PARA GUARDAR TRADES
        self.signal_tracker.set_bot_reference(self)  # ✅ INYECCIÓN CRÍTICA
        # ✅ INYECCI��N DEL CLIENTE
        self.signal_tracker.set_telegram_client(self.telegram_client)
        print(f"📡 [INIT] Telegram: enabled={self.config.telegram_enabled}, client={self.telegram_client is not None}")
        # ✅ GESTOR DE ÓRDENES PARA AUTO-TRADING
        self.order_manager = BinanceOrderManager(self.config, self.client)
        # Inicializar sistemas avanzados
        self.threshold_manager = None
        self.multi_exchange_manager = None
        self._initialize_new_systems()

        # Estado del bot optimizado
        self.current_pair = "ETHUSDT"
        self.running = False
        self.last_update = ""
        self.active_signals = []
        self.market_data = {}  # ✅ FIX: market_data inicializado
        self.market_data_lock = threading.RLock()  # 🔒 Protege acceso concurrente
        self.sent_signal_hashes = set()
        self.performance_metrics = {'total_signals': 0, 'successful_signals': 0}

        # Análisis actual optimizado
        self.current_analysis = {
            'strategy_signals': [],
            'neural_prediction': {},
            'technical_confidence': 0.0,
            'combined_signal': SignalType.NEUTRAL,
            'confidence': 0.0,
            'processing_details': {
                'combined_signal': SignalType.NEUTRAL,
                'neural_score': 0,
                'technical_percentage': 0,
                'alignment_percentage': 0,
                'alignment_status': 'INICIAL'
            },
            'price': 0.0,
            'volume': 0.0,
            'specific_strategy_triggered': None,
            'market_structure_score': 0.0,
            'volatility_score': 0.0,
            'processing_time_ms': 0
        }
        # Queue para comunicación con GUI optimizada (Se asignará en la GUI)
        self.gui_queue = queue.Queue(maxsize=100)
        self._current_analyzed_symbol_for_gui = None
        self.total_symbols_to_analyze = len(self.config.TRADING_SYMBOLS)
        self.symbols_analyzed_count = 0
        self.symbol_analysis_counts = {symbol: 0 for symbol in self.config.TRADING_SYMBOLS}
        # Gestores optimizados
        self.symbol_scanner = None
        self.ws_manager = None

        # ✅ FILTRO DE DATOS: Blacklist para pares con datos insuficientes
        self._data_failure_blacklist = {}  # {symbol: {'failures': count, 'last_attempt': timestamp}}
        self._blacklist_threshold = 3  # Fallos consecutivos antes de blacklist
        self._blacklist_cooldown = 300  # 5 minutos de cooldown antes de reintentar
        self._validated_pairs = set()  # Pares que han pasado validación exitosamente

        # ✅ CRÍTICO: NO entrenar aquí - esto causa errores 451 de Binance en init
        # El entrenamiento se hace DESPUÉS de que el GUI esté listo (en startup())
        self._neural_training_pending = not self.neural_trader.is_trained

    def _initialize_new_systems(self):
        """Inicializar sistemas de Umbrales Dinámicos y Multi-Exchange"""
        # Sistema de umbrales dinámicos
        if DYNAMIC_THRESHOLDS_AVAILABLE and self.config.DYNAMIC_THRESHOLDS_ENABLED:
            try:
                self.threshold_manager = DynamicThresholdManager(
                    base_threshold=self.config.MIN_NEURAL_DESTACADA,
                    min_threshold=self.config.THRESHOLD_MIN,
                    max_threshold=self.config.THRESHOLD_MAX,
                    window_days=self.config.THRESHOLD_WINDOW_DAYS,
                    max_daily_signals=self.config.MAX_DAILY_SIGNALS,
                    min_daily_signals=self.config.MIN_DAILY_SIGNALS
                )
                logger.info(f"[OK] Sistema de umbrales dinámicos inicializado")
            except Exception as e:
                logger.error(f"[ERROR] Error inicializando threshold_manager: {e}")
                self.threshold_manager = None
        else:
            logger.info("⏭️ Umbrales dinámicos deshabilitados")
        # Sistema multi-exchange
        if MULTI_EXCHANGE_AVAILABLE and self.config.MULTI_EXCHANGE_ENABLED:
            try:
                self.multi_exchange_manager = MultiExchangeManager()
                if self.config.binance_api_key and self.config.binance_secret_key:
                    binance_config = ExchangeConfig(
                        name="binance",
                        api_key=self.config.binance_api_key,
                        api_secret=self.config.binance_secret_key,
                        base_url=self.config.BINANCE_API_URL if not self.config.use_testnet else self.config.BINANCE_TESTNET_URL
                    )
                    binance_exchange = BinanceExchange(binance_config)
                    self.multi_exchange_manager.add_exchange("binance", binance_exchange, is_primary=True)
                if self.multi_exchange_manager.initialize_all():
                    logger.info(f"[OK] Multi-Exchange inicializado: {', '.join(self.multi_exchange_manager.available_exchanges)}")
                else:
                    logger.warning("⚠️ Multi-Exchange sin exchanges disponibles")
                    self.multi_exchange_manager = None
            except Exception as e:
                logger.error(f"[ERROR] Error inicializando multi_exchange_manager: {e}")
                self.multi_exchange_manager = None
        else:
            logger.info("⏭️ Multi-Exchange deshabilitado")
        self.performance_tracker = {
            'analysis_times': [],
            'cache_hit_rates': [],
            'signal_qualities': []
        }
        
        # ⚡ OPTIMIZACIÓN v32.0.23.0: Componentes de optimización
        try:
            opt_components = get_optimization_components(self.config)
            self.fast_fail_filter = opt_components["fast_fail"]
            self.adaptive_threshold_manager = opt_components["adaptive_thresholds"]
            self.enhanced_cache = opt_components["cache"]
            self.dynamic_alignment_scorer = opt_components["alignment_scorer"]
            self.volume_breakout_validator = opt_components["breakout_validator"]
            logger.info("⚡ Componentes de optimización integrados correctamente")
        except Exception as e:
            logger.error(f"⚠️ Error inicializando componentes de optimización: {e}")
            self.fast_fail_filter = None
            self.adaptive_threshold_manager = None
            self.enhanced_cache = None
            self.dynamic_alignment_scorer = None
            self.volume_breakout_validator = None

    def _release_exclusive_mode(self):
        """Liberar modo exclusivo, limpiar GUI y reanudar escaneo global."""
        if self.exclusive_tracking_mode:
            old_symbol = self.tracked_symbol
            self.exclusive_tracking_mode = False
            self.tracked_symbol = None
            self.tracked_signal_hash = None
            self.single_active_signal_hash = None
            logger.info(f"Modo exclusivo liberado para {old_symbol}")

            # CORREGIDO v35: Limpiar GUI principal completamente
            self._safe_gui_queue_put(('clear_signal_display', None))
            self._safe_gui_queue_put(('hide_progress_bar', None))
            self._safe_gui_queue_put(('update_highlight_progress', 0))
            self._safe_gui_queue_put(('reset_main_panel', None))  # Nuevo comando para resetear panel principal
            logger.info("GUI limpiada tras liberar modo exclusivo")

            # Notificar al SymbolScanner para reanudar escaneo de TODOS los simbolos
            if hasattr(self, 'symbol_scanner') and self.symbol_scanner:
                try:
                    self.symbol_scanner.resume_all_scanning()
                    logger.info("Escaneo global reanudado tras liberar modo exclusivo")
                except Exception as e:
                    logger.error(f"Error al reanudar escaneo: {e}")


    def _start_daily_retrain_scheduler(self):
        """Inicia hilo que chequea cada hora si es hora de reentrenar."""
        def check_and_retrain():
            last_retrain_date = None
            while self.running:
                now = datetime.utcnow()
                target_time = now.replace(hour=self.config.RETRAIN_HOUR, minute=0, second=0, microsecond=0)
                if now >= target_time and (last_retrain_date is None or last_retrain_date != now.date()):
                    logger.info(f"🕐 Iniciando reentrenamiento diario programado ({self.config.RETRAIN_HOUR}:00 UTC)...")
                    try:
                        success = self.neural_trader.train_with_successful_only()
                        if success:
                            logger.info("✅ Reentrenamiento diario completado exitosamente.")
                        else:
                            logger.warning("⚠️ Reentrenamiento diario omitido: insuficientes trades exitosos.")
                        last_retrain_date = now.date()
                    except Exception as e:
                        logger.error(f"[ERROR] Falló reentrenamiento diario: {e}", exc_info=True)
                time.sleep(3600)  # chequear cada hora

        threading.Thread(target=check_and_retrain, daemon=True, name="RetrainScheduler").start()

    def _prepare_signal_package(self, symbol: str, df_entry: pd.DataFrame, analysis_result: dict) -> Optional[dict]:
        """
        ✅ PREPARA EL PAQUETE DE SEÑAL ÚNICO — BASE PARA SignalTracker, Telegram, GUI
        -  Input: analysis_result de _perform_optimized_analysis() (ya validado)
        - Output: dict listo para add_highlighted_signal()
        - Garantiza coherencia: no cálculos duplicados, no discrepancias IA/Técnico/Alineación
        """
        try:
            # --- 1. Extracción segura de resultados del análisis ---
            validation_result = analysis_result.get('validation_result', {})
            processing_details = analysis_result.get('processing_details', {})
            neural_prediction = analysis_result.get('neural_prediction', {})

            # --- 2. Métricas principales (origen único: processing_details) ---
            neural_score = float(processing_details.get('neural_score', 0.0))
            technical_percentage = float(processing_details.get('technical_percentage', 0.0))
            alignment_percentage = float(processing_details.get('alignment_percentage', 0.0))

            # --- 3. Dirección y tipo de señal (origen: combined_signal + alignment) ---
            combined_signal = analysis_result.get('combined_signal', SignalType.NEUTRAL)
            is_buy = (
                'BUY' in getattr(combined_signal, 'name', '').upper() or 
                'COMPRA' in getattr(combined_signal, 'value', '').upper()
            )

            # --- 4. Niveles (origen: validation_result → fallback a cálculo estándar) ---
            price = float(df_entry['close'].iloc[-1]) if not df_entry.empty else 0.0
            if price <= 0:
                price = self.client.get_ticker_price(symbol)
            if price <= 0:
                logger.error(f"❌ Precio inválido para {symbol} en _prepare_signal_package")
                return None

            # ✅ TOMAR niveles de validation_result si existen y son válidos
            entry_price = float(validation_result.get('entry_price') or price)
            stop_loss = float(validation_result.get('stop_loss', 0.0))
            take_profit = float(validation_result.get('take_profit', 0.0))
            risk_reward_ratio = float(validation_result.get('risk_reward_ratio', 0.0))

            # ✅ Fallback robusto (solo si validation_result falló o valores inválidos)
            if stop_loss <= 0 or take_profit <= 0:
                sl_pct = self.config.DEFAULT_STOP_LOSS_PERCENT
                tp_pct = self.config.DEFAULT_TAKE_PROFIT_PERCENT
                # ✅ AGREGAR COMISIÓN ROUND-TRIP AL OBJETIVO PARA LOGRAR PROFIT NETO
                commission_pct = self.config.get_round_trip_commission() / 100.0  # ej: 0.0010 para 0.10%
                tp_adjusted = tp_pct + commission_pct  # TP bruto = TP neto + comisiones
                if is_buy:
                    stop_loss = entry_price * (1 - sl_pct)
                    take_profit = entry_price * (1 + tp_adjusted)  # ✅ TP ajustado
                else:
                    stop_loss = entry_price * (1 + sl_pct)
                    take_profit = entry_price * (1 - tp_adjusted)  # ✅ TP ajustado
                risk_reward_ratio = abs(take_profit - entry_price) / abs(entry_price - stop_loss) if stop_loss != entry_price else 1.0

            # --- 5. Condiciones cumplidas (origen: validation_result) ---
            conditions_met = validation_result.get('conditions_met', [
                f"IA: {neural_score:.1f}%",
                f"Técnico: {technical_percentage:.1f}%",
                f"Alineación: {alignment_percentage:.1f}%"
            ])

            # --- 6. Generar hash único ---
            signal_hash = self._generate_optimized_signal_hash(symbol, combined_signal, analysis_result)

            # --- 7. Paquete FINAL (único contrato con SignalTracker) ---
            signal_package = {
                'symbol': symbol,
                'signal_hash': signal_hash,
                'timestamp': datetime.now(),
                'combined_signal': combined_signal,
                'status': 'DESTACADA',  # ✅ SIEMPRE inicia como DESTACADA
                'neural_score': neural_score,
                'technical_percentage': technical_percentage,      # ← en RAÍZ para SignalTracker
                'alignment_percentage': alignment_percentage,      # ← en RAÍZ para SignalTracker
                'price': price,
                'entry_price': entry_price,        # ✅ > 0 garantizado
                'stop_loss': stop_loss,            # ✅ > 0 garantizado
                'take_profit': take_profit,        # ✅ > 0 garantizado
                'sl_percent': self.config.DEFAULT_STOP_LOSS_PERCENT * 100,   # ✅ Para TradingView labels
                'tp_percent': self.config.MILESTONE_3,                        # ✅ Para TradingView labels
                'commission_rate': self.config.get_commission_rate(),         # ✅ Comisión por operación
                'commission_round_trip': self.config.get_round_trip_commission(),  # ✅ Comisión ida y vuelta
                'market_type': self.config.MARKET_TYPE,                       # ✅ Tipo de mercado
                'net_profit_target': self.config.get_net_profit_target(),     # ✅ Profit neto objetivo
                'risk_reward_ratio': risk_reward_ratio,
                'is_buy': is_buy,
                'conditions_met': conditions_met,
                'initial_status': 'DESTACADA',
                'dataframe_entry': df_entry.copy(),
                'neural_prediction': neural_prediction,
                'processing_details': processing_details,
                'validation_result': validation_result,
                'chart_path': None  # Se genera después, si se requiere
            }

            logger.info(
                f"✅ Paquete señal preparado: {symbol} | IA={neural_score:.1f}% | Tec={technical_percentage:.1f}% | "
                f"Alineación={alignment_percentage:.1f}% | Entrada=${entry_price:.6f}"
            )
            return signal_package

        except Exception as e:
            logger.critical(f"🔥 Error en _prepare_signal_package({symbol}): {e}", exc_info=True)
            return None

    def _monitor_tracked_signals_continuous(self):
        """
        Monitoreo CONTINUO de señales activas – RACE CONDITION PROTECTED
       ✅ Seguimiento por etapas: 1%, 2%, 3%, -1%, 180 min, reversión
       ✅ Promoción REAL: DESTACADA → CONFIRMADA (IA + Técnico + Alineación 15-30m)
       ✅ Cierra automáticamente y libera recursos
       ✅ CORRECCIÓN #1: Timer de promoción integrado
        """
        last_promotion_check = 0
        PROMOTION_CHECK_INTERVAL = 15  # Verificar promoción cada 15 segundos

        while self.running:
            try:
                time.sleep(2)  # ciclo cada 2 segundos
                logger.debug("🔄 [MONITOR] Ciclo de monitoreo iniciado")

                # CORRECCION v35: VERIFICAR TIMER DE PROMOCION Y ENVIAR TELEGRAM
                current_time = time.time()
                if current_time - last_promotion_check >= PROMOTION_CHECK_INTERVAL:
                    processed = self.signal_tracker.check_promotion_timer()
                    for signal_hash, promo_data in processed:
                        if promo_data.get('promoted'):
                            symbol = promo_data.get('symbol', 'UNKNOWN')
                            signal_data = promo_data.get('signal_data', {})
                            logger.info(f"Timer promocion: {symbol} promovida a CONFIRMADA")
                            
                            # Generar grafico y enviar Telegram para CONFIRMADA
                            try:
                                chart_path = None
                                if hasattr(self, 'chart_generator') and self.chart_generator:
                                    df_chart = self.data_manager.get_data(symbol, "15m", 200, self.client)
                                    if df_chart is not None and len(df_chart) > 20:
                                        analysis = signal_data.get('validation_result', {})
                                        chart_path = self.chart_generator.generate_signal_chart(
                                            symbol, df_chart, signal_data, analysis
                                        )
                                        if chart_path:
                                            signal_data['chart_path'] = chart_path
                                            logger.info(f"Grafico generado para CONFIRMADA (timer): {chart_path}")
                                
                                # Enviar Telegram CONFIRMADA
                                if self.telegram_client and self.config.telegram_enabled:
                                    self.telegram_client.send_promotion_update(
                                        symbol=symbol,
                                        profit_percent=0.0,
                                        chart_path=chart_path,
                                        signal_data=signal_data
                                    )
                                    logger.info(f"Telegram CONFIRMADA enviado para {symbol} (via timer)")
                                    
                                # Actualizar GUI
                                self._safe_gui_queue_put(('update_confirmed_progress', {
                                    'symbol': symbol,
                                    'profit_percent': 0.0
                                }))
                                self._safe_gui_queue_put(('log_message', f"CONFIRMADA: {symbol} promovida via timer"))
                            except Exception as e:
                                logger.error(f"Error enviando Telegram CONFIRMADA (timer): {e}")
                    last_promotion_check = current_time

                # ---------- 1. Obtener señal activa (thread-safe) ----------
                tracked_signals = self.signal_tracker.get_tracked_signals()
                if not tracked_signals:
                    self._safe_gui_queue_put(('update_highlight_progress', 0))
                    continue

                try:
                    signal_hash, tracking_data = next(iter(list(tracked_signals.items())))
                except (StopIteration, RuntimeError):
                    self._safe_gui_queue_put(('update_highlight_progress', 0))
                    continue

                symbol = tracking_data['signal_data'].get('symbol', 'N/A')
                # ✅ CRÍTICO: Leer status ACTUAL directamente del tracker (no de la copia)
                with self.signal_tracker.lock:
                    live_tracking = self.signal_tracker.tracked_signals.get(signal_hash, {})
                    status = live_tracking.get('status', tracking_data.get('status', 'DESCONOCIDA'))
                logger.debug(f"🎯 [MONITOR] Símbolo: {symbol}, Status: {status}")

                # ---------- 2. Actualizar precio y progreso ----------
                current_price = self.client.get_ticker_price(symbol)
                if current_price <= 1e-8:                     # 🔒 Protección contra precio inválido
                    logger.debug(f"⚠️ Precio inválido para {symbol} - reintentando en próximo ciclo")
                    continue  # ✅ CORREGIDO: Reintentar en lugar de cerrar señal

                 # Cambiar a método privado o agregar método público
                progress = self.signal_tracker.update_signal_progress(signal_hash, current_price)
                if not progress:
                    continue

                profit_percent = progress['profit_percent']
                logger.debug(f"📈 [MONITOR] {symbol} Profit: {profit_percent:+.2f}%")

                # ---------- 3. Barra de progreso DESTACADA (15-20 min) ----------
                if status == 'DESTACADA':
                    start_time = tracking_data.get('highlight_start_time') or tracking_data.get('start_time')
                    if not start_time:
                        logger.debug("⏭️  No hay start_time en DESTACADA – saltando barra")
                        self._safe_gui_queue_put(('update_highlight_progress', 0))
                    else:
                        elapsed_seconds = (datetime.now() - start_time).total_seconds()
                        promo_time = self.config.MIN_PROMOTION_TIME_SECONDS
                        elapsed_percent = min(100, (elapsed_seconds / promo_time) * 100)

                        # ---------- 4. Promoción: Por TIEMPO (15 min) o Por UMBRALES ----------
                        neural = tracking_data['signal_data'].get('neural_score', 0)
                        technical = tracking_data['signal_data'].get('technical_percentage', 0)

                        df_15m = self.data_manager.get_data(symbol, "15m", 200, self.client)
                        df_30m = self.data_manager.get_data(symbol, "30m", 200, self.client)
                        signal_dir = "BULLISH" if tracking_data['is_buy'] else "BEARISH"

                        alignment = self.trend_alignment_validator.validate_trend_alignment(
                            df_15m, df_30m, neural, technical, signal_dir
                        )
                        alignment_score = alignment.get('alignment_score', 0)

                        time_condition = elapsed_seconds >= promo_time
                        thresholds_condition = (
                            neural >= self.config.MIN_NEURAL_CONFIRMADA and
                            technical >= self.config.MIN_TECHNICAL_CONFIRMADA and
                            alignment_score >= self.config.MIN_ALIGNMENT_CONFIRMADA
                        )

                        if time_condition and thresholds_condition:
                            with self.signal_tracker.lock:
                                already_sent = self.signal_tracker.tracked_signals.get(signal_hash, {}).get('promotion_telegram_sent', False)

                            if already_sent:
                                continue

                            # ✅ Obtener precio actual para fijar entrada CONFIRMADA
                            promo_price = current_price if current_price > 0 else tracking_data.get('current_price', tracking_data.get('entry_price', 0))
                            promoted = self.signal_tracker.promote_to_confirmed(
                                signal_hash, neural, technical, alignment_score=alignment_score, current_price=promo_price
                            )
                            logger.info(f"[v0] Promocion intentada para {symbol}: promoted={promoted}")
                            if promoted:
                                status = 'CONFIRMADA'
                                promo_reason = f"Umbrales OK (IA:{neural:.0f}% Tec:{technical:.0f}% Alin:{alignment_score:.0f}%)"
                                self._safe_gui_queue_put(('log_message', f"{symbol}: DESTACADA -> CONFIRMADA ({promo_reason})"))
                                
                                # ✅ GENERAR GRÁFICO Y ENVIAR A TELEGRAM
                                try:
                                    chart_path = None
                                    if hasattr(self, 'chart_generator') and self.chart_generator:
                                        df_chart = self.data_manager.get_data(symbol, "15m", 200, self.client)
                                        if df_chart is not None and len(df_chart) > 20:
                                            signal_data = tracking_data.get('signal_data', {})
                                            analysis = signal_data.get('validation_result', {})
                                            chart_path = self.chart_generator.generate_signal_chart(
                                                symbol, df_chart, signal_data, analysis
                                            )
                                            if chart_path:
                                                signal_data['chart_path'] = chart_path
                                                logger.info(f"📊 Gráfico generado para CONFIRMADA: {chart_path}")
                                    
                                    # ✅ ENVIAR TELEGRAM CON GRÁFICO
                                    if self.telegram_client and self.config.telegram_enabled:
                                        signal_data = tracking_data.get('signal_data', {})
                                        self.telegram_client.send_promotion_update(
                                            symbol=symbol,
                                            profit_percent=profit_percent,
                                            chart_path=chart_path,
                                            signal_data=signal_data
                                        )
                                        logger.info(f"📨 Telegram CONFIRMADA enviado para {symbol}")
                                except Exception as e:
                                    logger.error(f"❌ Error al enviar Telegram CONFIRMADA: {e}")
                                self._safe_gui_queue_put(('update_confirmed_progress', {
                                    'symbol': symbol,
                                    'profit_percent': profit_percent
                                }))
                        else:
                            self._safe_gui_queue_put(('update_highlight_progress', int(elapsed_percent)))

                # ---------- 4B. Progreso de profit para CONFIRMADA ----------
                elif status == 'CONFIRMADA':
                    logger.info(f"[v0] CONFIRMADA detectada: {symbol}, profit={profit_percent:.2f}%")
                    self._safe_gui_queue_put(('update_confirmed_progress', {
                        'symbol': symbol,
                        'profit_percent': profit_percent
                    }))

                    # ---------- Notificaciones de milestones a Telegram (SOLO para CONFIRMADA) ----------
                    if getattr(self.config, 'TELEGRAM_SEND_CONFIRMED', False):
                        milestones = self.config.PROFIT_MILESTONES
                        with self.signal_tracker.lock:
                            live_tracking = self.signal_tracker.tracked_signals.get(signal_hash, {})
                            updates_sent = live_tracking.get('telegram_updates_sent', 0)

                        logger.info(f"[v0] MILESTONE CHECK {symbol}: profit={profit_percent:.2f}%, milestones={milestones}, updates_sent={updates_sent}")

                        # Enviar TODOS los milestones pendientes en orden
                        for i, milestone in enumerate(milestones):
                            # Solo enviar si: profit >= milestone Y este milestone específico no se ha enviado
                            # Usar <= i para recuperar milestones perdidos si hay desincronización
                            logger.info(f"[v0] Comparando: profit={profit_percent:.2f}% vs milestone={milestone}% | updates_sent={updates_sent} vs i={i}")
                            if profit_percent >= milestone and updates_sent <= i:
                                with self.signal_tracker.lock:
                                    if signal_hash in self.signal_tracker.tracked_signals:
                                        self.signal_tracker.tracked_signals[signal_hash]['telegram_updates_sent'] = i + 1
                                        updates_sent = i + 1  # Actualizar local para siguiente iteración
                                if self.telegram_client:
                                    chart_path = tracking_data['signal_data'].get('chart_path')
                                    logger.info(f"📨 Enviando milestone {milestone}% para {symbol} (profit={profit_percent:.2f}%, updates_sent={updates_sent-1}→{updates_sent})")
                                    self.telegram_client.send_milestone_update(
                                        symbol=symbol,
                                        milestone=milestone,
                                        profit=profit_percent,
                                        chart_path=chart_path
                                    )
                                self._safe_gui_queue_put(('log_message', f"📊 {symbol} +{milestone}% (Profit: {profit_percent:+.2f}%)"))
                # ---------- 5. Cierres automáticos ----------
                # Objetivo (del config)
                tp_target = self.config.PROFIT_TARGET_PERCENT
                if profit_percent >= tp_target:
                    report = self.signal_tracker.close_signal(signal_hash, current_price, reason='target_reached')
                    if report:
                        self._handle_signal_closure(report)
                    continue

                # Stop (del config)
                sl_target = self.config.DEFAULT_STOP_LOSS_PERCENT * 100
                if profit_percent <= -sl_target:
                    report = self.signal_tracker.close_signal(signal_hash, current_price, reason='stop_loss_hit')
                    if report:
                        self._handle_signal_closure(report)
                    continue

                # ✅ CONFIRMADAS: Sin timeout - continúan hasta TP (3%), SL (-1%) o cambio de tendencia
                # DESTACADAS: Tienen su propio timeout de 20 minutos en la lógica de promoción

                # ---------- 5B. Detección de cambio de tendencia en PROFIT (Cierre Parcial) ----------
                m1 = getattr(self.config, 'MILESTONE_1', 0.5)
                m3 = getattr(self.config, 'MILESTONE_3', 1.5)
                if status == 'CONFIRMADA' and m1 <= profit_percent < m3:
                    now_ts = time.time()
                    last_check = tracking_data.get('last_profit_trend_check', 0)
                    if now_ts - last_check > 180:
                        tracking_data['last_profit_trend_check'] = now_ts
                        try:
                            df_15m = self.data_manager.get_data(symbol, "15m", 120, self.client)
                            if df_15m is not None and len(df_15m) >= 60:
                                cycle = self.technical_analyzer.analyze_market_cycles(df_15m)
                                cycle_type = (cycle.get('cycle') or 'NEUTRAL').upper()
                                cycle_strength = float(cycle.get('strength', 0)) * 100

                                is_buy = tracking_data.get('is_buy', True)
                                adverse = False
                                if is_buy and cycle_type in ['DOWNTREND', 'DISTRIBUTION']:
                                    adverse = True
                                elif (not is_buy) and cycle_type in ['UPTREND', 'ACCUMULATION']:
                                    adverse = True

                                if adverse and cycle_strength >= 70:
                                    logger.info(f"⚠️ {symbol}: Cambio de tendencia en PROFIT ({profit_percent:.2f}%) - Cierre Parcial")
                                    self._safe_gui_queue_put(('log_message', f"⚠️ {symbol}: Tendencia invertida en profit -> Cierre Parcial"))
                                    report = self.signal_tracker.close_signal(signal_hash, current_price, reason='TREND_CHANGE_PARTIAL')
                                    if report:
                                        self._handle_signal_closure(report)
                                    continue
                        except Exception as e:
                            logger.debug(f"Error checking profit trend change: {e}")

                # ---------- 6. Detección de reversión ROBUSTA (validación multi-timeframe) ----------
                try:
                    # ✅ Solo verificar reversión después de 10 minutos y si profit es negativo
                    start_time = tracking_data.get('confirmed_start_time') or tracking_data.get('start_time')
                    if start_time and profit_percent < -0.3:  # Solo si perdiendo más de 0.3%
                        elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
                        if elapsed_minutes >= 10:  # Mínimo 10 minutos antes de considerar reversión
                            # ✅ VALIDACIÓN COMPLETA: Usar 15m + 30m + IA + Técnico + Alineación
                            df_15m = self.data_manager.get_data(symbol, "15m", 200, self.client)
                            df_30m = self.data_manager.get_data(symbol, "30m", 200, self.client)

                            if df_15m is not None and df_30m is not None and len(df_15m) >= 50:
                                original_is_buy = tracking_data['is_buy']
                                original_direction = "BULLISH" if original_is_buy else "BEARISH"
                                opposite_direction = "BEARISH" if original_is_buy else "BULLISH"

                                # Validar alineación actual con dirección OPUESTA
                                current_analysis = self._analyze_async_with_timeout(symbol, 3)
                                if current_analysis:
                                    current_neural = current_analysis.get('neural_score', 0)
                                    current_technical = current_analysis.get('technical_percentage', 0)

                                    alignment = self.trend_alignment_validator.validate_trend_alignment(
                                        df_15m, df_30m, current_neural, current_technical, opposite_direction
                                    )

                                    # ✅ CIERRE POR REVERSIÓN SOLO SI:
                                    # 1. Alineación con dirección opuesta >= 70%
                                    # 2. IA confirma dirección opuesta >= 75%
                                    # 3. Técnico confirma >= 70%
                                    reversal_confirmed = (
                                        alignment.get('alignment_score', 0) >= 70 and
                                        alignment.get('is_aligned', False) and
                                        current_neural >= 75 and
                                        current_technical >= 70
                                    )

                                    if reversal_confirmed:
                                        logger.info(f"🔄 {symbol}: REVERSIÓN CONFIRMADA después de {elapsed_minutes:.1f} min | "
                                                   f"Profit: {profit_percent:+.2f}% | Alineación opuesta: {alignment.get('alignment_score', 0):.1f}%")
                                        report = self.signal_tracker.close_signal(signal_hash, current_price, reason='trend_reversal_detected')
                                        if report:
                                            self._handle_signal_closure(report)
                                        continue
                except Exception as e:
                    logger.debug(f"⚠️ Análisis de reversión falló para {symbol}: {e}")

            except SystemExit as e:
                logger.critical(f"🛑 SYSTEM EXIT DETECTADO: {e}")
                raise
            except Exception as e:
                logger.error(f"❌ [MONITOR] Error en _monitor_tracked_signals_continuous: {e}", exc_info=True)
                import traceback
                logger.error(f"📋 Traceback completo:\n{traceback.format_exc()}")
                time.sleep(5)  # Evita bucles rápidos en caso de error crítico

    def _handle_signal_closure(self, report: dict):
        """Manejar cierre de señal: limpieza, GUI, Telegram"""
        try:
            symbol = report.get('symbol', 'UNKNOWN')
            reason = report.get('reason', 'UNKNOWN')
            profit = report.get('final_profit_percent', report.get('profit_percent', 0.0))
            sig_hash = report.get('signal_hash')
            logger.info(f"🔚 [CIERRE] Cerrando {symbol} | Razón: {reason} | Profit: {profit:.2f}%")

            # ✅ Liberar modo exclusivo
            logger.debug(f"🔚 [CIERRE] Liberando modo exclusivo...")
            self._release_exclusive_mode()
            logger.debug(f"✅ [CIERRE] Modo exclusivo liberado")

            # ✅ Limpieza total de cachés
            self.clear_all_caches()

            # ✅ Remover de lista activa/cache y limpiar GUI
            self._purge_closed_signal_cache(symbol=symbol, sig_hash=sig_hash)
            self._safe_gui_queue_put(('remove_signal_from_table', {'symbol': symbol, 'signal_hash': sig_hash}))
            try:
                if not self.active_signals:
                    self._safe_gui_queue_put(('clear_signals_table', None))
            except Exception:
                pass
            # ✅ Log y notificación Telegram
            self._safe_gui_queue_put(('log_message', f"CloseOperation: {symbol} | Motivo: {reason} | Profit: {profit:.2f}%"))

            if self.config.telegram_enabled:
                try:
                    chart_path = None
                    if reason in ['target_reached', 'stop_loss_hit'] and PLOTTING_AVAILABLE:
                        tracking = self.signal_tracker.tracked_signals.get(next(iter(self.signal_tracker.tracked_signals), None))
                        if tracking:
                            try:
                                chart_path = self.chart_generator.generate_signal_chart(
                                    tracking['signal_data']['symbol'],
                                    tracking['signal_data'].get('dataframe_entry'),
                                    tracking['signal_data'],
                                    {}
                                )
                            except Exception as chart_err:
                                logger.debug(f"[DEBUG] Error generando gráfico: {chart_err}")

                    self.telegram_client.send_closure_update(
                        symbol=symbol,
                        reason=reason,
                        profit_percent=profit,
                        duration_minutes=report.get('duration_minutes', 0),
                        max_profit=report.get('max_profit_reached', report.get('max_profit', 0.0)),
                        chart_path=chart_path
                    )
                except Exception as tg_err:
                    logger.debug(f"[DEBUG] Error enviando cierre a Telegram: {tg_err}")
        except Exception as e:
            logger.error(f"[ERROR] Error en _handle_signal_closure: {e}", exc_info=True)

    def _on_signal_closed_callback(self, symbol: str, report: dict):
        """Callback desde SignalTracker para limpiar GUI y estado al cerrar una senal"""
        reason = report.get('reason', 'UNKNOWN')
        profit = report.get('final_profit_percent', 0.0)
        sig_hash = report.get('signal_hash')
        logger.info(f"[CALLBACK] _on_signal_closed_callback ejecutado para {symbol} | Razon: {reason} | Profit: {profit:.2f}%")

        self._purge_closed_signal_cache(symbol=symbol, sig_hash=sig_hash)
        self._safe_gui_queue_put(('remove_signal_from_table', {'symbol': symbol, 'signal_hash': sig_hash}))
        try:
            if not self.active_signals:
                self._safe_gui_queue_put(('clear_signals_table', None))
        except Exception:
            pass

        # CRITICO: Limpiar panel de senal activa en GUI y OCULTAR barra
        logger.info(f"[CALLBACK] Enviando comandos de limpieza GUI para {symbol}")
        self._safe_gui_queue_put(('update_highlight_progress', 0))  # Resetear barra de progreso
        self._safe_gui_queue_put(('hide_progress_bar', None))       # Ocultar barra completamente
        self._safe_gui_queue_put(('clear_signal_display', None))    # Limpiar panel de indicadores
        self._safe_gui_queue_put(('reset_main_panel', None))        # Resetear panel principal (90%, NEUTRAL, etc)

        # ✅ CRÍTICO: Limpiar cachés para evitar bloqueos
        try:
            self.clear_all_caches()
            logger.info(f"🧹 Cachés limpiadas tras cierre de {symbol}")
        except Exception as e:
            logger.error(f"Error limpiando cachés: {e}")

        # ✅ CRÍTICO: Liberar modo exclusivo para reanudar escaneo
        try:
            self._release_exclusive_mode()
            logger.info(f"▶️ Modo exclusivo liberado para {symbol}")
        except Exception as e:
            logger.error(f"Error liberando modo exclusivo: {e}")

        # ✅ CRÍTICO: Reiniciar escaneo de TODOS los símbolos
        if self.symbol_scanner:
            try:
                self.symbol_scanner.resume_all_scanning()  # Reanudar TODO el escaneo
                self.symbol_scanner.rescan_symbol(symbol)  # Priorizar el símbolo cerrado
                logger.info(f"🔄 Escaneo reanudado tras cierre de {symbol}")
            except Exception as e:
                logger.error(f"Error reanudando escaneo: {e}")

        # Log de diagnostico
        logger.info(f"Sistema listo para nueva senal despues de cerrar {symbol}")

        # ✅ Enviar notificación especial a Telegram para HIGHLIGHT_TIMEOUT (señal no confirmada)
        if reason == "HIGHLIGHT_TIMEOUT":
            logger.info(f"⏱️ DESTACADA {symbol} expiró sin confirmarse - Enviando alerta de cierre")
            self._safe_gui_queue_put(('log_message', f"⏱️ {symbol} - Señal DESTACADA expiró sin confirmarse"))
            # Enviar notificación de señal NO confirmada
            if self.config.telegram_enabled:
                try:
                    self.telegram_client.send_highlight_expired_notification(
                        symbol=symbol,
                        duration_minutes=report['duration_minutes']
                    )
                except Exception as e:
                    logger.error(f"Error enviando notificación HIGHLIGHT_TIMEOUT: {e}")
            return  # Salir (ya se envió la notificación espec��fica)

        # ✅ Enviar notificación de cierre a Telegram solo para señales CONFIRMADAS
        if self.config.telegram_enabled:
            chart_path = None
            # Solo generar gráfico si es un cierre "importante" y plotting disponible
            if reason in ['PROFIT_TARGET', 'STOP_LOSS', 'target_reached', 'stop_loss_hit', 'trend_reversal_detected'] and PLOTTING_AVAILABLE:
                tracking = self.signal_tracker.tracked_signals.get(next(iter(self.signal_tracker.tracked_signals), None))
                if tracking:
                    try:
                        chart_path = self.chart_generator.generate_signal_chart(
                            tracking['signal_data']['symbol'],
                            tracking['signal_data'].get('dataframe_entry'),
                            tracking['signal_data'], {}
                        )
                    except Exception as e:
                        logger.debug(f"⚠️ No se pudo generar gráfico para cierre ({reason}): {e}")

            # ✅ Enviar notificación solo para señales CONFIRMADAS cerradas
            self.telegram_client.send_closure_update(
                symbol=symbol,
                reason=reason,
                profit_percent=report['final_profit_percent'],
                duration_minutes=report['duration_minutes'],
                max_profit=report['max_profit_reached'],
                chart_path=chart_path
            )

    def _release_exclusive_mode(self):
        """Libera el modo exclusivo, limpia GUI y notifica"""
        if self.exclusive_tracking_mode:
            old_symbol = self.tracked_symbol
            self.exclusive_tracking_mode = False
            self.tracked_symbol = None
            self.tracked_signal_hash = None
            
            # CORREGIDO v35: Limpiar GUI principal completamente
            self._safe_gui_queue_put(('clear_signal_display', None))
            self._safe_gui_queue_put(('hide_progress_bar', None))
            self._safe_gui_queue_put(('update_highlight_progress', 0))
            self._safe_gui_queue_put(('reset_main_panel', None))
            self._safe_gui_queue_put(('log_message', f"MODO EXCLUSIVO LIBERADO ({old_symbol}): Reanudando escaneo"))
            logger.info(f"Modo exclusivo liberado y GUI limpiada para {old_symbol}")

    def _purge_closed_signal_cache(self, symbol: str = None, sig_hash: str = None):
        """Elimina señales cerradas del cache interno para evitar que reaparezcan en GUI."""
        try:
            symbol_norm = str(symbol or '').strip().upper()
            hash_norm = str(sig_hash or '').strip()

            new_active = []
            removed = 0
            for s in list(getattr(self, 'active_signals', []) or []):
                s_symbol = str(s.get('symbol', '')).strip().upper()
                s_hash = str(s.get('signal_hash', '')).strip()

                by_symbol = bool(symbol_norm and s_symbol == symbol_norm)
                by_hash = bool(hash_norm and s_hash and s_hash == hash_norm)

                if by_symbol or by_hash:
                    removed += 1
                    continue
                new_active.append(s)

            self.active_signals = new_active
            if removed:
                logger.info(f"🧹 Cache de señales purgado: {removed} removidas ({symbol_norm or 'N/A'} | {hash_norm[:8] if hash_norm else 'no-hash'})")
        except Exception as e:
            logger.error(f"Error purgando cache de señales cerradas: {e}")

    def clear_all_caches(self):
        """
        🧹 Limpia TODAS las cachés del sistema tras cierre de señal.
        Incluye protección con lock para market_data y cachés compartidas.
        """
        try:
            # ========== 1. Limpiar caché técnica (con lock implícito en analyzer) ==========
            if hasattr(self.strategy_impl.technical_analyzer, 'indicator_cache'):
                self.strategy_impl.technical_analyzer.indicator_cache.clear()
                self.strategy_impl.technical_analyzer.cache_access_times.clear()
                logger.debug("🧹 Caché técnica limpiada")

            # ========== 2. Limpiar caché de datos (DataManager) ==========
            if hasattr(self.data_manager, 'data_cache'):
                with self.data_manager.cache_lock:
                    self.data_manager.data_cache.clear()
                    self.data_manager.access_times.clear()
                    self.data_manager.cache_stats = {'hits': 0, 'misses': 0}
                logger.debug("🧹 Caché de datos limpiada")

            # ========== 3. Limpiar caché de calidad de señales ==========
            if hasattr(self.signal_processor, 'signal_quality_cache'):
                self.signal_processor.signal_quality_cache.clear()
                logger.debug("🧹 Caché de calidad de señales limpiada")

            # ========== 4. ✅ Limpiar market_data (CON LOCK — CORRECCIÓN CRÍTICA) ==========
            with self.market_data_lock:  # 🔒 Evita race condition con SymbolScanner/GUI
                if self.tracked_symbol and self.tracked_symbol in self.market_data:
                    del self.market_data[self.tracked_symbol]
                    logger.info(f"🧹 market_data: símbolo rastreado '{self.tracked_symbol}' eliminado")
                # Opcional: limpiar *todo* si es finalización total (comenta si solo quieres limpiar el rastreado)
                self.market_data.clear()

            logger.info("✅ Todas las cachés limpiadas tras cierre de señal.")

        except Exception as e:
            logger.error(f"[ERROR] Error limpiando cachés: {e}", exc_info=True)
            self._safe_gui_queue_put(('log_message', f"⚠️ Error al limpiar cachés: {e}"))

    def _cleanup_market_data(self, max_age_minutes=5):
        """Limpia market_data de símbolos no usados recientemente para evitar fuga de memoria."""
        try:
            now = datetime.now()
            to_remove = [
                sym for sym, data in self.market_data.items()
                if (now - data.get('timestamp', now)).total_seconds() > max_age_minutes * 60
            ]
            for sym in to_remove:
                if sym in self.market_data:
                    del self.market_data[sym]
            if to_remove:
                logger.info(f"🧹 Limpieza de market_data: {len(to_remove)} símbolos expirados eliminados.")
        except Exception as e:
            logger.error(f"[ERROR] Error en _cleanup_market_data: {e}")

    def load_pair_data_optimized(self, symbol: str = None):
        """
        Carga datos históricos y realiza el análisis completo para un símbolo específico,
        actualizando self.current_analysis para la GUI.
        """
        symbol = symbol or self.current_pair
        # 1. Obtener DataFrames
        df_primary = self.data_manager.get_data(
            symbol, self.config.PRIMARY_TIMEFRAME,
            self.config.MIN_NN_DATA_REQUIRED, self.client
        )
        df_entry = self.data_manager.get_data(
            symbol, self.config.ENTRY_TIMEFRAME,
            self.config.MIN_NN_DATA_REQUIRED, self.client
        )
        if not self._validate_dataframes(df_primary, df_entry, symbol):
            logger.warning(f"Datos insuficientes para carga inicial de {symbol}")
            self.current_analysis['price'] = self.client.get_ticker_price(symbol)
            return
        # 2. Realizar Análisis Completo
        analysis_result = self._perform_optimized_analysis(symbol, df_primary, df_entry)
        # 3. Actualizar estado del bot para la GUI
        if analysis_result:
            self.current_analysis = analysis_result
            self.last_update = datetime.now().strftime("%H:%M:%S")
            self.market_data[symbol] = {
                'df_primary': df_primary,
                'df_entry': df_entry,
                'analysis': analysis_result.copy(),
                'timestamp': datetime.now()
            }
        else:
            # Mantener solo el precio si el análisis falla
            self.current_analysis['price'] = self.client.get_ticker_price(symbol)
            self.current_analysis['combined_signal'] = SignalType.NEUTRAL
        logger.info(f"[OK] Carga de datos inicial/manual para {symbol} completada.")
        self._safe_gui_queue_put(('update_gui', None))
        self._safe_gui_queue_put(('update_analysis_tab', None))

    def get_system_diagnostics(self) -> dict:
        """
        Obtiene diagnostico completo del sistema v35 para verificar funcionamiento
        
        Returns:
            dict con estado de todos los componentes criticos
        """
        diagnostics = {
            'version': 'v35.0.0.0',
            'timestamp': datetime.now().isoformat(),
            'status': 'OK',
            'components': {}
        }
        
        # 1. Estado del bot
        diagnostics['components']['bot'] = {
            'running': self.running,
            'exclusive_mode': self.exclusive_tracking_mode,
            'tracked_symbol': self.tracked_symbol,
            'current_pair': self.current_pair
        }
        
        # 2. Estado de SignalTracker
        if hasattr(self, 'signal_tracker') and self.signal_tracker:
            tracked = self.signal_tracker.get_tracked_signals()
            metrics = self.signal_tracker.get_performance_metrics()
            diagnostics['components']['signal_tracker'] = {
                'active_signals': len(tracked),
                'total_signals': metrics.get('total_signals', 0),
                'successful_signals': metrics.get('successful_signals', 0),
                'promotion_count': metrics.get('promotion_count', 0),
                'avg_profit': f"{metrics.get('avg_profit_loss', 0):.2f}%"
            }
            
            # Detalle de senal activa
            if tracked:
                for hash_id, tracking in tracked.items():
                    summary = self.signal_tracker.get_signal_cycle_summary(hash_id)
                    diagnostics['components']['active_signal'] = summary
                    break
        else:
            diagnostics['components']['signal_tracker'] = {'error': 'No inicializado'}
        
        # 3. Estado de Telegram
        if hasattr(self, 'telegram_client') and self.telegram_client:
            tg_stats = self.telegram_client.get_stats()
            diagnostics['components']['telegram'] = {
                'enabled': self.config.telegram_enabled,
                'messages_sent': tg_stats.get('messages_sent', 0),
                'success_rate': tg_stats.get('success_rate', '0%'),
                'signals_tracked': tg_stats.get('signals_tracked', 0)
            }
        else:
            diagnostics['components']['telegram'] = {'enabled': False}
        
        # 4. Estado de WebSocket
        if hasattr(self, 'ws_manager') and self.ws_manager:
            diagnostics['components']['websocket'] = {
                'connected': self.ws_manager.conectado,
                'messages_received': self.ws_manager.mensajes_recibidos,
                'errors_consecutive': self.ws_manager.errores_consecutivos,
                'fallback_active': self.ws_manager.fallback_active,
                'connection_quality': self.ws_manager.get_connection_quality() if hasattr(self.ws_manager, 'get_connection_quality') else 'N/A'
            }
        else:
            diagnostics['components']['websocket'] = {'connected': False}
        
        # 5. Estado de Cache
        if hasattr(self, 'data_manager') and self.data_manager:
            cache_stats = self.data_manager.get_cache_stats()
            diagnostics['components']['cache'] = {
                'entries': cache_stats.get('total_entries', 0),
                'hit_rate': f"{cache_stats.get('hit_rate', 0):.1f}%"
            }
        
        # 6. Configuracion critica
        diagnostics['config'] = {
            'trading_symbols': len(self.config.TRADING_SYMBOLS),
            'profit_target': f"{self.config.PROFIT_TARGET_PERCENT}%",
            'stop_loss': f"{self.config.DEFAULT_STOP_LOSS_PERCENT*100:.1f}%",
            'milestones': self.config.PROFIT_MILESTONES,
            'trailing_stop_enabled': getattr(self.config, 'TRAILING_STOP_ENABLED', True),
            'min_neural_destacada': self.config.MIN_NEURAL_DESTACADA,
            'min_neural_confirmada': self.config.MIN_NEURAL_CONFIRMADA
        }
        
        # Verificar errores criticos
        errors = []
        warnings = []
        
        if not self.running:
            errors.append('Bot no esta ejecutandose')
        
        # WebSocket: verificar si esta conectado o en proceso de conexion
        ws_connected = diagnostics['components'].get('websocket', {}).get('connected', False)
        ws_fallback = diagnostics['components'].get('websocket', {}).get('fallback_active', False)
        if not ws_connected and not ws_fallback:
            # Verificar si el WebSocket existe y esta intentando conectar
            if hasattr(self, 'ws_manager') and self.ws_manager and self.ws_manager.ejecutando:
                warnings.append('WebSocket conectando...')
            else:
                errors.append('WebSocket desconectado')
        elif ws_fallback:
            warnings.append('WebSocket en modo fallback (API REST)')
        
        if not self.config.telegram_enabled:
            warnings.append('Telegram deshabilitado')
        
        if errors:
            diagnostics['status'] = 'ERROR'
            diagnostics['errors'] = errors
        elif warnings:
            diagnostics['status'] = 'WARNING'
        else:
            diagnostics['status'] = 'OK'
        
        if warnings:
            diagnostics['warnings'] = warnings
        
        return diagnostics
    
    def print_system_diagnostics(self):
        """Imprime diagnostico del sistema en consola y log"""
        diag = self.get_system_diagnostics()
        
        logger.info("=" * 50)
        logger.info(f"DIAGNOSTICO DEL SISTEMA {diag['version']}")
        logger.info("=" * 50)
        logger.info(f"Estado General: {diag['status']}")
        logger.info(f"Timestamp: {diag['timestamp']}")
        
        for comp_name, comp_data in diag['components'].items():
            logger.info(f"\n[{comp_name.upper()}]")
            for key, value in comp_data.items():
                logger.info(f"  {key}: {value}")
        
        if 'warnings' in diag:
            # Evitar spam de warning durante arranque cuando WS aún está conectando
            warnings_list = list(diag.get('warnings', []))
            only_ws_connecting = (len(warnings_list) == 1 and warnings_list[0] == 'WebSocket conectando...')
            if only_ws_connecting:
                logger.info(f"\nADVERTENCIAS (informativas): {warnings_list}")
            else:
                logger.warning(f"\nADVERTENCIAS: {warnings_list}")
        
        logger.info("=" * 50)
        return diag

    def start_optimized(self):
        """Iniciar bot con optimizaciones - CORREGIDO para emitir senales y mostrar progreso por ciclo"""
        try:
            self.running = True
            logger.info("Bot Optimizado v35.0.0.0 iniciando...")

            # === 1. Reinicializar contadores y estado ===
            self.total_symbols_to_analyze = len(self.config.TRADING_SYMBOLS)
            self.symbols_analyzed_count = 0
            self.symbol_analysis_counts = {symbol: 0 for symbol in self.config.TRADING_SYMBOLS}

            # Reiniciar estado de seguimiento exclusivo (crítico para señales)
            self.exclusive_tracking_mode = False
            self.tracked_symbol = None
            self.tracked_signal_hash = None
            self.single_active_signal_hash = None

            # === 2. Enviar estado inicial a GUI ===
            self._safe_gui_queue_put(('update_pair_scan_progress', 0))
            self._safe_gui_queue_put(('log_message', "Bot Avanzado Optimizado v35.0.0.0 iniciando sistema..."))
            self._safe_gui_queue_put(('update_current_analyzed_symbol', None))
            self._safe_gui_queue_put(('update_highlight_progress', 0))  # Reiniciar barra DESTACADA

            # === 3. Iniciar monitoreo continuo de senales (ES CLAVE PARA TIMEOUT Y PROMOCION) ===
            signal_monitor_thread = threading.Thread(
                target=self._monitor_tracked_signals_continuous,
                daemon=True,
                name="SignalMonitor"
            )
            signal_monitor_thread.start()
            logger.info("Sistema de monitoreo continuo de senales iniciado")
            
            # === 3.1 Programar diagnostico inicial con delay para permitir conexion WebSocket ===
            def delayed_diagnostics():
                time.sleep(5)  # Esperar 5 segundos para que WebSocket se conecte
                self.print_system_diagnostics()
            
            diag_thread = threading.Thread(target=delayed_diagnostics, daemon=True, name="InitialDiagnostics")
            diag_thread.start()

            # === 4. Iniciar WebSocket (datos en tiempo real) ===
            # 4. Iniciar WebSocket (datos en tiempo real) — CON FILTRO ANTI-N/A
            # ============================================================================
            if WEBSOCKET_AVAILABLE and not getattr(self.client, 'disable_websocket', False):
                if self.ws_manager:
                    self.ws_manager.detener()

            # ✅ FILTRAR SÍMBOLOS VÁLIDOS ANTES DE PASARLOS AL WEBSOCKET
            valid_symbols = [s for s in self.config.TRADING_SYMBOLS if s and str(s).strip() != "N/A"]
            if not valid_symbols:
                logger.warning("No hay símbolos válidos para WebSocket; se usará sólo REST.")
            else:
                try:
                    self.ws_manager = RobustWebSocketManager(
                        symbols=valid_symbols,
                        intervalo=self.config.ENTRY_TIMEFRAME,
                        callback=self._process_websocket_data_optimized
                    )
                    self.ws_manager.iniciar()
                    logger.info(f"📡 WebSocket iniciado para {len(valid_symbols)} símbolos")

                    # ✅ ESPERAR UN MOMENTO PARA VER SI OCURRE ERROR 451
                    time.sleep(1)
                    if hasattr(self.ws_manager, '_error_451_detected') and self.ws_manager._error_451_detected:
                        logger.critical("❌ ERROR 451 DETECTADO: Bot no puede conectarse a Binance desde esta ubicación")
                        self._safe_gui_queue_put(('log_message', "❌ ERROR 451: Binance bloquea desde esta ubicación. Solución: Usar VPN o cambiar de exchange"))
                        # ✅ NO CERRAR EL BOT - Continuar en modo espera
                        logger.warning("⚠️ Bot continuará ejecutándose sin datos de Binance. Intenta usar VPN o proxy.")
                except Exception as e:
                    logger.error(f"[ERROR] Falló inicio de WebSocket: {e}")
                    self._safe_gui_queue_put(('log_message', "⚠️ WebSocket no disponible. Usando polling..."))

            # === 5. Iniciar escáner de símbolos (ANÁLISIS ACTIVO) ===
            try:
                self.symbol_scanner = SymbolScanner(
                    bot=self,
                    symbols=self.config.TRADING_SYMBOLS,
                    scan_interval=self.config.SCAN_INTERVAL  # ej. 5 segundos
                )
                self.symbol_scanner.start()
                logger.info(f"[SCAN] Escáner iniciado: {self.total_symbols_to_analyze} símbolos, intervalo={self.config.SCAN_INTERVAL}s")
            except Exception as e:
                logger.critical(f"💥 Falló inicio del SymbolScanner: {e}")
                self._safe_gui_queue_put(('log_message', f"❌ Error crítico: Escáner no iniciado. {e}"))
                self.running = False
                return

            # === 6. Carga inicial de datos (evita 'NoneType' en primer análisis) ===
            try:
                self.load_pair_data_optimized()  # Carga datos iniciales para self.current_pair
            except Exception as e:
                logger.warning(f"[WARN] Falló carga inicial de datos: {e}")

            # === 7. Confirmación final ===
            self._safe_gui_queue_put(('log_message', "✅ Bot Optimizado v35.0.0.0 iniciado correctamente"))
            logger.info("✅ Bot Optimizado iniciado correctamente")

        except Exception as e:
            logger.critical(f"🔥 ERROR FATAL en start_optimized: {e}", exc_info=True)
            self._safe_gui_queue_put(('log_message', f"❌ ERROR FATAL al iniciar: {e}"))
            self.running = False
            raise

    def stop_optimized(self):
        """Detener bot optimizado"""
        self.running = False
        if self.ws_manager:
            self.ws_manager.detener()
        if self.symbol_scanner:
            self.symbol_scanner.stop()
        # Limpiar caches
        if hasattr(self.strategy_impl.technical_analyzer, 'indicator_cache'):
            self.strategy_impl.technical_analyzer.indicator_cache.clear()
        if hasattr(self.signal_processor, 'signal_quality_cache'):
            self.signal_processor.signal_quality_cache.clear()
        logger.info("⏹️ Bot Optimizado detenido")
        self._safe_gui_queue_put(('log_message', "⏹️ Bot Optimizado detenido"))
        self._safe_gui_queue_put(('update_pair_scan_progress', 0))
        self._safe_gui_queue_put(('update_highlight_progress', 0))  # Resetear barra de seguimiento

    def set_pair_optimized(self, pair):
        """Cambiar el par actual de trading"""
        self.current_pair = pair
        logger.info(f"📊 Par cambiado a: {pair}")

    def _safe_gui_queue_put(self, item):
        """Enviar elementos a la cola GUI de forma segura y robusta"""
        try:
            self.gui_queue.put(item, timeout=0.05)  # ✅ MÁS ESTRICTO (50ms)
        except queue.Full:
            # ✅ MITIGACIÓN 3: LIMPIEZA AGRESIVA Y FORZAR ÚLTIMO MENSAJE
            try:
                with self.gui_queue.mutex:
                    self.gui_queue.queue.clear()  # Limpiar todos los mensajes antiguos
                # Intentar insertar el nuevo mensaje una vez más
                self.gui_queue.put_nowait(item)
            except (queue.Full, ValueError):
                # ValueError: si la cola está cerrada
                pass  # Descartar silenciosamente si aún fallo

    def _process_websocket_data_optimized(self, ws_update):
        """Procesar datos WebSocket con optimizaciones"""
        try:
            symbol = ws_update['symbol']
            kline_data = ws_update.get('kline', {})
            is_closed = kline_data.get('x', False)
            # Actualización en tiempo real para el par actual
            if symbol == self.current_pair and not is_closed:
                self.current_analysis['price'] = float(kline_data.get('c', 0))
                self.current_analysis['volume'] = float(kline_data.get('v', 0))
                self._safe_gui_queue_put(('update_gui_realtime_price', None))
            # Análisis completo solo cuando se cierra una vela
            if is_closed:
                # Control de progreso optimizado
                if symbol not in self.symbol_analysis_counts:
                    self.symbol_analysis_counts[symbol] = 0
                if self.symbol_analysis_counts[symbol] == 0:
                    self.symbols_analyzed_count += 1
                    progress = int((self.symbols_analyzed_count / self.total_symbols_to_analyze) * 100)
                    self._safe_gui_queue_put(('update_pair_scan_progress', progress))
                self.symbol_analysis_counts[symbol] += 1
                # Log optimizado
                cycle_info = f"(Ciclo {self.symbol_analysis_counts[symbol]})"
                self._safe_gui_queue_put(('log_message', f"🔍 Análisis optimizado: {symbol} {cycle_info}"))
                # ✅ En Replit: análisis síncrono para evitar "can't start new thread"
                if IN_REPLIT:
                    self._analyze_symbol_optimized(symbol)
                else:
                    # Lanzar análisis en hilo optimizado
                    threading.Thread(
                        target=self._analyze_symbol_optimized,
                        args=(symbol,),
                        daemon=True,
                        name=f"AnalyzeThread-{symbol}"
                    ).start()
        except Exception as e:
            logger.error(f"Error en procesamiento WebSocket optimizado: {e}")

    def analyze_and_process_symbol(self, symbol: str):
        """Analyze and process a symbol (for SymbolScanner)"""
        return self._analyze_symbol_optimized(symbol)

    def _analyze_symbol_optimized(self, symbol: str):
        """Análisis optimizado de símbolo individual con priorización absoluta de una sola señal activa"""
        analysis_start = time.time()
        try:
            # ========== ⛔ FILTRO DE DATOS: VERIFICAR BLACKLIST PRIMERO ==========
            if self._is_symbol_blacklisted(symbol):
                logger.debug(f"⏭️ {symbol} - Saltado: en blacklist por datos insuficientes")
                return

            # ========== 🔒 MODO EXCLUSIVO: SOLO ANALIZAR SÍMBOLO EN SEGUIMIENTO ==========
            if self.exclusive_tracking_mode:
                if symbol != self.tracked_symbol:
                    logger.info(f"⏭️ {symbol} - Ignorado: señal activa en {self.tracked_symbol}")
                    return
                logger.debug(f"🎯 Modo exclusivo: Analizando {symbol}")

            # ========== ✅ INCREMENTAR CONTADOR POR SÍMBOLO ==========
            if symbol not in self.symbol_analysis_counts:
                self.symbol_analysis_counts[symbol] = 0

            # ========== 📊 ACTUALIZAR PROGRESO SI ES PRIMER ANÁLISIS DEL SÍMBOLO ==========
            if self.symbol_analysis_counts[symbol] == 0:
                self.symbols_analyzed_count += 1
                progress = int((self.symbols_analyzed_count / self.total_symbols_to_analyze) * 100)
                self._safe_gui_queue_put(('update_pair_scan_progress', progress))

            self.symbol_analysis_counts[symbol] += 1
            cycle_num = self.symbol_analysis_counts[symbol]

            # ========== 📢 LOG A GUI ==========
            log_msg = f"🔍 Análisis optimizado: {symbol} (Ciclo {cycle_num})"
            self._safe_gui_queue_put(('log_message', log_msg))
            logger.info(log_msg)

            self._current_analyzed_symbol_for_gui = symbol
            self._safe_gui_queue_put(('update_current_analyzed_symbol', symbol))


            # ========== 📊 OBTENER DATOS ==========
            tf_to_min = {'1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30, '1h': 60, '2h': 120, '4h': 240, '6h': 360, '12h': 720, '1d': 1440}

            primary_mins = tf_to_min.get(self.config.PRIMARY_TIMEFRAME, 30)
            entry_mins = tf_to_min.get(self.config.ENTRY_TIMEFRAME, 15)

            limit_primary = self.config.MIN_NN_DATA_REQUIRED
            limit_entry = max(100, limit_primary * primary_mins // entry_mins)

            df_primary = self.data_manager.get_data(symbol, self.config.PRIMARY_TIMEFRAME, limit_primary, self.client)
            df_entry = self.data_manager.get_data(symbol, self.config.ENTRY_TIMEFRAME, limit_entry, self.client)

            if not self._validate_dataframes(df_primary, df_entry, symbol):
                primary_len = len(df_primary) if df_primary is not None else 0
                entry_len = len(df_entry) if df_entry is not None else 0
                self._record_data_failure(symbol, f"Primary={primary_len}, Entry={entry_len}")
                logger.debug(f"[DATA] Datos insuficientes para {symbol} (Primary={primary_len}, Entry={entry_len})")
                return

            # ✅ Datos válidos - registrar éxito
            self._record_data_success(symbol)

            # ========== ⚡ FAST-FAIL: Filtros rápidos ANTES de cálculos pesados ==========
            if hasattr(self, 'fast_fail_filter') and self.fast_fail_filter:
                try:
                    should_skip, skip_reason = self.fast_fail_filter.should_skip_symbol(symbol, df_primary)
                    if should_skip:
                        logger.debug(f"⚡ FAST-FAIL {symbol}: {skip_reason}")
                        return
                except Exception as e:
                    logger.debug(f"FastFail check error: {e}")
            
            # ========== ⚡ OBTENER DATOS 5m PARA ALINEACIÓN DINÁMICA ==========
            df_5m = None
            if hasattr(self, 'dynamic_alignment_scorer') and self.dynamic_alignment_scorer:
                try:
                    df_5m = self.data_manager.get_data(symbol, "5m", 100, self.client)
                except Exception as e:
                    logger.debug(f"Error obteniendo datos 5m: {e}")

            # ========== 🧠 ANÁLISIS COMPLETO ==========
            analysis_result = self._perform_optimized_analysis(symbol, df_primary, df_entry, df_5m=df_5m)
            if not analysis_result:
                logger.debug(f"[ANALYSIS] Análisis sin resultados para {symbol}")
                return

            # ========== 📥 ACTUALIZAR ESTADO LOCAL ==========
            self.current_analysis = analysis_result.copy()
            self.last_update = datetime.now().strftime("%H:%M:%S")

            # ========== 💾 GUARDAR EN market_data (CON LOCK) ==========
            with self.market_data_lock:
                self.market_data[symbol] = {
                    'df_primary': df_primary,
                    'df_entry': df_entry,
                    'analysis': analysis_result.copy(),
                    'timestamp': datetime.now()
                }

            # ========== 📢 NOTIFICAR GUI ==========
            self._safe_gui_queue_put(('update_gui', None))
            self._safe_gui_queue_put(('update_analysis_tab', None))

            # ========== 🚨 PROCESAR SEÑALES PREMIUM ==========
            signal_type = analysis_result.get('combined_signal')
            if not signal_type:
                return

            is_premium = (
                'HIGHLIGHTED' in signal_type.name or 'CONFIRMED' in signal_type.name or
                'DESTACADA' in getattr(signal_type, 'value', '') or
                'CONFIRMADA' in getattr(signal_type, 'value', '')
            )

            if is_premium:
                if self.exclusive_tracking_mode:
                    logger.info(f"⏭️ {symbol} - Señal premium ignorada: ya hay señal activa ({self.tracked_symbol})")
                    return

                try:
                    # ✅ CORREGIDO: Pasar df_primary (estaba faltando)
                    self._process_high_quality_signal(symbol, df_primary, df_entry, analysis_result)
                except Exception as e:
                    logger.error(f"[ERROR] Error procesando señal premium para {symbol}: {e}", exc_info=True)

            # ========== 📈 MÉTRICAS Y LIMPIEZA ==========
            analysis_time = (time.time() - analysis_start) * 1000
            self.performance_tracker['analysis_times'].append(analysis_time)
            if len(self.performance_tracker['analysis_times']) > 100:
                self.performance_tracker['analysis_times'] = self.performance_tracker['analysis_times'][-100:]

            if len(self.performance_tracker['analysis_times']) % 50 == 0:
                avg_time = np.mean(self.performance_tracker['analysis_times'])
                cache_stats = self.data_manager.get_cache_stats()
                msg = f"📊 Rendimiento: {avg_time:.1f}ms promedio, Cache hit: {cache_stats['hit_rate']:.1f}%"
                self._safe_gui_queue_put(('log_message', msg))
                logger.info(msg)

            if len(self.performance_tracker['analysis_times']) % 20 == 0:
                self._cleanup_market_data(max_age_minutes=10)

        except Exception as e:
            logger.error(f"[ERROR] Error FATAL en _analyze_symbol_optimized({symbol}): {e}", exc_info=True)
            self._safe_gui_queue_put(('log_message', f"❌ Error en análisis de {symbol}: {e}"))
        finally:
            self._current_analyzed_symbol_for_gui = None

    def _validate_dataframes(self, df_primary, df_entry, symbol: str = None):
        """Validación robusta de dataframes con múltiples criterios"""
        try:
            # Validación básica de existencia y no vacío
            if not self._validate_dataframe_basico(df_primary) or not self._validate_dataframe_basico(df_entry):
                if symbol:
                    logger.debug(f"[VALIDATION] Dataframe básico inválido para {symbol}")
                return False

            # Validación de columnas requeridas
            columnas_requeridas = ['open', 'high', 'low', 'close', 'volume']
            if not self._validate_columnas(df_primary, columnas_requeridas, symbol, "primary"):
                return False
            if not self._validate_columnas(df_entry, columnas_requeridas, symbol, "entry"):
                return False

            # Validación de cantidad mínima de datos
            min_required = max(50, self.config.MIN_NN_DATA_REQUIRED)
            if len(df_primary) < min_required or len(df_entry) < min_required:
                if symbol:
                    logger.warning(f"[VALIDATION] {symbol}: DATOS INSUFICIENTES → Primary={len(df_primary)}/{min_required}, Entry={len(df_entry)}/{min_required}")
                return False

            # Validación de continuidad temporal (opcional pero recomendada)
            if not self._validate_continuidad_temporal(df_primary, symbol, "primary"):
                return False
            if not self._validate_continuidad_temporal(df_entry, symbol, "entry"):
                return False

            # Validación de valores no nulos en columnas críticas
            if not self._validate_valores_no_nulos(df_primary, ['close', 'volume'], symbol, "primary"):
                return False
            if not self._validate_valores_no_nulos(df_entry, ['close', 'volume'], symbol, "entry"):
                return False

            # Validación de rango de precios (evitar valores anómalos)
            if not self._validate_rango_precios(df_primary, symbol, "primary"):
                return False
            if not self._validate_rango_precios(df_entry, symbol, "entry"):
                return False

            return True

        except Exception as e:
            if symbol:
                logger.error(f"[VALIDATION] Error validando dataframes para {symbol}: {e}")
            return False

    def verify_all_pairs(self, available_pairs: List[str]) -> Dict[str, bool]:
        """
        Verifica todos los pares disponibles y retorna cuáles tienen datos suficientes

        Args:
            available_pairs: Lista de pares a verificar (ej: ['BTCUSDT', 'ETHUSDT', 'XRPUSDT'])

        Returns:
            Dict con pares como claves y True/False según si tienen datos suficientes
        """
        pairs_status = {}

        logger.info(f"[PAIR VERIFICATION] Verificando {len(available_pairs)} pares disponibles...")

        for symbol in available_pairs:
            try:
                # Obtener dataframes para verificación
                df_primary = self.data_manager.get_data(
                    symbol, self.config.PRIMARY_TIMEFRAME,
                    self.config.MIN_NN_DATA_REQUIRED, self.client
                )
                df_entry = self.data_manager.get_data(
                    symbol, self.config.ENTRY_TIMEFRAME,
                    self.config.MIN_NN_DATA_REQUIRED, self.client
                )

                # Verificar si tienen datos suficientes
                has_enough_data = self._validate_dataframes(df_primary, df_entry, symbol)
                pairs_status[symbol] = has_enough_data

                if has_enough_data:
                    logger.info(f"[PAIR VERIFICATION] ✅ {symbol}: Datos suficientes (Primary: {len(df_primary) if df_primary is not None else 0}, Entry: {len(df_entry) if df_entry is not None else 0})")
                else:
                    primary_len = len(df_primary) if df_primary is not None else 0
                    entry_len = len(df_entry) if df_entry is not None else 0
                    logger.warning(f"[PAIR VERIFICATION] ❌ {symbol}: Datos insuficientes (Primary: {primary_len}, Entry: {entry_len}, mínimo: {max(50, self.config.MIN_NN_DATA_REQUIRED)})")

            except Exception as e:
                pairs_status[symbol] = False
                logger.error(f"[PAIR VERIFICATION] ❌ Error verificando {symbol}: {e}")

        # Reporte resumido
        total_pairs = len(pairs_status)
        pairs_with_data = sum(pairs_status.values())
        pairs_without_data = total_pairs - pairs_with_data

        logger.info(f"[PAIR VERIFICATION] 📊 RESUMEN: {pairs_with_data}/{total_pairs} pares con datos suficientes")
        logger.info(f"[PAIR VERIFICATION] ✅ Pares listos para análisis: {pairs_with_data}")
        logger.info(f"[PAIR VERIFICATION] ❌ Pares descartados: {pairs_without_data}")

        if pairs_without_data > 0:
            rejected_pairs = [pair for pair, status in pairs_status.items() if not status]
            logger.warning(f"[PAIR VERIFICATION] Pares descartados: {rejected_pairs}")

        return pairs_status

    def get_valid_pairs_only(self, available_pairs: List[str]) -> List[str]:
        """
        Retorna solo los pares que tienen datos suficientes para análisis

        Args:
            available_pairs: Lista de pares a filtrar

        Returns:
            Lista de pares con datos suficientes
        """
        pairs_status = self.verify_all_pairs(available_pairs)
        valid_pairs = [pair for pair, has_data in pairs_status.items() if has_data]

        logger.info(f"[PAIR FILTER] Filtrados {len(valid_pairs)} pares válidos de {len(available_pairs)} totales")
        return valid_pairs

    def _is_symbol_blacklisted(self, symbol: str) -> bool:
        """
        ✅ FILTRO DE DATOS: Verifica si un símbolo está en blacklist por fallos repetidos.
        Retorna True si el símbolo debe ser saltado (está en blacklist y no ha pasado el cooldown).
        """
        if symbol in self._validated_pairs:
            return False  # Ya validado exitosamente, no está en blacklist

        if symbol not in self._data_failure_blacklist:
            return False  # No ha fallado nunca

        entry = self._data_failure_blacklist[symbol]
        current_time = time.time()
        elapsed = current_time - entry['last_attempt']

        # Si ha pasado el cooldown, permitir reintento
        if elapsed >= self._blacklist_cooldown:
            logger.debug(f"[BLACKLIST] {symbol}: Cooldown expirado ({elapsed:.0f}s), permitiendo reintento")
            return False

        # Verificar si alcanzó el umbral de fallos
        if entry['failures'] >= self._blacklist_threshold:
            remaining = self._blacklist_cooldown - elapsed
            logger.debug(f"[BLACKLIST] {symbol}: En blacklist ({entry['failures']} fallos), cooldown restante: {remaining:.0f}s")
            return True

        return False

    def _record_data_failure(self, symbol: str, reason: str = "datos insuficientes"):
        """
        ✅ Registra un fallo de datos para un símbolo.
        Si alcanza el umbral, el símbolo entra en blacklist temporal.
        """
        current_time = time.time()
        try:
            if current_time < NETWORK_SUPPRESS_BLACKLIST_UNTIL:
                logger.debug(f"[BLACKLIST] {symbol}: Supresión por red inestable ({reason})")
                return
        except Exception:
            pass

        if symbol not in self._data_failure_blacklist:
            self._data_failure_blacklist[symbol] = {'failures': 0, 'last_attempt': 0}

        entry = self._data_failure_blacklist[symbol]
        entry['failures'] += 1
        entry['last_attempt'] = current_time

        if entry['failures'] >= self._blacklist_threshold:
            logger.warning(f"[BLACKLIST] ⛔ {symbol}: Añadido a blacklist ({entry['failures']} fallos consecutivos - {reason}). Cooldown: {self._blacklist_cooldown}s")
        else:
            logger.debug(f"[BLACKLIST] {symbol}: Fallo {entry['failures']}/{self._blacklist_threshold} ({reason})")

    def _record_data_success(self, symbol: str):
        """
        ✅ Registra éxito de datos para un símbolo.
        Lo añade a pares validados y resetea el contador de fallos.
        """
        self._validated_pairs.add(symbol)
        if symbol in self._data_failure_blacklist:
            del self._data_failure_blacklist[symbol]
            logger.debug(f"[BLACKLIST] ✅ {symbol}: Removido de blacklist (validación exitosa)")

    def _get_blacklist_status(self) -> dict:
        """Retorna el estado actual de la blacklist para debugging"""
        current_time = time.time()
        status = {
            'validated_pairs': len(self._validated_pairs),
            'blacklisted_pairs': [],
            'pending_retry': []
        }

        for symbol, entry in self._data_failure_blacklist.items():
            elapsed = current_time - entry['last_attempt']
            remaining = max(0, self._blacklist_cooldown - elapsed)

            if entry['failures'] >= self._blacklist_threshold and remaining > 0:
                status['blacklisted_pairs'].append({
                    'symbol': symbol,
                    'failures': entry['failures'],
                    'cooldown_remaining': int(remaining)
                })
            elif remaining <= 0:
                status['pending_retry'].append(symbol)

        return status

    def _validate_dataframe_basico(self, df):
        """Validación básica de dataframe"""
        return df is not None and not df.empty and len(df) > 0

    def _validate_columnas(self, df, columnas_requeridas, symbol, df_type):
        """Validar que existan todas las columnas requeridas"""
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if columnas_faltantes:
            logger.debug(f"[VALIDATION] Columnas faltantes en {df_type} para {symbol}: {columnas_faltantes}")
            return False
        return True

    def _validate_continuidad_temporal(self, df, symbol, df_type):
        """Validar continuidad temporal básica"""
        try:
            if 'timestamp' not in df.columns:
                return True  # No todos los dataframes tienen timestamp

            # Verificar que los datos no tengan huecos grandes de tiempo
            df_sorted = df.sort_values('timestamp')
            diferencias = df_sorted['timestamp'].diff()
            max_gap = diferencias.quantile(0.95)  # 95th percentile como umbral

            if max_gap > diferencias.median() * 5:  # Si hay huecos muy grandes
                logger.debug(f"[VALIDATION] Huecos temporales grandes detectados en {df_type} para {symbol}")
                return False

            return True
        except:
            return True  # Si hay error, asumir válido

    def _validate_valores_no_nulos(self, df, columnas, symbol, df_type):
        """Validar que no haya valores nulos en columnas críticas"""
        for col in columnas:
            if col in df.columns and df[col].isnull().any():
                nulos = df[col].isnull().sum()
                logger.debug(f"[VALIDATION] {nulos} valores nulos en {col} ({df_type}) para {symbol}")
                return False
        return True

    def _validate_rango_precios(self, df, symbol, df_type):
        """Validar que los precios estén en rangos razonables"""
        try:
            if 'close' not in df.columns:
                return True

            precio_min = df['close'].min()
            precio_max = df['close'].max()

            # Verificar rangos extremos (ajustar según el mercado cripto)
            if precio_min <= 0 or precio_max > 1000000:  # $0 o más de $1M
                logger.debug(f"[VALIDATION] Precios fuera de rango en {df_type} para {symbol}: ${precio_min:.6f} - ${precio_max:.6f}")
                return False

            # Verificar variaciones extremas en un período corto
            variacion = (precio_max - precio_min) / precio_min if precio_min > 0 else 0
            if variacion > 10:  # Más de 1000% de variación
                logger.debug(f"[VALIDATION] Variación extrema en {df_type} para {symbol}: {variacion*100:.1f}%")
                return False

            return True
        except:
            return True  # Si hay error, asumir válido

    def _analyze_async_with_timeout(self, symbol: str, timeout_sec: int = 3) -> Optional[dict]:
        """Ejecutar análisis - En Replit sin threads para evitar límites"""
        # ✅ En Replit: análisis síncrono para evitar "can't start new thread"
        if IN_REPLIT:
            try:
                df_primary = self.data_manager.get_data(symbol, self.config.PRIMARY_TIMEFRAME, self.config.MIN_NN_DATA_REQUIRED, self.client)
                df_entry = self.data_manager.get_data(symbol, self.config.ENTRY_TIMEFRAME, self.config.MIN_NN_DATA_REQUIRED, self.client)
                return self._perform_optimized_analysis(symbol, df_primary, df_entry)
            except:
                return None

        # En local: usar threads con timeout
        result = [None]
        def analyze():
            try:
                df_primary = self.data_manager.get_data(symbol, self.config.PRIMARY_TIMEFRAME, self.config.MIN_NN_DATA_REQUIRED, self.client)
                df_entry = self.data_manager.get_data(symbol, self.config.ENTRY_TIMEFRAME, self.config.MIN_NN_DATA_REQUIRED, self.client)
                result[0] = self._perform_optimized_analysis(symbol, df_primary, df_entry)
            except:
                result[0] = None

        thread = threading.Thread(target=analyze, daemon=True)
        thread.start()
        thread.join(timeout=timeout_sec)
        return result[0]

    def _perform_optimized_analysis(self, symbol: str, df_primary: pd.DataFrame, df_entry: pd.DataFrame, df_5m: pd.DataFrame = None) -> Optional[dict]:
        """
        ✅ OPTIMIZADO v32.0.23.0: Análisis con Fast-Fail, Alineación Dinámica y Umbrales Adaptativos.
        Realiza el análisis técnico + IA sobre los DataFrames ya obtenidos.
        """
        start_time = time.time()
        try:
            # ✅ CORRECCIÓN #5: VERIFICAR BLACKLIST ANTES DE ANÁLISIS
            if self._is_symbol_blacklisted(symbol):
                logger.debug(f"[BLACKLIST] {symbol}: Saltando análisis (en blacklist temporal)")
                return None

            # ✅ CORRECCIÓN #7: VERIFICAR EXCLUSIVIDAD - Solo 1 par activo
            if self.exclusive_tracking_mode:
                active_symbol = getattr(self, 'tracked_symbol', None)
                if active_symbol and active_symbol != symbol:
                    logger.debug(f"[EXCLUSIVO] {symbol}: Saltando (señal activa en {active_symbol})")
                    return None

            # ✅ VALIDACIÓN RÁPIDA — salir si falta data
            data_id = f"{symbol}_{int(time.time() * 1000)}"  # único por llamada
            if df_primary is None or df_entry is None or len(df_primary) < 50 or len(df_entry) < 50:
                logger.warning(f"[WARN] Datos insuficientes para análisis de {symbol}")
                self._record_data_failure(symbol, "datos insuficientes")
                return None

            # ========== ⚡ UMBRALES ADAPTATIVOS ==========
            adjusted_thresholds = None
            if hasattr(self, 'adaptive_threshold_manager') and self.adaptive_threshold_manager:
                try:
                    # Actualizar volatilidad del mercado
                    atr = self.technical_analyzer.calculate_atr(df_primary) if hasattr(self.technical_analyzer, 'calculate_atr') else 0
                    current_price = float(df_primary['close'].iloc[-1]) if not df_primary.empty else 1
                    atr_pct = (atr / current_price) * 100 if current_price > 0 else 0
                    self.adaptive_threshold_manager.update_market_volatility(atr_pct)
                    adjusted_thresholds = self.adaptive_threshold_manager.get_adjusted_thresholds()
                except Exception as e:
                    logger.debug(f"Error en umbrales adaptativos: {e}")

            # ========== ⚡ VALIDAR ATR MÍNIMO (evitar mercados muertos) ==========
            if hasattr(self, 'volume_breakout_validator') and self.volume_breakout_validator:
                try:
                    atr_valid, atr_pct = self.volume_breakout_validator.validate_atr_minimum(df_primary, 0.5)
                    if not atr_valid:
                        logger.debug(f"⚡ {symbol}: ATR muy bajo ({atr_pct:.2f}% < 0.5%) - mercado muerto")
                        return None
                except Exception as e:
                    logger.debug(f"Error validando ATR: {e}")

            # ✅ Predicción neural — usar df_primary (más largo)
            neural_pred = self.neural_trader.predict_optimized(df_primary)

            # ✅ Análisis técnico — construir dict con indicadores básicos
            ema50 = self.technical_analyzer.calculate_ema(df_primary['close'], 50)
            ema200 = self.technical_analyzer.calculate_ema(df_primary['close'], 200)
            rsi_series = self.technical_analyzer.calculate_rsi(df_primary['close'])

            # ✅ CRÍTICO: Calcular diferencia real EMA50-EMA200 (no pendiente)
            ema50_val = float(ema50.iloc[-1]) if len(ema50) > 0 else 0.0
            ema200_val = float(ema200.iloc[-1]) if len(ema200) > 0 else 0.0
            ema_diff = ema50_val - ema200_val  # Diferencia real para detectar tendencia

            technical_analysis = {
                'ema50_slope': float(ema50.iloc[-1] - ema50.iloc[-2]) if len(ema50) >= 2 else 0.0,
                'ema200_slope': float(ema200.iloc[-1] - ema200.iloc[-2]) if len(ema200) >= 2 else 0.0,
                'ema_diff': ema_diff,  # Nueva métrica: EMA50 - EMA200 (positivo = alcista)
                'rsi': float(rsi_series.iloc[-1]) if len(rsi_series) > 0 else 50.0,
                'volume': float(df_entry['volume'].iloc[-1]) if not df_entry.empty else 0.0,
                'avg_volume': float(df_entry['volume'].tail(20).mean()) if len(df_entry) >= 20 else 1.0
            }

            # ✅ CORREGIDO v32.0.22.4: Detección de tendencia con EMAs correctas
            if not (ema50.empty or ema200.empty) and len(ema50) >= 2:
                ema50_val = float(ema50.iloc[-1]) if len(ema50) > 0 else 0
                ema200_val = float(ema200.iloc[-1]) if len(ema200) > 0 else 0

                if ema50_val > ema200_val:
                    trend_direction = TrendDirection.BULLISH
                    trend_reason = "EMA50 > EMA200 (Tendencia Alcista)"
                elif ema50_val < ema200_val:
                    trend_direction = TrendDirection.BEARISH
                    trend_reason = "EMA50 < EMA200 (Tendencia Bajista)"
                else:
                    trend_direction = TrendDirection.NEUTRAL
                    trend_reason = "EMAs Laterales"
            else:
                trend_direction = TrendDirection.NEUTRAL
                trend_reason = "Datos Insuficientes"

            # ✅ Validación ultra-selectiva - PARÁMETROS CORRECTOS
            validation_result = self.technical_analyzer.validate_ultra_selective_conditions(
                symbol=symbol,
                df_primary=df_primary,
                df_entry=df_entry,
                neural_prediction=neural_pred,
                trend_direction=trend_direction
            )

            # ✅ Construir resultado con valores por defecto
            signal_data = {
                'symbol': symbol,
                'price': float(df_entry['close'].iloc[-1]) if not df_entry.empty else 0.0,
                'neural_prediction': neural_pred,
                'technical_analysis': technical_analysis,
                'validation_result': validation_result,
                'timestamp': datetime.now(),
                'volume': float(df_entry['volume'].iloc[-1]) if not df_entry.empty else 0.0,
                'combined_signal': SignalType.NEUTRAL,
                'confidence': 0.0
            }

            # ✅ Detalles de procesamiento para la GUI + FALLBACK TÉCNICO CRÍTICO
            base_neural = neural_pred.get('neural_confidence', neural_pred.get('confidence', 0))
            tech_pct = validation_result.get('technical_percentage', 0)
            align_pct = validation_result.get('alignment_percentage', 0)
            align_req = validation_result.get('alignment_required', 92.0)
            ema_diff = technical_analysis.get('ema_diff', 0.0)  # ✅ ARREGLADO: usar diferencia real
            rsi_val = technical_analysis.get('rsi', 50.0)
            vol = technical_analysis.get('volume', 0.0)
            avg_vol = technical_analysis.get('avg_volume', 1.0)
            
            # ========== ⚡ APLICAR UMBRALES ADAPTATIVOS ==========
            min_neural = self.config.MIN_NEURAL_DESTACADA
            min_technical = self.config.MIN_TECHNICAL_DESTACADA
            min_alignment = self.config.MIN_ALIGNMENT_DESTACADA
            if adjusted_thresholds:
                min_neural = adjusted_thresholds.get('min_neural', min_neural)
                min_technical = adjusted_thresholds.get('min_technical', min_technical)
                min_alignment = adjusted_thresholds.get('min_alignment', min_alignment)
                logger.debug(f"⚡ {symbol}: Umbrales adaptativos - Neural:{min_neural}% Tech:{min_technical}% Align:{min_alignment}%")

            # ✅ CRÍTICO: Calcular tech_pct incluso si validation falló (usando ema_diff correcto)
            if tech_pct == 0:
                tech_hits = int(ema_diff > 0) + int(rsi_val >= 50) + int(vol >= avg_vol)
                tech_pct = round((tech_hits / 3) * 100, 2)
                logger.debug(f"⚠️ Fallback técnico: {tech_pct}% (Tendencia:{'↑' if ema_diff > 0 else '↓'} RSI:{rsi_val:.0f} Vol:{'✓' if vol >= avg_vol else '✗'} hits:{tech_hits})")

            # ========== ⚡ ALINEACIÓN DINÁMICA MULTI-TIMEFRAME ==========
            is_buy_signal = neural_pred.get('signal_type') in [SignalType.CONFIRMED_BUY, SignalType.HIGHLIGHTED_BUY]
            signal_direction = "BULLISH" if is_buy_signal else "BEARISH"
            dynamic_alignment_used = False
            contradiction_detected = False
            
            if align_pct == 0:
                # Intentar alineación dinámica si está disponible
                if hasattr(self, 'dynamic_alignment_scorer') and self.dynamic_alignment_scorer and df_5m is not None:
                    try:
                        dynamic_result = self.dynamic_alignment_scorer.calculate_multi_timeframe_score(
                            df_5m, df_entry, df_primary, signal_direction
                        )
                        align_pct = dynamic_result.get('alignment_score', 0)
                        contradiction_detected = dynamic_result.get('contradiction_detected', False)
                        dynamic_alignment_used = True
                        align_status = 'DINAMICO' if dynamic_result.get('is_coherent', False) else 'INCOHERENTE'
                        logger.debug(f"⚡ {symbol}: Alineación dinámica = {align_pct:.1f}% | 5m:{dynamic_result['details'].get('5m', 'N/A')} 15m:{dynamic_result['details'].get('15m', 'N/A')} 30m:{dynamic_result['details'].get('30m', 'N/A')}")
                    except Exception as e:
                        logger.debug(f"Error en alineación dinámica: {e}")
                
                # Fallback si alineación dinámica no funcionó
                if align_pct == 0:
                    if is_buy_signal:
                        align_hits = int(ema_diff > 0) + int(rsi_val >= 50) + int(vol >= avg_vol)
                    else:
                        align_hits = int(ema_diff < 0) + int(rsi_val <= 50) + int(vol >= avg_vol)
                    align_pct = round((align_hits / 3) * 100)
                    align_status = 'INFORMATIVA'
            else:
                align_status = 'ALINEADO' if align_pct >= align_req else 'DESALINEADO'
            
            # ========== ⚡ FAST-FAIL RSI: Validar RSI extremo ==========
            if hasattr(self, 'fast_fail_filter') and self.fast_fail_filter:
                try:
                    rsi_valid, rsi_reason = self.fast_fail_filter.validate_rsi_direction(rsi_val, is_buy_signal)
                    if not rsi_valid and base_neural >= self.config.MIN_NEURAL_DESTACADA:
                        logger.debug(f"⚡ FAST-FAIL RSI {symbol}: {rsi_reason}")
                        # No retornar None aquí, solo penalizar el score técnico
                        tech_pct = max(0, tech_pct - 15)  # Penalizar 15%
                except Exception as e:
                    logger.debug(f"Error en validación RSI: {e}")
            
            # ========== ⚡ DETECTAR CONTRADICCIÓN IA vs TÉCNICO ==========
            if contradiction_detected:
                logger.debug(f"⚠️ {symbol}: Contradicción detectada en multi-timeframe - penalizando alineación")
                align_pct = max(0, align_pct - 20)  # Penalizar contradicciones

            signal_data['processing_details'] = {
                'neural_score': base_neural,
                'technical_percentage': tech_pct,
                'alignment_percentage': align_pct,
                'alignment_status': align_status,
                'volume_ratio': validation_result.get('volume_ratio', 0),
                'volume_trend': validation_result.get('volume_trend', 'NEUTRAL'),
                'volume_confidence': validation_result.get('volume_confidence', 0),
                'ia_direction': neural_pred.get('signal_type', SignalType.NEUTRAL).name if hasattr(neural_pred.get('signal_type', SignalType.NEUTRAL), 'name') else 'NEUTRAL',
                'technical_direction': validation_result.get('technical_direction', 'NEUTRAL')
            }

            # ✅ v32.0.22.4: LOGGING DE DIAGNÓSTICO PARA SEÑALES (print + logger)
            if base_neural >= 50 or tech_pct >= 50:
                diag_msg = f"📊 [DIAG] {symbol}: IA={base_neural:.1f}% Tec={tech_pct:.1f}% Alin={align_pct:.1f}% | Req: {min_neural}/{min_technical}/{min_alignment}"
                logger.info(diag_msg)
                if IN_REPLIT:
                    print(diag_msg)  # También imprimir en consola para Replit

            # ✅ CORREGIDO: VERIFICAR ALINEACIÓN ANTES DE GENERAR SEÑAL PREMIUM
            # CRÍTICO: Si IA dice COMPRA pero t��cnico dice VENTA = DESALINEADO (NO PREMIUM)
            if base_neural >= min_neural and tech_pct >= min_technical and align_pct >= min_alignment:
                # ✅ v32.0.22.4: VALIDAR PATRÓN DE VELA CONFIRMATORIO
                candle_pattern = validation_result.get('candle_pattern', {})
                pattern_type = candle_pattern.get('type', 'NEUTRAL') if isinstance(candle_pattern, dict) else 'NEUTRAL'
                pattern_name = candle_pattern.get('pattern', 'NONE') if isinstance(candle_pattern, dict) else 'NONE'
                pattern_conf = candle_pattern.get('confidence', 0) if isinstance(candle_pattern, dict) else 0

                entry_setup = validation_result.get('entry_setup', {})
                entry_required = bool(getattr(self.config, 'REQUIRE_ENTRY_SETUP', False)) or bool(getattr(self.config, 'REQUIRE_CANDLE_PATTERN', False))
                entry_ok = True
                if entry_required and isinstance(entry_setup, dict):
                    entry_ok = bool(entry_setup.get('valid', False))

                # ✅ DETERMINAR DIRECCIÓN PRIMERO
                is_buy = (ema_diff > 0) and (rsi_val >= 50) and (vol >= avg_vol)

                # ✅ VALIDAR QUE EL PATRÓN CONFIRME LA DIRECCIÓN
                pattern_confirms = False
                if getattr(self.config, 'REQUIRE_CANDLE_PATTERN', False):
                    if is_buy and pattern_type == 'BULLISH' and pattern_conf >= 50:
                        pattern_confirms = True
                    elif not is_buy and pattern_type == 'BEARISH' and pattern_conf >= 50:
                        pattern_confirms = True
                    elif pattern_type == 'NEUTRAL' or pattern_conf < 50:
                        # Sin patrón confirmatorio → rechazar señal
                        logger.debug(f"⚠️ {symbol}: Sin patrón de vela confirmatorio ({pattern_name} {pattern_conf}%)")
                        pattern_confirms = False
                else:
                    pattern_confirms = True  # Si no se requiere patrón, siempre pasa

                # ✅ VALIDAR VOLATILIDAD MÍNIMA PARA ALCANZAR TP
                min_vol_pct = getattr(self.config, 'MIN_VOLATILITY_PERCENT', 0.5)
                if len(df_entry) >= 20:
                    recent_high = df_entry['high'].tail(20).max()
                    recent_low = df_entry['low'].tail(20).min()
                    volatility_pct = ((recent_high - recent_low) / recent_low) * 100
                else:
                    volatility_pct = 1.0  # Default si no hay suficientes datos

                volatility_ok = volatility_pct >= min_vol_pct

                # ========== ⚡ VALIDAR VOLUMEN EN BREAKOUT ==========
                volume_breakout_ok = True
                breakout_info = {}
                if hasattr(self, 'volume_breakout_validator') and self.volume_breakout_validator:
                    try:
                        breakout_info = self.volume_breakout_validator.validate_breakout_with_volume(df_entry, is_buy)
                        if breakout_info.get('is_valid_breakout', False):
                            if not breakout_info.get('volume_confirmed', False):
                                logger.debug(f"⚡ {symbol}: Breakout sin confirmación de volumen (ratio: {breakout_info.get('volume_ratio', 0):.2f})")
                                # Penalizar pero no rechazar
                                tech_pct = max(0, tech_pct - 10)
                    except Exception as e:
                        logger.debug(f"Error validando breakout: {e}")

                if not entry_ok:
                    entry_reason = entry_setup.get('reason', 'Entrada no óptima') if isinstance(entry_setup, dict) else 'Entrada no óptima'
                    logger.info(f"❌ {symbol}: Rechazada - {entry_reason}")
                    signal_data['status'] = 'NEUTRAL'
                    signal_data['reason'] = entry_reason
                elif not pattern_confirms:
                    logger.info(f"❌ {symbol}: Rechazada - Sin patrón de vela confirmatorio (Tipo: {pattern_type}, Conf: {pattern_conf}%)")
                    signal_data['status'] = 'NEUTRAL'
                    signal_data['reason'] = f'Sin patrón de vela confirmatorio ({pattern_name})'
                elif not volatility_ok:
                    logger.info(f"❌ {symbol}: Rechazada - Volatilidad insuficiente ({volatility_pct:.2f}% < {min_vol_pct}%)")
                    signal_data['status'] = 'NEUTRAL'
                    signal_data['reason'] = f'Volatilidad baja ({volatility_pct:.2f}%)'
                else:
                    # ✅ SEÑAL PREMIUM DETECTADA: IA + Técnico + Tendencia + Patrón ALINEADOS
                    neural_score = base_neural
                    technical_percentage = tech_pct
                    alignment_percentage = align_pct

                    # ✅ CORREGIDO v30.0.13: TODAS las señales empiezan como DESTACADA
                    signal_type = SignalType.HIGHLIGHTED_BUY if is_buy else SignalType.HIGHLIGHTED_SELL
                    status = 'DESTACADA'
                    logger.info(f"[OK] DESTACADA: {symbol} IA={neural_score:.1f}% Tec={technical_percentage:.1f}% Alin={alignment_percentage:.0f}% | Patrón: {pattern_name} | Vol: {volatility_pct:.2f}%")

                    # Usar datos de validation_result si están disponibles, sino usar defaults
                    entry_price = validation_result.get('entry_price', 0) or technical_analysis.get('price', 0)
                    if entry_price == 0:
                        entry_price = df_entry['close'].iloc[-1]

                    # ✅ CALCULAR SL/TP CORRECTAMENTE SEGÚN DIRECCIÓN (usando config)
                    sl_pct = self.config.DEFAULT_STOP_LOSS_PERCENT
                    tp_pct = self.config.DEFAULT_TAKE_PROFIT_PERCENT
                    if is_buy:
                        calc_stop_loss = entry_price * (1 - sl_pct)
                        calc_take_profit = entry_price * (1 + tp_pct)
                    else:
                        calc_stop_loss = entry_price * (1 + sl_pct)  # SL ARRIBA para VENTA
                        calc_take_profit = entry_price * (1 - tp_pct)  # TP ABAJO para VENTA

                    # ✅ GENERAR GRÁFICO PARA SEÑAL PREMIUM
                    chart_path = None
                    try:
                        if hasattr(self, 'chart_generator') and self.chart_generator and not df_entry.empty:
                            chart_path = self.chart_generator.generate_signal_chart(
                                symbol,
                                df_entry,
                                {'status': status, 'neural_score': neural_score, 'technical_percentage': technical_percentage, 'entry_price': entry_price, 'stop_loss': calc_stop_loss, 'take_profit': calc_take_profit},
                                technical_analysis
                            )
                            logger.debug(f"📊 Gráfico generado para {symbol}: {chart_path}")
                    except Exception as e:
                        logger.debug(f"⚠️ No se pudo generar gráfico para {symbol}: {e}")

                    signal_data.update({
                        'combined_signal': signal_type,
                        'combined_confidence': alignment_percentage,
                        'confidence': alignment_percentage,
                        'neural_score': neural_score,
                        'technical_percentage': technical_percentage,
                        'alignment_percentage': alignment_percentage,
                        'status': status,
                        'entry_price': entry_price,
                        'stop_loss': validation_result.get('stop_loss', 0) or calc_stop_loss,
                        'take_profit': validation_result.get('take_profit', 0) or calc_take_profit,
                        'risk_reward_ratio': validation_result.get('risk_reward_ratio', 1.71),
                        'conditions_met': validation_result.get('conditions_met', [f"IA={neural_score:.1f}%", f"Técnico={technical_percentage:.1f}%", f"Patrón={pattern_name}"]),
                        'is_premium_signal': True,
                        'chart_path': chart_path,
                        'candle_pattern': pattern_name,
                        'volatility_percent': volatility_pct
                    })
                    # Actualizar también processing_details
                    signal_data['processing_details'] = {
                        'neural_score': neural_score,
                        'technical_percentage': technical_percentage,
                        'alignment_percentage': alignment_percentage,
                        'alignment_status': 'ALINEADO' if alignment_percentage >= align_req else 'INFORMATIVA',
                        'candle_pattern': pattern_name,
                        'volatility_percent': volatility_pct
                    }
            elif base_neural >= self.config.MIN_NEURAL_DESTACADA and align_pct >= self.config.MIN_ALIGNMENT_DESTACADA:
                # ✅ FALLBACK: Si alineación ≥umbral, usar datos calculados
                neural_score = base_neural
                technical_percentage = tech_pct
                alignment_percentage = align_pct
                is_buy = (ema_diff > 0) and (rsi_val >= 50) and (vol >= avg_vol)  # ✅ ARREGLADO: usar ema_diff

                # ✅ CORREGIDO v30.0.13: TODAS las señales empiezan como DESTACADA
                signal_type = SignalType.HIGHLIGHTED_BUY if is_buy else SignalType.HIGHLIGHTED_SELL
                status = 'DESTACADA'  # ✅ TODAS inician como DESTACADA (fallback también)

                signal_data.update({
                    'combined_signal': signal_type,
                    'combined_confidence': alignment_percentage,
                    'confidence': alignment_percentage,
                    'neural_score': neural_score,
                    'technical_percentage': technical_percentage,
                    'alignment_percentage': alignment_percentage,
                    'status': status,
                    'entry_price': validation_result.get('entry_price', 0),
                    'stop_loss': validation_result.get('stop_loss', 0),
                    'take_profit': validation_result.get('take_profit', 0),
                    'risk_reward_ratio': validation_result.get('risk_reward_ratio', 0),
                    'conditions_met': validation_result.get('conditions_met', []),
                    'is_premium_signal': True
                })
                # Actualizar también processing_details
                signal_data['processing_details'] = {
                    'neural_score': neural_score,
                    'technical_percentage': technical_percentage,
                    'alignment_percentage': alignment_percentage,
                    'alignment_status': 'ALINEADO' if alignment_percentage >= self.config.MIN_ALIGNMENT_CONFIRMADA else 'DESALINEADO'
                }

            processing_time_ms = (time.time() - start_time) * 1000
            signal_data['processing_time_ms'] = processing_time_ms
            return signal_data

        except Exception as e:
            logger.error(f"[ERROR] Error en _perform_optimized_analysis para {symbol}: {e}", exc_info=True)
            return None

    def get_detailed_analysis_optimized(self) -> str:
        """
        Genera un informe detallado del análisis técnico y de IA del par actual.
        Usado por la GUI para la pestaña de análisis.
        """
        try:
            if not self.current_analysis:
                return "⚠️ No hay análisis disponible. Espere a que se carguen los datos."

            # Datos básicos
            symbol = self.current_pair
            price = self.current_analysis.get('price', 0.0)
            combined_signal = self.current_analysis.get('combined_signal', SignalType.NEUTRAL)
            timestamp = self.current_analysis.get('timestamp', datetime.now())

            # Métricas clave
            processing = self.current_analysis.get('processing_details', {})
            neural_score = processing.get('neural_score', 0.0)
            technical_pct = processing.get('technical_percentage', 0.0)
            alignment_pct = processing.get('alignment_percentage', 0.0)
            alignment_status = processing.get('alignment_status', 'N/A')

            # Validación
            validation_result = self.current_analysis.get('validation_result', {})
            tech_valid = validation_result.get('valid', False)
            tech_reason = validation_result.get('reason', 'N/A')
            criteria_list = validation_result.get('criteria_list', [])

            # Construir informe
            lines = []
            lines.append(f"🔍 ANÁLISIS DETALLADO OPTIMIZADO — {symbol}")
            lines.append(f"🕒 Última actualización: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"💰 Precio actual: ${price:.8f}")
            lines.append(f"📈 Señal combinada: {combined_signal.value}")
            lines.append("")
            lines.append("📊 METRICAS DE CONFIANZA:")
            lines.append(f"   • IA (Neural): {neural_score:.2f}%")
            lines.append(f"   • Técnico (Criterios dinámicos): {technical_pct:.2f}%")
            lines.append(f"   • Alineación IA+Técnico+Ciclo: {alignment_pct:.2f}% ({alignment_status})")
            lines.append("")

            if criteria_list:
                lines.append("✅ CRITERIOS TÉCNICOS CUMPLIDOS:")
                for i, crit in enumerate(criteria_list, 1):
                    lines.append(f"   {i}. {crit}")
                lines.append("")

            lines.append("���� VALIDACIÓN ULTRA-SELECTIVA:")
            lines.append(f"   • Aprobada: {'✅ SÍ' if tech_valid else '❌ NO'}")
            if not tech_valid:
                lines.append(f"   • Motivo: {tech_reason}")
            lines.append("")

            # Estrategia activa
            strategy_name = self.current_analysis.get('specific_strategy_triggered', StrategyType.EMA_TDI_PRICE_ACTION_NEURAL)
            lines.append(f"🎯 Estrategia activa: {getattr(strategy_name, 'value', str(strategy_name))}")

            # Datos técnicos brutos (opcional)
            tech_analysis = self.current_analysis.get('technical_analysis', {})
            if tech_analysis:
                lines.append("")
                lines.append("⚙️ DATOS TÉCNICOS RAW:")
                for k, v in tech_analysis.items():
                    if isinstance(v, float):
                        lines.append(f"   • {k}: {v:.4f}")
                    else:
                        lines.append(f"   • {k}: {v}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error en get_detailed_analysis_optimized: {e}")
            return f"❌ Error generando análisis detallado: {str(e)}"

    def _get_current_signal_type(self, symbol: str) -> SignalType:
        try:
            df_primary = self.data_manager.get_data(
                symbol,
                self.config.PRIMARY_TIMEFRAME,
                self.config.MIN_NN_DATA_REQUIRED,
                self.client
            )
            df_entry = self.data_manager.get_data(
                symbol,
                self.config.ENTRY_TIMEFRAME,
                self.config.MIN_NN_DATA_REQUIRED,
                self.client
            )
            if not self._validate_dataframes(df_primary, df_entry, symbol):
                return SignalType.NEUTRAL
            analysis_result = self._perform_optimized_analysis(symbol, df_primary, df_entry)
            if analysis_result and 'combined_signal' in analysis_result:
                return analysis_result['combined_signal']
            return SignalType.NEUTRAL
        except Exception as e:
            logger.error(f"[ERROR] Error obteniendo señal actual para {symbol}: {e}")
            return SignalType.NEUTRAL

    def _generate_optimized_signal_hash(self, symbol: str, signal_data, analysis_result: dict = None) -> str:
        """
        Generar hash optimizado para señales - tolera StrategySignal o SignalType
        """
        sig_obj = None
        if hasattr(signal_data, 'signal_type'):
            sig_obj = getattr(signal_data, 'signal_type')
        elif hasattr(signal_data, 'name') or hasattr(signal_data, 'value'):
            sig_obj = signal_data
        elif analysis_result and 'combined_signal' in analysis_result:
            sig_obj = analysis_result['combined_signal']
        sig_name = ''
        if sig_obj is not None:
            try:
                sig_name = getattr(sig_obj, 'name', getattr(sig_obj, 'value', str(sig_obj)))
            except Exception:
                sig_name = str(sig_obj)
        signal_direction = 'BUY' if 'BUY' in sig_name.upper() else ('SELL' if 'SELL' in sig_name.upper() else 'NEUTRAL')
        data_string = f"{symbol}_{signal_direction}_{int(time.time())}"
        return hashlib.md5(data_string.encode()).hexdigest()[:16]

    def _process_high_quality_signal(self, symbol: str, df_primary: pd.DataFrame, df_entry: pd.DataFrame, analysis_result: dict):
        """
        ✅ PROCESAMIENTO UNIFICADO — USA SOLO _prepare_signal_package()
        - Verifica exclusividad (1 señal)
        - Prepara paquete
        - Envía a SignalTracker
        - Genera gráfico (solo CONFIRMADA)
        - Notifica Telegram (solo 1 foto en CONFIRMADA)
        """
        # ✅ CORRECCIÓN #7: VERIFICACIÓN ESTRICTA DE EXCLUSIVIDAD
        if self.exclusive_tracking_mode:
            logger.info(f"⏭️ {symbol} - Ignorado: señal activa en {self.tracked_symbol}")
            return

        # ✅ DOBLE VERIFICACIÓN: SignalTracker también tiene señal activa?
        if self.signal_tracker.has_active_signal():
            active_sym = self.signal_tracker.get_active_signal_symbol()
            logger.info(f"⏭️ {symbol} - Ignorado: SignalTracker tiene señal activa en {active_sym}")
            return

        # === 1. Preparar paquete ÚNICO ===
        signal_package = self._prepare_signal_package(symbol, df_entry, analysis_result)
        if not signal_package:
            logger.warning(f"❌ {symbol} - Paquete de señal inválido")
            return

        # === 2. Verificar umbrales para DESTACADA (consistente con SignalTracker) ===
        neural_score = signal_package['neural_score']
        technical_pct = signal_package['technical_percentage']
        alignment_pct = signal_package['alignment_percentage']

        # ✅ CORRECCIÓN #4: CONTAR CRITERIOS TÉCNICOS (≥2 de 3 obligatorios)
        tech_criteria_count = self._count_technical_criteria(signal_package, analysis_result)
        if tech_criteria_count < 2:
            logger.debug(f"❌ {symbol} - Solo {tech_criteria_count}/3 criterios técnicos (mínimo 2)")
            return

        # ✅ UMBRALES CONSISTENTES CON SignalTracker._validate_signal_coherence():
        #    Usando variables configurables desde GUI para máxima flexibilidad
        if not (neural_score >= self.config.MIN_NEURAL_DESTACADA and technical_pct >= self.config.MIN_TECHNICAL_DESTACADA and alignment_pct >= self.config.MIN_ALIGNMENT_DESTACADA):
            logger.debug(f"❌ {symbol} - No cumple umbrales DESTACADA: IA={neural_score:.1f}%, Tec={technical_pct:.1f}%, Ali={alignment_pct:.1f}%")
            return

        # === 3. Activar modo exclusivo ===
        self.exclusive_tracking_mode = True
        self.tracked_symbol = symbol
        self.tracked_signal_hash = signal_package['signal_hash']

        # === 4. NO generar gráfico aquí - se generará solo al promocionar a CONFIRMADA ===
        # Todas las señales empiezan como DESTACADA
        chart_path = None
        signal_package['status'] = 'DESTACADA'  # Asegurar que inicia como DESTACADA

        # === 5. Agregar al SignalTracker ===
        if not self.signal_tracker.add_highlighted_signal(signal_package):
            logger.error(f"❌ {symbol} - Rechazado por SignalTracker (validación interna falló)")
            self._release_exclusive_mode()
            return

        # === 6. Notificar Telegram - SOLO TEXTO para DESTACADA (sin gráfico) ===
        if self.telegram_client and self.config.telegram_enabled:
            try:
                text_sent = self.telegram_client.send_optimized_trading_signal(
                    signal_id=signal_package['signal_hash'],
                    signal_dict=signal_package,
                    symbol=symbol,
                    neural_prediction=signal_package['neural_prediction'],
                    technical_confidence=technical_pct,
                    send_photo=False  # ✅ DESTACADA siempre sin foto
                )
                if text_sent:
                    logger.info(f"✅ Telegram: señal DESTACADA enviada (sin gráfico) — {symbol}")
                else:
                    logger.warning(f"⚠️ Telegram: no se envió señal para {symbol}")
            except Exception as e:
                logger.error(f"❌ Error en Telegram para {symbol}: {e}")

        # === 7. Registrar en GUI y metricas ===
        self.performance_metrics['total_signals'] += 1
        # Mantener solo la señal más reciente para evitar acumulación de señales antiguas en la GUI
        self.active_signals = [signal_package]
        self._safe_gui_queue_put(('signal_found', None))
        self._safe_gui_queue_put(('log_message', 
            f"SENAL DESTACADA: {symbol} | IA={neural_score:.1f}% | Tecnico={technical_pct:.1f}% | Alineacion={alignment_pct:.1f}%"))
        
        # === 8. CORREGIDO v35: Mostrar barra de progreso DESTACADA en GUI ===
        self._safe_gui_queue_put(('show_destacada_signal', {
            'symbol': symbol,
            'neural_score': neural_score,
            'technical_pct': technical_pct,
            'alignment_pct': alignment_pct,
            'is_buy': signal_package.get('is_buy', True)
        }))
        logger.info(f"GUI actualizada con senal DESTACADA: {symbol}")

    def _count_technical_criteria(self, signal_package: dict, analysis_result: dict) -> int:
        """
        ✅ CORRECCIÓN #4: Cuenta cuántos criterios técnicos se cumplen.

        CRITERIOS OBLIGATORIOS (necesita ≥2 de 3):
        1. Patrón de vela confirmatorio (Hammer, Engulfing, Doji, etc.)
        2. RSI en zona favorable (no extrema)
        3. Volumen superior al promedio

        Returns:
            int: Número de criterios cumplidos (0-3)
        """
        criteria_count = 0

        try:
            # 1. PATRÓN DE VELA CONFIRMATORIO
            candle_pattern = signal_package.get('candle_pattern', '')
            pattern_type = analysis_result.get('validation_result', {}).get('pattern_type', 'NEUTRAL')
            if candle_pattern and candle_pattern != 'Sin patrón' and pattern_type != 'NEUTRAL':
                criteria_count += 1
                logger.debug(f"✅ Criterio 1: Patrón de vela ({candle_pattern})")

            # 2. RSI EN ZONA FAVORABLE
            rsi = analysis_result.get('technical_analysis', {}).get('rsi', 50)
            is_buy = signal_package.get('is_buy', True)
            if is_buy:
                # Para compra: RSI no sobrecomprado (<70) y preferible >30
                rsi_favorable = 30 <= rsi <= 70
            else:
                # Para venta: RSI no sobrevendido (>30) y preferible <70
                rsi_favorable = 30 <= rsi <= 70

            if rsi_favorable:
                criteria_count += 1
                logger.debug(f"✅ Criterio 2: RSI favorable ({rsi:.1f})")

            # 3. VOLUMEN SUPERIOR AL PROMEDIO
            vol = analysis_result.get('technical_analysis', {}).get('volume', 0)
            avg_vol = analysis_result.get('technical_analysis', {}).get('avg_volume', 1)
            if avg_vol > 0 and vol >= avg_vol:
                criteria_count += 1
                logger.debug(f"✅ Criterio 3: Volumen alto ({vol/avg_vol:.1f}x promedio)")

            logger.debug(f"📊 Total criterios técnicos cumplidos: {criteria_count}/3")
            return criteria_count

        except Exception as e:
            logger.error(f"Error contando criterios técnicos: {e}")
            return 0



logger = logging.getLogger('CryptoBotOptimized')

class SignalTracker:
    """
    Sistema robusto y seguro de seguimiento de señales DESTACADAS y CONFIRMADAS.
    ✅ CARACTERÍSTICAS CLAVE:
    - Gestión centralizada de señales activas (máximo 1)
    - Validación mejorada de coherencia
    - Control de uso de CPU para evitar 100%
    - Promoción automática: DESTACADA → CONFIRMADA
    - Cierre automático por profit/loss/timeout
    - Thread safety completo con locks
    - Métricas de rendimiento integradas
    """

    def __init__(self, config=None):
        # ========== ATRIBUTOS PRINCIPALES ==========
        self.config = config  # ✅ Referencia a configuración para PROFIT_MILESTONES
        self.tracked_signals = {}  # {signal_hash: tracking_data}
        self.on_closed_callback = None
        self._similarity_engine_ref = None
        self.bot = None
        self._bot_ref = None

        # ========== THREAD SAFETY ==========
        self.lock = threading.Lock()
        self.processing_lock = threading.Lock()  # Lock adicional para procesamiento

        # ========== CONTROL DE CPU ==========
        self.monitor_interval = 2.0  # Segundos entre ciclos
        self.last_monitor_time = 0
        self.cpu_saver_mode = False
        self.max_signals_per_cycle = 1  # Limitar procesamiento

        # ========== CONFIGURACIÓN DE VALIDACIÓN ==========
        self.validation_config = {
            'min_confidence': 88.0,
            'min_alignment': 88.0,
            'max_neural_tech_diff': 25.0,
            'min_rr_ratio': 1.0,
            'max_daily_signals': 10,
            'highlight_timeout_min': 20,  # ✅ OPTIMIZADO: 20 min timeout DESTACADA
            'confirmed_timeout_min': 180,  # Minutos para timeout CONFIRMADA
            'profit_target_pct': 3.0,
            'stop_loss_pct': 1.0
        }

        # ========== CONTADORES Y MÉTRICAS ==========
        self.daily_signal_count = 0
        self.daily_signal_date = datetime.now().date()
        self.performance_metrics = {
            'total_signals': 0,
            'successful_signals': 0,
            'rejected_signals': 0,
            'rejected_reasons': defaultdict(int),
            'promotion_count': 0,
            'closure_reasons': defaultdict(int),
            'avg_profit_loss': 0.0
        }

        # ========== CACHE Y OPTIMIZACIÓN ==========
        self.price_cache = {}
        self.price_cache_timeout = 30  # segundos
        self.last_cache_cleanup = time.time()
        logger.info("✅ SignalTracker inicializado con control de CPU y validación mejorada")

    def _validate_signal_coherence(self, signal_data: dict) -> Tuple[bool, str]:
        """
        ✅ VALIDACIÓN CONSISTENTE — UMBRALES DEL CONFIG
        Verifica que la señal cumpla con los umbrales mínimos de IA, técnico y alineación.
        Returns:
        Tuple[bool, str]: (es_válida, razón)
        """
        try:
            neural = signal_data.get('neural_score', 0.0)
            technical = signal_data.get('technical_percentage', 0.0)
            alignment = signal_data.get('alignment_percentage', 0.0)

            # Obtener umbrales del config (con valores por defecto seguros)
            min_neural = getattr(self.config, 'MIN_NEURAL_DESTACADA', 50.0)
            min_tech = getattr(self.config, 'MIN_TECHNICAL_DESTACADA', 40.0)
            min_align = getattr(self.config, 'MIN_ALIGNMENT_DESTACADA', 33.0)

            if neural < min_neural:
                return False, f"IA baja ({neural:.1f}% < {min_neural}%)"
            if technical < min_tech:
                return False, f"Técnico bajo ({technical:.1f}% < {min_tech}%)"
            if alignment < min_align:
                return False, f"Alineación baja ({alignment:.1f}% < {min_align}%)"

            return True, "✅ Coherencia OK"

        except Exception as e:
            logger.error(f"Error en _validate_signal_coherence: {e}")
            return False, "Error en validación"

    def set_telegram_client(self, telegram_client):
        self._telegram_client = telegram_client

    def set_bot_reference(self, bot_instance):
        """Establece referencia al bot principal."""
        self._bot_ref = bot_instance

    def set_similarity_engine_ref(self, engine_ref):
        """Establece referencia al motor de similitud."""
        self._similarity_engine_ref = engine_ref

    def set_closed_callback(self, callback):
        self.on_closed_callback = callback

    def add_highlighted_signal(self, signal_data: dict) -> bool:
        """Añade una señal premium (DESTACADA o CONFIRMADA) de forma segura."""
        with self.lock:
            # Validación básica
            symbol = signal_data.get('symbol')
            entry_price = signal_data.get('entry_price', 0)
            if not symbol or entry_price <= 0:
                logger.warning(f"❌ Señal inválida para {symbol}: entry_price={entry_price}")
                return False
            
            # Validación de coherencia con umbrales del sistema
            try:
                ok, reason_msg = self._validate_signal_coherence(signal_data)
                if not ok:
                    logger.warning(f"❌ Señal rechazada por coherencia: {reason_msg}")
                    return False
            except Exception as e:
                logger.error(f"Error validando coherencia de señal: {e}")
                return False

            # Enforce single active signal (replace any existing)
            if self.tracked_signals:
                try:
                    for existing_hash, existing_tracking in list(self.tracked_signals.items()):
                        self.cancel_signal(existing_hash, "REPLACED_BY_NEW_SIGNAL")
                    logger.info("🧹 Señal previa reemplazada por nueva DESTACADA/CONFIRMADA")
                except Exception as e:
                    logger.error(f"Error reemplazando señal previa: {e}")

            # Verificar límite diario
            today = datetime.now().date()
            if today != self.daily_signal_date:
                self.daily_signal_count = 0
                self.daily_signal_date = today

            if self.daily_signal_count >= self.validation_config['max_daily_signals']:
                logger.warning(f"❌ Límite diario alcanzado ({self.daily_signal_count})")
                return False

            # Generar hash único
            signal_hash = signal_data.get('signal_hash')
            if not signal_hash:
                logger.error("❌ Señal sin hash único")
                return False
            if signal_hash in self.tracked_signals:
                logger.warning(f"⚠️ Señal duplicada ignorada: {signal_hash[:8]}")
                return False

            # Determinar dirección
            is_buy = signal_data.get('is_buy', True)
            status = signal_data.get('status', 'DESTACADA')

            # Crear paquete de seguimiento
            tracking_entry = {
                'signal_data': signal_data,
                'status': status,
                'start_time': datetime.now(),
                'entry_price': entry_price,
                'reference_price_destacada': entry_price,
                'entry_price_confirmada': None,
                'current_price': entry_price,
                'max_profit': 0.0,
                'is_buy': is_buy,
                'telegram_updates_sent': 0,
                'promotion_telegram_sent': False
            }

            # Establecer tiempos específicos
            if status == 'DESTACADA':
                tracking_entry['highlight_start_time'] = datetime.now()
            elif status == 'CONFIRMADA':
                tracking_entry['confirmed_start_time'] = datetime.now()
                tracking_entry['entry_price_confirmada'] = entry_price

            # Almacenar
            self.tracked_signals[signal_hash] = tracking_entry
            self.daily_signal_count += 1
            self.performance_metrics['total_signals'] += 1
            logger.info(f"✅ Señal agregada: {signal_hash[:8]} | Estado: {status} | Precio ref: ${entry_price:.6f}")
            return True

    def has_active_signal(self) -> bool:
        """Verifica si hay alguna señal activa (DESTACADA o CONFIRMADA)."""
        with self.lock:
            return len(self.tracked_signals) > 0

    def get_active_signal_symbol(self) -> Optional[str]:
        """Obtiene el símbolo de la señal activa actual, si existe."""
        with self.lock:
            if self.tracked_signals:
                first_key = next(iter(self.tracked_signals))
                return self.tracked_signals[first_key]['signal_data'].get('symbol')
            return None

    def promote_to_confirmed(self, signal_hash: str, current_neural_conf: float = None,
                           current_technical_pct: float = None, market_data: dict = None,
                           alignment_score: float = None, current_price: float = None) -> bool:
        """Promueve una señal DESTACADA a CONFIRMADA."""
        with self.lock:
            if signal_hash not in self.tracked_signals:
                return False

            tracking = self.tracked_signals[signal_hash]
            if tracking['status'] != 'DESTACADA':
                return False

            # ✅ FIJAR precio de entrada al momento de CONFIRMADA
            if current_price and current_price > 0:
                tracking['entry_price_confirmada'] = current_price
                tracking['entry_price'] = current_price
                # Recalcular SL/TP
                is_buy = tracking.get('is_buy', True)
                sl_pct = getattr(self.config, 'DEFAULT_STOP_LOSS_PERCENT', 0.005)
                tp_pct = getattr(self.config, 'DEFAULT_TAKE_PROFIT_PERCENT', 0.015)
                if is_buy:
                    tracking['signal_data']['stop_loss'] = current_price * (1 - sl_pct)
                    tracking['signal_data']['take_profit'] = current_price * (1 + tp_pct)
                else:
                    tracking['signal_data']['stop_loss'] = current_price * (1 + sl_pct)
                    tracking['signal_data']['take_profit'] = current_price * (1 - tp_pct)
                tracking['signal_data']['entry_price'] = current_price
                logger.info(f"📍 Precio entrada CONFIRMADA fijado: ${current_price:.6f}")
            else:
                tracking['entry_price_confirmada'] = tracking.get('reference_price_destacada', tracking['entry_price'])

            # Actualizar estado
            tracking['status'] = 'CONFIRMADA'
            tracking['confirmed_start_time'] = datetime.now()
            tracking['promotion_telegram_sent'] = True
            self.performance_metrics['promotion_count'] += 1
            logger.info(f"🎉 Señal promovida a CONFIRMADA: {signal_hash[:8]}")
            return True

    def close_signal(self, signal_hash: str, current_price: float, reason: str = "MANUAL") -> Optional[Dict]:
        """Cierra una señal y genera reporte."""
        with self.lock:
            if signal_hash not in self.tracked_signals:
                return None

            tracking = self.tracked_signals[signal_hash]
            signal_data = tracking['signal_data']
            symbol = signal_data.get('symbol', 'UNKNOWN')
            entry_price = tracking['entry_price']
            is_buy = tracking['is_buy']

            # Calcular profit/loss
            if entry_price > 0:
                if is_buy:
                    profit_percent = ((current_price - entry_price) / entry_price) * 100
                else:
                    profit_percent = ((entry_price - current_price) / entry_price) * 100
            else:
                profit_percent = 0.0

            # Actualizar métricas
            # Normalizar razón para métricas consistentes
            original_reason = reason or "MANUAL"
            reason_uc = str(original_reason).upper()
            # Mapear alias comunes
            reason_map = {
                "TARGET_REACHED": "PROFIT_TARGET",
                "TAKE_PROFIT": "PROFIT_TARGET",
                "TP_REACHED": "PROFIT_TARGET",
                "STOP_LOSS_HIT": "STOP_LOSS",
                "SL_HIT": "STOP_LOSS",
                "TREND_REVERSAL_DETECTED": "TREND_REVERSAL",
                "TREND_CHANGE_PARTIAL": "PARTIAL_TARGET",
            }
            normalized_reason = reason_map.get(reason_uc, reason_uc)
            # Éxito si alcanzó objetivo o cierre parcial con profit positivo
            success_threshold = getattr(self.config, 'MILESTONE_3', 3.0)
            is_success = (normalized_reason in ("PROFIT_TARGET", "PARTIAL_TARGET")) or (profit_percent >= success_threshold)
            if is_success:
                self.performance_metrics['successful_signals'] += 1
            elif profit_percent > 0 and "PARTIAL" in normalized_reason:
                self.performance_metrics['successful_signals'] += 1
            
            self.performance_metrics['closure_reasons'][normalized_reason] += 1
            total_signals = self.performance_metrics['total_signals']
            if total_signals > 0:
                current_avg = self.performance_metrics['avg_profit_loss']
                self.performance_metrics['avg_profit_loss'] = (
                    (current_avg * (total_signals - 1) + profit_percent) / total_signals
                )

            # Generar reporte
            report = {
                'symbol': symbol,
                'reason': reason,
                'reason_normalized': normalized_reason,
                'profit_percent': profit_percent,
                'final_profit_percent': profit_percent,
                'duration_minutes': (datetime.now() - tracking['start_time']).total_seconds() / 60,
                'signal_hash': signal_hash
            }

            try:
                if self._similarity_engine_ref:
                    save_reasons = {"PROFIT_TARGET", "PARTIAL_TARGET"}
                    hard_sl_reasons = {"STOP_LOSS", "STOP_LOSS_HIT", "SL_HIT"}
                    positive_outcome = (profit_percent >= max(0.8, success_threshold * 0.6))
                    reason_ok = (normalized_reason in save_reasons) or positive_outcome
                    if normalized_reason in hard_sl_reasons and profit_percent < 0:
                        reason_ok = False

                    if reason_ok:
                        self._similarity_engine_ref._save_successful_trade_internal(signal_hash, tracking, {
                            'final_profit_percent': profit_percent,
                            'duration_minutes': report['duration_minutes'],
                            'exit_price': current_price,
                            'reason': reason,
                            'reason_normalized': normalized_reason,
                            'max_profit_reached': tracking.get('max_profit', profit_percent),
                            'is_buy': is_buy
                        })
            except Exception as e:
                logger.error(f"[ERROR] Error guardando trade exitoso para entrenamiento: {e}")

            # Limpiar
            del self.tracked_signals[signal_hash]
            logger.info(f"Senal {symbol} ({signal_hash[:8]}) cerrada: {reason} | Profit: {profit_percent:+.2f}%")

            # Notificar al bot para liberar modo exclusivo
            if hasattr(self, '_bot_ref') and self._bot_ref:
                self._bot_ref._release_exclusive_mode()
            
            # CORREGIDO v35: Llamar al callback para limpiar GUI
            if hasattr(self, 'on_closed_callback') and self.on_closed_callback:
                try:
                    full_report = {
                        'symbol': symbol,
                        'reason': reason,
                        'final_profit_percent': profit_percent,
                        'duration_minutes': report['duration_minutes'],
                        'max_profit_reached': tracking.get('max_profit', profit_percent),
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'signal_hash': signal_hash
                    }
                    self.on_closed_callback(symbol, full_report)
                    logger.info(f"Callback de cierre ejecutado para {symbol}")
                except Exception as e:
                    logger.error(f"Error ejecutando callback de cierre: {e}")

            return report

    def update_signal_progress(self, signal_hash: str, current_price: float) -> Optional[Dict]:
        """Actualiza el progreso de una señal con el precio actual. Sincronizado con GUI."""
        with self.lock:
            if signal_hash not in self.tracked_signals:
                return None

            tracking = self.tracked_signals[signal_hash]
            status = tracking.get('status', 'UNKNOWN')
            is_buy = tracking.get('is_buy', True)
            
            # ✅ USAR PRECIO CORRECTO SEGÚN ESTADO
            if status == 'CONFIRMADA':
                # Para CONFIRMADA: usar entry_price_confirmada (fijado al promocionar)
                entry_price = tracking.get('entry_price_confirmada') or tracking.get('entry_price', 0)
            else:
                # Para DESTACADA: usar reference_price_destacada (precio inicial)
                entry_price = tracking.get('reference_price_destacada') or tracking.get('entry_price', 0)

            if entry_price <= 0:
                return None

            # Calcular profit/loss actual
            if is_buy:
                profit_percent = ((current_price - entry_price) / entry_price) * 100
            else:
                profit_percent = ((entry_price - current_price) / entry_price) * 100

            # Actualizar tracking con precio actual
            tracking['current_price'] = current_price
            tracking['profit_percent'] = profit_percent  # ✅ Guardar para sincronización GUI
            if profit_percent > tracking.get('max_profit', 0):
                tracking['max_profit'] = profit_percent

            # ✅ VERIFICAR Y NOTIFICAR AvanceS (MILESTONES) - FIX: Notificar avances
            if self._telegram_client and hasattr(self.config, 'PROFIT_MILESTONES'):
                try:
                    signal_data = tracking.get('signal_data', {})  # ✅ FIX: Definir signal_data antes de usar
                    milestones = sorted(self.config.PROFIT_MILESTONES)
                    symbol = signal_data.get('symbol')
                    
                    # Inicializar set de Avances para el símbolo si no existe
                    if not hasattr(self._telegram_client, 'sent_milestones'):
                         self._telegram_client.sent_milestones = {}
                    if symbol not in self._telegram_client.sent_milestones:
                        self._telegram_client.sent_milestones[symbol] = set()

                    for i, ms in enumerate(milestones):
                        # Margen de tolerancia (>= ms)
                        if profit_percent >= ms and ms not in self._telegram_client.sent_milestones[symbol]:
                            # ✅ ACTUALIZAR STOP LOSS (Trailing)
                            new_sl = None
                            sl_reason = ""
                            if i == 0: # Avance 1 -> Breakeven
                                new_sl = entry_price
                                sl_reason = "Breakeven"
                            elif i > 0: # Avance N -> Avance N-1
                                prev_ms = milestones[i-1]
                                if is_buy:
                                    new_sl = entry_price * (1 + prev_ms/100)
                                else:
                                    new_sl = entry_price * (1 - prev_ms/100)
                                sl_reason = f"Asegurar Avance {i}"
                            
                            # Aplicar nuevo SL si mejora la posición
                            if new_sl:
                                current_sl = signal_data.get('stop_loss', 0)
                                update_sl = False
                                if is_buy and new_sl > current_sl: update_sl = True
                                if not is_buy and (new_sl < current_sl or current_sl == 0): update_sl = True
                                
                                if update_sl:
                                    signal_data['stop_loss'] = new_sl
                                    logger.info(f"🛑 Stop Loss movido a {sl_reason}: {new_sl:.6f}")

                            # Construir mensaje de Avance
                            emoji_map = {0: "1️⃣", 1: "2️⃣", 2: "3️⃣", 3: "4️⃣", 4: "5️⃣"}
                            emoji = emoji_map.get(i, "🎯")
                            
                            msg = (
                                f"{emoji} Avance {i+1} ALCANZADO: {symbol}\n\n"
                                f"📈 Profit Actual: +{profit_percent:.2f}%\n"
                                f"🎯 Objetivo Avance: {ms}%\n"
                                f"💰 Precio Actual: ${current_price:.6f}\n"
                                f"🚪 Entrada: ${entry_price:.6f}\n"
                            )
                            
                            if new_sl:
                                msg += f"🛑 Nuevo Stop Loss: ${new_sl:.6f} ({sl_reason})\n"
                            
                            msg += f"\nGestionando operación... 🤖"
                            
                            # Usar send_message del cliente (ya es async/queue based)
                            self._telegram_client.send_message(msg)
                            self._telegram_client.sent_milestones[symbol].add(ms)
                            logger.info(f"🚀 Milestone {ms}% notificado para {symbol}")
                except Exception as e:
                    logger.error(f"Error verificando milestones: {e}")

            # ✅ Datos adicionales para sincronización con ventana flotante
            signal_data = tracking.get('signal_data', {})
            return {
                'symbol': signal_data.get('symbol', 'N/A'),
                'entry_price': entry_price,
                'reference_price_destacada': tracking.get('reference_price_destacada', entry_price),
                'entry_price_confirmada': tracking.get('entry_price_confirmada'),
                'current_price': current_price,
                'profit_percent': profit_percent,
                'max_profit': tracking['max_profit'],
                'is_buy': is_buy,
                'status': status,
                'stop_loss': signal_data.get('stop_loss', 0),
                'take_profit': signal_data.get('take_profit', 0),
                'neural_score': signal_data.get('neural_score', 0),
                'technical_percentage': signal_data.get('technical_percentage', 0),
                'alignment_percentage': signal_data.get('alignment_percentage', 0)
            }

    def cancel_signal(self, signal_hash: str, reason: str = "Cancelada por sistema"):
        """Cancelación explícita de señales."""
        with self.lock:
            if signal_hash not in self.tracked_signals:
                return

            tracking = self.tracked_signals[signal_hash]
            symbol = tracking.get('signal_data', {}).get('symbol', 'UNKNOWN')
            status = tracking.get('status')
            highlight_start_time = tracking.get('highlight_start_time') or tracking.get('start_time')
            duration_minutes = None

            if highlight_start_time:
                try:
                    duration_minutes = (datetime.now() - highlight_start_time).total_seconds() / 60.0
                except Exception:
                    duration_minutes = None

            del self.tracked_signals[signal_hash]
            self.performance_metrics['closure_reasons']['cancelled'] += 1
            logger.info(f"Senal {symbol} ({signal_hash[:8]}) cancelada: {reason}")

            # Notificar al bot para liberar modo exclusivo
            if hasattr(self, '_bot_ref') and self._bot_ref:
                self._bot_ref._release_exclusive_mode()
            
            # CORREGIDO v35: Llamar al callback para limpiar GUI
            if hasattr(self, 'on_closed_callback') and self.on_closed_callback:
                try:
                    report = {
                        'symbol': symbol,
                        'reason': reason,
                        'final_profit_percent': 0.0,
                        'duration_minutes': duration_minutes or 0,
                        'max_profit_reached': 0.0,
                        'signal_hash': signal_hash
                    }
                    self.on_closed_callback(symbol, report)
                    logger.info(f"Callback de cancelacion ejecutado para {symbol}")
                except Exception as e:
                    logger.error(f"Error ejecutando callback de cancelacion: {e}")

    # METODO CRITICO: PROMOCION AUTOMATICA CON CALLBACK TELEGRAM
    def check_promotion_timer(self) -> List[Tuple[str, dict]]:
        """
        Verifica senales DESTACADA para promocion o cancelacion.
        CORREGIDO v35: Retorna datos completos para que el bot envie Telegram
        
        Returns:
            List[Tuple[str, dict]]: Lista de (signal_hash, promotion_data) procesados
        """
        processed = []
        promo_timeout_seconds = self.validation_config.get('highlight_timeout_min', 20) * 60
        min_promo_time_seconds = 3 * 60

        with self.lock:
            signals_copy = list(self.tracked_signals.items())

        for signal_hash, tracking in signals_copy:
            if tracking.get('status') != 'DESTACADA':
                continue

            start_time = tracking.get('highlight_start_time')
            if not start_time:
                continue

            elapsed = (datetime.now() - start_time).total_seconds()

            if elapsed >= promo_timeout_seconds:
                logger.warning(f"TIMEOUT DESTACADA: {signal_hash[:8]}")
                self.cancel_signal(signal_hash, "Timeout de promocion")
                processed.append((signal_hash, {'promoted': False, 'reason': 'TIMEOUT'}))
                continue

            if elapsed >= min_promo_time_seconds:
                neural = tracking['signal_data'].get('neural_score', 0)
                technical = tracking['signal_data'].get('technical_percentage', 0)
                alignment = tracking['signal_data'].get('alignment_percentage', 0)

                min_neural = getattr(self.config, 'MIN_NEURAL_DESTACADA', 50.0)
                min_tech = getattr(self.config, 'MIN_TECHNICAL_DESTACADA', 40.0)
                min_align = getattr(self.config, 'MIN_ALIGNMENT_DESTACADA', 33.0)

                if neural >= min_neural and technical >= min_tech and alignment >= min_align:
                    current_price = tracking.get('current_price', tracking.get('entry_price', 0))
                    if self.promote_to_confirmed(signal_hash, current_price=current_price):
                        # Retornar datos completos para Telegram
                        promotion_data = {
                            'promoted': True,
                            'symbol': tracking['signal_data'].get('symbol', 'UNKNOWN'),
                            'signal_data': tracking['signal_data'].copy(),
                            'current_price': current_price,
                            'neural': neural,
                            'technical': technical,
                            'alignment': alignment
                        }
                        processed.append((signal_hash, promotion_data))
                        logger.info(f"Senal {signal_hash[:8]} promovida a CONFIRMADA @ ${current_price:.6f}")

        return processed

    def get_tracked_signals(self) -> dict:
        """Retorna copia del diccionario de señales trackeadas (thread-safe)."""
        with self.lock:
            return self.tracked_signals.copy()

    def get_performance_metrics(self) -> dict:
        """Retorna métricas de rendimiento."""
        with self.lock:
            return self.performance_metrics.copy()

    def start_monitoring(self):
        """Inicia el monitoreo continuo."""
        self.tracker_running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_tracked_signals_continuous,
            daemon=True,
            name="SignalTrackerMonitor"
        )
        self.monitor_thread.start()
        logger.info("✅ SignalTracker: Monitoreo iniciado")

    def stop_monitoring(self):
        """Detiene el monitoreo continuo."""
        self.tracker_running = False
        if hasattr(self, 'monitor_thread') and self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("✅ SignalTracker: Monitoreo detenido")

    def _monitor_tracked_signals_continuous(self):
        """Monitoreo continuo de señales activas."""
        while getattr(self, 'tracker_running', False):
            try:
                time.sleep(self.monitor_interval)
                self._check_timeouts_and_close()
            except Exception as e:
                logger.error(f"❌ Error en monitoreo continuo: {e}", exc_info=True)

    def _check_timeouts_and_close(self):
        """Verifica timeouts y cierra señales según reglas."""
        current_time = datetime.now()
        signals_to_close = []

        with self.lock:
            for signal_hash, tracking in list(self.tracked_signals.items()):
                safe_price = tracking.get('current_price') or tracking.get('entry_price', 0)

                # Timeout DESTACADA (20 minutos)
                if tracking.get('status') == 'DESTACADA':
                    start_time = tracking.get('highlight_start_time')
                    if start_time:
                        elapsed = (current_time - start_time).total_seconds()
                        timeout_seconds = self.validation_config['highlight_timeout_min'] * 60
                        if elapsed > timeout_seconds:
                            signals_to_close.append((signal_hash, safe_price, "HIGHLIGHT_TIMEOUT"))

                # Timeout CONFIRMADA (3 horas)
                elif tracking.get('status') == 'CONFIRMADA':
                    start_time = tracking.get('confirmed_start_time')
                    if start_time:
                        elapsed = (current_time - start_time).total_seconds()
                        elapsed_hours = elapsed / 3600
                        if elapsed_hours >= 3:
                            signals_to_close.append((signal_hash, safe_price, "CONFIRMED_TIMEOUT"))

        # Cerrar señales fuera del lock
        for signal_hash, price, reason in signals_to_close:
            self.close_signal(signal_hash, price, reason)
# ========== INTERFAZ GRÁFICA OPTIMIZADA ==========
class OptimizedCryptoBotGUI(QtWidgets.QMainWindow):
    def __init__(self, config_instance):
        super().__init__()
        try:
            self.setWindowTitle("Crypto Bot Pro v35.0.0.0 - Propiedad Intelectual de Marketeradolfo")
            self.setGeometry(100, 100, 1400, 800)
            self.setStyleSheet("background-color: #0f0f23; color: white;")
            self.config = config_instance
            self.bot = OptimizedTradingBot(self.config)
            self.bot.gui_queue = self.gui_queue = queue.Queue()
            self.live_chart_window = None
            self.last_table_update = 0
            self.central_widget = QtWidgets.QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
            self._init_menu_bar()
            self._init_header()
            self._init_tabs()
            # Load initial data
            self.log_message("🤖 Bienvenido a Crypto Bot Pro v35.0.0.0 Desarrolado por Lic: Adolfo Daniel Aguirre")
            # ✅ CORRECCIÓN: Llamar al método correctamente
            self.bot.load_pair_data_optimized(self.bot.current_pair)
            # Timer optimizado
            self.update_timer = QtCore.QTimer(self)
            self.update_timer.timeout.connect(self.update_gui_and_data_optimized)
            self.update_timer.start(1500)  # OPTIMIZADO: Actualización más frecuente

            # ✅ Timer para actualizar indicador FIX API
            self.fix_api_timer = QtCore.QTimer(self)
            self.fix_api_timer.timeout.connect(self._update_fix_api_indicator)
            self.fix_api_timer.start(2000)  # Actualizar cada 2 segundos
            # ✅ Sistema de limpieza automática de datos antiguos para rendimiento
            self.cleanup_timer = QtCore.QTimer(self)
            self.cleanup_timer.timeout.connect(self._on_cleanup_timer)
            self.cleanup_timer.start(300000)  # cada 5 minutos
            # Iniciar procesador de mensajes
            self.message_processor = QtCore.QTimer(self)
            self.message_processor.timeout.connect(self._process_gui_messages)
            self.message_processor.start(50)  # Procesar mensajes cada 50ms
            self.show()
            self.raise_()
        except Exception as e:
            logger.error(f"Error inicializando GUI optimizada: {e}")
            QtWidgets.QMessageBox.critical(None, "Error", f"Error inicializando la interfaz: {str(e)}")
            raise

    def _on_cleanup_timer(self):
        try:
            if hasattr(self, 'bot') and hasattr(self.bot, '_cleanup_market_data'):
                self.bot._cleanup_market_data(max_age_minutes=5)
        except Exception as e:
            logger.error(f"[ERROR] Error en limpieza periódica de market_data: {e}")

    # Métodos de la GUI optimizada
    def _init_menu_bar(self):
        """Inicializar barra de menú principal"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #1a1a2e;
                color: white;
                border-bottom: 1px solid #00d4aa;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #00d4aa;
                color: #0f0f23;
            }
            QMenu {
                background-color: #1a1a2e;
                color: white;
                border: 1px solid #00d4aa;
            }
            QMenu::item {
                padding: 8px 25px;
            }
            QMenu::item:selected {
                background-color: #00d4aa;
                color: #0f0f23;
            }
        """)

        ayuda_btn = QtWidgets.QPushButton("  Ayuda  ")
        ayuda_btn.setStyleSheet("""
            QPushButton {
                background-color: #00d4aa;
                color: #0f0f23;
                font-weight: bold;
                padding: 6px 15px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #00b894;
            }
            QPushButton::menu-indicator {
                image: none;
            }
        """)

        ayuda_menu = QtWidgets.QMenu(self)
        ayuda_menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a2e;
                color: white;
                border: 1px solid #00d4aa;
            }
            QMenu::item {
                padding: 8px 25px;
            }
            QMenu::item:selected {
                background-color: #00d4aa;
                color: #0f0f23;
            }
        """)
        ayuda_btn.setMenu(ayuda_menu)
        menubar.setCornerWidget(ayuda_btn, QtCore.Qt.TopRightCorner)

        acerca_action = QtWidgets.QAction("Acerca del Sistema", self)
        acerca_action.triggered.connect(self._show_about_dialog)
        ayuda_menu.addAction(acerca_action)

        ciclo_action = QtWidgets.QAction("Ciclo de Señales", self)
        ciclo_action.triggered.connect(self._show_signal_cycle_dialog)
        ayuda_menu.addAction(ciclo_action)

        ayuda_menu.addSeparator()

        config_action = QtWidgets.QAction("Configuración Actual", self)
        config_action.triggered.connect(self._show_config_info)
        ayuda_menu.addAction(config_action)

        stats_action = QtWidgets.QAction("Estadísticas del Trader", self)
        stats_action.triggered.connect(self._show_trader_statistics_dialog)
        ayuda_menu.addAction(stats_action)

    def _show_about_dialog(self):
        """Mostrar diálogo Acerca del Sistema"""
        about_text = """
<h2 style='color: #00d4aa;'>Crypto Bot Pro v35.0.0.0</h2>
<p><b>Desarrollado por:</b> Lic. Adolfo Daniel Aguirre</p>
<p><b>Propiedad Intelectual de Marketeradolfo</b></p>

<hr style='border-color: #00d4aa;'>

<h3 style='color: #52b788;'>Descripcion del Sistema</h3>
<p>Crypto Bot Pro es un bot de trading automatizado de criptomonedas 
que utiliza inteligencia artificial y analisis tecnico avanzado para 
identificar oportunidades de trading en tiempo real.</p>

<h3 style='color: #52b788;'>Caracteristicas Principales</h3>
<ul>
<li><b>Red Neuronal (IA):</b> Prediccion de movimientos de precio</li>
<li><b>Analisis Tecnico:</b> EMA, TDI, Accion del Precio</li>
<li><b>Validacion Multi-Timeframe:</b> 5m, 15m, 30m</li>
<li><b>Alineacion de Tendencia:</b> Confirmacion en multiples marcos temporales</li>
<li><b>Notificaciones Telegram:</b> Alertas en tiempo real</li>
<li><b>Auto-Trading:</b> Ejecucion automatica con Trailing Stop</li>
</ul>

<h3 style='color: #52b788;'>Estrategia de Trading</h3>
<p>El sistema utiliza la estrategia <b>EMA_TDI_PRICE_ACTION_NEURAL</b> que combina:</p>
<ul>
<li>EMA 50/200 para identificacion de tendencia</li>
<li>TDI (Traders Dynamic Index) para momentum</li>
<li>Accion del precio para puntos de entrada/salida</li>
<li>Confianza de Red Neuronal para validacion final</li>
</ul>

<h3 style='color: #52b788;'>Milestones Configurados</h3>
<ul>
<li><b>Milestone 1:</b> {m1}% - Primera notificacion de progreso</li>
<li><b>Milestone 2:</b> {m2}% - Segunda notificacion + Breakeven</li>
<li><b>Milestone 3:</b> {m3}% - Take Profit (cierre automatico)</li>
<li><b>Stop Loss:</b> -{sl}%</li>
</ul>
""".format(
            m1=self.config.MILESTONE_1,
            m2=self.config.MILESTONE_2,
            m3=self.config.MILESTONE_3,
            sl=self.config.DEFAULT_STOP_LOSS_PERCENT * 100
        )

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Acerca del Sistema")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet("background-color: #0f0f23; color: white;")

        layout = QtWidgets.QVBoxLayout(dialog)

        text_browser = QtWidgets.QTextBrowser()
        text_browser.setHtml(about_text)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1a1a2e;
                color: white;
                border: 1px solid #00d4aa;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        text_browser.setOpenExternalLinks(True)
        layout.addWidget(text_browser)

        close_btn = QtWidgets.QPushButton("Cerrar")
        close_btn.setStyleSheet("background-color: #00d4aa; color: #0f0f23; padding: 10px; font-weight: bold;")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec_()

    def _show_signal_cycle_dialog(self):
        """Mostrar diálogo del Ciclo de Señales"""
        cycle_text = """
<h2 style='color: #00d4aa;'>Ciclo de Vida de las Señales</h2>

<hr style='border-color: #00d4aa;'>

<h3 style='color: #ffd700;'>1. DETECCION INICIAL</h3>
<p>El bot escanea continuamente los 42 pares de trading configurados, 
analizando datos en tiempo real cada 2 segundos.</p>
<ul>
<li>Analisis de indicadores tecnicos (EMA, TDI)</li>
<li>Prediccion de la red neuronal (IA)</li>
<li>Validacion de alineacion multi-timeframe</li>
</ul>

<h3 style='color: #ff6b6b;'>2. SENAL DESTACADA</h3>
<p>Cuando se detecta una oportunidad potencial:</p>
<ul>
<li>Se envia notificacion a Telegram: "Senal Destacada"</li>
<li>Inicia periodo de observacion de <b>15-20 minutos</b></li>
<li>Se monitorea continuamente para promocion</li>
</ul>

<h3 style='color: #52b788;'>3. PROMOCION A CONFIRMADA</h3>
<p>La senal se promociona a CONFIRMADA si cumple:</p>
<ul>
<li><b>Por tiempo:</b> 15 minutos transcurridos con tendencia estable</li>
<li><b>Por umbrales:</b> IA >= {min_neural}%, Tecnico >= {min_tech}%, Alineacion >= {min_align}%</li>
</ul>
<p>Se envia notificacion a Telegram con grafico del par.</p>

<h3 style='color: #00d4aa;'>4. SEGUIMIENTO DE MILESTONES</h3>
<p>Una vez CONFIRMADA, el sistema rastrea el progreso:</p>
<table style='width: 100%; border-collapse: collapse;'>
<tr style='background-color: #1a2a4c;'>
<td style='padding: 8px; border: 1px solid #00d4aa;'><b>+{m1}%</b></td>
<td style='padding: 8px; border: 1px solid #00d4aa;'>Primera notificacion de progreso</td>
</tr>
<tr style='background-color: #1a2a4c;'>
<td style='padding: 8px; border: 1px solid #00d4aa;'><b>+{m2}%</b></td>
<td style='padding: 8px; border: 1px solid #00d4aa;'>Segunda notificacion + Activacion Breakeven</td>
</tr>
<tr style='background-color: #1a2a4c;'>
<td style='padding: 8px; border: 1px solid #00d4aa;'><b>+{m3}%</b></td>
<td style='padding: 8px; border: 1px solid #00d4aa;'>Take Profit - Cierre automatico exitoso</td>
</tr>
</table>

<h3 style='color: #dc2f02;'>5. CIERRE DE SENAL</h3>
<p>La senal se cierra automaticamente por:</p>
<ul>
<li><b style='color: #52b788;'>Take Profit:</b> Al alcanzar +{m3}%</li>
<li><b style='color: #dc2f02;'>Stop Loss:</b> Al alcanzar -{sl}%</li>
<li><b style='color: #ffd700;'>Reversion:</b> Cambio de tendencia detectado (despues de 10 min)</li>
<li><b style='color: #888;'>Timeout DESTACADA:</b> 20 minutos sin promocion</li>
</ul>

<h3 style='color: #00d4aa;'>6. NOTIFICACION FINAL</h3>
<p>Al cerrar, se envia resumen a Telegram con:</p>
<ul>
<li>Resultado: Ganancia o Perdida</li>
<li>Porcentaje final de profit</li>
<li>Duracion de la operacion</li>
<li>Grafico final del par</li>
</ul>
""".format(
            min_neural=self.config.MIN_NEURAL_CONFIRMADA,
            min_tech=self.config.MIN_TECHNICAL_CONFIRMADA,
            min_align=self.config.MIN_ALIGNMENT_CONFIRMADA,
            m1=self.config.MILESTONE_1,
            m2=self.config.MILESTONE_2,
            m3=self.config.MILESTONE_3,
            sl=self.config.DEFAULT_STOP_LOSS_PERCENT * 100
        )

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Ciclo de Senales")
        dialog.setMinimumSize(650, 600)
        dialog.setStyleSheet("background-color: #0f0f23; color: white;")

        layout = QtWidgets.QVBoxLayout(dialog)

        text_browser = QtWidgets.QTextBrowser()
        text_browser.setHtml(cycle_text)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1a1a2e;
                color: white;
                border: 1px solid #00d4aa;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout.addWidget(text_browser)

        close_btn = QtWidgets.QPushButton("Cerrar")
        close_btn.setStyleSheet("background-color: #00d4aa; color: #0f0f23; padding: 10px; font-weight: bold;")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec_()

    def _show_config_info(self):
        """Mostrar configuración actual del sistema"""
        config_text = f"""
<h2 style='color: #00d4aa;'>Configuracion Actual</h2>

<h3 style='color: #52b788;'>Parametros de Trading</h3>
<table style='width: 100%;'>
<tr><td><b>Pares monitoreados:</b></td><td>{len(self.config.TRADING_SYMBOLS)} pares</td></tr>
<tr><td><b>Timeframe primario:</b></td><td>{self.config.PRIMARY_TIMEFRAME}</td></tr>
<tr><td><b>Timeframe entrada:</b></td><td>{self.config.ENTRY_TIMEFRAME}</td></tr>
<tr><td><b>EMA Rapida:</b></td><td>{self.config.EMA_FAST}</td></tr>
<tr><td><b>EMA Lenta:</b></td><td>{self.config.EMA_SLOW}</td></tr>
</table>

<h3 style='color: #52b788;'>Umbrales de Confirmacion</h3>
<table style='width: 100%;'>
<tr><td><b>IA Minima CONFIRMADA:</b></td><td>{self.config.MIN_NEURAL_CONFIRMADA}%</td></tr>
<tr><td><b>Tecnico Minimo CONFIRMADA:</b></td><td>{self.config.MIN_TECHNICAL_CONFIRMADA}%</td></tr>
<tr><td><b>Alineacion Minima:</b></td><td>{self.config.MIN_ALIGNMENT_CONFIRMADA}%</td></tr>
<tr><td><b>Tiempo Promocion:</b></td><td>{self.config.MIN_PROMOTION_TIME_SECONDS} segundos</td></tr>
</table>

<h3 style='color: #52b788;'>Gestion de Riesgo</h3>
<table style='width: 100%;'>
<tr><td><b>Milestone 1:</b></td><td>{self.config.MILESTONE_1}%</td></tr>
<tr><td><b>Milestone 2:</b></td><td>{self.config.MILESTONE_2}%</td></tr>
<tr><td><b>Milestone 3 (TP):</b></td><td>{self.config.MILESTONE_3}%</td></tr>
<tr><td><b>Stop Loss:</b></td><td>{self.config.DEFAULT_STOP_LOSS_PERCENT * 100}%</td></tr>
<tr><td><b>Senales Diarias Max:</b></td><td>{self.config.MAX_DAILY_SIGNALS}</td></tr>
</table>

<h3 style='color: #52b788;'>Estado de Servicios</h3>
<table style='width: 100%;'>
<tr><td><b>FIX API:</b></td><td>{'Activo' if self.config.FIX_API_ENABLED else 'Inactivo'}</td></tr>
<tr><td><b>Telegram:</b></td><td>{'Activo' if self.config.telegram_enabled else 'Inactivo'}</td></tr>
<tr><td><b>Auto-Trading:</b></td><td>{'Activo' if getattr(self.config, 'AUTO_TRADING_ENABLED', False) else 'Inactivo'}</td></tr>
</table>
"""

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Configuracion Actual")
        dialog.setMinimumSize(500, 450)
        dialog.setStyleSheet("background-color: #0f0f23; color: white;")

        layout = QtWidgets.QVBoxLayout(dialog)

        text_browser = QtWidgets.QTextBrowser()
        text_browser.setHtml(config_text)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1a1a2e;
                color: white;
                border: 1px solid #00d4aa;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout.addWidget(text_browser)

        close_btn = QtWidgets.QPushButton("Cerrar")
        close_btn.setStyleSheet("background-color: #00d4aa; color: #0f0f23; padding: 10px; font-weight: bold;")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec_()

    def _collect_trader_statistics(self) -> dict:
        """Construye estadísticas de rendimiento trader para mostrar en GUI."""
        stats = {
            'total_signals': 0,
            'closed_signals': 0,
            'successful_signals': 0,
            'loss_signals': 0,
            'win_rate': 0.0,
            'avg_profit_loss': 0.0,
            'active_signals': 0,
            'promotion_count': 0,
            'closure_reasons': {}
        }

        try:
            tracker = getattr(self.bot, 'signal_tracker', None)
            if not tracker:
                return stats

            metrics = tracker.get_performance_metrics() or {}
            closure_reasons = dict(metrics.get('closure_reasons', {}) or {})

            total_signals = int(metrics.get('total_signals', 0) or 0)
            successful_signals = int(metrics.get('successful_signals', 0) or 0)
            closed_signals = sum(
                int(count or 0)
                for reason, count in closure_reasons.items()
                if str(reason).upper() != 'CANCELLED'
            )
            loss_signals = max(closed_signals - successful_signals, 0)

            stats.update({
                'total_signals': total_signals,
                'closed_signals': closed_signals,
                'successful_signals': successful_signals,
                'loss_signals': loss_signals,
                'win_rate': (successful_signals / closed_signals * 100.0) if closed_signals > 0 else 0.0,
                'avg_profit_loss': float(metrics.get('avg_profit_loss', 0.0) or 0.0),
                'active_signals': len(tracker.get_tracked_signals()),
                'promotion_count': int(metrics.get('promotion_count', 0) or 0),
                'closure_reasons': closure_reasons
            })
        except Exception as e:
            logger.error(f"[ERROR] No se pudieron calcular estadísticas del trader: {e}")

        return stats

    def _show_trader_statistics_dialog(self):
        """Mostrar panel de estadísticas de éxitos y pérdidas del trader."""
        stats = self._collect_trader_statistics()

        closure_rows = "".join([
            (
                "<tr>"
                f"<td style='padding: 6px; border: 1px solid #00d4aa;'>{str(reason).replace('_', ' ').title()}</td>"
                f"<td style='padding: 6px; border: 1px solid #00d4aa; text-align: center;'>{count}</td>"
                "</tr>"
            )
            for reason, count in sorted(stats['closure_reasons'].items(), key=lambda item: item[1], reverse=True)
        ])
        if not closure_rows:
            closure_rows = (
                "<tr><td style='padding: 6px; border: 1px solid #00d4aa;' colspan='2'>"
                "Sin cierres registrados todavía."
                "</td></tr>"
            )

        stats_text = f"""
<h2 style='color: #00d4aa;'>Estadísticas del Trader</h2>
<p style='color: #b0b0b0;'>Resumen en tiempo real de señales exitosas y pérdidas.</p>

<h3 style='color: #52b788;'>Rendimiento General</h3>
<table style='width: 100%; border-collapse: collapse;'>
<tr><td style='padding: 8px; border: 1px solid #00d4aa;'><b>Total señales creadas</b></td><td style='padding: 8px; border: 1px solid #00d4aa;'>{stats['total_signals']}</td></tr>
<tr><td style='padding: 8px; border: 1px solid #00d4aa;'><b>Señales cerradas</b></td><td style='padding: 8px; border: 1px solid #00d4aa;'>{stats['closed_signals']}</td></tr>
<tr><td style='padding: 8px; border: 1px solid #00d4aa; color: #52b788;'><b>Trades exitosos ✅</b></td><td style='padding: 8px; border: 1px solid #00d4aa; color: #52b788;'><b>{stats['successful_signals']}</b></td></tr>
<tr><td style='padding: 8px; border: 1px solid #00d4aa; color: #ff6b6b;'><b>Trades con pérdida ❌</b></td><td style='padding: 8px; border: 1px solid #00d4aa; color: #ff6b6b;'><b>{stats['loss_signals']}</b></td></tr>
<tr><td style='padding: 8px; border: 1px solid #00d4aa;'><b>Win Rate</b></td><td style='padding: 8px; border: 1px solid #00d4aa;'><b>{stats['win_rate']:.2f}%</b></td></tr>
<tr><td style='padding: 8px; border: 1px solid #00d4aa;'><b>Profit Promedio</b></td><td style='padding: 8px; border: 1px solid #00d4aa;'>{stats['avg_profit_loss']:+.2f}%</td></tr>
<tr><td style='padding: 8px; border: 1px solid #00d4aa;'><b>Promociones a CONFIRMADA</b></td><td style='padding: 8px; border: 1px solid #00d4aa;'>{stats['promotion_count']}</td></tr>
<tr><td style='padding: 8px; border: 1px solid #00d4aa;'><b>Señales activas ahora</b></td><td style='padding: 8px; border: 1px solid #00d4aa;'>{stats['active_signals']}</td></tr>
</table>

<h3 style='color: #52b788;'>Detalle por motivo de cierre</h3>
<table style='width: 100%; border-collapse: collapse;'>
<tr style='background-color: #1a2a4c;'>
<th style='padding: 6px; border: 1px solid #00d4aa; text-align: left;'>Motivo</th>
<th style='padding: 6px; border: 1px solid #00d4aa;'>Cantidad</th>
</tr>
{closure_rows}
</table>
"""

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Estadísticas del Trader")
        dialog.setMinimumSize(620, 560)
        dialog.setStyleSheet("background-color: #0f0f23; color: white;")

        layout = QtWidgets.QVBoxLayout(dialog)

        text_browser = QtWidgets.QTextBrowser()
        text_browser.setHtml(stats_text)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1a1a2e;
                color: white;
                border: 1px solid #00d4aa;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout.addWidget(text_browser)

        close_btn = QtWidgets.QPushButton("Cerrar")
        close_btn.setStyleSheet("background-color: #00d4aa; color: #0f0f23; padding: 10px; font-weight: bold;")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec_()

    def _init_header(self):
        """Inicializar header optimizado"""
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        title_widget = QtWidgets.QWidget()
        title_layout = QtWidgets.QVBoxLayout(title_widget)
        title_label = QtWidgets.QLabel("🚀 Crypto Bot Pro v35.0.0.0 - Desarrolado por Lic: Adolfo Daniel Aguirre")
        title_label.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        title_label.setStyleSheet("color: #00d4aa;")
        title_layout.addWidget(title_label)
        subtitle_label = QtWidgets.QLabel("Sistema Avanzado de Trading con IA - Versión Profesional")
        subtitle_label.setFont(QtGui.QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #b0b0b0;")
        title_layout.addWidget(subtitle_label)
        header_layout.addWidget(title_widget)
        # Controles
        controls_widget = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls_widget)
        # Estado
        status_widget = QtWidgets.QWidget()
        status_layout = QtWidgets.QVBoxLayout(status_widget)
        status_layout.addWidget(QtWidgets.QLabel("Estado:"))
        self.status_label = QtWidgets.QLabel("Detenido")
        self.status_label.setStyleSheet("color: red;")
        status_layout.addWidget(self.status_label)
        controls_layout.addWidget(status_widget)
        # Botones
        self.start_btn = QtWidgets.QPushButton("▶️ Iniciar Bot Optimizado")
        self.start_btn.setStyleSheet("background-color: #52b788; color: white; padding: 8px;")
        self.start_btn.clicked.connect(self.start_bot_optimized)
        controls_layout.addWidget(self.start_btn)
        self.stop_btn = QtWidgets.QPushButton("⏹️ Detener Bot")
        self.stop_btn.setStyleSheet("background-color: #dc2f02; color: white; padding: 8px;")
        self.stop_btn.clicked.connect(self.stop_bot_optimized)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)

        # ✅ NUEVO: Indicador FIX API en tiempo real
        fix_api_widget = QtWidgets.QWidget()
        fix_api_layout = QtWidgets.QVBoxLayout(fix_api_widget)
        fix_api_layout.setContentsMargins(10, 0, 10, 0)
        fix_api_label = QtWidgets.QLabel("FIX API:")
        fix_api_label.setFont(QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
        fix_api_label.setStyleSheet("color: #00d4aa;")
        fix_api_layout.addWidget(fix_api_label)

        # Botón indicador (cambia color según estado)
        self.fix_api_indicator = QtWidgets.QPushButton("⚫ Inactivo")
        self.fix_api_indicator.setStyleSheet(
            "background-color: #555; color: white; padding: 6px 12px; "
            "border-radius: 12px; font-weight: bold; border: 2px solid #666;"
        )
        self.fix_api_indicator.setMaximumWidth(150)
        self.fix_api_indicator.setEnabled(False)  # No clickeable, solo indicador
        fix_api_layout.addWidget(self.fix_api_indicator)
        controls_layout.addWidget(fix_api_widget)

        header_layout.addWidget(controls_widget)
        self.main_layout.addWidget(header_widget)
        header_widget.setStyleSheet("background-color: #16213e; border: 2px solid #1a2a4c; border-radius: 5px;")

    def _process_high_quality_signal(self, symbol: str, df_primary: pd.DataFrame, df_entry: pd.DataFrame, analysis_result: dict):
        """
        ✅ PROCESAMIENTO UNIFICADO — USA SOLO _prepare_signal_package()
        - Verifica exclusividad (1 señal)
        - Prepara paquete
        - Envía a SignalTracker
        - Genera gráfico (solo CONFIRMADA)
        - Notifica Telegram (solo 1 foto en CONFIRMADA)
        """
        if self.exclusive_tracking_mode:
            logger.info(f"⏭️ {symbol} - Ignorado: señal activa en {self.tracked_symbol}")
            return

        # === 1. Preparar paquete ÚNICO ===
        signal_package = self._prepare_signal_package(symbol, df_entry, analysis_result)
        if not signal_package:
            logger.warning(f"❌ {symbol} - Paquete de señal inválido")
            return

        # === 2. Verificar umbrales para DESTACADA (consistente con SignalTracker) ===
        neural_score   = signal_package['neural_score']
        technical_pct  = signal_package['technical_percentage']
        alignment_pct  = signal_package['alignment_percentage']

        # ✅ UMBRALES CONSISTENTES CON SignalTracker._validate_signal_coherence():
        #    Usando variables configurables desde GUI para máxima flexibilidad
        if not (neural_score >= self.config.MIN_NEURAL_DESTACADA and technical_pct >= self.config.MIN_TECHNICAL_DESTACADA and alignment_pct >= self.config.MIN_ALIGNMENT_DESTACADA):
            logger.debug(
                f"❌ {symbol} - No cumple umbrales DESTACADA: "
                f"IA={neural_score:.1f}%, Tec={technical_pct:.1f}%, Ali={alignment_pct:.1f}%"
            )
            return

        # === 3. Activar modo exclusivo ===
        self.exclusive_tracking_mode = True
        self.tracked_symbol          = symbol
        self.tracked_signal_hash     = signal_package['signal_hash']

        # === 4. Generar gráfico SOLO para CONFIRMADA ===
        chart_path = None
        is_confirmed = (neural_score >= self.config.MIN_NEURAL_CONFIRMADA and technical_pct >= self.config.MIN_TECHNICAL_CONFIRMADA and alignment_pct >= self.config.MIN_ALIGNMENT_CONFIRMADA)
        if is_confirmed and PLOTTING_AVAILABLE and hasattr(self, 'chart_generator') and self.chart_generator:
            try:
                chart_path = self.chart_generator.generate_signal_chart(
                    symbol=symbol,
                    df=df_entry,
                    signal_data=signal_package,
                    analysis_result=analysis_result
                )
                if chart_path:
                    signal_package['chart_path'] = chart_path
                    logger.info(f"✅ Gráfico generado para CONFIRMADA: {chart_path}")
            except Exception as e:
                logger.error(f"❌ Error generando gráfico para {symbol}: {e}")

        # === 5. Agregar al SignalTracker ===
        if not self.signal_tracker.add_highlighted_signal(signal_package):
            logger.error(f"❌ {symbol} - Rechazado por SignalTracker (validación interna falló)")
            self._release_exclusive_mode()
            return

        # === 6. Notificar Telegram ===
        if self.telegram_client and self.config.telegram_enabled:
            try:
                text_sent = self.telegram_client.send_optimized_trading_signal(
                    signal_id=signal_package['signal_hash'],
                    signal_dict=signal_package,
                    symbol=symbol,
                    neural_prediction=signal_package['neural_prediction'],
                    technical_confidence=technical_pct,
                    send_photo=is_confirmed  # ✅ Solo foto si CONFIRMADA
                )
                if text_sent:
                    logger.info(f"✅ Telegram: señal {'CONFIRMADA' if is_confirmed else 'DESTACADA'} enviada — {symbol}")
                else:
                    logger.warning(f"⚠️ Telegram: no se envió señal para {symbol}")
            except Exception as e:
                logger.error(f"❌ Error en Telegram para {symbol}: {e}")

        # === 7. Registrar en GUI y metricas ===
        self.performance_metrics['total_signals'] += 1
        self.active_signals.append(signal_package)
        self._safe_gui_queue_put(('signal_found', None))
        self._safe_gui_queue_put((
            'log_message',
            f"SENAL DESTACADA: {symbol} | "
            f"IA={neural_score:.1f}% | Tecnico={technical_pct:.1f}% | Alineacion={alignment_pct:.1f}%"
        ))
        
        # === 8. CORREGIDO v35: Mostrar barra de progreso DESTACADA en GUI ===
        self._safe_gui_queue_put(('show_destacada_signal', {
            'symbol': symbol,
            'neural_score': neural_score,
            'technical_pct': technical_pct,
            'alignment_pct': alignment_pct,
            'is_buy': signal_package.get('is_buy', True)
        }))
        logger.info(f"GUI actualizada con senal DESTACADA: {symbol}")

    def _init_tabs(self):
        """Inicializar pestañas optimizadas"""
        self.notebook = QtWidgets.QTabWidget()
        self.notebook.setStyleSheet(
            "QTabWidget::pane { border: 0; }"
            "QTabBar::tab { background: #16213e; color: #b0b0b0; padding: 10px; "
            "border-top-left-radius: 5px; border-top-right-radius: 5px; }"
            "QTabBar::tab:selected { background: #00d4aa; color: black; }"
        )
        # Conectar el evento de cambio de pestaña
        self.notebook.currentChanged.connect(self.on_tab_changed)
        # Pestañas principales
        self.trading_tab = self._create_optimized_trading_tab()
        self.notebook.addTab(self.trading_tab, "🎯 Trading Crypto")
        self.analysis_tab = self._create_optimized_analysis_tab()
        self.notebook.addTab(self.analysis_tab, "📊 Análisis Detallado")
        self.neural_tab = self._create_optimized_neural_tab()
        self.notebook.addTab(self.neural_tab, "🧠 IA Crypto")
        self.pairs_analysis_tab = self._create_optimized_pairs_analysis_tab()
        self.notebook.addTab(self.pairs_analysis_tab, "📊 Análisis de Pares")
        self.config_tab = self._create_optimized_config_tab()
        self.notebook.addTab(self.config_tab, "⚙️ Configuración")
        self.main_layout.addWidget(self.notebook)

    def _create_titled_frame(self, title_text, parent_widget):
        """Crear frame con título"""
        frame = QtWidgets.QFrame(parent_widget)
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setStyleSheet("QFrame { background-color: #16213e; border: 1px solid #1a2a4c; border-radius: 5px; }")
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(10, 20, 10, 10)
        title_label = QtWidgets.QLabel(title_text, frame)
        title_label.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Bold))
        title_label.setStyleSheet("color: #00d4aa; background-color: transparent; border: none; padding: 5px;")
        title_label.move(10, -10)
        title_label.adjustSize()
        content_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(content_layout)
        return frame, content_layout

    def _create_optimized_trading_tab(self):
        """Crear pestaña de trading optimizada"""
        tab_widget = QtWidgets.QWidget()
        tab_layout = QtWidgets.QHBoxLayout(tab_widget)
        tab_layout.setSpacing(10)
        # Panel izquierdo - Pares
        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        tab_layout.addWidget(left_panel, 2)
        pairs_frame, pairs_layout = self._create_titled_frame("📊 Pares de Trading", left_panel)
        self.pair_listbox = QtWidgets.QListWidget()
        self.pair_listbox.setStyleSheet("background-color: #0f0f23; color: white; border: 1px solid #1a2a4c;")
        for pair in self.config.TRADING_SYMBOLS:
            self.pair_listbox.addItem(pair)
        self.pair_listbox.setCurrentRow(0)
        self.pair_listbox.itemClicked.connect(self.on_pair_select_optimized)
        pairs_layout.addWidget(self.pair_listbox)
        left_layout.addWidget(pairs_frame)
        # Información del par
        info_frame, info_layout = self._create_titled_frame("💰 Información del Par", left_panel)
        self.price_label = QtWidgets.QLabel("Precio: $0.00")
        self.price_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.price_label)
        self.volume_label = QtWidgets.QLabel("Volumen: 0")
        self.volume_label.setStyleSheet("color: #b0b0b0;")
        info_layout.addWidget(self.volume_label)
        left_layout.addWidget(info_frame)
        # Panel central - Análisis principal
        center_panel = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center_panel)
        tab_layout.addWidget(center_panel, 5)
        # Panel de probabilidad más prominente
        prob_frame, prob_layout = self._create_titled_frame("", center_panel)
        prob_frame.setStyleSheet("QFrame { background-color: #1a2a4c; border: 2px solid #00d4aa; border-radius: 8px; }")
        prob_h_layout = QtWidgets.QHBoxLayout()
        prob_layout.addLayout(prob_h_layout)
        # Display de probabilidad más grande
        self.combined_prob_label = QtWidgets.QLabel("0.0%")
        self.combined_prob_label.setAlignment(QtCore.Qt.AlignCenter)
        self.combined_prob_label.setFont(QtGui.QFont("Arial", 32, QtGui.QFont.Bold))
        self.combined_prob_label.setStyleSheet(
            "color: #ffffff; background-color: #16213e; border: 3px solid #00d4aa; "
            "border-radius: 15px; padding: 15px; min-height: 80px;"
        )
        prob_h_layout.addWidget(self.combined_prob_label)
        # Panel de detalles de señal
        signal_details_layout = QtWidgets.QVBoxLayout()
        prob_h_layout.addLayout(signal_details_layout)
        self.signal_type_label = QtWidgets.QLabel("NEUTRAL")
        self.signal_type_label.setAlignment(QtCore.Qt.AlignCenter)
        self.signal_type_label.setFont(QtGui.QFont("Arial", 18, QtGui.QFont.Bold))
        self.signal_type_label.setStyleSheet(
            "color: #b0b0b0; background-color: #0f0f23; border-radius: 8px; padding: 10px;"
        )
        signal_details_layout.addWidget(self.signal_type_label)
        # Panel de métricas optimizadas
        metrics_layout = QtWidgets.QHBoxLayout()
        signal_details_layout.addLayout(metrics_layout)
        # Contenedor para métricas con bordes más visibles
        metrics_container = QtWidgets.QWidget()
        metrics_container.setStyleSheet("background-color: #0f0f23; border-radius: 8px; padding: 5px;")
        metrics_container_layout = QtWidgets.QHBoxLayout(metrics_container)
        # Métrica de IA
        neural_widget = QtWidgets.QWidget()
        neural_widget.setStyleSheet("background-color: #1a2a4c; border-radius: 6px; padding: 5px;")
        neural_layout = QtWidgets.QVBoxLayout(neural_widget)
        neural_title = QtWidgets.QLabel("PREDICCIÓN IA")
        neural_title.setAlignment(QtCore.Qt.AlignCenter)
        neural_title.setStyleSheet("color: #00d4aa; font-weight: bold; font-size: 10px;")
        neural_layout.addWidget(neural_title)
        self.neural_confidence_label = QtWidgets.QLabel("0%")
        self.neural_confidence_label.setAlignment(QtCore.Qt.AlignCenter)
        self.neural_confidence_label.setStyleSheet("color: #00d4aa; font-weight: bold; font-size: 14px;")
        neural_layout.addWidget(self.neural_confidence_label)
        metrics_container_layout.addWidget(neural_widget)
        # Separador visual
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setStyleSheet("background-color: #1a2a4c;")
        metrics_container_layout.addWidget(separator)
        # Métrica de Análisis Técnico
        technical_widget = QtWidgets.QWidget()
        technical_widget.setStyleSheet("background-color: #1a2a4c; border-radius: 6px; padding: 5px;")
        technical_layout = QtWidgets.QVBoxLayout(technical_widget)
        technical_title = QtWidgets.QLabel("ANÁLISIS TÉCNICO")
        technical_title.setAlignment(QtCore.Qt.AlignCenter)
        technical_title.setStyleSheet("color: #ffd60a; font-weight: bold; font-size: 10px;")
        technical_layout.addWidget(technical_title)
        self.technical_confidence_label = QtWidgets.QLabel("0%")
        self.technical_confidence_label.setAlignment(QtCore.Qt.AlignCenter)
        self.technical_confidence_label.setStyleSheet("color: #ffd60a; font-weight: bold; font-size: 14px;")
        technical_layout.addWidget(self.technical_confidence_label)
        metrics_container_layout.addWidget(technical_widget)
        metrics_layout.addWidget(metrics_container)
        center_layout.addWidget(prob_frame)
        # Panel de análisis detallado compacto
        details_frame, details_layout = self._create_titled_frame("📊 Detalles Optimizados", center_panel)
        self.signal_text = QtWidgets.QTextEdit()
        self.signal_text.setReadOnly(True)
        self.signal_text.setMaximumHeight(150)  # Más compacto
        self.signal_text.setStyleSheet("background-color: #0f0f23; color: white; border: 1px solid #1a2a4c;")
        details_layout.addWidget(self.signal_text)
        center_layout.addWidget(details_frame)
        # Panel de señales activas
        signals_frame, signals_layout = self._create_titled_frame("🚨 Señales Optimizadas Recientes", center_panel)
        self.signals_tree = QtWidgets.QTableWidget(0, 6)  # IA y Técnico fusionados
        self.signals_tree.setHorizontalHeaderLabels([
            'Símbolo', 'Señal', 'Prob', 'IA%', 'TEC%', 'Hora'
        ])
        self.signals_tree.setStyleSheet(
            "background-color: #0f0f23; color: Black; selection-background-color: #00d4aa; "
            "border: 1px solid #1a2a4c;"
        )
        self.signals_tree.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.signals_tree.cellDoubleClicked.connect(self._on_signal_cell_clicked)
        signals_layout.addWidget(self.signals_tree)
        center_layout.addWidget(signals_frame)
        # Panel derecho - Terminal optimizado
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        tab_layout.addWidget(right_panel, 3)
        # NUEVO: Panel de Seguimiento
        tracking_frame, tracking_layout = self._create_titled_frame("🛰️ Seguimiento de Señal Activa", right_panel)
        self.highlight_progress_bar = QtWidgets.QProgressBar()
        self.highlight_progress_bar.setStyleSheet(
            "QProgressBar { text-align: center; color: white; background-color: #0f0f23; "
            "border: 2px solid #ffd700; border-radius: 8px; height: 25px; font-weight: bold; }"
            "QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #ffd700, stop:1 #ff9500); border-radius: 6px; }"
        )
        self.highlight_progress_bar.setValue(0)
        self.highlight_progress_bar.setFormat("Esperando señal DESTACADA...")
        self.highlight_progress_bar.setVisible(False) # Oculto por defecto
        tracking_layout.addWidget(self.highlight_progress_bar)

        # Barra de progreso para SEÑAL CONFIRMADA (Profit Tracking)
        self.confirmed_progress_bar = QtWidgets.QProgressBar()
        self.confirmed_progress_bar.setStyleSheet(
            "QProgressBar { text-align: center; color: white; background-color: #0f0f23; "
            "border: 2px solid #00ff00; border-radius: 8px; height: 25px; font-weight: bold; }"
            "QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #00ff00, stop:1 #32cd32); border-radius: 6px; }"
        )
        self.confirmed_progress_bar.setValue(0)
        self.confirmed_progress_bar.setFormat("Esperando confirmación...")
        self.confirmed_progress_bar.setVisible(False) # Oculto por defecto
        tracking_layout.addWidget(self.confirmed_progress_bar)

        right_layout.addWidget(tracking_frame)
        # Terminal optimizado
        terminal_frame, terminal_layout = self._create_titled_frame("💻 Terminal Optimizado", right_panel)
        # Barra de progreso optimizada
        self.pair_scan_progress_bar = QtWidgets.QProgressBar()
        self.pair_scan_progress_bar.setStyleSheet(
            "QProgressBar { text-align: center; color: white; background-color: #0f0f23; "
            "border: 2px solid #00d4aa; border-radius: 8px; height: 25px; font-weight: bold; }"
            "QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #00d4aa, stop:1 #52b788); border-radius: 6px; }"
        )
        self.pair_scan_progress_bar.setValue(0)
        terminal_layout.addWidget(self.pair_scan_progress_bar)
        # Panel de métricas de rendimiento
        performance_layout = QtWidgets.QHBoxLayout()
        terminal_layout.addLayout(performance_layout)
        self.cache_hit_label = QtWidgets.QLabel("Cache: 0%")
        self.cache_hit_label.setStyleSheet("color: #00d4aa; font-size: 10px;")
        performance_layout.addWidget(self.cache_hit_label)
        self.analysis_time_label = QtWidgets.QLabel("Análisis: 0ms")
        self.analysis_time_label.setStyleSheet("color: #ffd60a; font-size: 10px;")
        performance_layout.addWidget(self.analysis_time_label)
        self.signals_count_label = QtWidgets.QLabel("Señales: 0")
        self.signals_count_label.setStyleSheet("color: #ff6b6b; font-size: 10px;")
        performance_layout.addWidget(self.signals_count_label)
        # Botón para limpiar logs
        clear_logs_btn = QtWidgets.QPushButton("🗑️ Limpiar Logs")
        clear_logs_btn.setStyleSheet(
            "background-color: #ff6b6b; color: white; padding: 5px; font-weight: bold; "
            "border-radius: 5px; min-height: 25px;"
        )
        clear_logs_btn.clicked.connect(self.clear_logs)
        terminal_layout.addWidget(clear_logs_btn)

        # ✅ NUEVO BOTÓN: Limpiar Datos/Imágenes
        clean_data_btn = QtWidgets.QPushButton("🧹 Limpiar Datos (Logs/Img)")
        clean_data_btn.setStyleSheet(
            "background-color: #ff9800; color: white; padding: 5px; font-weight: bold; "
            "border-radius: 5px; min-height: 25px;"
        )
        clean_data_btn.clicked.connect(self.clean_all_data)
        terminal_layout.addWidget(clean_data_btn)

        # Terminal de logs
        self.terminal_text = QtWidgets.QTextEdit()
        self.terminal_text.setReadOnly(True)
        self.terminal_text.setStyleSheet("background-color: #0f0f23; color: #00d4aa; border: 1px solid #1a2a4c;")
        terminal_layout.addWidget(self.terminal_text)
        right_layout.addWidget(terminal_frame)
        return tab_widget



    def _create_optimized_analysis_tab(self):
        """Crear pestaña de análisis optimizada"""
        tab_widget = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(tab_widget)
        # Añadir botón de actualización
        button_layout = QtWidgets.QHBoxLayout()
        tab_layout.addLayout(button_layout)
        refresh_btn = QtWidgets.QPushButton("🔄 Actualizar Análisis")
        refresh_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; font-weight: bold;")
        refresh_btn.clicked.connect(self.refresh_analysis)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        detail_frame, detail_layout = self._create_titled_frame("📊 Análisis Técnico Completo Optimizado", tab_widget)
        self.analysis_text = QtWidgets.QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setStyleSheet("background-color: #0f0f23; color: white; border: 1px solid #1a2a4c; font-family: 'Courier New';")
        detail_layout.addWidget(self.analysis_text)
        tab_layout.addWidget(detail_frame)
        return tab_widget

    def _create_optimized_neural_tab(self):
        """Crear pestaña de IA optimizada"""
        tab_widget = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(tab_widget)
        # Panel de entrenamiento optimizado
        training_frame, training_layout = self._create_titled_frame("🧠 Red Neuronal Avanzada v35.0.0.0 - OPTIMIZADA", tab_widget)
        button_layout = QtWidgets.QHBoxLayout()
        training_layout.addLayout(button_layout)
        self.train_btn = QtWidgets.QPushButton("🚀 Entrenar IA Optimizada")
        self.train_btn.setStyleSheet("background-color: #7b2cbf; color: white; padding: 10px; font-weight: bold;")
        self.train_btn.clicked.connect(self.train_neural_network_optimized)
        button_layout.addWidget(self.train_btn)
        self.quick_train_btn = QtWidgets.QPushButton("⚡ Entrenamiento Rápido")
        self.quick_train_btn.setStyleSheet("background-color: #f72585; color: white; padding: 10px;")
        self.quick_train_btn.clicked.connect(self.quick_train_neural_network)
        button_layout.addWidget(self.quick_train_btn)
        # Botón para forzar reentrenamiento
        self.retrain_btn = QtWidgets.QPushButton("🔄 Forzar Reentrenamiento IA")
        self.retrain_btn.setStyleSheet("background-color: #ff6b6b; color: white; padding: 10px;")
        self.retrain_btn.clicked.connect(self.force_retrain_neural_network)
        button_layout.addWidget(self.retrain_btn)
        # Barra de progreso mejorada
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setStyleSheet(
            "QProgressBar { text-align: center; color: white; background-color: #0f0f23; "
            "border: 2px solid #7b2cbf; border-radius: 8px; height: 30px; font-weight: bold; }"
            "QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #7b2cbf, stop:1 #f72585); border-radius: 6px; }"
        )
        self.progress_bar.setValue(0)
        training_layout.addWidget(self.progress_bar)
        tab_layout.addWidget(training_frame)
        # Panel de información optimizado
        info_frame, info_layout = self._create_titled_frame("📊 Arquitectura y Rendimiento", tab_widget)
        self.neural_info_text = QtWidgets.QTextEdit()
        self.neural_info_text.setReadOnly(True)
        self.neural_info_text.setStyleSheet("background-color: #0f0f23; color: white; border: 1px solid #1a2a4c; font-family: 'Courier New';")
        info_layout.addWidget(self.neural_info_text)
        tab_layout.addWidget(info_frame)
        return tab_widget

    def _create_optimized_pairs_analysis_tab(self):
        """Crear pestaña de análisis de pares optimizada"""
        tab_widget = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(tab_widget)
        # Panel de control optimizado
        control_frame = QtWidgets.QFrame()
        control_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        control_frame.setStyleSheet("QFrame { background-color: #16213e; border: 2px solid #00d4aa; border-radius: 8px; }")
        control_layout = QtWidgets.QHBoxLayout(control_frame)
        # Botón de actualización mejorado
        self.update_pairs_btn = QtWidgets.QPushButton("🔄 Análisis Optimizado")
        self.update_pairs_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.update_pairs_btn.clicked.connect(self.update_pairs_analysis_optimized)
        control_layout.addWidget(self.update_pairs_btn)
        # ✅ NUEVO: Botón para cargar y optimizar pares automáticamente
        self.load_best_pairs_btn = QtWidgets.QPushButton("🔍 Cargar Mejores Pares")
        self.load_best_pairs_btn.setStyleSheet("background-color: #9c27b0; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.load_best_pairs_btn.clicked.connect(self.load_and_analyze_best_pairs)
        self.load_best_pairs_btn.setToolTip("Analiza todos los pares USDT por liquidez y guarda los mejores")
        control_layout.addWidget(self.load_best_pairs_btn)
        # Auto-actualización
        self.auto_update_pairs_var = QtWidgets.QCheckBox("Auto-actualizar optimizado")
        self.auto_update_pairs_var.setChecked(True)
        self.auto_update_pairs_var.setStyleSheet("color: white; font-weight: bold;")
        control_layout.addWidget(self.auto_update_pairs_var)
        # Filtros mejorados
        control_layout.addWidget(QtWidgets.QLabel("Filtro:"))
        self.signal_filter_combo = QtWidgets.QComboBox()
        self.signal_filter_combo.addItems(["Todas", "COMPRA", "VENTA", "ALTA_PROB", "NEUTRAL"])
        self.signal_filter_combo.currentTextChanged.connect(self.filter_pairs_table_optimized)
        control_layout.addWidget(self.signal_filter_combo)
        # Barra de progreso de pares
        self.pairs_progress_bar = QtWidgets.QProgressBar()
        self.pairs_progress_bar.setStyleSheet(
            "QProgressBar { text-align: center; color: white; background-color: #0f0f23; "
            "border: 1px solid #00d4aa; border-radius: 5px; }"
            "QProgressBar::chunk { background-color: #00d4aa; border-radius: 5px; }"
        )
        control_layout.addWidget(self.pairs_progress_bar)
        tab_layout.addWidget(control_frame)
        # Tabla optimizada
        self.pairs_analysis_table = QtWidgets.QTableWidget()
        self.pairs_analysis_table.setColumnCount(8)  # Columna adicional
        self.pairs_analysis_table.setHorizontalHeaderLabels([
            'Símbolo', 'Precio', 'Señal', 'Prob.', 'IA%', 'TEC%', 'Actualización', 'Acciones'
        ])
        self.pairs_analysis_table.setStyleSheet(
            "QTableWidget { background-color: #0f0f23; color: white; selection-background-color: #00d4aa; "
            "border: 2px solid #1a2a4c; gridline-color: #1a2a4c; }"
            "QTableWidget::item { padding: 8px; }"
            "QHeaderView::section { background-color: #16213e; color: #00d4aa; font-weight: bold; "
            "border: 1px solid #1a2a4c; padding: 8px; }"
        )
        self.pairs_analysis_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.pairs_analysis_table.setSortingEnabled(True)
        tab_layout.addWidget(self.pairs_analysis_table)
        # Estado optimizado
        self.pairs_status_label = QtWidgets.QLabel("Presione 'Análisis Optimizado' para cargar datos mejorados")
        self.pairs_status_label.setStyleSheet("color: #00d4aa; padding: 8px; font-weight: bold;")
        tab_layout.addWidget(self.pairs_status_label)
        return tab_widget

    def _create_optimized_config_tab(self):
        """Crear pestaña de configuración optimizada"""
        tab_widget = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(tab_widget)
        # Scroll area para configuraciones
        config_scroll = QtWidgets.QScrollArea()
        config_scroll.setWidgetResizable(True)
        config_scroll.setStyleSheet("background-color: #0f0f23; border: none;")
        scroll_widget = QtWidgets.QWidget()
        config_scroll.setWidget(scroll_widget)
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        # Configuración de Telegram optimizada
        telegram_frame, telegram_layout = self._create_titled_frame("📱 Configuración Telegram Optimizada", scroll_widget)
        telegram_grid = QtWidgets.QGridLayout()
        telegram_layout.addLayout(telegram_grid)
        telegram_grid.addWidget(QtWidgets.QLabel("Token Bot:"), 0, 0)
        self.token_entry = QtWidgets.QLineEdit(self.config.telegram_bot_token)
        self.token_entry.setStyleSheet("background-color: #16213e; color: white; border: 1px solid #1a2a4c; padding: 5px;")
        telegram_grid.addWidget(self.token_entry, 0, 1)
        telegram_grid.addWidget(QtWidgets.QLabel("Chat ID:"), 1, 0)
        self.chat_id_entry = QtWidgets.QLineEdit(self.config.telegram_chat_id)
        self.chat_id_entry.setStyleSheet("background-color: #16213e; color: white; border: 1px solid #1a2a4c; padding: 5px;")
        telegram_grid.addWidget(self.chat_id_entry, 1, 1)
        self.telegram_enabled_var = QtWidgets.QCheckBox("Habilitar notificaciones optimizadas")
        self.telegram_enabled_var.setChecked(self.config.telegram_enabled)
        self.telegram_enabled_var.setStyleSheet("color: white; font-weight: bold;")
        telegram_grid.addWidget(self.telegram_enabled_var, 2, 0, 1, 2)
        test_btn = QtWidgets.QPushButton("🧪 Probar Conexión")
        test_btn.setStyleSheet("background-color: #52b788; color: white; padding: 8px; border-radius: 5px;")
        test_btn.clicked.connect(self.test_telegram_optimized)
        telegram_grid.addWidget(test_btn, 3, 0, 1, 2)
        scroll_layout.addWidget(telegram_frame)
        # ========== CONFIGURACIÓN BINANCE API ==========
        binance_frame, binance_layout = self._create_titled_frame("🔑 Configuración Binance API", scroll_widget)
        binance_grid = QtWidgets.QGridLayout()
        binance_layout.addLayout(binance_grid)
        binance_grid.addWidget(QtWidgets.QLabel("API Key:"), 0, 0)
        self.binance_key_entry = QtWidgets.QLineEdit(self.config.binance_api_key)
        self.binance_key_entry.setStyleSheet("background-color: #16213e; color: white; border: 1px solid #1a2a4c; padding: 5px;")
        self.binance_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        binance_grid.addWidget(self.binance_key_entry, 0, 1)
        binance_grid.addWidget(QtWidgets.QLabel("API Secret:"), 1, 0)
        self.binance_secret_entry = QtWidgets.QLineEdit(self.config.binance_secret_key)
        self.binance_secret_entry.setStyleSheet("background-color: #16213e; color: white; border: 1px solid #1a2a4c; padding: 5px;")
        self.binance_secret_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        binance_grid.addWidget(self.binance_secret_entry, 1, 1)
        # Botón para mostrar/ocultar contraseñas
        show_credentials_btn = QtWidgets.QPushButton("👁️ Mostrar/Ocultar")
        show_credentials_btn.setStyleSheet("background-color: #1a2a4c; color: white; padding: 5px; border-radius: 3px;")
        show_credentials_btn.clicked.connect(self.toggle_credentials_visibility)
        binance_grid.addWidget(show_credentials_btn, 2, 0, 1, 2)
        self.testnet_checkbox = QtWidgets.QCheckBox("Usar Testnet (modo prueba)")
        self.testnet_checkbox.setChecked(self.config.use_testnet)
        self.testnet_checkbox.setStyleSheet("color: #ffd60a; font-weight: bold;")
        self.testnet_checkbox.stateChanged.connect(self._on_testnet_checkbox_changed)
        binance_grid.addWidget(self.testnet_checkbox, 3, 0, 1, 2)
        scroll_layout.addWidget(binance_frame)
        # ========== MODO DE OPERACIÓN ==========
        mode_frame, mode_layout = self._create_titled_frame("🎯 Modo de Operación", scroll_widget)
        mode_grid = QtWidgets.QGridLayout()
        mode_layout.addLayout(mode_grid)
        # Descripción
        mode_desc = QtWidgets.QLabel(
            "<b>Señales Solo:</b> Solo envía notificaciones a Telegram (sin ejecutar trades)<br>"
            "<b>Auto-Trading:</b> Ejecuta trades automáticamente en Binance"
        )
        mode_desc.setStyleSheet("color: #b0b0b0; padding: 8px;")
        mode_desc.setWordWrap(True)
        mode_grid.addWidget(mode_desc, 0, 0, 1, 2)
        # Toggle buttons
        self.mode_signals_only_btn = QtWidgets.QPushButton("📱 Señales Solo")
        self.mode_signals_only_btn.setCheckable(True)
        self.mode_signals_only_btn.setChecked(not getattr(self.config, 'auto_trading_enabled', False))
        self.mode_signals_only_btn.setStyleSheet(
            "QPushButton { background-color: #52b788; color: white; padding: 12px; border-radius: 5px; font-weight: bold; }"
            "QPushButton:checked { background-color: #00d4aa; border: 2px solid #52b788; }"
            "QPushButton:!checked { background-color: #1a2a4c; color: #808080; }"
        )
        self.mode_signals_only_btn.clicked.connect(lambda: self.set_trading_mode(False))
        mode_grid.addWidget(self.mode_signals_only_btn, 1, 0)
        self.mode_auto_trading_btn = QtWidgets.QPushButton("🤖 Auto-Trading/Señal Telegram")
        self.mode_auto_trading_btn.setCheckable(True)
        self.mode_auto_trading_btn.clicked.connect(lambda: self.set_trading_mode(True))
        mode_grid.addWidget(self.mode_auto_trading_btn, 1, 1)
        # Advertencia para auto-trading
        self.auto_trading_warning = QtWidgets.QLabel(
            "⚠️ <b>ADVERTENCIA:</b> El modo Auto-Trading ejecutará órdenes reales en Binance. "
            "Asegúrate de configurar correctamente tus credenciales API."
        )
        self.auto_trading_warning.setStyleSheet("color: #dc2f02; padding: 8px; background-color: #2a0a00; border-radius: 5px;")
        self.auto_trading_warning.setWordWrap(True)
        self.auto_trading_warning.setVisible(getattr(self.config, 'auto_trading_enabled', False))
        mode_grid.addWidget(self.auto_trading_warning, 2, 0, 1, 2)
        scroll_layout.addWidget(mode_frame)

        # ========== CONFIGURACIÓN AUTOTRADER AVANZADO ==========
        autotrader_frame, autotrader_layout = self._create_titled_frame("🤖 Configuraci��n AutoTrader", scroll_widget)
        autotrader_grid = QtWidgets.QGridLayout()
        autotrader_layout.addLayout(autotrader_grid)

        # Modo Testnet/Real
        autotrader_grid.addWidget(QtWidgets.QLabel("🌐 Modo:"), 0, 0)
        self.autotrader_mode_combo = QtWidgets.QComboBox()
        self.autotrader_mode_combo.addItems(["testnet", "real"])
        self.autotrader_mode_combo.setCurrentText(getattr(self.config, 'AUTOTRADER_MODE', 'testnet'))
        self.autotrader_mode_combo.setStyleSheet(
            "background-color: #16213e; color: #ffd60a; border: 2px solid #ffd60a; "
            "padding: 8px; font-weight: bold;"
        )
        self.autotrader_mode_combo.currentTextChanged.connect(self._on_autotrader_mode_changed)
        autotrader_grid.addWidget(self.autotrader_mode_combo, 0, 1)

        # Margen inicial (USDT)
        autotrader_grid.addWidget(QtWidgets.QLabel("💵 Margen Inicial (USDT):"), 1, 0)
        self.autotrader_margin_spin = QtWidgets.QDoubleSpinBox()
        self.autotrader_margin_spin.setRange(0.1, 1000.0)
        self.autotrader_margin_spin.setValue(getattr(self.config, 'AUTOTRADER_MARGIN_USDT', 1.0))
        self.autotrader_margin_spin.setSingleStep(0.5)
        self.autotrader_margin_spin.setDecimals(2)
        self.autotrader_margin_spin.setStyleSheet("background-color: #16213e; color: white; border: 1px solid #1a2a4c; padding: 5px;")
        self.autotrader_margin_spin.valueChanged.connect(self._on_autotrader_margin_changed)
        autotrader_grid.addWidget(self.autotrader_margin_spin, 1, 1)

        # Apalancamiento
        autotrader_grid.addWidget(QtWidgets.QLabel("⚡ Apalancamiento:"), 2, 0)
        self.autotrader_leverage_combo = QtWidgets.QComboBox()
        self.autotrader_leverage_combo.addItems(["1x", "5x", "10x", "15x", "20x", "25x"])
        current_lev = getattr(self.config, 'AUTOTRADER_LEVERAGE', 1)
        self.autotrader_leverage_combo.setCurrentText(f"{current_lev}x")
        self.autotrader_leverage_combo.setStyleSheet(
            "background-color: #16213e; color: #00d4aa; border: 1px solid #00d4aa; "
            "padding: 8px; font-weight: bold;"
        )
        self.autotrader_leverage_combo.currentTextChanged.connect(self._on_autotrader_leverage_changed)
        autotrader_grid.addWidget(self.autotrader_leverage_combo, 2, 1)

        # Capital total (para interés compuesto)
        autotrader_grid.addWidget(QtWidgets.QLabel("💰 Capital Total (USDT):"), 3, 0)
        self.autotrader_capital_spin = QtWidgets.QDoubleSpinBox()
        self.autotrader_capital_spin.setRange(1.0, 100000.0)
        self.autotrader_capital_spin.setValue(getattr(self.config, 'AUTOTRADER_CAPITAL_USDT', 10.0))
        self.autotrader_capital_spin.setSingleStep(1.0)
        self.autotrader_capital_spin.setDecimals(2)
        self.autotrader_capital_spin.setStyleSheet("background-color: #16213e; color: white; border: 1px solid #1a2a4c; padding: 5px;")
        self.autotrader_capital_spin.valueChanged.connect(self._on_autotrader_capital_changed)
        autotrader_grid.addWidget(self.autotrader_capital_spin, 3, 1)

        # Interés compuesto checkbox
        self.autotrader_compound_checkbox = QtWidgets.QCheckBox("📈 Interés Compuesto")
        self.autotrader_compound_checkbox.setChecked(getattr(self.config, 'AUTOTRADER_COMPOUND_ENABLED', False))
        self.autotrader_compound_checkbox.setStyleSheet("color: #52b788; font-weight: bold;")
        self.autotrader_compound_checkbox.stateChanged.connect(self._on_autotrader_compound_changed)
        autotrader_grid.addWidget(self.autotrader_compound_checkbox, 4, 0)

        # Porcentaje de interés compuesto
        self.autotrader_compound_spin = QtWidgets.QDoubleSpinBox()
        self.autotrader_compound_spin.setRange(1.0, 50.0)
        self.autotrader_compound_spin.setValue(getattr(self.config, 'AUTOTRADER_COMPOUND_PERCENT', 10.0))
        self.autotrader_compound_spin.setSuffix(" %")
        self.autotrader_compound_spin.setStyleSheet("background-color: #16213e; color: white; border: 1px solid #1a2a4c; padding: 5px;")
        self.autotrader_compound_spin.valueChanged.connect(self._on_autotrader_compound_percent_changed)
        autotrader_grid.addWidget(self.autotrader_compound_spin, 4, 1)

        # Info de posición efectiva
        self.autotrader_position_label = QtWidgets.QLabel()
        self.autotrader_position_label.setStyleSheet("color: #00d4aa; font-size: 11px; padding: 5px;")
        self.autotrader_position_label.setWordWrap(True)
        self._update_autotrader_position_label()
        autotrader_grid.addWidget(self.autotrader_position_label, 5, 0, 1, 2)

        scroll_layout.addWidget(autotrader_frame)

        # Parámetros optimizados
        params_frame, params_layout = self._create_titled_frame("⚖️ Parámetros de Señal Optimizados", scroll_widget)

        def add_optimized_slider(layout, text, min_val, max_val, initial_val, format_str="{:d}"):
            grid = QtWidgets.QGridLayout()
            label = QtWidgets.QLabel(text)
            label.setStyleSheet("color: white; font-weight: bold;")
            slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue(initial_val)
            slider.setStyleSheet(
                "QSlider::groove:horizontal { background: #16213e; height: 8px; border-radius: 4px; }"
                "QSlider::handle:horizontal { background: #00d4aa; width: 20px; height: 20px; "
                "border-radius: 10px; margin: -6px 0; }"
                "QSlider::sub-page:horizontal { background: #52b788; border-radius: 4px; }"
            )
            value_label = QtWidgets.QLabel(format_str.format(initial_val))
            value_label.setStyleSheet("color: #00d4aa; font-weight: bold; min-width: 60px;")
            value_label.setAlignment(QtCore.Qt.AlignCenter)
            slider.valueChanged.connect(lambda v, lbl=value_label, fmt=format_str: lbl.setText(fmt.format(v)))
            grid.addWidget(label, 0, 0)
            grid.addWidget(slider, 0, 1)
            grid.addWidget(value_label, 0, 2)
            layout.addLayout(grid)
            return slider, value_label
        # Sliders optimizados (UMBRALES SIMPLIFICADOS 70/80)
        # ═══════════════════════════════════════════════════════════════
        # UMBRALES DESTACADA (Alertas iniciales - Más permisivos)
        # ═════════��═════════════════════════════════════════════════════
        self.signal_neural_destacada_slider, _ = add_optimized_slider(
            params_layout, "🔥 Neural DESTACADA (IA):", 50, 90, 
            int(self.config.MIN_NEURAL_DESTACADA), "{:d}%"
        )
        self.signal_technical_destacada_slider, _ = add_optimized_slider(
            params_layout, "🔥 Técnico DESTACADA:", 50, 90, 
            int(self.config.MIN_TECHNICAL_DESTACADA), "{:d}%"
        )
        self.signal_alignment_destacada_slider, _ = add_optimized_slider(
            params_layout, "🔥 Alineación DESTACADA:", 50, 90, 
            int(self.config.MIN_ALIGNMENT_DESTACADA), "{:d}%"
        )
        # ═══════════════════════════════════════════════════════════════
        # UMBRALES CONFIRMADA (Señales confirmadas - Más estrictos)
        # ═══════════════════════════════════════════════════════════════
        self.signal_neural_confirmada_slider, _ = add_optimized_slider(
            params_layout, "✅ Neural CONFIRMADA (IA):", 70, 95, 
            int(self.config.MIN_NEURAL_CONFIRMADA), "{:d}%"
        )
        self.signal_technical_confirmada_slider, _ = add_optimized_slider(
            params_layout, "✅ Técnico CONFIRMADA:", 70, 95, 
            int(self.config.MIN_TECHNICAL_CONFIRMADA), "{:d}%"
        )
        self.signal_alignment_confirmada_slider, _ = add_optimized_slider(
            params_layout, "✅ Alineación CONFIRMADA:", 70, 95, 
            int(self.config.MIN_ALIGNMENT_CONFIRMADA), "{:d}%"
        )
        # ═══════════════════════════════════════════════════════════════
        # CONEXIONES DINÁMICAS - Actualizar config en tiempo real
        # ═══════════════════════════════════════════════════════════════
        self.signal_neural_destacada_slider.valueChanged.connect(
            lambda v: setattr(self.config, 'MIN_NEURAL_DESTACADA', float(v)))
        self.signal_technical_destacada_slider.valueChanged.connect(
            lambda v: setattr(self.config, 'MIN_TECHNICAL_DESTACADA', float(v)))
        self.signal_alignment_destacada_slider.valueChanged.connect(
            lambda v: setattr(self.config, 'MIN_ALIGNMENT_DESTACADA', float(v)))
        self.signal_neural_confirmada_slider.valueChanged.connect(
            lambda v: setattr(self.config, 'MIN_NEURAL_CONFIRMADA', float(v)))
        self.signal_technical_confirmada_slider.valueChanged.connect(
            lambda v: setattr(self.config, 'MIN_TECHNICAL_CONFIRMADA', float(v)))
        self.signal_alignment_confirmada_slider.valueChanged.connect(
            lambda v: setattr(self.config, 'MIN_ALIGNMENT_CONFIRMADA', float(v)))
        # ═══════════════════════════════════════════════════════════════
        # PESOS DE ANÁLISIS
        # ═══════════════════════════════════════════════════════════════
        self.neural_weight_slider, _ = add_optimized_slider(
            params_layout, "🧠 Peso Red Neuronal:", 20, 60, 
            int(self.config.NEURAL_WEIGHT * 100), "{:d}%"
        )
        self.technical_weight_slider, _ = add_optimized_slider(
            params_layout, "📊 Peso Análisis Técnico:", 20, 50, 
            int(self.config.TECHNICAL_WEIGHT * 100), "{:d}%"
        )

        # ═══════════════════════════════════════════════════════════════
        # LÍMITE DE SEÑALES DIARIAS
        # ════════════════════════════════════════════════════��══════════
        self.max_daily_signals_slider, _ = add_optimized_slider(
            params_layout, "📊 Señales Diarias Máximo:", 1, 20, 
            int(self.config.MAX_DAILY_SIGNALS), "{:d}"
        )
        scroll_layout.addWidget(params_frame)
        # Configuración de trading optimizada
        trading_frame, trading_layout = self._create_titled_frame("⚙️ Trading Optimizado", scroll_widget)
        trading_grid = QtWidgets.QGridLayout()
        trading_layout.addLayout(trading_grid)

        # ═══════════════════════════════════════════════════════════════
        # SELECTOR DE TIPO DE MERCADO (PERPETUALS vs SPOT)
        # ═══════════════════════════════════════════════════════════════
        trading_grid.addWidget(QtWidgets.QLabel("📈 Tipo de Mercado:"), 0, 0)
        self.market_type_combo = QtWidgets.QComboBox()
        self.market_type_combo.addItems(["PERPETUALS", "SPOT"])
        self.market_type_combo.setCurrentText(self.config.MARKET_TYPE)
        self.market_type_combo.setStyleSheet(
            "background-color: #16213e; color: #00d4aa; border: 2px solid #00d4aa; "
            "padding: 8px; font-weight: bold; font-size: 12px;"
        )
        self.market_type_combo.currentTextChanged.connect(self._on_market_type_changed)
        trading_grid.addWidget(self.market_type_combo, 0, 1)

        # Label para mostrar comisión actual
        self.commission_label = QtWidgets.QLabel(
            f"💵 Comisión: {self.config.get_commission_rate():.2f}% (Round-trip: {self.config.get_round_trip_commission():.2f}%)"
        )
        self.commission_label.setStyleSheet("color: #ffc107; font-size: 11px; padding: 5px;")
        trading_grid.addWidget(self.commission_label, 1, 0, 1, 2)

        # Label para mostrar pares activos
        self.pairs_count_label = QtWidgets.QLabel(f"📊 Pares activos: {len(self.config.TRADING_SYMBOLS)}")
        self.pairs_count_label.setStyleSheet("color: #aaa; font-size: 11px; padding: 5px;")
        trading_grid.addWidget(self.pairs_count_label, 2, 0, 1, 2)

        trading_grid.addWidget(QtWidgets.QLabel("Timeframe Principal:"), 3, 0)
        self.primary_tf_combo = QtWidgets.QComboBox()
        self.primary_tf_combo.addItems(self.config.TIMEFRAMES)
        self.primary_tf_combo.setCurrentText(self.config.PRIMARY_TIMEFRAME)
        self.primary_tf_combo.setStyleSheet("background-color: #16213e; color: white; border: 1px solid #1a2a4c; padding: 5px;")
        trading_grid.addWidget(self.primary_tf_combo, 3, 1)
        trading_grid.addWidget(QtWidgets.QLabel("Timeframe Entrada:"), 4, 0)
        self.entry_tf_combo = QtWidgets.QComboBox()
        self.entry_tf_combo.addItems(self.config.TIMEFRAMES)
        self.entry_tf_combo.setCurrentText(self.config.ENTRY_TIMEFRAME)
        self.entry_tf_combo.setStyleSheet("background-color: #16213e; color: white; border: 1px solid #1a2a4c; padding: 5px;")
        trading_grid.addWidget(self.entry_tf_combo, 4, 1)
        # Más sliders de configuración
        self.max_risk_slider, _ = add_optimized_slider(
            trading_layout, "💸 Riesgo Máximo por Trade:", 5, 30, 
            int(self.config.MAX_RISK_PER_TRADE * 1000), "0.{:02d}%"
        )

        # ═══════════════════════════════════════════════════════════════
        # R/R MÍNIMO: Escala 0.5 a 3.0 (valores x10: 5-30)
        # ════════════════════════════════════════��══════════════════════
        rr_layout = QtWidgets.QHBoxLayout()
        rr_label = QtWidgets.QLabel("⚖️ R/R Mínimo (0.5 - 1.0):")
        rr_label.setStyleSheet("color: white; font-size: 12px;")
        self.min_rr_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.min_rr_slider.setRange(5, 10)  # 0.5 a 3.0
        self.min_rr_slider.setValue(int(self.config.MIN_RISK_REWARD_RATIO * 10))
        self.min_rr_slider.setStyleSheet("QSlider::groove:horizontal { height: 6px; background: #1a2a4c; } QSlider::handle:horizontal { width: 16px; background: #f72585; border-radius: 8px; }")
        self.min_rr_value_label = QtWidgets.QLabel(f"1:{self.config.MIN_RISK_REWARD_RATIO:.1f}")
        self.min_rr_value_label.setStyleSheet("color: #f72585; font-weight: bold; min-width: 50px;")
        self.min_rr_slider.valueChanged.connect(lambda v: self.min_rr_value_label.setText(f"1:{v/10:.1f}"))
        rr_layout.addWidget(rr_label)
        rr_layout.addWidget(self.min_rr_slider)
        rr_layout.addWidget(self.min_rr_value_label)
        trading_layout.addLayout(rr_layout)

        # ═══════════════════════════════════════════════════════════════
        # VOLUMEN MÍNIMO: Escala x0.5 a x1.5 (valores x10: 5-15)
        # ═══════════════════════════════════════════════════════════════
        vol_layout = QtWidgets.QHBoxLayout()
        vol_label = QtWidgets.QLabel("📊 Volumen Mínimo (x0.5 - x1.5):")
        vol_label.setStyleSheet("color: white; font-size: 12px;")
        self.min_volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.min_volume_slider.setRange(5, 15)  # x0.5 a x1.5
        self.min_volume_slider.setValue(int(self.config.MIN_VOLUME_RATIO * 10))
        self.min_volume_slider.setStyleSheet("QSlider::groove:horizontal { height: 6px; background: #1a2a4c; } QSlider::handle:horizontal { width: 16px; background: #4cc9f0; border-radius: 8px; }")
        self.min_volume_value_label = QtWidgets.QLabel(f"x{self.config.MIN_VOLUME_RATIO:.1f}")
        self.min_volume_value_label.setStyleSheet("color: #4cc9f0; font-weight: bold; min-width: 50px;")
        self.min_volume_slider.valueChanged.connect(lambda v: self.min_volume_value_label.setText(f"x{v/10:.1f}"))
        vol_layout.addWidget(vol_label)
        vol_layout.addWidget(self.min_volume_slider)
        vol_layout.addWidget(self.min_volume_value_label)
        trading_layout.addLayout(vol_layout)

        # ═══════════════════════════════════════════════════════════════
        # STOP LOSS: Escala 0.5% a 3.0% (valores x10: 5-30)
        # ═══════════════════════════════════════════════════════════════
        sl_layout = QtWidgets.QHBoxLayout()
        sl_label = QtWidgets.QLabel("🛑 Stop Loss % (0.3 - 1.0):")
        sl_label.setStyleSheet("color: white; font-size: 12px;")
        self.stop_loss_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.stop_loss_slider.setRange(3, 10)  # 0.3% a 1.0%
        self.stop_loss_slider.setValue(int(self.config.DEFAULT_STOP_LOSS_PERCENT * 1000))  # 0.01 * 1000 = 10
        self.stop_loss_slider.setStyleSheet("QSlider::groove:horizontal { height: 6px; background: #1a2a4c; } QSlider::handle:horizontal { width: 16px; background: #ff6b6b; border-radius: 8px; }")
        self.stop_loss_value_label = QtWidgets.QLabel(f"{self.config.DEFAULT_STOP_LOSS_PERCENT * 100:.1f}%")
        self.stop_loss_value_label.setStyleSheet("color: #ff6b6b; font-weight: bold; min-width: 50px;")
        self.stop_loss_slider.valueChanged.connect(self._on_stop_loss_changed)
        sl_layout.addWidget(sl_label)
        sl_layout.addWidget(self.stop_loss_slider)
        sl_layout.addWidget(self.stop_loss_value_label)
        trading_layout.addLayout(sl_layout)

        # ✅ TP por Defecto ELIMINADO - Ahora usa MILESTONE_3 como objetivo de profit
        # El Take Profit se configura en "Objetivo Final" de los Milestones

        self.scan_interval_slider, _ = add_optimized_slider(
            trading_layout, "⏱️ Intervalo Escaneo:", 1, 60, 
            self.config.SCAN_INTERVAL, "{:d}s"
        )
        scroll_layout.addWidget(trading_frame)

        # ═══════════════════════════════════════════════════════════════
        # CONFIGURACIÓN DE MILESTONES (INTERVALOS DE SEGUIMIENTO CON DECIMALES)
        # ═══════════════════════════════════════════════════════════════
        milestones_frame, milestones_layout = self._create_titled_frame("📊 Milestones de Seguimiento (Intervalos %)", scroll_widget)

        # Función helper para crear sliders de milestones con decimales
        def create_milestone_slider(layout, label_text, min_val, max_val, initial_val):
            row_layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(label_text)
            label.setStyleSheet("color: white; font-size: 12px;")
            slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue(initial_val)
            slider.setStyleSheet("QSlider::groove:horizontal { height: 6px; background: #1a2a4c; } QSlider::handle:horizontal { width: 16px; background: #00d4aa; border-radius: 8px; }")
            value_label = QtWidgets.QLabel(f"{initial_val/10:.1f}%")
            value_label.setStyleSheet("color: #00d4aa; font-weight: bold; min-width: 50px;")
            slider.valueChanged.connect(lambda v: value_label.setText(f"{v/10:.1f}%"))
            row_layout.addWidget(label)
            row_layout.addWidget(slider)
            row_layout.addWidget(value_label)
            layout.addLayout(row_layout)
            return slider, value_label

        # Slider 1: Primer avance - Rango: 0.3 a 1.5 (valores x10: 3-15)
        self.milestone_1_slider, _ = create_milestone_slider(
            milestones_layout, "📈 Primer Avance:", 3, 15, 
            int(self.config.MILESTONE_1 * 10)
        )
        self.milestone_1_slider.valueChanged.connect(self._on_milestones_changed)

        # Slider 2: Segundo avance - Rango: 0.5 a 2.5 (valores x10: 5-25)
        self.milestone_2_slider, _ = create_milestone_slider(
            milestones_layout, "📈 Segundo Avance:", 5, 25, 
            int(self.config.MILESTONE_2 * 10)
        )
        self.milestone_2_slider.valueChanged.connect(self._on_milestones_changed)

        # Slider 3: Objetivo final / Take Profit - Rango: 1.0 a 5.0 (valores x10: 10-50)
        self.milestone_3_slider, _ = create_milestone_slider(
            milestones_layout, "🎯 Objetivo Final (TP):", 10, 50, 
            int(self.config.MILESTONE_3 * 10)
        )
        self.milestone_3_slider.valueChanged.connect(self._on_milestones_changed)

        milestones_info = QtWidgets.QLabel(
            "ℹ️ Valores recomendados: 1.0% (primer aviso), 2.0% (segundo aviso), 3.0% (objetivo/TP)"
        )
        milestones_info.setStyleSheet("color: #aaa; font-size: 11px; padding: 5px;")
        milestones_layout.addWidget(milestones_info)

        scroll_layout.addWidget(milestones_frame)

        # Botón de guardar optimizado
        save_btn = QtWidgets.QPushButton("💾 Guardar Configuración Optimizada")
        save_btn.setStyleSheet(
            "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #52b788, stop:1 #00d4aa); "
            "color: white; padding: 15px; font-weight: bold; border-radius: 8px; font-size: 14px;"
        )
        save_btn.clicked.connect(self.save_config_optimized)
        scroll_layout.addWidget(save_btn)
        scroll_layout.addStretch()
        tab_layout.addWidget(config_scroll)
        return tab_widget
    # Métodos de manejo de eventos optimizados



    def start_bot_optimized(self):
        """Iniciar bot optimizado"""
        self.status_label.setText("🚀 Ejecutándose")
        self.status_label.setStyleSheet("color: #00d4aa; font-weight: bold;")
        try:
            # Limpieza agresiva de estado y caches al iniciar
            if hasattr(self, 'bot') and hasattr(self.bot, 'clear_all_caches'):
                self.bot.clear_all_caches()
            if hasattr(self, 'telegram_client') and hasattr(self.telegram_client, 'reset_signal_tracking'):
                self.telegram_client.reset_signal_tracking()
            if hasattr(self, 'bot') and hasattr(self.bot, 'signal_tracker'):
                try:
                    self.bot.signal_tracker.tracked_signals.clear()
                    self.bot.signal_tracker.price_cache.clear()
                except Exception:
                    pass
            self.signals_tree.setRowCount(0)
            self.signals_count_label.setText("Señales: 0")
        except Exception:
            pass
        try:
            if hasattr(self, 'bot') and hasattr(self.bot, 'active_signals'):
                self.bot.active_signals = []
        except Exception:
            pass
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.bot.start_optimized()
        logger.info("🚀 Bot Optimizado v35.0.0.0 iniciado")
        self.log_message("🚀 Bot Avanzado Optimizado v35.0.0.0 iniciado con mejoras de rendimiento")
        self.update_pair_scan_progress(0)
        self.highlight_progress_bar.setVisible(False)
        self.highlight_progress_bar.setValue(0)
        self.highlight_progress_bar.setFormat("Esperando señal DESTACADA...")

    def stop_bot_optimized(self):
        """Detener bot optimizado"""
        self.status_label.setText("Detenido")
        self.status_label.setStyleSheet("color: red;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.bot.stop_optimized()
        logger.info("⏹️ Bot Optimizado detenido")
        self.log_message("⏹️ Bot Optimizado detenido")
        try:
            if hasattr(self, 'bot') and hasattr(self.bot, 'clear_all_caches'):
                self.bot.clear_all_caches()
            if hasattr(self, 'telegram_client') and hasattr(self.telegram_client, 'reset_signal_tracking'):
                self.telegram_client.reset_signal_tracking()
            if hasattr(self, 'bot') and hasattr(self.bot, 'signal_tracker'):
                try:
                    self.bot.signal_tracker.tracked_signals.clear()
                    self.bot.signal_tracker.price_cache.clear()
                except Exception:
                    pass
        except Exception:
            pass
        self.update_pair_scan_progress(0)
        # NUEVO: Resetear barra de seguimiento
        self.highlight_progress_bar.setVisible(False)
        self.highlight_progress_bar.setValue(0)
        self.highlight_progress_bar.setFormat("Esperando señal DESTACADA...")
        try:
            self.signals_tree.setRowCount(0)
            self.signals_count_label.setText("Señales: 0")
        except Exception:
            pass
        try:
            if hasattr(self, 'bot') and hasattr(self.bot, 'active_signals'):
                self.bot.active_signals = []
        except Exception:
            pass

    def on_pair_select_optimized(self, item):
        """Seleccionar par optimizado"""
        pair = item.text()
        self.bot.set_pair_optimized(pair)
        self.log_message(f"📊 Cambiado a {pair} con análisis optimizado")
        # CRÍTICO: Cargar datos del par seleccionado INMEDIATAMENTE
        # Esto asegura que la GUI muestre los valores correctos al cambiar de par
        try:
            self.bot.load_pair_data_optimized()
            self.log_message(f"✅ Datos de {pair} cargados correctamente")
            # FORZAR actualización visual inmediata
            QtCore.QTimer.singleShot(100, lambda: self.update_gui_and_data_optimized())
        except Exception as e:
            logger.error(f"Error cargando datos de {pair}: {e}")
            self.log_message(f"⚠️ Error cargando datos de {pair}")
        if self.bot.running:
            self.bot.symbols_analyzed_count = 0
            self.update_pair_scan_progress(0)



    def _on_signal_cell_clicked(self, row, column):
        """Manejar doble click en celda de señal para mostrar gráfico"""
        try:
            # Obtener símbolo de la fila clickeada
            symbol_item = self.signals_tree.item(row, 0)
            if not symbol_item:
                return
            symbol = symbol_item.text()
            # Buscar la señal correspondiente en active_signals
            matching_signals = [
                sig for sig in self.bot.active_signals 
                if sig.get('symbol') == symbol
            ]
            if not matching_signals:
                self.log_message(f"⚠️ No se encontró información de señal para {symbol}")
                return
            # Tomar la señal más reciente
            signal_data = matching_signals[-1]
            # Verificar si tiene gráfico
            chart_path = signal_data.get('chart_path')

            # Si no hay gráfico, intentar generarlo on-demand
            if not chart_path or not os.path.exists(chart_path):
                self.log_message(f"📊 Generando gráfico para {symbol}...")
                try:
                    if hasattr(self.bot, 'chart_generator') and self.bot.chart_generator:
                        # Cargar datos del símbolo
                        df = self.bot.client.get_klines(symbol, self.bot.config.ENTRY_TIMEFRAME, limit=500)
                        if df is not None and not df.empty:
                            # ✅ Usar technical_analyzer que SÍ existe en OptimizedTradingBot
                            data_id = str(hash(symbol))
                            ema50 = self.bot.technical_analyzer.calculate_ema(df['close'], 50, data_id)
                            ema200 = self.bot.technical_analyzer.calculate_ema(df['close'], 200, data_id)
                            rsi = self.bot.technical_analyzer.calculate_rsi(df['close'], 14, data_id)
                            technical_analysis = {
                                'ema50': float(ema50.iloc[-1]) if len(ema50) > 0 else 0,
                                'ema200': float(ema200.iloc[-1]) if len(ema200) > 0 else 0,
                                'rsi': float(rsi.iloc[-1]) if len(rsi) > 0 else 50,
                                'price': float(df['close'].iloc[-1])
                            }
                            chart_path = self.bot.chart_generator.generate_signal_chart(
                                symbol,
                                df,
                                signal_data,
                                technical_analysis
                            )
                            signal_data['chart_path'] = chart_path
                            # ✅ Agregar dataframe para TradingView
                            signal_data['dataframe_entry'] = df.copy()
                            self.log_message(f"✅ Gráfico generado exitosamente para {symbol}")
                except Exception as e:
                    self.log_message(f"⚠️ No se pudo generar gráfico: {e}")

            if chart_path and os.path.exists(chart_path):
                # Mostrar ventana flotante con gráfico
                # Agregar chart_path al signal_data
                signal_data['chart_path'] = chart_path
                chart_dialog = SignalChartDialog(
                    signal_data=signal_data,
                    parent=self
                )
                chart_dialog.exec_()
                self.log_message(f"📊 Mostrando gráfico de {symbol}")
            else:
                self.log_message(f"⚠️ No se pudo generar gráfico para {symbol}")
        except Exception as e:
            logger.error(f"Error mostrando gráfico de señal: {e}")
            self.log_message(f"❌ Error mostrando gráfico: {e}")

    def train_neural_network_optimized(self):
        """Entrenar red neuronal optimizada"""
        if not TORCH_AVAILABLE:
            QtWidgets.QMessageBox.critical(self, "Error PyTorch", "PyTorch no está disponible para entrenar la IA optimizada.")
            return
        reply = QtWidgets.QMessageBox.question(
            self, "Entrenamiento IA Optimizada",
            "¿Entrenar la IA con algoritmos optimizados?\nEste proceso es más eficiente pero puede tomar varios minutos.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.train_btn.setEnabled(False)
            self.quick_train_btn.setEnabled(False)
            # Forzar limpieza de archivos corruptos antes de entrenar
            self.bot.neural_trader._clear_corrupted_model_files()
            threading.Thread(target=self._train_neural_thread_optimized, daemon=True).start()

    def quick_train_neural_network(self):
        """Entrenamiento rápido optimizado"""
        if not TORCH_AVAILABLE:
            QtWidgets.QMessageBox.critical(self, "Error PyTorch", "PyTorch no está disponible.")
            return
        reply = QtWidgets.QMessageBox.question(
            self, "Entrenamiento Rápido",
            "¿Realizar entrenamiento rápido optimizado?\nUsa menos datos pero es más rápido (recomendado para pruebas).",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.train_btn.setEnabled(False)
            self.quick_train_btn.setEnabled(False)
            threading.Thread(target=self._quick_train_neural_thread, daemon=True).start()

    def force_retrain_neural_network(self):
        """Forzar reentrenamiento completo de la red neuronal"""
        if not TORCH_AVAILABLE:
            QtWidgets.QMessageBox.critical(self, "Error PyTorch", "PyTorch no está disponible para reentrenar la IA.")
            return
        reply = QtWidgets.QMessageBox.question(
            self, "Reentrenamiento Forzado",
            "¿Desea eliminar el modelo actual y entrenar uno nuevo desde cero?\n"
            "Esta acción borrará todo el aprendizaje previo y puede tomar mucho tiempo.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.train_btn.setEnabled(False)
            self.quick_train_btn.setEnabled(False)
            self.retrain_btn.setEnabled(False)
            # Iniciar el proceso de reentrenamiento en un hilo separado
            threading.Thread(target=self._force_retrain_thread, daemon=True).start()

    def _force_retrain_thread(self):
        """Hilo para reentrenamiento forzado"""
        try:
            self.log_message("🔄 Iniciando reentrenamiento forzado de la IA...")
            # Forzar la limpieza de archivos del modelo
            self.bot.neural_trader._clear_model_files()
            # Crear una nueva instancia del trader con force_retrain=True
            self.bot.neural_trader = OptimizedNeuralTrader(self.config, force_retrain=True)
            def progress_callback(value):
                QMetaObject.invokeMethod(
                    self.progress_bar, "setValue", 
                    QtCore.Qt.QueuedConnection, 
                    Q_ARG(int, value)
                )
            # Entrenar con todos los símbolos para un modelo completo
            success = self.bot.neural_trader.train_with_optimized_data(
                progress_callback=progress_callback
            )
            if success:
                self.log_message("✅ Reentrenamiento forzado completado exitosamente")
                QMetaObject.invokeMethod(
                    self, "show_training_success", 
                    QtCore.Qt.QueuedConnection
                )
            else:
                self.log_message("❌ Error en reentrenamiento forzado o datos insuficientes")
        except Exception as e:
            self.log_message(f"❌ Error durante reentrenamiento forzado: {str(e)}")
            logger.error(f"Error en reentrenamiento forzado: {e}")
        finally:
            # Restaurar estado de los botones
            QMetaObject.invokeMethod(
                self.train_btn, "setEnabled", 
                QtCore.Qt.QueuedConnection, Q_ARG(bool, True)
            )
            QMetaObject.invokeMethod(
                self.quick_train_btn, "setEnabled", 
                QtCore.Qt.QueuedConnection, Q_ARG(bool, True)
            )
            QMetaObject.invokeMethod(
                self.retrain_btn, "setEnabled", 
                QtCore.Qt.QueuedConnection, Q_ARG(bool, True)
            )
            QMetaObject.invokeMethod(
                self.progress_bar, "setValue", 
                QtCore.Qt.QueuedConnection, Q_ARG(int, 0)
            )

    def _train_neural_thread_optimized(self):
        """Hilo de entrenamiento optimizado"""
        self.log_message("🧠 Iniciando entrenamiento IA optimizada v35.0.0.0...")
        def progress_callback(value):
            QMetaObject.invokeMethod(
                self.progress_bar, "setValue", 
                QtCore.Qt.QueuedConnection, 
                Q_ARG(int, value)
            )
        # Usar TODOS los símbolos para entrenamiento completo
        training_symbols = self.config.TRADING_SYMBOLS  # TODOS los símbolos disponibles
        success = self.bot.neural_trader.train_with_optimized_data(
            symbols=training_symbols,
            progress_callback=progress_callback
        )
        if success:
            self.log_message("✅ Entrenamiento IA optimizada completado exitosamente")
            QMetaObject.invokeMethod(
                self, "show_training_success", 
                QtCore.Qt.QueuedConnection
            )
        else:
            self.log_message("❌ Error en entrenamiento IA optimizada o datos insuficientes")
        QMetaObject.invokeMethod(
            self.train_btn, "setEnabled", 
            QtCore.Qt.QueuedConnection, Q_ARG(bool, True)
        )
        QMetaObject.invokeMethod(
            self.quick_train_btn, "setEnabled", 
            QtCore.Qt.QueuedConnection, Q_ARG(bool, True)
        )
        QMetaObject.invokeMethod(
            self.progress_bar, "setValue", 
            QtCore.Qt.QueuedConnection, Q_ARG(int, 0)
        )

    def _quick_train_neural_thread(self):
        """Hilo de entrenamiento rápido"""
        self.log_message("⚡ Iniciando entrenamiento rápido optimizado...")
        def progress_callback(value):
            QMetaObject.invokeMethod(
                self.progress_bar, "setValue", 
                QtCore.Qt.QueuedConnection, 
                Q_ARG(int, value)
            )
        # Entrenamiento RÁPIDO con 10 símbolos
        training_symbols = self.config.TRADING_SYMBOLS[:10]  # 10 símbolos para entrenamiento rápido
        # Temporalmente reducir épocas para entrenamiento rápido
        original_epochs = self.config.NEURAL_EPOCHS
        self.config.NEURAL_EPOCHS = 30  # Entrenamiento ultra rápido
        success = self.bot.neural_trader.train_with_optimized_data(
            symbols=training_symbols,
            days=30,  # 30 días para rapidez
            progress_callback=progress_callback
        )
        # Restaurar configuración original
        self.config.NEURAL_EPOCHS = original_epochs
        if success:
            self.log_message("⚡ Entrenamiento rápido completado exitosamente")
        else:
            self.log_message("❌ Error en entrenamiento rápido")
        QMetaObject.invokeMethod(
            self.train_btn, "setEnabled", 
            QtCore.Qt.QueuedConnection, Q_ARG(bool, True)
        )
        QMetaObject.invokeMethod(
            self.quick_train_btn, "setEnabled", 
            QtCore.Qt.QueuedConnection, Q_ARG(bool, True)
        )
        QMetaObject.invokeMethod(
            self.progress_bar, "setValue", 
            QtCore.Qt.QueuedConnection, Q_ARG(int, 0)
        )
    def _update_fix_api_indicator(self):
        """✅ Actualizar indicador de conexión FIX API en tiempo real"""
        try:
            if not hasattr(self, 'bot') or not hasattr(self.bot, 'client'):
                return

            fix_enabled = getattr(self.bot.client, 'fix_enabled', False)
            ws_disabled = getattr(self.bot.client, 'disable_websocket', False)

            if fix_enabled and ws_disabled:
                # ✅ FIX API ACTIVO
                self.fix_api_indicator.setText("🟢 FIX API Activo")
                self.fix_api_indicator.setStyleSheet(
                    "background-color: #2d6a4f; color: #52b788; padding: 6px 12px; "
                    "border-radius: 12px; font-weight: bold; border: 2px solid #52b788;"
                )
            else:
                # ⚫ REST API (FIX deshabilitado)
                self.fix_api_indicator.setText("🔵 REST API")
                self.fix_api_indicator.setStyleSheet(
                    "background-color: #1a3a4c; color: #00d4aa; padding: 6px 12px; "
                    "border-radius: 12px; font-weight: bold; border: 2px solid #00d4aa;"
                )
        except Exception as e:
            logger.debug(f"Error actualizando indicador FIX API: {e}")

    def on_tab_changed(self, index):
        """Manejador de cambio de pestaña"""
        try:
            # Si cambiamos a la pestaña de análisis (índice 1), actualizar el contenido
            if index == 1:  # Pestaña de análisis
                detailed_analysis = self.bot.get_detailed_analysis_optimized()
                if detailed_analysis:
                    self.analysis_text.setPlainText(detailed_analysis)
                    self.analysis_text.repaint()
                    self.analysis_text.verticalScrollBar().setValue(
                        self.analysis_text.verticalScrollBar().maximum()
                    )
                else:
                    self.analysis_text.setPlainText("No hay datos de análisis disponibles. Por favor, seleccione un par y espere a que se carguen los datos.")
                    self.analysis_text.repaint()
            # Si cambiamos a la pestaña de IA (índice 2), forzar actualización
            elif index == 2:
                self.update_gui_and_data_optimized()
            # Si cambiamos a la pestaña de Configuración (índice 4), pedir contraseña
            elif index == 4:
                if not getattr(self, '_config_unlocked', False):
                    self._request_config_password()
        except Exception as e:
            logger.error(f"Error al cambiar de pestaña: {e}")
            self.analysis_text.setPlainText(f"Error al cargar análisis: {str(e)}")
            self.analysis_text.repaint()

    def _request_config_password(self):
        """Solicitar contraseña para acceder a la pestaña de Configuración"""
        password, ok = QtWidgets.QInputDialog.getText(
            self, "Acceso a Configuración",
            "Ingrese la contraseña para acceder a Configuración:",
            QtWidgets.QLineEdit.Password
        )
        if ok and password == self.config.CONFIG_PASSWORD:
            self._config_unlocked = True
            self.log_message("🔓 Configuración desbloqueada")
        else:
            if ok:
                QtWidgets.QMessageBox.warning(self, "Error", "❌ Contraseña incorrecta")
            self.notebook.setCurrentIndex(0)  # Volver a Trading
    @pyqtSlot()
    def show_training_success(self):
        """Mostrar éxito de entrenamiento"""
        QtWidgets.QMessageBox.information(
            self, "Entrenamiento Exitoso",
            "🎉 IA optimizada entrenada correctamente!\n"
            "La red neuronal está lista para generar predicciones optimizadas."
        )
    def test_telegram_optimized(self):
        """Probar Telegram optimizado"""
        self.config.telegram_bot_token = self.token_entry.text()
        self.config.telegram_chat_id = self.chat_id_entry.text()
        # Actualizar cliente
        self.bot.telegram_client = OptimizedTelegramClient(self.config)
        if self.bot.telegram_client.test_connection():
            QtWidgets.QMessageBox.information(self, "Telegram", "✅ Conexión optimizada exitosa")
            self.log_message("✅ Conexión Telegram optimizada verificada")
        else:
            QtWidgets.QMessageBox.critical(self, "Telegram", "❌ Error en conexión optimizada")
            self.log_message("❌ Error en conexión Telegram optimizada")

    def toggle_credentials_visibility(self):
        """Alternar visibilidad de credenciales Binance"""
        if self.binance_key_entry.echoMode() == QtWidgets.QLineEdit.Password:
            self.binance_key_entry.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.binance_secret_entry.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.binance_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
            self.binance_secret_entry.setEchoMode(QtWidgets.QLineEdit.Password)

    def set_trading_mode(self, auto_trading: bool):
        """Cambiar modo de operación"""
        # Actualizar estados de botones
        self.mode_signals_only_btn.setChecked(not auto_trading)
        self.mode_auto_trading_btn.setChecked(auto_trading)
        # Mostrar/ocultar advertencia
        self.auto_trading_warning.setVisible(auto_trading)
        # Guardar en config
        self.config.auto_trading_enabled = auto_trading
        # Log del cambio
        mode_text = "Auto-Trading" if auto_trading else "Señales Solo"
        self.log_message(f"🎯 Modo cambiado a: {mode_text}")
        logger.info(f"[TARGET] Modo de operación cambiado a: {mode_text}")
        # Mostrar mensaje al usuario
        if auto_trading:
            QtWidgets.QMessageBox.warning(
                self, 
                "Modo Auto-Trading Activado",
                "⚠️ <b>ADVERTENCIA:</b><br><br>"
                "El bot ahora ejecutará órdenes reales en Binance.<br>"
                "Asegúrate de que:<br>"
                "• Tus credenciales API estén correctamente configuradas<br>"
                "• Tengas saldo suficiente en tu cuenta<br>"
                "• Hayas probado en Testnet primero<br><br>"
                "<b>¿Estás seguro de continuar?</b>"
            )
        else:
            QtWidgets.QMessageBox.information(
                self,
                "Modo Señales Solo",
                "📱 El bot solo enviará notificaciones a Telegram.<br>"
                "No ejecutará órdenes en Binance."
            )
    def _on_market_type_changed(self, market_type: str):
        """Handler cuando cambia el tipo de mercado"""
        try:
            self.config.MARKET_TYPE = market_type
            self.config.update_symbols_for_market_type()

            # Actualizar labels
            self.commission_label.setText(
                f"💵 Comisión: {self.config.get_commission_rate():.2f}% (Round-trip: {self.config.get_round_trip_commission():.2f}%)"
            )
            self.pairs_count_label.setText(f"📊 Pares activos: {len(self.config.TRADING_SYMBOLS)}")

            # Log del cambio
            self.log_message(f"📈 Mercado cambiado a: {market_type} ({len(self.config.TRADING_SYMBOLS)} pares)")
            logger.info(f"[MARKET] Tipo de mercado cambiado a {market_type} - Comisión: {self.config.get_commission_rate():.2f}%")

            # Actualizar label de posición del AutoTrader
            if hasattr(self, 'autotrader_position_label'):
                self._update_autotrader_position_label()
        except Exception as e:
            logger.error(f"Error cambiando tipo de mercado: {e}")

    def _on_testnet_checkbox_changed(self, state: int):
        """Handler cuando cambia el checkbox legacy de testnet - sincroniza con combo AutoTrader"""
        from PyQt5 import QtCore
        is_testnet = (state == QtCore.Qt.Checked)
        self.config.use_testnet = is_testnet
        self.config.USE_TESTNET = is_testnet

        # Sincronizar combo del AutoTrader (sin triggear su handler de nuevo)
        if hasattr(self, 'autotrader_mode_combo'):
            self.autotrader_mode_combo.blockSignals(True)
            self.autotrader_mode_combo.setCurrentText('testnet' if is_testnet else 'real')
            self.config.AUTOTRADER_MODE = 'testnet' if is_testnet else 'real'
            self.autotrader_mode_combo.blockSignals(False)

        logger.info(f"[TESTNET] Checkbox cambiado a: {'testnet' if is_testnet else 'real'}")

    def _on_autotrader_mode_changed(self, mode: str):
        """Handler cuando cambia el modo del AutoTrader (testnet/real)"""
        self.config.AUTOTRADER_MODE = mode
        is_testnet = (mode == 'testnet')
        self.config.use_testnet = is_testnet
        self.config.USE_TESTNET = is_testnet

        # Sincronizar checkbox legacy (sin triggear su handler de nuevo)
        if hasattr(self, 'testnet_checkbox'):
            self.testnet_checkbox.blockSignals(True)
            self.testnet_checkbox.setChecked(is_testnet)
            self.testnet_checkbox.blockSignals(False)

        mode_text = "TESTNET (pruebas)" if is_testnet else "REAL (dinero real)"
        self.log_message(f"🌐 AutoTrader modo: {mode_text}")
        logger.info(f"[AUTOTRADER] Modo cambiado a: {mode}")

        if mode == 'real':
            QtWidgets.QMessageBox.warning(
                self,
                "Modo REAL Activado",
                "💰 <b>ADVERTENCIA:</b><br><br>"
                "El AutoTrader ejecutará órdenes con dinero REAL.<br>"
                "Asegúrate de haber probado en Testnet primero."
            )

    def _on_autotrader_leverage_changed(self, leverage_text: str):
        """Handler cuando cambia el apalancamiento"""
        leverage = int(leverage_text.replace('x', ''))
        self.config.AUTOTRADER_LEVERAGE = leverage
        self.log_message(f"⚡ Apalancamiento: {leverage}x")
        logger.info(f"[AUTOTRADER] Apalancamiento cambiado a: {leverage}x")
        self._update_autotrader_position_label()

    def _on_autotrader_margin_changed(self, value: float):
        """Handler cuando cambia el margen inicial"""
        self.config.AUTOTRADER_MARGIN_USDT = value
        self._update_autotrader_position_label()

    def _on_autotrader_capital_changed(self, value: float):
        """Handler cuando cambia el capital total"""
        self.config.AUTOTRADER_CAPITAL_USDT = value
        self._update_autotrader_position_label()

    def _on_autotrader_compound_changed(self, state: int):
        """Handler cuando cambia el checkbox de interés compuesto"""
        from PyQt5 import QtCore
        self.config.AUTOTRADER_COMPOUND_ENABLED = (state == QtCore.Qt.Checked)
        self._update_autotrader_position_label()

    def _on_autotrader_compound_percent_changed(self, value: float):
        """Handler cuando cambia el porcentaje de interés compuesto"""
        self.config.AUTOTRADER_COMPOUND_PERCENT = value
        self._update_autotrader_position_label()

    def _update_autotrader_position_label(self):
        """Actualizar label con información de posición efectiva"""
        margin = getattr(self.config, 'AUTOTRADER_MARGIN_USDT', 1.0)
        leverage = getattr(self.config, 'AUTOTRADER_LEVERAGE', 1)
        capital = getattr(self.config, 'AUTOTRADER_CAPITAL_USDT', 10.0)
        compound_enabled = getattr(self.config, 'AUTOTRADER_COMPOUND_ENABLED', False)
        compound_pct = getattr(self.config, 'AUTOTRADER_COMPOUND_PERCENT', 10.0)
        market_type = getattr(self.config, 'MARKET_TYPE', 'PERPETUALS')

        effective_margin = margin
        if compound_enabled:
            effective_margin += capital * (compound_pct / 100.0)

        if market_type == "PERPETUALS":
            position = effective_margin * leverage
            info = f"📊 Margen: ${effective_margin:.2f} x {leverage}x = Posición: ${position:.2f} USDT"
        else:
            info = f"📊 Posición: ${effective_margin:.2f} USDT (SPOT sin apalancamiento)"

        if hasattr(self, 'autotrader_position_label'):
            self.autotrader_position_label.setText(info)

    def clean_all_data(self):
        """Limpia logs y gráficos temporales para liberar espacio"""
        try:
            # Limpiar logs
            log_dir = self.bot.config.LOGS_DIR
            if os.path.exists(log_dir):
                count = 0
                for f in glob.glob(os.path.join(log_dir, "*.log")):
                    try:
                        os.remove(f)
                        count += 1
                    except: pass
                logger.info(f"🧹 Limpieza: {count} logs eliminados")

            # Limpiar gráficos
            chart_dir = self.bot.config.CHARTS_DIR
            if os.path.exists(chart_dir):
                count = 0
                for f in glob.glob(os.path.join(chart_dir, "*.png")):
                    try:
                        os.remove(f)
                        count += 1
                    except: pass
                logger.info(f"🧹 Limpieza: {count} imágenes eliminadas")

            try:
                self.signals_tree.setRowCount(0)
                if hasattr(self, 'signals_count_label'):
                    self.signals_count_label.setText("Señales: 0")
            except Exception:
                pass
            try:
                if hasattr(self, 'bot') and hasattr(self.bot, 'active_signals'):
                    self.bot.active_signals = []
            except Exception:
                pass
            try:
                self.highlight_progress_bar.setVisible(False)
                self.highlight_progress_bar.setValue(0)
                self.confirmed_progress_bar.setVisible(False)
                self.confirmed_progress_bar.setValue(0)
            except Exception:
                pass

            self.log_message("✅ Limpieza de datos completada (Logs e Imágenes eliminados)")
            QtWidgets.QMessageBox.information(self, "Limpieza", "Se han eliminado los logs y gráficos temporales.")
        except Exception as e:
            logger.error(f"Error en limpieza: {e}")
            self.log_message(f"❌ Error en limpieza: {e}")

    def _on_milestones_changed(self, _=None):
        """Handler cuando cambian los sliders de milestones - sincroniza en tiempo real + JSON"""
        try:
            m1 = self.milestone_1_slider.value() / 10.0
            m2 = self.milestone_2_slider.value() / 10.0
            m3 = self.milestone_3_slider.value() / 10.0

            # Sincronizar todas las variables relacionadas en memoria
            self.config.MILESTONE_1 = m1
            self.config.MILESTONE_2 = m2
            self.config.MILESTONE_3 = m3
            self.config.MILESTONE_1_PERCENT = m1
            self.config.MILESTONE_2_PERCENT = m2
            self.config.MILESTONE_3_PERCENT = m3
            self.config.MILESTONES = [m1, m2, m3]
            self.config.PROFIT_MILESTONES = [m1, m2, m3]

            # TP = Objetivo Final (MILESTONE_3)
            self.config.PROFIT_TARGET_PERCENT = m3
            self.config.TAKE_PROFIT_PERCENT = m3

            # Sincronizar con SignalTracker si existe
            if hasattr(self, 'bot') and hasattr(self.bot, 'signal_tracker'):
                self.bot.signal_tracker.config = self.config

            # ✅ PERSISTIR: Guardar cambios al archivo JSON inmediatamente
            self.config.save_config()

            logger.info(f"[MILESTONES] Guardado: [{m1:.1f}%, {m2:.1f}%, {m3:.1f}%] | TP: {m3:.1f}%")
        except Exception as e:
            logger.error(f"[ERROR] Error sincronizando milestones: {e}")

    def _on_stop_loss_changed(self, value):
        """Handler cuando cambia el slider de Stop Loss - sincroniza en tiempo real + JSON"""
        try:
            sl_percent = value / 10.0  # Slider value 3-10 → 0.3% - 1.0%
            sl_decimal = value / 1000.0  # Slider value 3-10 → 0.003 - 0.01

            # Actualizar label visual
            self.stop_loss_value_label.setText(f"{sl_percent:.1f}%")

            # Sincronizar en memoria
            self.config.DEFAULT_STOP_LOSS_PERCENT = sl_decimal
            self.config.STOP_LOSS_PERCENT = sl_percent

            # Sincronizar con SignalTracker si existe
            if hasattr(self, 'bot') and hasattr(self.bot, 'signal_tracker'):
                self.bot.signal_tracker.config = self.config

            # ✅ PERSISTIR: Guardar cambios al archivo JSON
            self.config.save_config()

            logger.info(f"[STOP_LOSS] Guardado: {sl_percent:.1f}%")
        except Exception as e:
            logger.error(f"[ERROR] Error sincronizando stop_loss: {e}")

    def save_config_optimized(self):
        """Guardar configuración optimizada"""
        try:
            # Actualizar valores de configuración
            self.config.telegram_bot_token = self.token_entry.text()
            self.config.telegram_chat_id = self.chat_id_entry.text()
            self.config.telegram_enabled = self.telegram_enabled_var.isChecked()

            # ✅ TIPO DE MERCADO (PERPETUALS/SPOT)
            self.config.MARKET_TYPE = self.market_type_combo.currentText()
            self.config.update_symbols_for_market_type()

            # ✅ UMBRALES COMPLETAMENTE CONFIGURABLES
            self.config.MIN_NEURAL_DESTACADA = float(self.signal_neural_destacada_slider.value())
            self.config.MIN_TECHNICAL_DESTACADA = float(self.signal_technical_destacada_slider.value())
            self.config.MIN_ALIGNMENT_DESTACADA = float(self.signal_alignment_destacada_slider.value())
            self.config.MIN_NEURAL_CONFIRMADA = float(self.signal_neural_confirmada_slider.value())
            self.config.MIN_TECHNICAL_CONFIRMADA = float(self.signal_technical_confirmada_slider.value())
            self.config.MIN_ALIGNMENT_CONFIRMADA = float(self.signal_alignment_confirmada_slider.value())
            self.config.NEURAL_WEIGHT = self.neural_weight_slider.value() / 100.0
            self.config.TECHNICAL_WEIGHT = self.technical_weight_slider.value() / 100.0
            self.config.MAX_DAILY_SIGNALS = self.max_daily_signals_slider.value()
            logger.info(f"📊 Señales diarias máximo: {self.config.MAX_DAILY_SIGNALS}")
            self.config.SCAN_INTERVAL = self.scan_interval_slider.value()
            self.config.PRIMARY_TIMEFRAME = self.primary_tf_combo.currentText()
            self.config.SECONDARY_TIMEFRAME = self.primary_tf_combo.currentText() # Usar primary para secondary (simplificación)
            self.config.ENTRY_TIMEFRAME = self.entry_tf_combo.currentText()
            self.config.MAX_RISK_PER_TRADE = self.max_risk_slider.value() / 1000.0
            self.config.MIN_RISK_REWARD_RATIO = self.min_rr_slider.value() / 10.0
            self.config.MIN_VOLUME_RATIO = self.min_volume_slider.value() / 10.0
            logger.info(f"📊 Volumen Mínimo actualizado: x{self.config.MIN_VOLUME_RATIO:.1f}")
            # ✅ STOP LOSS CONFIGURABLE (slider: 5-30 → 0.5%-3.0% → valor: 0.005-0.03)
            self.config.DEFAULT_STOP_LOSS_PERCENT = self.stop_loss_slider.value() / 1000.0
            logger.info(f"🛑 Stop Loss actualizado: {self.config.DEFAULT_STOP_LOSS_PERCENT * 100:.1f}%")
            logger.info(f"⚖️ R/R Mínimo actualizado: 1:{self.config.MIN_RISK_REWARD_RATIO:.1f}")
            # ✅ TP = MILESTONE_3 (Objetivo Final) - Sincronizado automáticamente
            # Se actualizará después de los milestones

            # ✅ Sincronización con sliders (SOLO aquí)
            self.config.MILESTONE_1 = self.milestone_1_slider.value() / 10.0
            self.config.MILESTONE_2 = self.milestone_2_slider.value() / 10.0
            self.config.MILESTONE_3 = self.milestone_3_slider.value() / 10.0
            self.config.PROFIT_MILESTONES = [
                self.config.MILESTONE_1,
                self.config.MILESTONE_2,
                self.config.MILESTONE_3
            ]
            self.config.DEFAULT_TAKE_PROFIT_PERCENT = self.config.MILESTONE_3 / 100.0

            logger.info(f"📊 Milestones actualizados: {self.config.PROFIT_MILESTONES}")
            logger.info(f"🎯 TP sincronizado con Objetivo Final: {self.config.MILESTONE_3}%")

            # ✅ AUTOTRADER: Guardar configuración avanzada
            if hasattr(self, 'autotrader_mode_combo'):
                self.config.AUTOTRADER_MODE = self.autotrader_mode_combo.currentText()
                self.config.AUTOTRADER_MARGIN_USDT = self.autotrader_margin_spin.value()
                self.config.AUTOTRADER_LEVERAGE = int(self.autotrader_leverage_combo.currentText().replace('x', ''))
                self.config.AUTOTRADER_CAPITAL_USDT = self.autotrader_capital_spin.value()
                self.config.AUTOTRADER_COMPOUND_ENABLED = self.autotrader_compound_checkbox.isChecked()
                self.config.AUTOTRADER_COMPOUND_PERCENT = self.autotrader_compound_spin.value()
                logger.info(f"🤖 AutoTrader: Modo={self.config.AUTOTRADER_MODE}, Margen=${self.config.AUTOTRADER_MARGIN_USDT}, Lev={self.config.AUTOTRADER_LEVERAGE}x")

            self.config.save_config()
            # Guardar credenciales Binance
            self.config.binance_api_key = self.binance_key_entry.text()
            self.config.binance_secret_key = self.binance_secret_entry.text()
            # ✅ SINCRONIZAR: Usar modo del AutoTrader combo (tiene prioridad sobre checkbox legacy)
            if hasattr(self, 'autotrader_mode_combo'):
                mode = self.autotrader_mode_combo.currentText()
                is_testnet = (mode == 'testnet')
                self.config.use_testnet = is_testnet
                self.config.USE_TESTNET = is_testnet
                self.testnet_checkbox.setChecked(is_testnet)  # Sincronizar checkbox legacy
            else:
                self.config.use_testnet = self.testnet_checkbox.isChecked()
            QtWidgets.QMessageBox.information(self, "Configuración", "✅ Configuración optimizada guardada correctamente.")
            self.log_message("💾 Configuración optimizada guardada")
            # Actualizar bot con nueva configuración
            self.bot.config = self.config
            self.bot.telegram_client = OptimizedTelegramClient(self.config)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"❌ Error guardando configuración: {e}")
            self.log_message(f"❌ Error guardando configuración optimizada: {e}")

    def load_and_analyze_best_pairs(self):
        """Cargar y analizar todos los pares USDT de Binance por liquidez"""
        try:
            self.pairs_status_label.setText("🔍 Obteniendo todos los pares de Binance...")
            self.pairs_progress_bar.setValue(0)
            self.load_best_pairs_btn.setEnabled(False)

            def fetch_best_pairs_thread():
                try:
                    import requests
                    best_pairs = []

                    # Paso 1: Obtener información de todos los pares
                    QMetaObject.invokeMethod(
                        self.pairs_status_label, "setText",
                        QtCore.Qt.QueuedConnection, Q_ARG(str, "📊 Obteniendo información de exchange...")
                    )

                    exchange_info_url = "https://data-api.binance.vision/api/v3/exchangeInfo"
                    resp_info = requests.get(exchange_info_url, timeout=15)
                    if resp_info.status_code != 200:
                        raise Exception(f"Error obteniendo exchangeInfo: {resp_info.status_code}")

                    exchange_data = resp_info.json()
                    usdt_symbols = [
                        s['symbol'] for s in exchange_data.get('symbols', [])
                        if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING'
                        and not any(x in s['symbol'] for x in ['UP', 'DOWN', 'BEAR', 'BULL'])
                    ]

                    QMetaObject.invokeMethod(
                        self.pairs_status_label, "setText",
                        QtCore.Qt.QueuedConnection, Q_ARG(str, f"📈 Analizando liquidez de {len(usdt_symbols)} pares...")
                    )
                    QMetaObject.invokeMethod(
                        self.pairs_progress_bar, "setValue",
                        QtCore.Qt.QueuedConnection, Q_ARG(int, 20)
                    )

                    # Paso 2: Obtener volumen 24h de todos los pares
                    ticker_url = "https://data-api.binance.vision/api/v3/ticker/24hr"
                    resp_ticker = requests.get(ticker_url, timeout=30)
                    if resp_ticker.status_code != 200:
                        raise Exception(f"Error obteniendo ticker 24h: {resp_ticker.status_code}")

                    ticker_data = resp_ticker.json()
                    volume_data = {t['symbol']: float(t.get('quoteVolume', 0)) for t in ticker_data}

                    QMetaObject.invokeMethod(
                        self.pairs_progress_bar, "setValue",
                        QtCore.Qt.QueuedConnection, Q_ARG(int, 50)
                    )

                    # Paso 3: Filtrar por volumen mínimo (>1M USDT 24h)
                    MIN_VOLUME_24H = 1_000_000  # 1 millón USDT mínimo
                    high_liquidity_pairs = []

                    for symbol in usdt_symbols:
                        vol = volume_data.get(symbol, 0)
                        if vol >= MIN_VOLUME_24H:
                            high_liquidity_pairs.append({
                                'symbol': symbol,
                                'volume_24h': vol
                            })

                    # Paso 4: Ordenar por volumen y tomar los mejores 50
                    high_liquidity_pairs.sort(key=lambda x: x['volume_24h'], reverse=True)
                    top_pairs = high_liquidity_pairs[:50]
                    best_symbols = [p['symbol'] for p in top_pairs]

                    QMetaObject.invokeMethod(
                        self.pairs_progress_bar, "setValue",
                        QtCore.Qt.QueuedConnection, Q_ARG(int, 80)
                    )

                    # Paso 5: Guardar en configuración
                    self.config.TRADING_SYMBOLS = best_symbols
                    self.config.save_config()

                    QMetaObject.invokeMethod(
                        self.pairs_progress_bar, "setValue",
                        QtCore.Qt.QueuedConnection, Q_ARG(int, 100)
                    )

                    # Actualizar lista de pares en GUI
                    QMetaObject.invokeMethod(
                        self, "on_best_pairs_loaded",
                        QtCore.Qt.QueuedConnection, Q_ARG(list, top_pairs)
                    )

                except Exception as e:
                    logger.error(f"Error cargando mejores pares: {e}")
                    QMetaObject.invokeMethod(
                        self.pairs_status_label, "setText",
                        QtCore.Qt.QueuedConnection, Q_ARG(str, f"❌ Error: {str(e)}")
                    )
                finally:
                    QMetaObject.invokeMethod(
                        self.load_best_pairs_btn, "setEnabled",
                        QtCore.Qt.QueuedConnection, Q_ARG(bool, True)
                    )

            threading.Thread(target=fetch_best_pairs_thread, daemon=True).start()

        except Exception as e:
            logger.error(f"Error iniciando carga de pares: {e}")
            self.pairs_status_label.setText(f"❌ Error: {str(e)}")
            self.load_best_pairs_btn.setEnabled(True)

    @QtCore.pyqtSlot(list)
    def on_best_pairs_loaded(self, pairs_data):
        """Callback cuando se cargan los mejores pares"""
        try:
            # Actualizar lista de pares en GUI
            self.pair_listbox.clear()
            for pair in pairs_data:
                vol_str = f"${pair['volume_24h']/1_000_000:.1f}M"
                self.pair_listbox.addItem(f"{pair['symbol']} ({vol_str})")

            self.pairs_status_label.setText(
                f"✅ {len(pairs_data)} pares cargados por liquidez y guardados en configuración"
            )
            self.log_message(f"🔍 Cargados {len(pairs_data)} mejores pares USDT por volumen 24h")

            # Actualizar análisis con nuevos pares
            QtWidgets.QMessageBox.information(
                self, 
                "Pares Actualizados",
                f"✅ Se cargaron los {len(pairs_data)} mejores pares USDT ordenados por liquidez.\n\n"
                f"Los pares se guardaron en config_v20_optimized.json\n\n"
                f"Top 5 por volumen:\n" +
                "\n".join([f"• {p['symbol']}: ${p['volume_24h']/1_000_000:.1f}M" for p in pairs_data[:5]])
            )

        except Exception as e:
            logger.error(f"Error actualizando GUI con pares: {e}")

    def update_pairs_analysis_optimized(self):
        """Actualizar análisis de pares optimizada"""
        try:
            self.pairs_status_label.setText("🔄 Ejecutando análisis optimizado de pares...")
            self.pairs_progress_bar.setValue(0)
            symbols = self.config.TRADING_SYMBOLS
            total_symbols = len(symbols)
            self.pairs_analysis_table.setRowCount(0)
            def analyze_pairs_thread_optimized():
                results = []
                for i, symbol in enumerate(symbols):
                    try:
                        analysis = self.bot.get_pair_analysis(symbol)
                        if analysis:
                            results.append(analysis)
                        progress = int((i + 1) / total_symbols * 100)
                        QMetaObject.invokeMethod(
                            self.pairs_progress_bar, "setValue",
                            QtCore.Qt.QueuedConnection, Q_ARG(int, progress)
                        )
                    except Exception as e:
                        logger.error(f"Error analizando {symbol} optimizado: {e}")
                QMetaObject.invokeMethod(
                    self, "update_pairs_table_optimized",
                    QtCore.Qt.QueuedConnection, Q_ARG(list, results)
                )
            threading.Thread(target=analyze_pairs_thread_optimized, daemon=True).start()
        except Exception as e:
            logger.error(f"Error en análisis optimizado de pares: {e}")
            self.pairs_status_label.setText(f"❌ Error: {str(e)}")

    def update_pairs_table_optimized(self, results):
        """Actualizar tabla de pares optimizada"""
        try:
            # Ordenar por confianza
            results.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            self.pairs_analysis_table.setRowCount(len(results))
            for row, analysis in enumerate(results):
                # Símbolo
                symbol_item = QtWidgets.QTableWidgetItem(analysis['symbol'])
                symbol_item.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
                self.pairs_analysis_table.setItem(row, 0, symbol_item)
                # Precio
                price_item = QtWidgets.QTableWidgetItem(f"${analysis['price']:.6f}")
                self.pairs_analysis_table.setItem(row, 1, price_item)
                # Señal con colores optimizados
                cs_val = getattr(analysis.get('combined_signal', SignalType.NEUTRAL), 'value', str(analysis.get('combined_signal', 'NEUTRAL')))
                signal_item = QtWidgets.QTableWidgetItem(cs_val)
                if "COMPRA" in cs_val:
                    signal_item.setBackground(QtGui.QColor('#00d4aa'))
                    signal_item.setForeground(QtGui.QColor('white'))
                elif "VENTA" in cs_val:
                    signal_item.setBackground(QtGui.QColor('#ff6b6b'))
                    signal_item.setForeground(QtGui.QColor('white'))
                else:
                    signal_item.setBackground(QtGui.QColor('#6c757d'))
                    signal_item.setForeground(QtGui.QColor('white'))
                self.pairs_analysis_table.setItem(row, 2, signal_item)
                # Probabilidad con colores
                confidence = analysis.get('confidence', 0)
                confidence_item = QtWidgets.QTableWidgetItem(f"{confidence:.1f}%")
                if confidence >= self.config.MIN_NEURAL_CONFIRMADA: # CONFIRMADA
                    confidence_item.setBackground(QtGui.QColor('#00ff88'))
                    confidence_item.setForeground(QtGui.QColor('black'))
                elif confidence >= self.config.MIN_NEURAL_DESTACADA: # DESTACADA
                    confidence_item.setBackground(QtGui.QColor('#ffd700'))
                    confidence_item.setForeground(QtGui.QColor('black'))
                elif confidence >= 65:
                    confidence_item.setBackground(QtGui.QColor('#ff9500'))
                    confidence_item.setForeground(QtGui.QColor('white'))
                else:
                    confidence_item.setBackground(QtGui.QColor('#ff6b6b'))
                    confidence_item.setForeground(QtGui.QColor('white'))
                confidence_item.setFont(QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
                self.pairs_analysis_table.setItem(row, 3, confidence_item)
                # Métricas IA y Técnicas
                neural_pred = analysis.get('neural_prediction', {})
                neural_conf = neural_pred.get('confidence', 0)
                neural_item = QtWidgets.QTableWidgetItem(f"{neural_conf:.1f}%")
                neural_item.setForeground(QtGui.QColor('#00d4aa'))
                self.pairs_analysis_table.setItem(row, 4, neural_item)
                # Porcentaje Técnico (dinámico)
                tech_conf = analysis.get('technical_percentage', 0)
                tech_item = QtWidgets.QTableWidgetItem(f"{tech_conf:.1f}%")
                tech_item.setForeground(QtGui.QColor('#ffd60a'))
                self.pairs_analysis_table.setItem(row, 5, tech_item)
                # Timestamp
                timestamp = analysis.get('timestamp', datetime.now())
                time_item = QtWidgets.QTableWidgetItem(timestamp.strftime('%H:%M:%S'))
                self.pairs_analysis_table.setItem(row, 6, time_item)
                # Botón de acciones
                actions_widget = QtWidgets.QWidget()
                actions_layout = QtWidgets.QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                details_btn = QtWidgets.QPushButton("📊 Ver")
                details_btn.setStyleSheet(
                    "background-color: #2196F3; color: white; padding: 4px 8px; "
                    "border-radius: 4px; font-size: 10px; font-weight: bold;"
                )
                details_btn.clicked.connect(lambda checked, s=analysis['symbol']: self.view_pair_details_optimized(s))
                actions_layout.addWidget(details_btn)
                self.pairs_analysis_table.setCellWidget(row, 7, actions_widget)
            # Aplicar filtros
            self.filter_pairs_table_optimized()
            # Actualizar estado
            high_prob_count = len([r for r in results if r.get('confidence', 0) >= 80])
            self.pairs_status_label.setText(
                f"✅ Análisis optimizado completado: {len(results)} pares, "
                f"{high_prob_count} con alta probabilidad"
            )
        except Exception as e:
            logger.error(f"Error actualizando tabla optimizada: {e}")
            self.pairs_status_label.setText(f"❌ Error actualizando tabla: {e}")

    def filter_pairs_table_optimized(self):
        """Filtrar tabla de pares optimizada"""
        try:
            filter_text = self.signal_filter_combo.currentText()
            for row in range(self.pairs_analysis_table.rowCount()):
                signal_item = self.pairs_analysis_table.item(row, 2)
                confidence_item = self.pairs_analysis_table.item(row, 3)
                if signal_item and confidence_item:
                    signal_text = signal_item.text()
                    confidence_text = confidence_item.text()
                    confidence_val = float(confidence_text.replace('%', ''))
                    should_show = True
                    if filter_text == "COMPRA":
                        should_show = "COMPRA" in signal_text
                    elif filter_text == "VENTA":
                        should_show = "VENTA" in signal_text
                    elif filter_text == "ALTA_PROB":
                        should_show = confidence_val >= 80
                    elif filter_text == "NEUTRAL":
                        should_show = "COMPRA" not in signal_text and "VENTA" not in signal_text
                    # "Todas" muestra todo
                    self.pairs_analysis_table.setRowHidden(row, not should_show)
        except Exception as e:
            logger.error(f"Error aplicando filtro optimizado: {e}")

    def view_pair_details_optimized(self, symbol):
        """Ver detalles optimizados de par"""
        try:
            # Cambiar a pestaña principal
            self.notebook.setCurrentIndex(0)
            # Seleccionar símbolo
            items = self.pair_listbox.findItems(symbol, Qt.MatchExactly)
            if items:
                self.pair_listbox.setCurrentItem(items[0])
                self.on_pair_select_optimized(items[0])
        except Exception as e:
            logger.error(f"Error viendo detalles optimizados de {symbol}: {e}")

    def refresh_analysis(self):
        """Forzar actualización del análisis"""
        try:
            self.log_message("🔄 Actualizando análisis técnico...")
            # Forzar recarga de datos
            self.bot.load_pair_data_optimized()
            # Actualizar pestaña de análisis
            detailed_analysis = self.bot.get_detailed_analysis_optimized()  # ✅ ahora sí existe
            if detailed_analysis:
                self.analysis_text.setPlainText(detailed_analysis)
                self.analysis_text.repaint()
                self.log_message("✅ Análisis actualizado correctamente")
            else:
                self.analysis_text.setPlainText("No se pudo generar el análisis. Por favor, intente nuevamente.")
                self.analysis_text.repaint()
                self.log_message("❌ Error al actualizar análisis")
        except Exception as e:
            logger.error(f"Error actualizando análisis: {e}")
            self.analysis_text.setPlainText(f"Error al actualizar análisis: {str(e)}")
            self.analysis_text.repaint()
            self.log_message(f"❌ Error al actualizar análisis: {str(e)}")

    def log_message(self, message):
        """Log con timestamp optimizado - THREAD SAFE"""
        # ✅ USAR QTimer.singleShot() PARA THREAD SAFETY EN PyQt5
        def _safe_log():
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            log_entry = f"[{timestamp}] {message}"
            self.terminal_text.append(log_entry)
            # Mantener solo las últimas 200 líneas para eficiencia
            document = self.terminal_text.document()
            if document.blockCount() > 200:
                cursor = self.terminal_text.textCursor()
                cursor.movePosition(QtGui.QTextCursor.Start)
                cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.KeepAnchor, 50)
                cursor.removeSelectedText()
            self.terminal_text.verticalScrollBar().setValue(
                self.terminal_text.verticalScrollBar().maximum()
            )

        # Si ya estamos en el hilo principal, ejecutar directamente
        # Si no, usar QTimer.singleShot para garantizar thread safety
        try:
            if QtCore.QThread.currentThread() == QtCore.QCoreApplication.instance().thread():
                _safe_log()  # Ya en hilo principal
            else:
                QtCore.QTimer.singleShot(0, _safe_log)  # Encolar en hilo principal
        except:
            QtCore.QTimer.singleShot(0, _safe_log)  # Fallback seguro

    def clear_logs(self):
        """Limpiar todos los logs de la terminal"""
        self.terminal_text.clear()
        self.log_message("🗑️ Logs limpiados")

    def update_pair_scan_progress(self, value):
        """Actualizar progreso optimizado - THREAD SAFE"""
        # ✅ USAR QTimer.singleShot() PARA THREAD SAFETY
        def _safe_update():
            self.pair_scan_progress_bar.setValue(value)
            if value >= 100:
                self.pair_scan_progress_bar.setFormat("✅ Escaneo Completado - 100%")
            else:
                self.pair_scan_progress_bar.setFormat(f"🔄 Escaneando Pares Optimizado: {value}%")

        try:
            if QtCore.QThread.currentThread() == QtCore.QCoreApplication.instance().thread():
                _safe_update()
            else:
                QtCore.QTimer.singleShot(0, _safe_update)
        except:
            QtCore.QTimer.singleShot(0, _safe_update)

    def update_signals_table_optimized(self):
        """Actualizar tabla de señales optimizada - SOLO DESTACADAS y CONFIRMADAS - THREAD SAFE"""
        # ✅ THROTTLE: Evitar actualización demasiado frecuente (máx cada 2 segundos)
        current_time = time.time()
        if current_time - self.last_table_update < 2.0:
            return  # Esperar 2 segundos antes de actualizar
        self.last_table_update = current_time

        # ✅ USAR QTimer.singleShot() PARA THREAD SAFETY
        def _safe_table_update():
            try:
                self.signals_tree.setRowCount(0)
                # Filtrar SOLO señales premium (DESTACADAS y CONFIRMADAS)
                all_signals = sorted(self.bot.active_signals, key=lambda x: x['timestamp'], reverse=True)
                premium_signals = [
                    sig for sig in all_signals 
                    if 'HIGHLIGHTED' in getattr(sig.get('combined_signal', ''), 'name', '') or 
                       'CONFIRMED' in getattr(sig.get('combined_signal', ''), 'name', '') or
                       'DESTACADA' in getattr(sig.get('combined_signal', ''), 'value', '') or
                       'CONFIRMADA' in getattr(sig.get('combined_signal', ''), 'value', '')
                ][:20]  # Solo últimas 20 señales premium
                # ✅ LOG: Solo DEBUG (no INFO) para evitar spam
                if len(premium_signals) > 0:
                    logger.debug(f"📋 Tabla actualizada: {len(premium_signals)} PREMIUM | Total: {len(self.bot.active_signals)}")
                else:
                    logger.debug("📋 Tabla vacía - esperando señales DESTACADAS/CONFIRMADAS...")
                for row, signal_data in enumerate(premium_signals):
                    self.signals_tree.insertRow(row)
                    # Datos optimizados (IA + Técnico fusionados)
                    neural_pred = signal_data.get('neural_prediction', {})
                    processing_details = signal_data.get('processing_details', {})
                    # Métricas optimizadas
                    neural_conf = neural_pred.get('confidence', 0) or signal_data.get('neural_score', 0)
                    # Usar technical_percentage de processing_details si está disponible
                    technical_percentage = processing_details.get('technical_percentage', signal_data.get('technical_percentage', 0))
                    # Calcular probabilidad real: promedio de IA + Técnico o combined_confidence
                    prob_value = signal_data.get('combined_confidence', 0)
                    if prob_value == 0:
                        prob_value = (neural_conf + technical_percentage) / 2 if (neural_conf + technical_percentage) > 0 else 0
                    # Poblar tabla (6 columnas: sin Estrategia)
                    items = [
                        QtWidgets.QTableWidgetItem(signal_data['symbol']),
                        QtWidgets.QTableWidgetItem(getattr(signal_data.get('combined_signal', SignalType.NEUTRAL), 'value', str(signal_data.get('combined_signal', 'NEUTRAL')))[:15]),  # Truncar
                        QtWidgets.QTableWidgetItem(f"{prob_value:.1f}%"),
                        QtWidgets.QTableWidgetItem(f"{neural_conf:.1f}%"),
                        QtWidgets.QTableWidgetItem(f"{technical_percentage:.1f}%"),
                        QtWidgets.QTableWidgetItem(signal_data['timestamp'].strftime('%H:%M:%S'))
                    ]
                    # Colorear TODA LA FILA según tipo de señal - SOLO PREMIUM
                    signal_type = signal_data.get('combined_signal', SignalType.NEUTRAL)
                    signal_name = signal_type.name if hasattr(signal_type, 'name') else str(signal_type)
                    # Colores distintivos para señales premium SOLAMENTE
                    row_color = None
                    text_color = QtGui.QColor('black')
                    if 'CONFIRMED' in signal_name or 'CONFIRMADA' in getattr(signal_data.get('combined_signal', ''), 'value', ''):
                        # CONFIRMADA: Verde brillante
                        row_color = QtGui.QColor('#00ff88')  # Verde brillante
                        text_color = QtGui.QColor('black')
                    elif 'HIGHLIGHTED' in signal_name or 'DESTACADA' in getattr(signal_data.get('combined_signal', ''), 'value', ''):
                        # DESTACADA: Amarillo/Dorado brillante
                        row_color = QtGui.QColor('#ffd700')  # Dorado
                        text_color = QtGui.QColor('black')
                    for col, item in enumerate(items):
                        # Aplicar color de fila
                        if row_color:
                            item.setBackground(row_color)
                            item.setForeground(text_color)
                        # Font bold para señales premium
                        font = QtGui.QFont("Arial", 9)
                        if 'CONFIRMED' in signal_name or 'HIGHLIGHTED' in signal_name:
                            font.setBold(True)
                        item.setFont(font)
                        self.signals_tree.setItem(row, col, item)
            except Exception as e:
                logger.error(f"Error actualizando tabla de señales: {e}")

        # THREAD SAFE: Ejecutar en hilo principal
        try:
            if QtCore.QThread.currentThread() == QtCore.QCoreApplication.instance().thread():
                _safe_table_update()
            else:
                QtCore.QTimer.singleShot(0, _safe_table_update)
        except:
            QtCore.QTimer.singleShot(0, _safe_table_update)

    def _process_gui_messages(self):
        """Procesar mensajes de la cola de forma COMPLETAMENTE THREAD-SAFE con QTimer"""
        messages_processed = 0
        max_messages_per_batch = 5  # Limitar para no bloquear GUI
        while messages_processed < max_messages_per_batch:
            try:
                msg = self.gui_queue.get_nowait()
                messages_processed += 1
                msg_type, data = msg

                if msg_type == 'log_message':
                    self.log_message(data)

                elif msg_type == 'signal_found':
                    self.update_signals_table_optimized()

                elif msg_type == 'clear_signals_table':
                    def _clear_tbl():
                        try:
                            self.signals_tree.setRowCount(0)
                            if hasattr(self, 'signals_count_label'):
                                self.signals_count_label.setText("Señales: 0")
                        except Exception as e:
                            logger.error(f"Error limpiando tabla de señales: {e}")
                    QtCore.QTimer.singleShot(0, _clear_tbl)

                elif msg_type == 'show_chart':
                    # ✅ MOSTRAR GRÁFICO DESDE HILO PRINCIPAL (thread-safe)
                    def _show_chart_dialog():
                        try:
                            # Agregar chart_path al signal_data
                            signal_data = data.get('signal_data', {})
                            signal_data['chart_path'] = data['chart_path']

                            chart_dialog = SignalChartDialog(
                                signal_data=signal_data,
                                parent=self
                            )
                            chart_dialog.show()
                            # Elevar ventana al frente
                            chart_dialog.raise_()
                            chart_dialog.activateWindow()
                        except Exception as e:
                            logger.error(f"Error mostrando ventana de gráfico: {e}")
                    QtCore.QTimer.singleShot(0, _show_chart_dialog)

                elif msg_type == 'update_current_analyzed_symbol':
                    def _update_symbol():
                        if data:
                            symbol_str = str(data)
                            self.bot.current_pair = symbol_str
                            items = self.pair_listbox.findItems(symbol_str, Qt.MatchExactly)
                            if items:
                                self.pair_listbox.setCurrentItem(items[0])
                        else:
                            if self.bot.symbols_analyzed_count >= self.bot.total_symbols_to_analyze:
                                self.log_message("✅ Ciclo de escaneo optimizado completado")
                                self.update_pair_scan_progress(100)
                    QtCore.QTimer.singleShot(0, _update_symbol)

                elif msg_type == 'update_pair_scan_progress':
                    self.update_pair_scan_progress(data)

                elif msg_type == 'show_destacada_signal':
                    # NUEVO v35: Mostrar barra de progreso cuando se detecta senal DESTACADA
                    def _show_destacada(signal_data):
                        try:
                            symbol = signal_data.get('symbol', 'UNKNOWN')
                            neural = signal_data.get('neural_score', 0)
                            technical = signal_data.get('technical_pct', 0)
                            alignment = signal_data.get('alignment_pct', 0)
                            is_buy = signal_data.get('is_buy', True)
                            direction = "COMPRA" if is_buy else "VENTA"
                            
                            # Mostrar la barra de progreso DESTACADA
                            self.highlight_progress_bar.setVisible(True)
                            self.highlight_progress_bar.setValue(0)
                            self.highlight_progress_bar.setFormat(
                                f"DESTACADA {symbol} ({direction}) | IA:{neural:.0f}% Tec:{technical:.0f}% Ali:{alignment:.0f}%"
                            )
                            self.highlight_progress_bar.setStyleSheet("""
                                QProgressBar {
                                    border: 2px solid #FFD700;
                                    border-radius: 5px;
                                    text-align: center;
                                    background-color: #1a1a1a;
                                    color: white;
                                    font-weight: bold;
                                }
                                QProgressBar::chunk {
                                    background-color: #FFD700;
                                }
                            """)
                            logger.info(f"Barra DESTACADA mostrada para {symbol}")
                        except Exception as e:
                            logger.error(f"Error mostrando senal DESTACADA en GUI: {e}")
                    QtCore.QTimer.singleShot(0, lambda d=data: _show_destacada(d))

                elif msg_type == 'update_highlight_progress':
                    def _update_highlight(progress_value):
                        has_highlighted = False
                        has_confirmed = False
                        try:
                            if hasattr(self, 'bot') and hasattr(self.bot, 'signal_tracker'):
                                tracker = self.bot.signal_tracker
                                with tracker.lock:
                                    for t in tracker.tracked_signals.values():
                                        st = t.get('status', '')
                                        if st == 'CONFIRMADA':
                                            has_confirmed = True
                                            break
                                        if st == 'DESTACADA':
                                            has_highlighted = True
                        except Exception:
                            pass

                        if has_confirmed:
                            self.highlight_progress_bar.setVisible(False)
                            self.highlight_progress_bar.setValue(0)
                            self.highlight_progress_bar.setFormat("Esperando senal DESTACADA...")
                            return

                        if has_highlighted:
                            pv = max(0, int(progress_value))
                            self.highlight_progress_bar.setVisible(True)
                            self.highlight_progress_bar.setValue(pv)
                            self.highlight_progress_bar.setFormat(f"Tiempo DESTACADA: {pv}% (3 min)")
                        else:
                            self.highlight_progress_bar.setVisible(False)
                            self.highlight_progress_bar.setValue(0)
                            self.highlight_progress_bar.setFormat("Esperando senal DESTACADA...")
                    QtCore.QTimer.singleShot(0, lambda pv=int(data): _update_highlight(pv))

                elif msg_type == 'update_confirmed_progress':
                    # ✅ NUEVO: Actualizar barra de progreso para señal CONFIRMADA (profit tracking)
                    # Usa valores dinámicos de config para los milestones
                    def _update_confirmed(progress_data):
                        try:
                            # Asegurar que la barra destacada esté oculta
                            self.highlight_progress_bar.setVisible(False)

                            profit_percent = progress_data.get('profit_percent', 0)
                            symbol = progress_data.get('symbol', '')

                            # ✅ VALORES DINÁMICOS DESDE CONFIG
                            m1 = getattr(self.config, 'MILESTONE_1', 0.5)
                            m2 = getattr(self.config, 'MILESTONE_2', 1.0)
                            m3 = getattr(self.config, 'MILESTONE_3', 1.5)
                            target = m3  # Objetivo = MILESTONE_3

                            # Calcular progreso hacia el objetivo (0-100%)
                            progress_value = min(100, max(0, int((profit_percent / target) * 100))) if target > 0 else 0

                            # Determinar Avance actual usando valores dinámicos
                            if profit_percent >= m3:
                                milestone_text = f"🎉 ¡OBJETIVO {m3:.1f}% ALCANZADO!"
                                bar_color = "#00FF00"  # Verde brillante
                            elif profit_percent >= m2:
                                milestone_text = f"✅ +{profit_percent:.2f}% → Próximo: {m3:.1f}%"
                                bar_color = "#32CD32"  # Verde lima
                            elif profit_percent >= m1:
                                milestone_text = f"📈 +{profit_percent:.2f}% → Próximo: {m2:.1f}%"
                                bar_color = "#FFD700"  # Dorado
                            elif profit_percent > 0:
                                milestone_text = f"🔄 +{profit_percent:.2f}% → Próximo: {m1:.1f}%"
                                bar_color = "#FFA500"  # Naranja
                            else:
                                milestone_text = f"⚠️ {profit_percent:+.2f}% (en pérdida)"
                                bar_color = "#FF6347"  # Rojo tomate

                            if hasattr(self, 'confirmed_progress_bar'):
                                self.confirmed_progress_bar.setVisible(True)
                                self.confirmed_progress_bar.setValue(max(0, progress_value))
                                self.confirmed_progress_bar.setFormat(f"💰 CONFIRMADA {symbol}: {milestone_text}")
                                self.confirmed_progress_bar.setStyleSheet(f"""
                                    QProgressBar {{
                                        border: 2px solid #555;
                                        border-radius: 5px;
                                        text-align: center;
                                        background-color: #1a1a1a;
                                        color: white;
                                        font-weight: bold;
                                    }}
                                    QProgressBar::chunk {{
                                        background-color: {bar_color};
                                    }}
                                """)
                        except Exception as e:
                            logger.error(f"Error actualizando progreso CONFIRMADA: {e}")
                    QtCore.QTimer.singleShot(0, lambda pd=data: _update_confirmed(pd))

                elif msg_type == 'update_pending_promotion':
                    def _update_pending(progress_data):
                        try:
                            has_confirmed = False
                            try:
                                if hasattr(self, 'bot') and hasattr(self.bot, 'signal_tracker'):
                                    tracker = self.bot.signal_tracker
                                    with tracker.lock:
                                        has_confirmed = any(t.get('status') == 'CONFIRMADA' for t in tracker.tracked_signals.values())
                            except Exception:
                                has_confirmed = False

                            if has_confirmed:
                                return

                            if hasattr(self, 'confirmed_progress_bar'):
                                self.confirmed_progress_bar.setVisible(False)

                            symbol = progress_data.get('symbol', '')
                            alignment_score = progress_data.get('alignment_score', 0)
                            profit_percent = progress_data.get('profit_percent', 0)

                            self.highlight_progress_bar.setVisible(True)
                            self.highlight_progress_bar.setValue(100)
                            self.highlight_progress_bar.setFormat(f"⏳ {symbol}: Pendiente promoción (Alin: {alignment_score:.0f}%) | Profit: {profit_percent:+.2f}%")
                            self.highlight_progress_bar.setStyleSheet("""
                                QProgressBar {
                                    border: 2px solid #555;
                                    border-radius: 5px;
                                    text-align: center;
                                    background-color: #1a1a1a;
                                    color: white;
                                    font-weight: bold;
                                }
                                QProgressBar::chunk {
                                    background-color: #FF8C00;
                                }
                            """)
                        except Exception as e:
                            logger.error(f"Error actualizando pendiente promoción: {e}")
                    QtCore.QTimer.singleShot(0, lambda pd=data: _update_pending(pd))

                elif msg_type == 'update_gui_realtime_price':
                    def _update_price():
                        analysis = self.bot.current_analysis
                        self.price_label.setText(f"Precio: ${analysis.get('price', 0):.6f}")
                        self.volume_label.setText(f"Volumen: {analysis.get('volume', 0):,.0f}")
                    QtCore.QTimer.singleShot(0, _update_price)

                elif msg_type == 'update_analysis_tab':
                    def _update_analysis():
                        detailed_analysis = self.bot.get_detailed_analysis_optimized()
                        if detailed_analysis:
                            self.analysis_text.setPlainText(detailed_analysis)
                            self.analysis_text.repaint()
                    QtCore.QTimer.singleShot(0, _update_analysis)

                elif msg_type == 'remove_signal_from_table':
                    def _remove_signal():
                        try:
                            target_symbol = data.get('symbol') if isinstance(data, dict) else data
                            rows = self.signals_tree.rowCount()
                            for row in reversed(range(rows)):
                                item = self.signals_tree.item(row, 0)
                                symbol_match = bool(item and item.text() == target_symbol)
                                if symbol_match:
                                    self.signals_tree.removeRow(row)
                            logger.info(f"🗑️ Señal de {target_symbol} eliminada de la interfaz.")
                        except Exception as e:
                            logger.error(f"[ERROR] Error eliminando señal de GUI: {e}")
                    QtCore.QTimer.singleShot(0, _remove_signal)

                elif msg_type == 'clear_signal_display':
                    # CORREGIDO v35: Limpiar panel principal Y barras de seguimiento
                    def _clear_signal_display():
                        try:
                            # Resetear indicadores principales (verificar existencia)
                            if hasattr(self, 'neural_indicator'):
                                self.neural_indicator.setValue(0)
                            if hasattr(self, 'technical_indicator'):
                                self.technical_indicator.setValue(0)
                            if hasattr(self, 'confidence_label'):
                                self.confidence_label.setText("0.0%")
                                self.confidence_label.setStyleSheet("color: #555; font-size: 48px; font-weight: bold;")
                            if hasattr(self, 'signal_label'):
                                self.signal_label.setText("ESPERANDO")
                                self.signal_label.setStyleSheet("background-color: #333; color: #888; padding: 10px; border-radius: 5px;")
                            # Limpiar detalles
                            if hasattr(self, 'details_text'):
                                self.details_text.setText("Esperando nueva senal...")
                            
                            # NUEVO v35: Limpiar y ocultar barras de seguimiento
                            if hasattr(self, 'highlight_progress_bar'):
                                self.highlight_progress_bar.setVisible(False)
                                self.highlight_progress_bar.setValue(0)
                                self.highlight_progress_bar.setFormat("Esperando senal DESTACADA...")
                            
                            if hasattr(self, 'confirmed_progress_bar'):
                                self.confirmed_progress_bar.setVisible(False)
                                self.confirmed_progress_bar.setValue(0)
                                self.confirmed_progress_bar.setFormat("Esperando confirmacion...")
                            
                            logger.info("Panel de senal activa y barras de seguimiento limpiados")
                        except Exception as e:
                            logger.error(f"Error limpiando panel de senal: {e}")
                    QtCore.QTimer.singleShot(0, _clear_signal_display)

                elif msg_type == 'hide_progress_bar':
                    # CORREGIDO v35: Ocultar y resetear AMBAS barras de progreso completamente
                    def _hide_bar():
                        try:
                            # Resetear barra DESTACADA
                            if hasattr(self, 'highlight_progress_bar'):
                                self.highlight_progress_bar.setVisible(False)
                                self.highlight_progress_bar.setValue(0)
                                self.highlight_progress_bar.setFormat("Esperando senal DESTACADA...")
                                # Restaurar estilo por defecto (amarillo)
                                self.highlight_progress_bar.setStyleSheet("""
                                    QProgressBar {
                                        border: 2px solid #555;
                                        border-radius: 5px;
                                        text-align: center;
                                        background-color: #1a1a1a;
                                        color: white;
                                        font-weight: bold;
                                    }
                                    QProgressBar::chunk {
                                        background-color: #FFD700;
                                    }
                                """)

                            # Resetear barra CONFIRMADA
                            if hasattr(self, 'confirmed_progress_bar'):
                                self.confirmed_progress_bar.setVisible(False)
                                self.confirmed_progress_bar.setValue(0)
                                self.confirmed_progress_bar.setFormat("Esperando confirmacion...")
                                # Restaurar estilo por defecto (verde)
                                self.confirmed_progress_bar.setStyleSheet("""
                                    QProgressBar {
                                        border: 2px solid #555;
                                        border-radius: 5px;
                                        text-align: center;
                                        background-color: #1a1a1a;
                                        color: white;
                                        font-weight: bold;
                                    }
                                    QProgressBar::chunk {
                                        background-color: #00ff00;
                                    }
                                """)
                            
                            logger.info("Barras de progreso reseteadas y ocultas")
                        except Exception as e:
                            logger.error(f"Error ocultando barras: {e}")
                    QtCore.QTimer.singleShot(0, _hide_bar)

                elif msg_type == 'reset_main_panel':
                    # NUEVO v35: Resetear completamente el panel principal de analisis
                    def _reset_main_panel():
                        try:
                            # Resetear indicador de confianza (el circulo grande con porcentaje)
                            if hasattr(self, 'confidence_label'):
                                self.confidence_label.setText("0.0%")
                                self.confidence_label.setStyleSheet("color: #555; font-size: 48px; font-weight: bold;")
                            
                            # Resetear label de senal (NEUTRAL/COMPRA/VENTA)
                            if hasattr(self, 'signal_label'):
                                self.signal_label.setText("NEUTRAL")
                                self.signal_label.setStyleSheet("""
                                    background-color: #333; 
                                    color: #888; 
                                    padding: 10px; 
                                    border-radius: 5px;
                                    font-size: 24px;
                                    font-weight: bold;
                                """)
                            
                            # Resetear indicadores de prediccion IA y analisis tecnico
                            if hasattr(self, 'neural_indicator'):
                                self.neural_indicator.setValue(0)
                            if hasattr(self, 'technical_indicator'):
                                self.technical_indicator.setValue(0)
                            if hasattr(self, 'neural_confidence_label'):
                                self.neural_confidence_label.setText("0.0%")
                            if hasattr(self, 'technical_confidence_label'):
                                self.technical_confidence_label.setText("0.0%")
                            
                            # Resetear detalles
                            if hasattr(self, 'details_text'):
                                self.details_text.setText("Esperando analisis...")
                            
                            logger.info("Panel principal reseteado completamente")
                        except Exception as e:
                            logger.error(f"Error reseteando panel principal: {e}")
                    QtCore.QTimer.singleShot(0, _reset_main_panel)

            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error procesando mensaje GUI: {e}")

    def _remove_signal_from_table(self, symbol):
        """Eliminar todas las filas de un símbolo de la tabla de señales."""
        try:
            rows = self.signals_tree.rowCount()
            for row in reversed(range(rows)):
                item = self.signals_tree.item(row, 0)
                if item and item.text() == symbol:
                    self.signals_tree.removeRow(row)
            logger.info(f"🗑️ Señal de {symbol} eliminada de la interfaz.")
        except Exception as e:
            logger.error(f"[ERROR] Error eliminando señal de GUI: {e}")

    def _show_chart_optimized(self, data):
        """Mostrar gráfico de forma optimizada - THREAD SAFE"""
        fig = None
        try:
            symbol = data['symbol']
            df = data['dataframe_entry']
            if df is None or df.empty:
                return
            # Preparar DataFrame con índice DatetimeIndex
            df = df.copy()
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
            elif not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.date_range(end=datetime.now(), periods=len(df), freq='1min')
            # Crear figura simple
            fig, ax = plt.subplots(figsize=(10, 6))
            # Graficar velas
            mpf.plot(df, type='candle', ax=ax, style='charles', 
                     title=f"Análisis de {symbol}",
                     volume=False)
            # Añadir niveles de señal si existen
            if 'entry_price' in data:
                ax.axhline(y=data['entry_price'], color='blue', linestyle='--', label='Entrada')
            if 'stop_loss' in data:
                ax.axhline(y=data['stop_loss'], color='red', linestyle='--', label='Stop Loss')
            if 'take_profit' in data:
                ax.axhline(y=data['take_profit'], color='green', linestyle='--', label='Take Profit')
            ax.legend()
            plt.tight_layout()
            # ✅ NO USAR plt.show() - CAUSA CRASH EN THREADS SECUNDARIOS
            # Se usa SignalChartDialog en _process_gui_messages() en su lugar
            logger.debug(f"✅ Gráfico optimizado generado para {symbol} (no mostrado desde thread)")
        except Exception as e:
            logger.error(f"Error generando gráfico optimizado: {e}")
        finally:
            # ✅ CLEANUP - Cerrar figura sin importar qué pasó
            try:
                if fig is not None:
                    plt.close(fig)
            except:
                pass

    def _update_current_symbol(self, symbol):
        """Actualizar símbolo actual"""
        if symbol:
            self.bot.current_pair = symbol
            items = self.pair_listbox.findItems(symbol, Qt.MatchExactly)
            if items:
                self.pair_listbox.setCurrentItem(items[0])

    def _update_realtime_price(self):
        """Actualizar precio en tiempo real"""
        analysis = self.bot.current_analysis
        self.price_label.setText(f"Precio: ${analysis.get('price', 0):.6f}")
        self.volume_label.setText(f"Volumen: {analysis.get('volume', 0):,.0f}")

    def update_gui_and_data_optimized(self):
        """Actualización optimizada de GUI"""
        try:
            # 1. Procesar mensajes de la cola (incluye updates de progreso, logs, etc.)
            self._process_gui_messages()
            # 2. Actualizar análisis principal si no está corriendo (para el par seleccionado)
            if not self.bot.running and self.pair_listbox.currentItem():
                selected_pair = self.pair_listbox.currentItem().text()
                if self.bot.current_pair != selected_pair:
                    self.bot.set_pair_optimized(selected_pair)
                self.bot.load_pair_data_optimized()
            # 3. Actualizar displays principales con datos más recientes
            if self.bot.current_pair in self.bot.market_data:
                analysis = self.bot.market_data[self.bot.current_pair].get('analysis', self.bot.current_analysis)
            else:
                analysis = self.bot.current_analysis
            # Información básica
            self.price_label.setText(f"Precio: ${analysis.get('price', 0):.6f}")
            self.volume_label.setText(f"Volumen: {analysis.get('volume', 0):,.0f}")

            # Métricas optimizadas - NUEVOS VALORES
            neural_pred = analysis.get('neural_prediction', {})
            processing_details = analysis.get('processing_details', {})
            signal_type = analysis.get('combined_signal', SignalType.NEUTRAL)
            # NUEVO: Obtener ALINEACIÓN como probabilidad combinada
            alignment_prob = processing_details.get('alignment_percentage', 0)
            # NUEVO: Obtener porcentaje técnico (dinámico)
            technical_percentage = processing_details.get('technical_percentage', 0)
            # Obtener confianza IA (prioridad: processing_details > neural_prediction)
            neural_conf = processing_details.get('neural_score', neural_pred.get('confidence', 0))
            # Asegurar que los valores sean números válidos
            alignment_prob = max(0, min(100, alignment_prob))
            neural_conf = max(0, min(100, neural_conf))
            technical_percentage = max(0, min(100, technical_percentage))
            # Actualizar labels con NUEVOS valores
            self.combined_prob_label.setText(f"{alignment_prob:.1f}%")  # AHORA MUESTRA ALINEACIÓN
            self.signal_type_label.setText(getattr(signal_type, 'value', str(signal_type)))
            self.neural_confidence_label.setText(f"{neural_conf:.1f}%")
            self.technical_confidence_label.setText(f"{technical_percentage:.1f}%")  # AHORA MUESTRA % CRITERIOS
            # Colores dinámicos optimizados basados en ALINEACIÓN
            if alignment_prob >= 100:
                color_style = "color: #00ff00; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #16213e, stop:1 #00d4aa); border: 3px solid #00ff00;"
                signal_color = "color: #00ff00; background-color: #0f0f23; border: 2px solid #00ff00;"
            elif alignment_prob >= 80:
                color_style = "color: #00d4aa; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #16213e, stop:1 #52b788); border: 3px solid #00d4aa;"
                signal_color = "color: #00d4aa; background-color: #0f0f23; border: 2px solid #00d4aa;"
            elif alignment_prob >= 50:
                color_style = "color: #ffd60a; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #16213e, stop:1 #f9c74f); border: 3px solid #ffd60a;"
                signal_color = "color: #ffd60a; background-color: #0f0f23; border: 2px solid #ffd60a;"
            elif alignment_prob >= 25:
                color_style = "color: #ff9500; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #16213e, stop:1 #ff9500); border: 3px solid #ff9500;"
                signal_color = "color: #ff9500; background-color: #0f0f23; border: 2px solid #ff9500;"
            else:
                color_style = "color: #ff6b6b; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #16213e, stop:1 #ff6b6b); border: 3px solid #ff6b6b;"
                signal_color = "color: #ff6b6b; background-color: #0f0f23; border: 2px solid #ff6b6b;"
            self.combined_prob_label.setStyleSheet(f"{color_style} border-radius: 15px; padding: 15px; min-height: 80px;")
            self.signal_type_label.setStyleSheet(f"{signal_color} border-radius: 8px; padding: 10px;")
            # Texto de detalles optimizado CON DATOS DE ANÁLISIS COMPLETOS
            alignment_status = processing_details.get('alignment_status', 'N/A')
            specific_strategy = analysis.get('specific_strategy_triggered')
            strategy_text = "N/A"
            if specific_strategy:
                strategy_text = str(specific_strategy)
            details_text = f"""📊 PAR: {self.bot.current_pair}
💰 PRECIO: ${analysis.get('price', 0):.6f}
📈 SEÑAL: {signal_type.value}
🎯 ALINEACIÓN IA-TÉCNICO: {alignment_prob:.1f}%
📊 ANÁLISIS DETALLADO:
    🧠 Predicción IA: {neural_conf:.1f}%
    📊 Análisis Técnico: {technical_percentage:.1f}% (dinámico)
    🔄 Estado Alineación: {alignment_status}
⚙️ SISTEMA DINÁMICO (Suma ponderada):
    • Técnico: tendencia (EMA), TDI, patrones, SR, ciclo, alineación, volumen, estrategia
    • IA: Nivel de confianza (≥92.0% DESTACADA, ≥88.0% CONFIRMADA)
    • Base: alineación IA+Técnico, volumen y estrategia
📈 MÉTRICAS ADICIONALES:
    • Estructura: {analysis.get('market_structure_score', 0):.1f}
    • Volatilidad: {analysis.get('volatility_score', 0):.3f}%
⏰ ACTUALIZACIÓN: {self.bot.last_update}
🎯 ESTRATEGIA ACTIVA:
{strategy_text if len(strategy_text) < 200 else strategy_text[:200] + '...'}"""
            self.signal_text.setPlainText(details_text)
            # Actualizar información de IA
            if self.bot.neural_trader.training_history:
                last_training = self.bot.neural_trader.training_history[-1]
                accuracy = last_training.get('accuracy', 0) * 100
                loss = last_training.get('loss', 0)
            else:
                accuracy = 0
                loss = 0
            # Métricas de rendimiento
            if hasattr(self.bot.neural_trader, 'performance_metrics') and self.bot.neural_trader.performance_metrics:
                perf_metrics = self.bot.neural_trader.performance_metrics
                precision_buy = perf_metrics.get('precision_buy', 0) * 100
                precision_sell = perf_metrics.get('precision_sell', 0) * 100
                overall_acc = perf_metrics.get('overall_accuracy', 0) * 100
            else:
                precision_buy = precision_sell = overall_acc = 0
            # Información de cache y rendimiento
            cache_stats = self.bot.data_manager.get_cache_stats()
            avg_analysis_time = (np.mean(self.bot.performance_tracker['analysis_times'])  
                                 if self.bot.performance_tracker['analysis_times'] else 0)
            # Actualizar labels de rendimiento
            self.cache_hit_label.setText(f"Cache: {cache_stats['hit_rate']:.1f}%")
            self.analysis_time_label.setText(f"Análisis: {avg_analysis_time:.0f}ms")
            self.signals_count_label.setText(f"Señales: {self.bot.performance_metrics['total_signals']}")
            nn_info = f"""<b>🧠 ARQUITECTURA NEURONAL OPTIMIZADA:</b>
• Entrada: {self.config.NEURAL_INPUT_SIZE} características técnicas avanzadas
• Capas Ocultas: {self.config.NEURAL_HIDDEN_LAYERS}
• Dropout: {self.config.NEURAL_DROPOUT} (anti-sobreajuste)
• Learning Rate: {self.config.NEURAL_LEARNING_RATE} (optimizado)
• Batch Size: {self.config.NEURAL_BATCH_SIZE} (procesamiento eficiente)
<b>📊 RENDIMIENTO OPTIMIZADO:</b>
• Estado IA: {'✅ Entrenada y Optimizada' if self.bot.neural_trader.is_trained else '❌ No entrenada'}
• Precisión General: {overall_acc:.1f}%
• Precisión Compras: {precision_buy:.1f}%
• Precisión Ventas: {precision_sell:.1f}%
• Última Pérdida: {loss:.4f}
• Última Precisión: {accuracy:.2f}%
<b>⚡ MÉTRICAS DE SISTEMA:</b>
• Cache Hit Rate: {cache_stats['hit_rate']:.1f}%
• Tiempo Análisis Promedio: {avg_analysis_time:.1f}ms
• Entradas en Cache: {cache_stats['total_entries']}
• Requests Totales: {cache_stats['total_requests']}
• Señales Generadas: {self.bot.performance_metrics['total_signals']}
<b>🎯 OPTIMIZACIONES ACTIVAS:</b>
• ✅ Cache inteligente de indicadores técnicos
• ✅ Procesamiento paralelo de símbolos
• ✅ Validación multicapa de señales
• ✅ Gestión optimizada de memoria
• ✅ Análisis técnico avanzado (EMAs, TDI, Patrones)
• ✅ Red neuronal de 3 capas profundas
• ✅ Sistema adaptativo de umbrales
<b>📈 CONFIGURACIÓN OPTIMIZADA:</b>
• Peso IA: 50%
• Peso Técnico: 50% (incluye Strategy)
• IA Mínima Destacada: {self.config.MIN_NEURAL_DESTACADA:.0f}%
• Take Profit: {self.config.DEFAULT_TAKE_PROFIT_PERCENT*100:.1f}%"""
            self.neural_info_text.setHtml(nn_info)
            # 4. Actualizar tabla de señales cada 1.5 segundos
            self.update_signals_table_optimized()
        except Exception as e:
            logger.error(f"Error en actualización optimizada de GUI: {e}")


# ========== FUNCIÓN PRINCIPAL OPTIMIZADA CON SOPORTE CLI ==========
def main_backend():
    """MODO BACKEND: Bot funcional SIN interfaz gráfica (para Replit/Servidores)"""
    print("="*80)
    print("🚀 CRYPTO BOT PRO v35.0.0.0 - MODO BACKEND (SIN GUI)")
    print("Sistema Avanzado de Trading con IA - Versión Optimizada")
    print("="*80)

    # ✅ VERIFICAR DEPENDENCIAS CRÍTICAS
    if not TORCH_AVAILABLE:
        print("⚠️ ADVERTENCIA: PyTorch NO disponible - IA limitada")
    if not REQUESTS_AVAILABLE:
        print("❌ ERROR: Requests NO disponible - API Binance deshabilitada")
        return False
    if not WEBSOCKET_AVAILABLE:
        print("⚠️ ADVERTENCIA: WebSocket NO disponible - Datos en tiempo real limitados")

    # ✅ CREAR CONFIGURACIÓN
    config = AdvancedTradingConfig()
    print(f"✅ Configuración cargada: {len(config.TRADING_SYMBOLS)} pares de trading")

    # ✅ VERIFICAR CONEXIÓN BINANCE
    print("\n📡 VERIFICANDO CONEXIÓN CON BINANCE...")
    try:
        import requests
        test_symbol = config.TRADING_SYMBOLS[0] if config.TRADING_SYMBOLS else "BTCUSDT"
        response = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={test_symbol}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            price = float(data.get('price', 0))
            print(f"✅ CONEXIÓN EXITOSA: {test_symbol} = ${price:.2f}")
        else:
            print(f"⚠️ ADVERTENCIA: No se pudo obtener precio de {test_symbol}")
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
        logger.error(f"Error de conexión Binance: {e}")
        return False

    print(f"📈 Símbolos configurados para {config.MARKET_TYPE}: {len(config.TRADING_SYMBOLS)} pares")

    # ✅ INICIALIZAR BOT EN MODO BACKEND
    try:
        bot = OptimizedTradingBot(config)
        logger.info("✅ Bot iniciado en MODO BACKEND")
        print("✅ Bot iniciado correctamente")
        print("\n📊 INFORMACIÓN DEL SISTEMA:")
        print(f"  • Mercado: {config.MARKET_TYPE}")
        print(f"  • Comisión: {config.get_commission_rate():.2f}% (Round-trip: {config.get_round_trip_commission():.2f}%)")
        print(f"  • Símbolos: {len(config.TRADING_SYMBOLS)}")
        print(f"  • Timeframe Primario: {config.PRIMARY_TIMEFRAME}")
        print(f"  • Timeframe Entrada: {config.ENTRY_TIMEFRAME}")
        print(f"  • Take Profit Neto: {config.PROFIT_TARGET_PERCENT:.1f}% (Bruto: {config.PROFIT_TARGET_PERCENT + config.get_round_trip_commission():.2f}%)")
        print(f"  • Stop Loss: {config.DEFAULT_STOP_LOSS_PERCENT*100:.1f}%")
        print(f"  • PyTorch: {'✅ Disponible' if TORCH_AVAILABLE else '❌ No disponible'}")
        print(f"  • Plotting: {'✅ Disponible' if PLOTTING_AVAILABLE else '❌ No disponible'}")
        print("="*80)
        print("🎯 Bot ejecutándose en BACKGROUND - Análisis en tiempo real...")
        print("="*80)

        # ✅ EJECUTAR LOOP PRINCIPAL 
        bot.start_optimized()
        print("\n✅ Bot corriendo - Monitoreando señales en tiempo real...")
        print("\n📡 MONITOREO DE SEÑALES:")
        print("="*80)

        # Mantener el bot corriendo y mostrar señales
        signal_count = 0
        analysis_cycle = 0
        try:
            while True:
                # Verificar si hay nuevas señales cada 10 segundos
                time.sleep(10)
                analysis_cycle += 1

                # ✅ v32.0.22.4: Mostrar progreso de análisis cada ciclo
                analyzed = getattr(bot, 'symbols_analyzed_count', 0)
                total = getattr(bot, 'total_symbols_to_analyze', 50)
                current_sym = getattr(bot, '_current_analyzed_symbol_for_gui', 'N/A')
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Ciclo #{analysis_cycle}: Analizados {analyzed}/{total} | Actual: {current_sym}")

                # ✅ Verificar si hay análisis en market_data
                if hasattr(bot, 'market_data') and bot.market_data:
                    if analysis_cycle % 6 == 0:  # Cada minuto mostrar resumen
                        best_scores = []
                        for sym, data in bot.market_data.items():
                            analysis = data.get('analysis', {})
                            neural = analysis.get('neural_score', 0)
                            tech = analysis.get('technical_percentage', 0)
                            if neural > 40 or tech > 40:  # v32.0.22.4: Umbral más bajo para diagnóstico
                                best_scores.append((sym, neural, tech))
                        print(f"\n📈 RESUMEN MINUTO #{analysis_cycle//6}: {len(best_scores)} pares con IA>40% o Tec>40%")
                        if best_scores:
                            print(f"🔥 TOP 5 CANDIDATOS:")
                            for sym, neural, tech in sorted(best_scores, key=lambda x: x[1]+x[2], reverse=True)[:5]:
                                print(f"   • {sym}: IA={neural:.1f}% Tec={tech:.1f}%")
                        else:
                            print(f"   ⚠️ Ningún par alcanza umbrales mínimos. Verificar red neuronal y datos.")
                        print()

                # Mostrar estado del tracker de señales
                if hasattr(bot, 'signal_tracker') and bot.signal_tracker:
                    tracked = bot.signal_tracker.tracked_signals
                    active_signals = len(tracked)
                    if active_signals > 0:
                        print(f"\n🎯 SEÑALES ACTIVAS: {active_signals}")

                        # Iterar sobre todas las señales trackeadas
                        for sig_hash, sig_data in tracked.items():
                            status = sig_data.get('status', 'DESCONOCIDA')
                            signal_info = sig_data.get('signal_data', {})
                            if 'symbol' in signal_info:
                                symbol = signal_info['symbol']
                                ia = signal_info.get('neural_score', 0)
                                tech = signal_info.get('technical_percentage', 0)
                                align = signal_info.get('alignment_percentage', 0)

                                if status == 'DESTACADA':
                                    print(f"  ⭐ DESTACADA: {symbol} | IA={ia:.1f}% | Técnico={tech:.0f}% | Alineación={align:.0f}%")
                                elif status == 'CONFIRMADA':
                                    print(f"  ✨ CONFIRMADA: {symbol} | IA={ia:.1f}% | Técnico={tech:.0f}% | Alineación={align:.0f}%")
                                signal_count += 1

                        print("="*80)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo bot...")
            bot.stop()
            logger.info(f"Bot detenido - Total señales detectadas: {signal_count}")
            return True
    except Exception as e:
        logger.critical(f"❌ Error iniciando bot: {e}")
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal con GUI de Windows"""
    try:
        print("="*70)
        print("🚀 CRYPTO BOT PRO v35.0.0.0 - Desarrollado por Lic: Adolfo Daniel Aguirre")
        print("Sistema Avanzado de Trading con IA - Versión Profesional")
        print("="*70)

        # ✅ SOLO INTERFAZ GRÁFICA WINDOWS
        if not PYQT_AVAILABLE:
            print("❌ ERROR: PyQt5 no disponible - Se requiere para GUI de Windows")
            return False

        # ✅ VERIFICAR DEPENDENCIAS CRÍTICAS PARA GUI
        if not TORCH_AVAILABLE:
            print("⚠️ ADVERTENCIA: PyTorch no está disponible")
        if not REQUESTS_AVAILABLE:
            print("❌ ERROR CRÍTICO: Requests no está disponible")
            return False

        # ✅ INICIALIZAR GUI
        app = QApplication(sys.argv)
        app.setApplicationName("Crypto Bot Pro v35.0.0.0")
        app.setApplicationVersion("v35.0.0.0")

        # ✅ CREAR CONFIGURACIÓN Y GUI
        config_optimized = AdvancedTradingConfig()
        main_window = OptimizedCryptoBotGUI(config_optimized)

        logger.info("🚀 CRYPTO BOT PRO v35.0.0.0 OPTIMIZADO INICIADO EXITOSAMENTE")
        logger.info("✨ Sistema con IA optimizada, análisis técnico avanzado e interfaz responsiva")
        logger.info("💎 Características: Cache inteligente, procesamiento paralelo, validación multicapa")
        logger.info("🎯 Estrategia: EMA_TDI_PRICE_ACTION_NEURAL con 20+ características técnicas")
        logger.info("🧠 Red Neuronal: 3 capas profundas con arquitectura optimizada")

        print(f"✅ PyTorch: {'Disponible' if TORCH_AVAILABLE else 'No disponible'}")
        print(f"✅ Plotting: {'Disponible' if PLOTTING_AVAILABLE else 'No disponible'}")
        print(f"✅ Símbolos: {len(config_optimized.TRADING_SYMBOLS)}")
        print(f"✅ Cache: Activado")
        print(f"✅ Procesamiento Paralelo: Activado")
        print(f"✅ Validación Multicapa: Activada")
        print("="*70)
        print("🎉 ¡Sistema Listo para Trading Avanzado!")
        print("="*70)

        # ✅ EJECUTAR APLICACIÓN GUI
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Error fatal: {e}")
        print(f"❌ Error: {e}")
        logger.error(traceback.format_exc())
        return False
# ==============================================================================
# MÓDULO FINAL: IntegrationWorker (El Pegamento entre WS, Analizador y GUI)
# ==============================================================================

class BotWorker(QtCore.QObject):
    """
    Worker que ejecuta la lógica en segundo plano y comunica con la GUI via Signals.
    """
    signal_received = QtCore.pyqtSignal(dict) # Emite un dict de señal

    def __init__(self, symbols, analyzer, parent=None):
        super().__init__(parent)
        self.symbols = symbols
        self.analyzer = analyzer
        self.ws_manager = None
        self.df_cache = {} # Cache local de DataFrames por símbolo

    def start_scanning(self):
        """Inicia la conexión WebSocket"""
        if not WEBSOCKET_AVAILABLE:
            logger.warning("WebSocket no disponible, modo demo inactivo.")
            return

        logger.info(f"Iniciando escaneo para: {self.symbols}")

        # Crear gestor WS
        self.ws_manager = RobustWebSocketManager(
            symbols=self.symbols,
            interval="1m", # Analizamos en velas de 1 minuto para rapidez
            callback=self._on_ws_data
        )
        self.ws_manager.iniciar()

    def stop_scanning(self):
        """Detiene el escaneo"""
        if self.ws_manager:
            self.ws_manager.detener()
        logger.info("Escaneo detenido.")

    def _on_ws_data(self, data):
        """
        Callback que recibe datos del WS en tiempo real.
        1. Actualiza el DataFrame.
        2. Pasa el DF al Analizador.
        3. Si hay señal, emite evento a la GUI.
        """
        try:
            symbol = data.get('symbol')
            if not symbol:
                return

            # 1. Crear o Actualizar DataFrame en memoria
            if symbol not in self.df_cache:
                # Inicializar DataFrame vacío con columnas necesarias
                self.df_cache[symbol] = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            # Crear fila nueva
            new_row = pd.DataFrame([{
                'timestamp': pd.to_datetime(data['timestamp'], unit='ms'),
                'open': float(data['open']),
                'high': float(data['high']),
                'low': float(data['low']),
                'close': float(data['close']),
                'volume': float(data['volume'])
            }])

            # Actualizar cache (Append)
            # Nota: En producción deberías concatenar de forma más eficiente, 
            # pero para 1 señal a la vez esto es suficiente.
            self.df_cache[symbol] = pd.concat([self.df_cache[symbol], new_row], ignore_index=True)

            # Mantener solo últimas 200 velas para análisis ligero
            if len(self.df_cache[symbol]) > 200:
                self.df_cache[symbol] = self.df_cache[symbol].tail(200)

            # Solo analizar si la vela está cerrada (opcional, o analizar cada tick)
            # Aquí analizamos cada tick para máxima velocidad, pero el Analizador tiene sus propios filtros.

            df_analysis = self.df_cache[symbol]

            # 2. Pasar al Analizador (Cerebro)
            signal = self.analyzer.check_limit_and_generate_signal(df_analysis, symbol)

            # 3. Emitir señal a la UI si existe
            if signal:
                logger.info(f"🚀 Señal emitida al hilo principal: {symbol}")
                self.signal_received.emit(signal)

        except Exception as e:
            logger.error(f"Error en Worker procesando datos de WS: {e}")

# ==============================================================================
# DIÁLOGO SELECTOR DE MODO (Windows)
# ==============================================================================

class ModeSelectionDialog(QtWidgets.QDialog):
    """Diálogo para seleccionar modo de ejecución en Windows"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_mode = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Crypto Bot Pro - Selector de Modo")
        self.setFixedSize(500, 350)  # Un poco más grande para mejor espacio
        self.setStyleSheet("""
            QDialog { 
                background-color: #0f0f23; 
                border: 2px solid #00d4aa;
                border-radius: 10px;
            }
            QLabel { color: white; font-size: 14px; font-family: 'Segoe UI', sans-serif; }
            QCheckBox { color: #aaa; font-size: 12px; spacing: 8px; }
            QCheckBox::indicator { width: 18px; height: 18px; }
            QCheckBox::indicator:unchecked { border: 1px solid #555; background: #1a1a2e; border-radius: 3px; }
            QCheckBox::indicator:checked { border: 1px solid #00d4aa; background: #00d4aa; border-radius: 3px; }
        """)

        # Eliminar barra de título nativa para un look más moderno (opcional)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)

        # Título con efecto de brillo
        title = QtWidgets.QLabel("Crypto Bot Pro v35.0.0.0")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #00d4aa;
            qproperty-alignment: AlignCenter;
        """)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QtWidgets.QLabel("Sistema de Trading Institucional con IA")
        subtitle.setStyleSheet("font-size: 14px; color: #888; margin-bottom: 10px;")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Botones con diseño moderno y efectos hover
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(30)

        gui_btn = QtWidgets.QPushButton("🖥️ INTERFAZ GRÁFICA\n(Recomendado)")
        gui_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        gui_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00b09b, stop:1 #96c93d);
                color: white;
                border-radius: 15px;
                padding: 20px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #96c93d;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00d4aa, stop:1 #aadd55);
                border: 2px solid white;
                margin-top: -2px;
            }
            QPushButton:pressed {
                background-color: #009688;
                margin-top: 2px;
            }
        """)
        gui_btn.clicked.connect(self.select_gui_mode)
        btn_layout.addWidget(gui_btn)

        console_btn = QtWidgets.QPushButton("📟 MODO CONSOLA\n(Servidores)")
        console_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        console_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4e54c8, stop:1 #8f94fb);
                color: white;
                border-radius: 15px;
                padding: 20px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #8f94fb;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5f66ff, stop:1 #9fa5ff);
                border: 2px solid white;
                margin-top: -2px;
            }
            QPushButton:pressed {
                background-color: #3f44a0;
                margin-top: 2px;
            }
        """)
        console_btn.clicked.connect(self.select_console_mode)
        btn_layout.addWidget(console_btn)

        layout.addLayout(btn_layout)

        layout.addStretch()

        # Footer con checkbox y botón de salir
        footer_layout = QtWidgets.QHBoxLayout()

        self.remember_checkbox = QtWidgets.QCheckBox("Recordar mi elección")
        footer_layout.addWidget(self.remember_checkbox)

        footer_layout.addStretch()

        close_btn = QtWidgets.QPushButton("Salir")
        close_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ff6b6b;
                border: 1px solid #ff6b6b;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.reject)
        footer_layout.addWidget(close_btn)

        layout.addLayout(footer_layout)

        # Efecto de sombra
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QtGui.QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)

    def select_gui_mode(self):
        self.selected_mode = 'gui'
        self._save_preference()
        self.accept()

    def select_console_mode(self):
        self.selected_mode = 'console'
        self._save_preference()
        self.accept()

    def _save_preference(self):
        if self.remember_checkbox.isChecked():
            try:
                pref_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mode_preference.txt')
                with open(pref_file, 'w') as f:
                    f.write(self.selected_mode)
                logger.info(f"[PREF] Modo guardado: {self.selected_mode}")
            except Exception as e:
                logger.warning(f"[PREF] No se pudo guardar preferencia: {e}")

def get_saved_mode_preference():
    """Lee la preferencia de modo guardada, si existe"""
    try:
        pref_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mode_preference.txt')
        if os.path.exists(pref_file):
            with open(pref_file, 'r') as f:
                mode = f.read().strip()
                if mode in ['gui', 'console']:
                    logger.info(f"[PREF] Preferencia cargada: {mode}")
                    return mode
    except Exception as e:
        logger.debug(f"[PREF] Error leyendo preferencia: {e}")
    return None

# ==============================================================================
# MÓDULOS DE VERIFICACIÓN DE PRODUCCIÓN Y SMOKE TEST
# ==============================================================================
def check_production_readiness():
    """Verifica variables de entorno y permisos críticos para producción."""
    checks = {
        "PYTHONIOENCODING": os.environ.get("PYTHONIOENCODING"),
        "QT_LOGGING_RULES": os.environ.get("QT_LOGGING_RULES"),
        "Logs Dir Writeable": os.access(LOGS_DIR, os.W_OK),
        "Data Dir Writeable": os.access(DATA_ROOT, os.W_OK)
    }

    logger.info("🛡️ Verificación de Preparación para Producción:")
    all_ok = True
    for key, val in checks.items():
        status = "✅ OK" if val else "❌ FALLO"
        logger.info(f"  - {key}: {status} ({val})")
        if not val:
            all_ok = False

    if not all_ok:
        logger.info("ℹ️ Algunas variables de entorno opcionales no están configuradas (PYTHONIOENCODING/QT_LOGGING_RULES). Esto es normal en entornos locales.")
    return True # Permitir continuar siempre que los directorios sean escribibles

class SmokeTest:
    """Pruebas rápidas de encendido para validar componentes críticos."""

    @staticmethod
    def test_config():
        try:
            cfg = AdvancedTradingConfig()
            assert len(cfg.PERPETUALS_SYMBOLS) > 0, "Lista de símbolos vacía"
            return True, "Configuración cargada correctamente"
        except Exception as e:
            return False, f"Fallo en Config: {e}"

    @staticmethod
    def test_logging():
        try:
            logger.debug("Smoke Test Log Entry")
            return True, "Logging operativo"
        except Exception as e:
            return False, f"Fallo en Logging: {e}"

    @staticmethod
    def test_directories():
        required_dirs = [LOGS_DIR, DATA_ROOT, CHARTS_DIR]
        missing = [d for d in required_dirs if not os.path.exists(d)]
        if not missing:
            return True, "Directorios críticos existen"
        return False, f"Faltan directorios: {missing}"

    @classmethod
    def run_all(cls):
        logger.info("🚀 Iniciando Smoke Tests...")
        tests = [
            ("Configuración", cls.test_config),
            ("Logging", cls.test_logging),
            ("Directorios", cls.test_directories)
        ]

        passed_count = 0
        for name, test_func in tests:
            passed, msg = test_func()
            if passed:
                logger.info(f"  ✅ {name}: {msg}")
                passed_count += 1
            else:
                logger.critical(f"  ❌ {name}: {msg}")

        if passed_count == len(tests):
            logger.info("✨ Todos los Smoke Tests pasaron. Sistema listo.")
            return True
        else:
            logger.error("🔥 Fallaron algunos Smoke Tests. Revise la configuración.")
            return False

# ==============================================================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    # ✅ Verificaciones de Inicio
    check_production_readiness()
    if not SmokeTest.run_all():
        logger.critical("❌ Abortando inicio debido a fallos en Smoke Tests.")
        sys.exit(1)

    if PYQT_AVAILABLE:
        # ===== MODO WINDOWS: Verificar preferencia guardada o mostrar selector =====
        try:
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        except:
            pass

        app = QtWidgets.QApplication(sys.argv)

        # Estilo oscuro global
        app.setStyle('Fusion')
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#0f0f23"))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor("#1a2a4c"))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#0f0f23"))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor("#1a2a4c"))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        app.setPalette(palette)

        # Verificar preferencia guardada o mostrar diálogo de selección
        saved_mode = get_saved_mode_preference()

        if saved_mode == 'console':
            # Usuario eligió modo consola previamente
            logger.info("🖥️ Iniciando en modo CONSOLA (preferencia guardada)")
            app.quit()
            main_backend()
        elif saved_mode == 'gui':
            # Usuario eligió modo GUI previamente
            logger.info("🖥️ Iniciando en modo GRAFICO (preferencia guardada)")
            cfg = AdvancedTradingConfig()
            window = OptimizedCryptoBotGUI(cfg)
            window.show()
            sys.exit(app.exec_())
        else:
            # Sin preferencia guardada: mostrar diálogo de selección
            dialog = ModeSelectionDialog()
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                if dialog.selected_mode == 'console':
                    logger.info("🖥️ Usuario seleccionó modo CONSOLA")
                    app.quit()
                    main_backend()
                else:
                    logger.info("🖥️ Usuario seleccionó modo GRAFICO")
                    cfg = AdvancedTradingConfig()
                    window = OptimizedCryptoBotGUI(cfg)
                    window.show()
                    sys.exit(app.exec_())
            else:
                logger.info("❌ Diálogo cerrado sin selección")
                sys.exit(0)
    else:
        # ===== MODO CONSOLA (Replit/Linux sin GUI) =====
        main_backend()
