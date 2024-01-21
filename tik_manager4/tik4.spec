# -*- mode: python ; coding: utf-8 -*-

st_a = Analysis(
    ['dcc\\standalone\\tik4_standalone.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
st_pyz = PYZ(st_a.pure)

st_exe = EXE(
    st_pyz,
    st_a.scripts,
    [],
    exclude_binaries=True,
    name='tik4_standalone',
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

ps_a = Analysis(
    ['dcc\\photoshop\\tik4_photoshop.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
ps_pyz = PYZ(ps_a.pure)

ps_exe = EXE(
    ps_pyz,
    ps_a.scripts,
    [],
    exclude_binaries=True,
    name='tik4_photoshop',
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
    ps_exe,
    ps_a.binaries,
    ps_a.datas,
    st_exe,
    st_a.binaries,
    st_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tik4',
)
