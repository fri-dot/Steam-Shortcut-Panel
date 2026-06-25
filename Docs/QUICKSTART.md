# Quick Start - Build & Run

## 📌 TL;DR - Just Build It!

```bash
build_exe.bat
```

Then run:
```
dist\Steam Shortcut Panel.exe
```

Done! ✓

---

## What This Creates

✅ **Single Executable File:**
- `Steam Shortcut Panel.exe` (15-50 MB)
- Blue leaf icon
- No installation needed
- Automatic setup wizard

✅ **On First Run:**
- Setup wizard appears (if packages missing)
- One click to install requirements
- App launches automatically

✅ **After First Run:**
- App starts directly
- No more setup dialogs
- Full functionality available

---

## System Requirements

- **Windows 10 or newer**
- **Python 3.9+** (for setup wizard to install packages)
- **Internet connection** (first run only, for package download)

---

## Build Breakdown

The `build_exe.bat` script automatically:

1. Upgrades pip
2. Installs Python dependencies (requests, Pillow)
3. Installs PyInstaller
4. Generates blue leaf icon (`icon.ico`)
5. Builds executable with PyInstaller
6. Creates `dist/Steam Shortcut Panel.exe`

**Total time:** ~5-10 minutes (first time)

---

## After Building

1. **Location:** `dist/Steam Shortcut Panel.exe`
2. **Size:** 15-50 MB
3. **Distribute:** Just copy this single file
4. **Requirements:** Python 3.9+ on user's PC

---

## Features Included

✨ Modern dark UI with glowing title  
🎨 Blue leaf icon  
🔧 Automatic setup wizard  
🎮 Steam game detection  
📁 Manual library folder selection  
🎯 Smart icon searching  
⚡ Fast multi-threaded processing  

---

## Troubleshooting

**Build fails?**
- Make sure Python 3.9+ is installed
- Check internet connection
- Try: `python -m pip install -r requirements.txt`
- Run `build_exe.bat` again

**Exe won't run?**
- Ensure Python 3.9+ is installed
- Run with admin privileges
- Check Windows Defender (may block first run)

**Setup wizard doesn't appear?**
- Python might already be installed
- Packages may already be present
- This is normal - just proceed to use the app

---

## Files Reference

| File | Purpose |
|------|---------|
| `build_exe.bat` | Build script (run this) |
| `main.py` | Main application |
| `setup.py` | Setup wizard |
| `create_icon.py` | Icon generator |
| `main.spec` | Build configuration |
| `requirements.txt` | Dependencies |
| `dist/Steam Shortcut Panel.exe` | Final executable |

---

## That's It!

You now have a professional, standalone executable of Steam Shortcut Panel with:
- Blue leaf icon ✓
- Setup wizard ✓
- Modern UI ✓
- Automatic installation ✓

**Share `dist/Steam Shortcut Panel.exe` with anyone!**

---

For detailed information:
- See `BUILD.md` for build issues
- See `SETUP_GUIDE.md` for user guide
- See `README.md` for features
- See `DEPLOYMENT_SUMMARY.md` for overview
