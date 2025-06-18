# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['GameMenu.py'],
    pathex=[],
    binaries=[('D:\\Users\\lenovo\\anaconda3\\envs\\GUI\\DLLs\\_sqlite3.pyd', '.')],
    datas=[('.', '.')],
    hiddenimports=['sqlite3', 'requests', 'tkinter.simpledialog'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GameMenu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
