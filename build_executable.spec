# -*- mode: python ; coding: utf-8 -*-
"""
Crypto Bot Pro v34.0.1.2 - PyInstaller Spec File (Single-File Executable)
============================================================================
Compila TODO dentro de un único .exe sin dependencias externas

CARACTERÍSTICAS:
✅ Modo single-file: TODO empaquetado en 1 .exe
✅ Sin dependencias externas
✅ Incluye todos los modelos y configuraciones
✅ Soporte para PyQt5, PyTorch, Matplotlib, etc.
✅ Optimizado con UPX (compresión)
✅ Icono y versionado incluidos
✅ Carpeta CryptoBotPro_Data se crea automáticamente al ejecutar

INSTALACIÓN:
    pip install PyInstaller pandas numpy torch scikit-learn scipy requests matplotlib mplfinance PyQt5 websocket-client schedule psutil Pillow

CONSTRUCCIÓN:
    pyinstaller build_executable.spec

RESULTADO:
    dist/CryptoBotPro.exe (archivo único, ~150-300 MB según modelos)

EJECUCIÓN:
    dist/CryptoBotPro.exe
    Crea automáticamente:
    - CryptoBotPro_Data/
    - logs/
    - cache/
    - models/
    - signal_charts/
    - training_data/
"""

import os
import sys
from PyInstaller.utils.hooks import collect_all, get_module_file_attribute

# ==============================
# CONFIGURACIÓN GLOBAL
# ==============================
MAIN_SCRIPT = 'Crypto-Pro-Python v34.0.1.2.py'
EXE_NAME = 'CryptoBotPro'
VERSION_STRING = '34.0.1.2'

# ==============================
# 1. DATOS - Archivos empaquetados DENTRO del .exe
# ==============================
datas = []

# A. Recursos UI
if os.path.exists('ui_resources'):
    datas.append(('ui_resources', 'ui_resources'))

# B. Modelos de IA (neural networks, scalers)
models_dir = os.path.join('CryptoBotPro_Data', 'models')
if os.path.exists(models_dir):
    datas.append((models_dir, 'CryptoBotPro_Data/models'))

# C. Datos de entrenamiento (opcionales pero incluidos)
training_data_dir = os.path.join('CryptoBotPro_Data', 'training_data')
if os.path.exists(training_data_dir):
    datas.append((training_data_dir, 'CryptoBotPro_Data/training_data'))

# D. Archivos de configuración críticos
config_files = [
    'config_v20_optimized.json',
    'authcreds.json',
    'telegram_creds.json',
    'CONFIGURACION_RECOMENDADA.md',
]

for config_file in config_files:
    if os.path.exists(config_file):
        datas.append((config_file, '.'))

# E. Datos estáticos del bot
static_data_files = [
    'threshold_history.json',
    'MEJORAS_WIN_RATE_RESUMEN.json',
]

for data_file in static_data_files:
    if os.path.exists(data_file):
        datas.append((data_file, '.'))

# ==============================
# 2. IMPORTACIONES OCULTAS (Hidden Imports)
# ==============================
# Estas son módulos que PyInstaller NO detecta automáticamente

hiddenimports = [
    # === PyQt5 (GUI Framework) ===
    'PyQt5.QtWidgets',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtNetwork',
    'PyQt5.QtSvg',
    'PyQt5.sip',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtWebEngine',
    'PyQt5.QtWebChannel',
    'PyQt5.QtPrintSupport',
    'PyQt5.QtSql',
    'PyQt5.QtOpenGL',

    # === Pandas (Data Analysis) ===
    'pandas',
    'pandas._libs.tslibs.offsets',
    'pandas._libs.tslibs.parsing',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.np_datetime',
    'pandas.core.arrays.datetimes',
    'pandas.core.arrays.timedeltas',
    'pandas.core.computation.expressions',
    'pandas.io.formats',

    # === NumPy (Numerical Computing) ===
    'numpy',
    'numpy.core._methods',
    'numpy.lib.format',
    'numpy.random._mt19937',
    'numpy.random._generator',
    'numpy.random._bit_generator',

    # === PyTorch (Machine Learning) ===
    'torch',
    'torch.nn',
    'torch.nn.modules',
    'torch.nn.modules.loss',
    'torch.optim',
    'torch.optim.lr_scheduler',
    'torch.utils',
    'torch.utils.data',
    'torch.cuda',
    'torch.jit',
    'torch.fx',

    # === Scikit-Learn (ML Algorithms) ===
    'sklearn',
    'sklearn.ensemble',
    'sklearn.preprocessing',
    'sklearn.model_selection',
    'sklearn.metrics',
    'sklearn.decomposition',
    'sklearn.neighbors',
    'sklearn.tree',
    'sklearn.linear_model',

    # === SciPy (Scientific Computing) ===
    'scipy',
    'scipy.signal',
    'scipy.stats',
    'scipy.optimize',
    'scipy.fft',
    'scipy.interpolate',

    # === Matplotlib (Visualization) ===
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_qt5',
    'matplotlib.figure',
    'matplotlib.gridspec',
    'matplotlib.patches',
    'matplotlib.lines',
    'matplotlib.collections',
    'matplotlib.artist',
    'matplotlib.widgets',
    'matplotlib.ticker',
    'matplotlib.dates',
    'mplfinance',

    # === Binance API ===
    'binance',
    'binance.client',
    'binance.exceptions',
    'binance.enums',

    # === Networking & Requests ===
    'requests',
    'requests.auth',
    'requests.utils',
    'urllib3',
    'urllib3.util',
    'certifi',
    'websocket',
    'websocket._core',
    'websocket._app',
    'aiohttp',
    'asyncio',

    # === Telegram Bot API ===
    'telegram',
    'telegram.ext',

    # === Imaging ===
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL.ImageOps',

    # === Scheduling & System ===
    'schedule',
    'psutil',
    'psutil._psutil_windows',
    'psutil._psutil_winfuncs',

    # === Utilities ===
    'joblib',
    'json',
    'threading',
    'logging',
    'logging.handlers',
    'datetime',
    'time',
    'hashlib',
    'uuid',
    'decimal',
    'functools',
    'itertools',
    'collections',
    'queue',
    'concurrent',
    'concurrent.futures',
    'pickle',
    'base64',
    'hmac',
]

# ==============================
# 3. RECOLECTAR DATOS DE LIBRERÍAS
# ==============================
# PyQt5 tiene muchos recursos binarios que deben incluirse

try:
    pyqt5_binaries, pyqt5_datas, pyqt5_hiddenimports = collect_all('PyQt5')
    datas += pyqt5_datas
    hiddenimports += pyqt5_hiddenimports
    print("[✓] PyQt5 recursos incluidos")
except Exception as e:
    print(f"[!] Advertencia: PyQt5 - {e}")

# PyQtWebEngine para gráficos interactivos
try:
    webengine_binaries, webengine_datas, webengine_hiddenimports = collect_all('PyQtWebEngine')
    datas += webengine_datas
    hiddenimports += webengine_hiddenimports
    print("[✓] PyQtWebEngine recursos incluidos")
except Exception as e:
    print(f"[!] Advertencia: PyQtWebEngine - {e}")

# ==============================
# 4. ANÁLISIS DE DEPENDENCIAS
# ==============================
a = Analysis(
    [MAIN_SCRIPT],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Seguridad
        'tkinter',
        'test',
        'tests',
        'unittest',
        'pytest',
        'nose',
        
        # Documentación y herramientas de desarrollo
        'pydoc',
        'doctest',
        'pdb',
        'cProfile',
        'profile',
        
        # Bases de datos
        'sqlite3',
        'dbm',
        'shelve',
        
        # Procesamiento
        'multiprocessing',
        'email',
        'xml',
        'htmllib',
        'html',
        
        # Conflictos de Qt
        'PySide6',
        'PySide2',
        'PyQt6',
        'PyQt3',
        
        # Conflictos de setuptools
        'distutils',
        'setuptools._distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ==============================
# 5. EMPAQUETADO (PYZ)
# ==============================
# Combina todo el código Python en un archivo comprimido
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ==============================
# 6. GENERACIÓN DEL .EXE
# ==============================
# SINGLE-FILE: Todo va dentro de 1 archivo .exe

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    
    # === Parámetros del ejecutable ===
    name=EXE_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                          # Compresión UPX activada
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                     # False = Sin consola (GUI), True = Con consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    
    # === Icono (opcional) ===
    icon=None,  # Cambiar a 'icon.ico' si existe
    
    # === Información de versión (opcional) ===
    version_file=None,  # Cambiar a 'version_info.txt' si existe
)

# ==============================
# CONFIGURACIÓN ALTERNATIVA - MODO DIRECTORIO (si necesitas archivos separados)
# ==============================
# Si necesitas que genere un directorio en lugar de un archivo único,
# descomenta el siguiente bloque y comenta el exe anterior:

# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='CryptoBotPro_dist'
# )

# ==============================
# INSTRUCCIONES FINALES
# ==============================
"""
PRÓXIMOS PASOS:

1. CREAR EL EJECUTABLE:
   pyinstaller build_executable.spec

2. RESULTADO:
   - dist/CryptoBotPro.exe (Archivo único)
   - Tamaño: ~150-300 MB (dependiendo de modelos)

3. DISTRIBUIR:
   - Envía solo el .exe
   - El usuario lo ejecuta y automáticamente se crea CryptoBotPro_Data/

4. SOLUCIONAR PROBLEMAS:

   Si falta algún módulo:
   - Agrega el nombre a 'hiddenimports'
   - Reconstruye: pyinstaller build_executable.spec

   Si es muy grande:
   - Desactiva UPX: upx=False
   - Excluye modelos innecesarios de 'datas'

   Si falla al ejecutar:
   - Activa consola: console=True
   - Lee los mensajes de error en la consola

   Si necesitas verificar qué está incluido:
   - pyinstaller --analyze build_executable.spec
   - Ver el archivo build/CryptoBotPro/xref-CryptoBotPro.html

5. OPTIMIZACIONES AVANZADAS:
   - UPX reduce tamaño ~50% pero ralentiza inicio
   - Puedes usar 'noarchive=True' para más compresión
   - Los datos se extraen a carpeta temporal (_internal) en el .exe

INFORMACIÓN DE DISTRIBUCIÓN:

Requisitos del usuario final:
- Windows 7+ (SP1) o Windows 10/11
- Mínimo 4GB RAM (recomendado 8GB)
- ~500MB libres en disco
- Conexión a internet (para APIs)

El .exe contendrá:
✅ Python 3.9+
✅ Todas las librerías (pandas, numpy, torch, etc.)
✅ Modelos de IA preentrenados
✅ Configuraciones predeterminadas
✅ Interfaz GUI (PyQt5)
✅ Conexión Binance/Telegram
❌ Credenciales (deben proporcionarse al ejecutar)

SEGURIDAD:
- No incluyas archivos sensibles (claves API, contraseñas)
- El usuario debe proporcionar sus propias credenciales
- Los archivos .json se almacenan en CryptoBotPro_Data/ local
"""
