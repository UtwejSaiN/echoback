# Echoback - Build Instructions

Complete guide to building a distributable Windows executable.

---

## Prerequisites

### 1. Install Build Dependencies

```powershell
# Activate your virtual environment
.\.venv\Scripts\Activate.ps1

# Install PyInstaller and Pillow (for icon generation)
pip install pyinstaller Pillow

# Or install all at once:
pip install -r requirements.txt pyinstaller Pillow
```

### 2. Verify Installation

```powershell
# Check PyInstaller
pyinstaller --version

# Check Pillow
python -c "from PIL import Image; print('Pillow OK')"
```

---

## Build Process

### Step 1: Run Build Script

```powershell
# From project root directory
python build_product.py
```

**What it does:**
1. ✅ Checks all dependencies
2. 🎨 Generates `echoback_icon.ico` (red circle with C3 text)
3. 📄 Creates `version_info.txt` (version properties for EXE)
4. 📜 Creates `c3_manifest.xml` (Windows manifest - no UAC prompt)
5. 🔨 Runs PyInstaller to bundle everything
6. 📦 Copies config and recordings folders to `dist/`
7. 🧹 Cleans up build artifacts

### Step 2: Wait for Build

Build time: ~1-3 minutes (depending on your system)

You'll see output like:
```
==================================================
C3 TIME-MACHINE - BUILD SCRIPT
==================================================
Version: 1.0.0
Author: Utwej Sai Nalluri
==================================================

Checking dependencies...
✓ PyQt6
✓ sounddevice
✓ numpy
✓ pyinstaller
✓ Pillow
✓ All dependencies satisfied

Generating application icon...
✓ Icon created: echoback_icon.ico

Creating version info file...
✓ Created: version_info.txt

Creating Windows manifest...
✓ Created: c3_manifest.xml
  - Execution level: asInvoker (no UAC prompt)

Building executable with PyInstaller...
...
✓ BUILD SUCCESSFUL!
```

### Step 3: Verify Output

Check the `dist/` folder:

```
dist/
├── Echoback.exe      ← Main executable (~40-60 MB)
├── echoback_icon.ico            ← Icon file
├── config/
│   └── default_config.json
└── recordings/
    └── .gitkeep
```

---

## Testing the Executable

### First Test: Development Machine

```powershell
cd dist
.\Echoback.exe
```

**What to verify:**
1. App launches without console window
2. Pill widget appears on screen
3. Recording starts (check console if any appears)
4. System tray icon appears (bottom-right)
5. Press GO button, wait 60 seconds
6. Check `recordings/` folder for WAV file

### Second Test: Clean Environment

1. Copy `dist/` folder to a different location
2. Rename to `Echoback`
3. Run `Echoback.exe`
4. Should work without Python installed

---

## Distribution Options

### Option 1: Folder Distribution

**Pros:** Simple, users can see config and recordings

**Steps:**
1. Rename `dist/` to `Echoback`
2. Zip the entire folder: `Echoback.zip`
3. Share the ZIP file

**User Instructions:**
1. Extract ZIP
2. Run `Echoback.exe`
3. Follow first-run setup if prompted

### Option 2: Installer (Advanced)

Use a tool like **Inno Setup** to create a proper installer:

1. Download Inno Setup: https://jrsoftware.org/isinfo.php
2. Create installer script (`.iss` file)
3. Bundle the `dist/` contents
4. Generate `Echoback_Setup.exe`

---

## Version Info

When users right-click `Echoback.exe` → Properties → Details:

```
File description: Retroactive meeting audio capture utility
Product name:     Echoback
Product version:  1.0.0
Copyright:        Copyright © 2026 Utwej Sai Nalluri
Company:          Utwej Sai Nalluri
Developer:        Utwej Sai Nalluri
```

---

## Manifest Details

The embedded manifest ensures:

- **No UAC prompt** (`asInvoker` execution level)
- Runs as standard user (no admin required)
- Compatible with Windows 10 and 11
- Proper DPI awareness

---

## Troubleshooting

### Build Fails: "PyInstaller not found"

```powershell
pip install pyinstaller
```

### Build Fails: "No module named 'PIL'"

```powershell
pip install Pillow
```

### Build Succeeds but EXE Crashes

1. **Check for missing DLL:**
   - Run `Echoback.exe` from PowerShell
   - Look for error messages
   - May need to install VC++ Redistributable

2. **Debug with console:**
   - Edit `build_product.py`
   - Change `--noconsole` to `--console`
   - Rebuild: `python build_product.py`
   - Run EXE and read console output

3. **Test dependencies:**
   ```powershell
   python -c "import PyQt6; import sounddevice; import numpy; print('OK')"
   ```

### Icon Doesn't Appear

If icon generation fails:

1. **Manual icon:** Use an online generator (e.g., favicon.io)
2. **Skip icon:** Comment out icon line in `build_product.py`
3. **Default icon:** PyInstaller will use Python logo

### Antivirus False Positive

Some antivirus programs flag PyInstaller EXEs as suspicious:

**Solutions:**
1. **Code sign:** Purchase a code signing certificate (~$100/year)
2. **Submit false positive:** Report to antivirus vendor
3. **Add exception:** Users can whitelist the EXE
4. **Alternative:** Use Nuitka instead of PyInstaller

---

## File Sizes

**Expected sizes:**
- `Echoback.exe`: ~40-60 MB (includes Python runtime, Qt, NumPy)
- `echoback_icon.ico`: ~50 KB
- ZIP distribution: ~15-25 MB (compressed)

**Why so large?**
- PyQt6 libraries: ~20 MB
- NumPy: ~10 MB
- Python runtime: ~10 MB
- sounddevice + dependencies: ~5 MB

---

## Updating Version

To release v1.1.0:

1. Edit `version.py`:
   ```python
   __version__ = "1.1.0"
   ```

2. Rebuild:
   ```powershell
   python build_product.py
   ```

3. EXE properties will show new version

---

## Advanced: Reduce EXE Size

### Use UPX Compression

```powershell
# Install UPX: https://upx.github.io/
# Add to build_product.py:
--upx-dir=C:\path\to\upx
```

**Reduction:** ~30-40% smaller (but slower startup)

### Exclude Unused Modules

If you know certain PyQt6 modules aren't used:

```powershell
# In build_product.py, add:
--exclude-module=PyQt6.QtBluetooth
--exclude-module=PyQt6.QtWebEngineWidgets
```

---

## Checklist Before Distribution

- [ ] Build completes without errors
- [ ] EXE runs on your machine
- [ ] Icon appears in EXE and task manager
- [ ] Version info correct (right-click → Properties)
- [ ] First-run dialog appears if no Stereo Mix
- [ ] System tray icon works
- [ ] Minimize to tray works
- [ ] GO button captures audio
- [ ] Cancel button works
- [ ] Recordings save to `recordings/` folder
- [ ] Test on clean Windows VM (no Python)
- [ ] Antivirus scan passes

---

## Release Workflow

### 1. Tag Release
```bash
git tag v1.0.0
git push origin v1.0.0
```

### 2. Build Distribution
```powershell
python build_product.py
```

### 3. Create ZIP
```powershell
Compress-Archive -Path dist\* -DestinationPath Echoback_v1.0.0.zip
```

### 4. Upload to GitHub Releases

1. Go to GitHub → Releases → Draft new release
2. Choose tag: `v1.0.0`
3. Title: "Echoback v1.0.0"
4. Upload: `Echoback_v1.0.0.zip`
5. Add release notes
6. Publish release

---

## Support

If you encounter issues:

1. Check `build_product.py` console output
2. Try building with `--console` to see errors
3. Test on a clean Windows VM
4. Verify all dependencies are installed

---

## Credits

Built with:
- **PyInstaller** - Executable bundling
- **PyQt6** - GUI framework
- **Pillow** - Icon generation
- **Python** - Core runtime

Author: Utwej Sai Nalluri
