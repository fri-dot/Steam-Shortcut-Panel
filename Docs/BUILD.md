# Build Instructions

## Quick Start (Windows)

### Option 1: Run from source (Recommended for development)
```bash
python -m pip install -r requirements.txt
python main.py
```

### Option 2: Build standalone executable

Simply run the build script:
```bash
build_exe.bat
```

This will:
1. Install all dependencies
2. Install PyInstaller
3. Generate the blue leaf icon
4. Build a standalone executable named `Steam Shortcut Panel.exe`
5. Save it to the `dist/` folder

The executable will be ready to distribute and run on any Windows system!

## Manual Build (Advanced)

If you prefer to build manually:

```bash
# 1. Install requirements
python -m pip install -r requirements.txt pyinstaller

# 2. Generate icon
python create_icon.py

# 3. Build executable
pyinstaller --onefile --windowed --name "Steam Shortcut Panel" --icon icon.ico main.py
```

## Running the Executable

1. Navigate to the `dist/` folder
2. Double-click `Steam Shortcut Panel.exe`
3. On first run, the app will check for required packages
4. If any packages are missing, a setup wizard will appear
5. Click "Install" to automatically install them
6. The app will then start normally

## What the Setup Wizard Does

When you first run the executable:
- Checks for required packages (requests, Pillow)
- If missing, displays a modern setup dialog
- Automatically installs packages using pip
- Handles errors gracefully

## Troubleshooting Build Issues

**"PyInstaller not found"**
- Run: `python -m pip install pyinstaller`

**"Icon not found"**
- Make sure `create_icon.py` ran successfully
- Check that `icon.ico` exists in the project folder

**"Build fails with errors"**
- Ensure Python 3.9+ is installed
- Run: `python -m pip install -r requirements.txt --upgrade`
- Try deleting the `build/` and `dist/` folders before rebuilding

## Distribution

Once built, you can:
- Share `dist/Steam Shortcut Panel.exe` with others
- No installation required - it's a standalone executable
- Users only need Python and the setup will install requirements automatically

## Files Generated

After building:
- `dist/Steam Shortcut Panel.exe` - The standalone executable
- `build/` - Intermediate build files (can be deleted)
- `Steam Shortcut Panel.spec` - PyInstaller configuration (can be deleted)

You only need the `.exe` file to distribute!
