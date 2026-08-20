# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['RNoTe/main.py',
    'RNoTe/core/config.py',
    'RNoTe/core/custom_notebook.py',
    'RNoTe/core/editor.py',
    'RNoTe/core/line_number_bar.py',
    'RNoTe/core/main_menu.py',
    'RNoTe/core/dialogs.py'],
    pathex=[],
    binaries=[],
    datas=[('RNoTe/data', 'RNoTe/data'), (''RNoTe/lang', ''RNoTe/lang')],
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
    [],
    exclude_binaries=True,
    name='RNoTe',
    icon='prog_icon.ico',
    version='file_version_info.txt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
