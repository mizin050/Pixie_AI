# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py', 'groq_ai.py', 'speech_to_text.py', 'voice_player.py', 'pixie_web_chat.py', 'fox_image.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('fox.png', '.'),
        ('chat.html', '.'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'webview',
        'pystray',
        'PIL',
        'PIL._tkinter_finder',
        'groq',
        'speech_recognition',
        'pyaudio',
        'tkinter',
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='fox.png',
)
