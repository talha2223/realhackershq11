# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['H-Dex\\client_template.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['websockets', 'websockets.client', 'websockets.exceptions', 'mss', 'pyautogui', 'pyperclip', 'psutil', 'requests', 'pynput', 'pynput.keyboard', 'pynput.mouse'],
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
    name='client_template',
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
