# Building Executables with PyInstaller

Complete guide for building standalone executables of Network Logging Monitor.

## Prerequisites

1. **Install PyInstaller:**
   ```bash
   # In your activated venv
   pip install pyinstaller
   ```

2. **Verify installation:**
   ```bash
   pyinstaller --version
   ```

## Quick Build (All Platforms)

### Windows
```cmd
build_windows.bat
```
Output: `dist\NetworkLoggingMonitor.exe` (~25-35 MB)

### Linux
```bash
./build_linux.sh
```
Output: `dist/NetworkLoggingMonitor` (~25-35 MB)

### macOS
```bash
./build_macos.sh
```
Output: `dist/NetworkLoggingMonitor.app` (~25-35 MB)

## Manual Build (Advanced)

If you want more control:

```bash
# Basic single-file build
pyinstaller --onefile --windowed --name NetworkLoggingMonitor network_logging_gui.py

# With icon
pyinstaller --onefile --windowed --icon=network_icon.ico network_logging_gui.py

# Using the spec file (recommended)
pyinstaller --clean network_logging_gui.spec
```

## Build Configuration

The `network_logging_gui.spec` file controls the build:

- **`--onefile`**: Creates single executable (easier distribution)
- **`--windowed`**: No console window (GUI only)
- **`console=False`**: Same as --windowed
- **`upx=True`**: Compress executable (smaller size)
- **`icon='network_icon.ico'`**: Custom application icon

### Included Files

The build automatically includes:
- `config.json` - Configuration template
- `netLogging.py` - Core monitoring module
- `discover_isp_hops.py` - ISP discovery script
- `probe_tcp_hosts.py` - TCP probing script
- `analyze_netlog.py` - Log analysis script
- `README.md` - Documentation
- `LICENSE` - MIT License

## Distribution

### Option 1: Single Executable Only
Distribute just the `.exe` or binary file. Users can:
- Run it directly
- Create `logs/` folder will be auto-created
- Need to create `config.json` or use GUI editor

### Option 2: Full Package (Recommended)
Distribute the entire `dist/` folder containing:
```
dist/
  NetworkLoggingMonitor.exe  (or binary)
  config.json                 (pre-configured)
  README.md                   (instructions)
  LICENSE                     (MIT)
  logs/                       (empty folder)
  setup_scripts/              (scheduler setup scripts)
```

### Option 3: Installer (Advanced)
Create an installer using:
- **Windows:** Inno Setup, NSIS, or WiX
- **macOS:** create-dmg or hdiutil
- **Linux:** AppImage, Flatpak, or Snap

## GitHub Release Assets

Upload to GitHub Releases:

1. **Build for each platform:**
   - Windows: `NetworkLoggingMonitor-v3.1.0-Windows-x64.exe`
   - Linux: `NetworkLoggingMonitor-v3.1.0-Linux-x86_64`
   - macOS: `NetworkLoggingMonitor-v3.1.0-macOS.app.zip`

2. **Calculate checksums:**
   ```bash
   # Windows
   certutil -hashfile NetworkLoggingMonitor.exe SHA256
   
   # Linux/macOS
   sha256sum NetworkLoggingMonitor
   ```

3. **Create SHA256SUMS.txt:**
   ```
   abc123...  NetworkLoggingMonitor-v3.1.0-Windows-x64.exe
   def456...  NetworkLoggingMonitor-v3.1.0-Linux-x86_64
   ghi789...  NetworkLoggingMonitor-v3.1.0-macOS.app.zip
   ```

## Common Issues

### Windows SmartScreen Warning
**Problem:** Windows shows "Windows protected your PC" warning

**Solutions:**
1. **For users:** Click "More info" → "Run anyway"
2. **For developers:** Code sign with certificate (~$100-400/year)
3. **Alternative:** Distribute as "portable app" in ZIP with instructions

### Antivirus False Positives
**Problem:** Antivirus flags the .exe as malware

**Why:** PyInstaller executables sometimes trigger heuristics

**Solutions:**
1. Submit to VirusTotal (shows it's clean)
2. Contact antivirus vendors to whitelist
3. Use `--noupx` flag (larger file, less suspicious)
4. Code signing (best solution)

### macOS Gatekeeper
**Problem:** "NetworkLoggingMonitor.app can't be opened because it is from an unidentified developer"

**Solution for users:**
```bash
# Option 1: Right-click → Open (shows "Open" button)

# Option 2: Remove quarantine
xattr -d com.apple.quarantine NetworkLoggingMonitor.app

# Option 3: System Preferences → Security → "Open Anyway"
```

**Solution for developers:**
- Get Apple Developer account ($99/year)
- Code sign with `codesign`
- Notarize with Apple

### Large File Size
**Problem:** Executable is 30-40 MB (seems big)

**Why:** Includes entire Python runtime + libraries

**Solutions:**
1. Already using UPX compression (saves ~30%)
2. Exclude unused modules in .spec file
3. Consider `--onedir` mode (faster startup, multiple files)

### Linux Dependencies
**Problem:** Binary doesn't run on other Linux distros

**Why:** Different glibc versions, missing system libraries

**Solutions:**
1. Build on older distro (better compatibility)
2. Use Docker for consistent builds
3. Create AppImage (bundles all dependencies)
4. Document required system packages

## Advanced: Cross-Compilation

**Note:** PyInstaller doesn't support cross-compilation!

You **must** build on the target platform:
- Windows .exe → build on Windows
- Linux binary → build on Linux  
- macOS .app → build on macOS

### Workarounds:
1. **Virtual Machines:** Use VirtualBox/VMware
2. **GitHub Actions:** Automated builds for all platforms
3. **Cloud VMs:** AWS/Azure/DigitalOcean temporary instances

## GitHub Actions Automated Build

Create `.github/workflows/build.yml`:

```yaml
name: Build Executables

on:
  release:
    types: [created]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install pyinstaller
      - run: pyinstaller --clean network_logging_gui.spec
      - uses: actions/upload-artifact@v2
        with:
          name: windows-exe
          path: dist/NetworkLoggingMonitor.exe

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install pyinstaller
      - run: pyinstaller --clean network_logging_gui.spec
      - uses: actions/upload-artifact@v2
        with:
          name: linux-binary
          path: dist/NetworkLoggingMonitor

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install pyinstaller
      - run: pyinstaller --clean network_logging_gui.spec
      - uses: actions/upload-artifact@v2
        with:
          name: macos-app
          path: dist/NetworkLoggingMonitor.app
```

## Testing Builds

Before distributing:

1. **Test on clean system** (no Python installed)
2. **Test with antivirus enabled**
3. **Test all GUI features:**
   - Start/Stop monitoring
   - Log viewer
   - Config editor
   - Scheduler setup (requires admin)
   - Manual tests
4. **Check file paths** (logs, config)
5. **Verify admin elevation** works

## Size Optimization

Current size: ~25-35 MB

Possible optimizations:
```python
# In .spec file, exclude unused modules:
excludes=[
    'matplotlib',  # If not using charts
    'PIL',         # If no image processing
    'numpy',       # If not needed
    'pandas',      # If not needed
]
```

With optimizations: ~15-20 MB possible

## Distribution Checklist

- [ ] Build for all target platforms
- [ ] Test on clean systems
- [ ] Generate SHA256 checksums
- [ ] Create release notes
- [ ] Upload to GitHub Releases
- [ ] Document SmartScreen/Gatekeeper workarounds
- [ ] Add download badges to README
- [ ] Announce on social media

## Support

For build issues:
1. Check PyInstaller docs: https://pyinstaller.org
2. Search GitHub issues: https://github.com/pyinstaller/pyinstaller/issues
3. Test with `--debug=all` flag for verbose output

## License Note

**Important:** Your executable includes:
- Your code (MIT License) ✓
- Python runtime (PSF License - redistribution OK) ✓
- Tkinter (PSF License) ✓
- PyInstaller bootloader (GPL exception for distribution) ✓

Your MIT license is compatible with all dependencies! 🎉
