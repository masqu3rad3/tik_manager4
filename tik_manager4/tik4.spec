# -*- mode: python ; coding: utf-8 -*-

st_a = Analysis(
    ['dcc\\standalone\\tik4_standalone.py'],
    pathex=[],
    binaries=[],
    datas=[('ui\\theme', 'ui\\theme')],
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
    icon='ui\\theme\\rc\\tik_main.ico'
)

ps_a = Analysis(
    [
        'dcc\\photoshop\\tik4_ps_main_ui.py',
        'dcc\\photoshop\\extract\\image.py',
        'dcc\\photoshop\\extract\\source.py',
        'dcc\\photoshop\\ingest\\source.py',
     ],
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
    icon='ui\\theme\\rc\\ps_mainui.ico'
)

ps_b = Analysis(
    ['dcc\\photoshop\\tik4_ps_new_version.py'],
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
ps_b_pyz = PYZ(ps_b.pure)

ps_b_exe = EXE(
    ps_b_pyz,
    ps_b.scripts,
    [],
    exclude_binaries=True,
    name='tik4_ps_new_version',
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
    icon='ui\\theme\\rc\\ps_version.ico'
)

ps_c = Analysis(
    ['dcc\\photoshop\\tik4_ps_publish.py'],
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
ps_c_pyz = PYZ(ps_c.pure)

ps_c_exe = EXE(
    ps_c_pyz,
    ps_c.scripts,
    [],
    exclude_binaries=True,
    name='tik4_ps_publish',
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
    icon='ui\\theme\\rc\\ps_publish.ico'
)

dcc_a = Analysis(
    ['dcc\\dcc_install.py'],
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
dcc_pyz = PYZ(dcc_a.pure)

dcc_exe = EXE(
    dcc_pyz,
    dcc_a.scripts,
    [],
    exclude_binaries=True,
    name='install_dccs',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    ps_b_exe,
    ps_b.binaries,
    ps_b.datas,
    ps_c_exe,
    ps_c.binaries,
    ps_c.datas,
    st_exe,
    st_a.binaries,
    st_a.datas,
    dcc_exe,
    dcc_a.binaries,
    dcc_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tik4',
)
