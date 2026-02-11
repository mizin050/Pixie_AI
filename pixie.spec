# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),  # Include entire src folder
        ('fox.png', '.'),
        ('.env', '.'),
    ],
    hiddenimports=[
        # Core modules
        'src.core.ai_engine',
        'src.core.memory',
        'src.ui.chat_window',
        'src.utils.speech',
        'src.utils.vision',
        'src.utils.documents',
        'src.utils.files',
        # External dependencies
        'webview',
        'pystray',
        'PIL',
        'PIL._tkinter_finder',
        'groq',
        'speech_recognition',
        'pyaudio',
        'tkinter',
        'mem0',
        'qdrant_client',
        'PyPDF2',
        'docx',
        'pandas',
        'openpyxl',
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
    name='PixieAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='fox.png',
)
