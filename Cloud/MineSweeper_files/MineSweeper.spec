# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['MineSweeper.py'],
    pathex=[],
    binaries=[],
    datas=[('Images', 'Images'), ('MineSweeper_Difficulty.py', '.'), ('MineSweeper_BoardManager.py', '.'), ('MineSweeper_GameBoard.py', '.'), ('MineSweeper_NetworkManager.py', '.'), ('MineSweeper_GameMessage.py', '.'), ('MineSweeper_ChatManager.py', '.'), ('MineSweeper_Timer.py', '.'), ('MineSweeper_Event.py', '.')],
    hiddenimports=[],
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
    name='MineSweeper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
