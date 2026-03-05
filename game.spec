# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None

# Đường dẫn gốc của project
project_root = os.path.abspath('.')

a = Analysis(
    # Entry point của game
    [os.path.join(project_root, 'src', 'main.py')],

    # PyInstaller tìm các module trong thư mục này
    pathex=[
        os.path.join(project_root, 'src'),
    ],

    binaries=[],

    # Thêm toàn bộ thư mục assets vào bundle
    # Format: (nguồn, đích trong bundle)
    datas=[
        (os.path.join(project_root, 'assets'), 'assets'),
    ],

    hiddenimports=[
        'pygame',
        'pygame.mixer',
        'pygame.font',
        'pygame.image',
    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BTL-Game2',           # Tên file exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                   # Nén file exe (cần cài upx nếu muốn)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,              # False = ẩn cửa sổ terminal (GUI mode)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
