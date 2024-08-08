# -*- mode: python ; coding: utf-8 -*-
#pyinstaller 终极图像处理.spec
#pyinstaller "E:\\AAAAAAAA\\VScode_HugeProject\\Soil-Conservation\\终极图像处理.spec"

block_cipher = None

a = Analysis(
    ['终极图像处理.py'],
    pathex=['E:\\AAAAAAAA\\VScode_HugeProject\\Soil-Conservation'],
    binaries=[],
    datas=[
        ('E:\\AAAAAAAA\\VScode_HugeProject\\Soil-Conservation\\cv2', 'cv2'),
        ('E:\\AAAAAAAA\\VScode_HugeProject\\Soil-Conservation\\sv_ttk', 'sv_ttk'),
    ],
    hiddenimports=[],
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
    name='终极图像处理',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='material\logo.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='终极图像处理',
)
