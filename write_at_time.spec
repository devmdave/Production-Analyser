# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['write_at_time.py'],
    pathex=['.'],  # Adjust if your script is in a different folder
    binaries=[],
    datas=[
        ('my_plc.py', '.'),  # Include your custom module
    ],
    hiddenimports=[
        # pandas hidden imports
        'pandas._libs.tslibs.nattype',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.fields',
        'pandas._libs.tslibs.parsing',
        # pycomm3 hidden imports
        'pycomm3.cip_messages',
        'pycomm3.cip_types',
        'pycomm3.cip_base',
        'pycomm3.tag',
        'pycomm3.connection',
        'pycomm3.log',
        'pycomm3.utils'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='write_at_time',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False  # 👈 Ensures silent background execution
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='write_at_time'
)
