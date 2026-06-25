# Steam Shortcut Panel

A modern Python application that creates desktop shortcuts for your **downloaded Steam games**. Uses the Steam Web API and automatically detects your Steam library to show only installed games. Each shortcut opens the Steam client via `steam://rungameid/<appid>` and includes a high-quality game icon.

**Available as a standalone executable with automatic setup!**

## Features

✨ **Modern Dark UI** - Sleek dark theme with glowing title
🎮 **Downloaded Games Only** - Automatically detects installed games from your Steam library
🎨 **Quality Icons** - Uses icons directly from game files, with fallback to Steam CDN
🔍 **Steam Library Detection** - Automatically finds your Steam installation path
📁 **Manual Folder Selection** - Select Steam library from any drive if auto-detection fails
⚡ **Fast & Efficient** - Multi-threaded processing with real-time status updates
🐛 **Enhanced Icon Search** - Searches multiple locations in game folders for icon files
📦 **Standalone Executable** - Build as single .exe with blue leaf icon
🔧 **Automatic Setup** - Built-in package installer for first-time users

## Quick Start

### Option 1: Run the Standalone Executable (Easiest)

1. Download or build `Steam Shortcut Panel.exe`
2. Double-click to run
3. The app will automatically check and install any missing requirements
4. Start creating shortcuts!

**No Python installation needed!**

### Option 2: Run from Source

```bash
python -m pip install -r requirements.txt
python main.py
```

## How it works

1. Enter your Steam Web API key
2. Enter your SteamID64 or Steam vanity name
3. Select your Steam library folder (auto-detected or manually selected)
4. Choose a destination folder (default is Desktop)
5. Click `Generate Shortcuts`
6. The app will:
   - Fetch all your owned games from Steam
   - Filter to only show downloaded/installed games
   - Search for icon files (.ico) in each game's directory (multiple locations)
   - Fall back to downloading icons from Steam CDN if not found locally
   - Create `.url` shortcuts in your chosen folder with proper icons

## Requirements

- Python 3.9+
- `requests`
- `Pillow`
- Windows (uses Windows registry to detect Steam library)

## Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Build an Executable

To create a standalone `Steam Shortcut Panel.exe`:

```bash
build_exe.bat
```

Or manually:

```bash
python -m pip install pyinstaller
python create_icon.py
pyinstaller --onefile --windowed --name "Steam Shortcut Panel" --icon icon.ico main.py
```

The generated executable will be located in `dist/Steam Shortcut Panel.exe`.

**See [BUILD.md](BUILD.md) for detailed build instructions and troubleshooting.**

## Getting Your Steam API Key

1. Visit: https://steamcommunity.com/dev/apikey
2. Accept the terms and generate your API key
3. Copy and paste it into the application

## Notes

- Your Steam profile must be set to **Public**
- The Steam Web API key must be valid
- Steam must be installed on your machine for the shortcuts to launch games
- The app automatically detects your Steam library from the Windows registry
- If auto-detection fails, you can manually select the Steam library folder (supports external drives)
- Only games you have downloaded/installed will get shortcuts (based on steamapps folder)
- **Icon Search** now looks in multiple locations:
  - Root directory of the game folder
  - Common subfolders: `redist/`, `icon/`, `icons/`, `resources/`, `assets/`
  - Recursively up to 3 levels deep
- Icons are cached locally to avoid redundant downloads
- If local icons aren't found, the app automatically downloads from Steam CDN

## Setup Wizard (Executable Only)

When running the standalone executable for the first time:
- The app checks for required packages (requests, Pillow)
- If any are missing, a modern setup dialog appears
- Click "Install" to automatically download and install them
- The app will then start normally
- Future runs skip the setup dialog

**Python must be installed on the system for the setup wizard to work.**

## Credits

Made by Fri.

## Troubleshooting

### Icons not showing on shortcuts
- Check the status log for "Found local icon" or download messages
- Some games don't include .ico files - the app will try to download from Steam CDN
- If CDN download fails, the shortcut will still work but without an icon
- Try running the app again - icons are cached after first run

### Steam library not detected
- Make sure Steam is installed
- Try manually selecting the Steam folder (usually `C:\Program Files\Steam` or `C:\Program Files (x86)\Steam`)
- If Steam is on another drive, use the Browse button to select it

### No games found
- Ensure you have games installed (shortcuts are only created for downloaded games)
- Check that your Steam profile is set to Public
- Verify your Steam API key is valid at https://steamcommunity.com/dev/apikey
