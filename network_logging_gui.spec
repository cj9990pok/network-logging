# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller build specification for Network Logging GUI
Generates single-file executables for Windows, Linux, and macOS
"""

block_cipher = None

a = Analysis(
    ['network_logging_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('netLogging.py', '.'),
        ('discover_isp_hops.py', '.'),
        ('probe_tcp_hosts.py', '.'),
        ('analyze_netlog.py', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[],
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
    name='NetworkLoggingMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI only)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='network_icon.ico' if os.path.exists('network_icon.ico') else None,
)

# For macOS app bundle
app = BUNDLE(
    exe,
    name='NetworkLoggingMonitor.app',
    icon='network_icon.ico',
    bundle_identifier='com.networklogging.monitor',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '3.1.0',
        'CFBundleVersion': '3.1.0',
    },
)
