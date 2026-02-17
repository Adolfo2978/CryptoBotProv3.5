# -*- mode: python ; coding: utf-8 -*-
"""
Crypto Bot Pro v32.0.22.15 - PyInstaller Spec File (Single-File, All-in-One)
===========================================================================
Compila TODO dentro de un único .exe
Sin dependencias externas
Crea automáticamente CryptoBotPro_Data/ al ejecutar
Soporta PyTorch, PyQt5 WebEngine, Binance API, Telegram
Optimizado para tamaño y rendimiento (UPX + excludes)

Uso:
    pyinstaller crypto_bot_pro.spec
    
Genera: dist/CryptoBotPro v32.0.22.15.exe
"""

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# ==============================
# 1. Recursos estáticos: empaquetados DENTRO del .exe
# ==============================
datas = []

# Carpeta de recursos UI (imágenes, templates, etc.)
if os.path.exists('ui_resources'):
    datas.append(('ui_resources', 'ui_resources'))

# Modelos en CryptoBotPro_Data/models/
models_dir = 'CryptoBotPro_Data/models'
if os.path.exists(models_dir):
    for f in os.listdir(models_dir):
        if f.endswith(('.pth', '.pkl')):
            datas.append((os.path.join(models_dir, f), 'CryptoBotPro_Data/models'))

# Archivos estáticos (config, credenciales, icono, versión)
static_files = [
    'config_v20_optimized.json',
    'authcreds.json',
    'telegram_creds.json',
    'neural_net_model_v20_optimized.pth',
    'scaler_v20_optimized.pkl',
    'icon.ico',
    'version_info.txt',
]

for f in static_files:
    if os.path.exists(f):
        datas.append((f, '.'))

# ==============================
# 2. Importaciones ocultas (hiddenimports)
# ==============================
hiddenimports = [
    # PyQt5
    'PyQt5',
    'PyQt5.QtWidgets',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.sip',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtWebEngine',
    'PyQt5.QtWebChannel',
    # Data Science
    'pandas',
    'pandas._libs',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.np_datetime',
    'numpy',
    'numpy.core._methods',
    'numpy.lib.format',
    # Machine Learning
    'torch',
    'torch.nn',
    'torch.optim',
    'sklearn',
    'sklearn.ensemble',
    'sklearn.preprocessing',
    'joblib',
    # Visualización
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.figure',
    'mplfinance',
    # Networking
    'websocket',
    'websocket._core',
    'requests',
    'urllib3',
    'certifi',
    'aiohttp',
    # Binance
    'binance',
    'binance.client',
    # Imaging
    'PIL',
    'PIL.Image',
    # Utilidades
    'scipy',
    'scipy.signal',
    'json',
    'threading',
    'logging',
    'datetime',
    'time',
    'os',
    'sys',
    'hashlib',
    'math',
    'queue',
    'collections',
    'shutil',
]

# ==============================
# 3. PyQt5 y WebEngine (recursos binarios y datos)
# ==============================
pyqt5_binaries, pyqt5_datas, pyqt5_hiddenimports = collect_all('PyQt5')
datas += pyqt5_datas
hiddenimports += pyqt5_hiddenimports

try:
    webengine_binaries, webengine_datas, webengine_hiddenimports = collect_all('PyQtWebEngine')
    datas += webengine_datas
    hiddenimports += webengine_hiddenimports
except Exception as e:
    print("PyQtWebEngine no disponible:", str(e))

# ==============================
# 4. Análisis principal
# ==============================
a = Analysis(
    ['crypto_bot_desktop_v32.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Seguridad y rendimiento
        'tkinter',
        'test',
        'unittest',
        'email',
        'xml',
        'pydoc',
        'doctest',
        'pdb',
        'sqlite3',
        'multiprocessing',
        # Evitar conflicto Py3.12 + PyInstaller
        'distutils',
        'setuptools._distutils',
        # Evitar conflicto Qt bindings múltiples
        'PySide6',
        'PySide2',
        'PyQt6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ==============================
# 5. PYZ — todo el código y recursos empaquetados
# ==============================
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ==============================
# 6. EXE — bootloader + PYZ (single-file)
# ==============================
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='CryptoBotPro v32.0.22.15',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola (GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)

# NO HAY COLLECT() — modo onefile empaqueta todo en el EXE
