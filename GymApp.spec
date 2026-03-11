# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('frontend_dist', 'frontend_dist'), ('gym_management.db', '.')],
    hiddenimports=['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 'starlette', 'jinja2', 'python-multipart', 'cors', 'sqlite3', 'jwt', 'bcrypt', 'passlib', 'python-jose'],
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
    name='GymApp',
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
    onefile=True,
)
