# GUI Installation Note

**WICHTIG:** Die GUI benötigt Tkinter, das als System-Paket installiert werden muss!

## Installation von Tkinter

### Debian/Ubuntu/Raspberry Pi OS:
```bash
sudo apt install python3-tk
```

### Fedora/RHEL/CentOS:
```bash
sudo dnf install python3-tkinter
```

### Arch Linux:
```bash
sudo pacman -S tk
```

### macOS:
Tkinter ist normalerweise vorinstalliert mit Python.

Falls nicht:
```bash
brew install python-tk@3.11  # Ersetze 3.11 mit deiner Python-Version
```

### Windows:
Tkinter ist im offiziellen Python-Installer enthalten.

Wenn es fehlt, Python neu installieren von python.org und "tcl/tk and IDLE" Option auswählen.

## Testen ob Tkinter installiert ist:

```python
python3 -c "import tkinter; print('Tkinter OK!')"
```

Wenn kein Fehler erscheint, ist Tkinter bereit!

## Nach Tkinter-Installation:

```bash
# Aktiviere venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Starte GUI
python3 network_logging_gui.py
```

## Alternative: CLI-Version nutzen

Wenn du keine GUI möchtest oder Tkinter nicht installieren kannst:

```bash
python3 netLogging.py  # Normale CLI-Version (funktioniert ohne Tkinter)
```

Die CLI-Version hat die gleiche Funktionalität, nur ohne grafische Oberfläche!
