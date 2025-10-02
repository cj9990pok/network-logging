# Building Release Binaries

Due to network share limitations, binaries should be built on local systems:

## Linux Binary
```bash
# On a Linux system
git clone https://github.com/yourusername/network-logging.git
cd network-logging
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt pyinstaller
./build_linux.sh

# Upload dist/NetworkLoggingGUI to GitHub Release
```

## Windows Binary
```bash
# On a Windows system
git clone https://github.com/yourusername/network-logging.git
cd network-logging
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt pyinstaller
build_windows.bat

# Upload dist\NetworkLoggingGUI.exe to GitHub Release
```

## macOS Binary
```bash
# On a macOS system
git clone https://github.com/yourusername/network-logging.git
cd network-logging
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt pyinstaller
./build_macos.sh

# Upload dist/NetworkLoggingGUI.app to GitHub Release
```

## Note
The build scripts are included in the repository. Users can build from source,
or maintainers can provide pre-built binaries in GitHub Releases.
