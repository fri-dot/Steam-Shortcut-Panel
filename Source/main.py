import os
import re
import threading
import tkinter as tk
from pathlib import Path
from io import BytesIO
from tkinter import filedialog, messagebox, scrolledtext
from shutil import copy2
import json
import winreg
from datetime import datetime
import sys

# Check and install requirements if needed
try:
    import requests
except ImportError:
    requests = None

try:
    from PIL import Image
except ImportError:
    Image = None

# If requirements are missing, try to install them using setup wizard
if requests is None or Image is None:
    try:
        # Add current directory to path to ensure setup can be imported
        if str(Path.cwd()) not in sys.path:
            sys.path.insert(0, str(Path.cwd()))
        
        from setup import show_setup_dialog, get_missing_packages
        missing = get_missing_packages()
        
        if missing:
            if not show_setup_dialog():
                raise SystemExit("Setup cancelled. Please install requirements manually using: python -m pip install -r requirements.txt")
            
            # Try to import again after setup completes
            try:
                import importlib
                import requests as req_module
                import importlib.util
                
                # Reload the modules
                if importlib.util.find_spec('requests'):
                    import requests
                if importlib.util.find_spec('PIL'):
                    from PIL import Image
            except Exception:
                pass
    except ImportError as e:
        # Setup module not found, try to continue anyway
        print(f"Note: Setup wizard not available ({e})")
    except Exception as e:
        print(f"Setup error: {e}")

STEAM_API_ROOT = "https://api.steampowered.com"
# Prefer smaller shortcut icons
STEAM_ICON_SOURCES = [
    "https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_184x69.jpg",
    "https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/library_hero.jpg",
    "https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg",
]


def get_steam_library_path() -> Path | None:
    """Get the Steam installation directory from Windows registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam") as key:
            install_path = winreg.QueryValueEx(key, "InstallPath")[0]
            return Path(install_path)
    except FileNotFoundError:
        # Try alternative registry path
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
                return Path(steam_path)
        except FileNotFoundError:
            return None


def get_installed_games(steam_path: Path) -> dict[int, Path]:
    """Get installed games with their app IDs and installation paths."""
    installed_games = {}
    
    # Check steamapps folder for game manifests
    steamapps = steam_path / "steamapps"
    if steamapps.exists():
        for manifest_file in steamapps.glob("appmanifest_*.acf"):
            try:
                appid = int(manifest_file.stem.replace("appmanifest_", ""))
                # Parse manifest to get game folder
                game_folder = parse_manifest(manifest_file, steamapps)
                if game_folder:
                    installed_games[appid] = game_folder
            except ValueError:
                continue
    
    return installed_games


def parse_manifest(manifest_file: Path, steamapps: Path) -> Path | None:
    """Parse Steam manifest ACF file to get the game installation folder."""
    try:
        content = manifest_file.read_text(encoding='utf-8', errors='ignore')
        for line in content.split('\n'):
            if '"installdir"' in line.lower():
                # Extract the folder name - handle different quote patterns
                # Format is typically: "installdir"\t\t"FolderName"
                parts = line.split('"')
                # Find the folder name (should be at index 3 or later)
                for i in range(len(parts)):
                    if parts[i].strip() and i > 0:
                        folder_name = parts[i].strip()
                        game_path = steamapps / "common" / folder_name
                        if game_path.exists():
                            return game_path
                        break
    except Exception:
        pass
    return None


def find_game_icon(game_path: Path) -> Path | None:
    """Search for .ico files in the game directory with multiple search patterns."""
    if not game_path or not game_path.exists():
        return None
    
    # Priority 1: Look for .ico files in root directory
    for ico_file in game_path.glob("*.ico"):
        return ico_file
    
    # Priority 2: Look in common subdirectories that contain icons
    for folder in ["redist", "icon", "icons", "resources", "assets"]:
        folder_path = game_path / folder
        if folder_path.exists():
            for ico_file in folder_path.glob("*.ico"):
                return ico_file
    
    # Priority 3: Deep search in game directory (limit depth)
    try:
        depth_count = 0
        for ico_file in game_path.rglob("*.ico"):
            depth = len(ico_file.relative_to(game_path).parts)
            if depth <= 3:
                return ico_file
    except:
        pass
    
    return None



def is_steamid64(value: str) -> bool:
    return value.isdigit() and len(value) == 17


def log(message: str, text_widget: scrolledtext.ScrolledText):
    text_widget.configure(state="normal")
    text_widget.insert("end", message + "\n")
    text_widget.see("end")
    text_widget.configure(state="disabled")


def safe_filename(value: str) -> str:
    value = re.sub(r'[<>:"/|?*]', "_", value)
    value = value.strip()
    return value or "steam-game"


def resolve_vanity(api_key: str, vanity: str) -> str:
    url = f"{STEAM_API_ROOT}/ISteamUser/ResolveVanityURL/v1/"
    params = {"key": api_key, "vanityurl": vanity}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json().get("response", {})
    if data.get("success") != 1:
        raise ValueError("Could not resolve vanity URL. Use a SteamID64 or a valid vanity name.")
    return data["steamid"]


def get_owned_games(api_key: str, steamid: str) -> list[dict]:
    url = f"{STEAM_API_ROOT}/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": api_key,
        "steamid": steamid,
        "include_appinfo": 1,
        "include_played_free_games": 1,
        "format": "json",
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json().get("response", {})
    if "games" not in payload:
        raise ValueError("No games were returned. Make sure your profile is public and the Steam API key is valid.")
    return payload["games"]


def download_icon(appid: int, output_dir: Path, game_path: Path | None, text_widget: scrolledtext.ScrolledText) -> Path | None:
    output_dir.mkdir(parents=True, exist_ok=True)
    icon_path = output_dir / f"{appid}.ico"
    
    # First, try to find icon in the game directory
    if game_path and game_path.exists():
        log(f"  Searching for icon in: {game_path}", text_widget)
        local_icon = find_game_icon(game_path)
        if local_icon and local_icon.exists():
            log(f"  ✓ Found: {local_icon.name}", text_widget)
            # Copy the icon to our icons folder
            try:
                copy2(str(local_icon), str(icon_path))
                return icon_path
            except Exception as e:
                log(f"  ✗ Copy error: {e}", text_widget)
        else:
            log(f"  ✗ No .ico found in game folder", text_widget)
    
    # If icon already cached, return it
    if icon_path.exists():
        return icon_path

    if Image is None:
        log("Pillow is not installed; skipping icon download.", text_widget)
        return None

    # Fall back to downloading from Steam CDN
    for source in STEAM_ICON_SOURCES:
        url = source.format(appid=appid)
        try:
            response = requests.get(url, timeout=12)
        except Exception:
            continue
        if response.status_code != 200:
            continue
        try:
            image = Image.open(BytesIO(response.content)).convert("RGBA")
            # Create smaller shortcut icon size (64x64 is perfect for shortcuts)
            image = image.resize((64, 64), Image.LANCZOS)
            image.save(icon_path, format="ICO", sizes=[(64, 64)])
            return icon_path
        except Exception:
            continue

    log(f"Could not find or download icon for appid {appid}.", text_widget)
    return None


def create_shortcut(appid: int, name: str, desktop_dir: Path, icon_path: Path | None, text_widget: scrolledtext.ScrolledText):
    safe_name = safe_filename(name)
    shortcut_path = desktop_dir / f"{safe_name}.url"
    url_value = f"steam://rungameid/{appid}"
    lines = [
        "[InternetShortcut]",
        f"URL={url_value}",
    ]
    if icon_path is not None and icon_path.exists():
        lines.append(f"IconFile={icon_path}")
        lines.append("IconIndex=0")
    shortcut_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"Created shortcut: {shortcut_path.name}", text_widget)


def generate_shortcuts(api_key: str, steamid_input: str, target_dir: Path, text_widget: scrolledtext.ScrolledText, button: tk.Button, steam_path: Path | None):
    try:
        if not is_steamid64(steamid_input):
            log("Resolving Steam vanity URL...", text_widget)
            steamid_input = resolve_vanity(api_key, steamid_input)
            log(f"Resolved SteamID64: {steamid_input}", text_widget)

        # Get installed games from Steam library
        installed_games = {}
        if steam_path and steam_path.exists():
            log("Detecting installed games from Steam library...", text_widget)
            installed_games = get_installed_games(steam_path)
            log(f"Found {len(installed_games)} installed games.", text_widget)
        else:
            log("Warning: Could not detect Steam library. Creating shortcuts for all owned games.", text_widget)

        log("Fetching owned games from Steam...", text_widget)
        games = get_owned_games(api_key, steamid_input)
        if not games:
            raise ValueError("No owned games were found for this account.")

        # Filter to only installed games if Steam path was found
        if installed_games:
            games = [g for g in games if g.get("appid") in installed_games]
            log(f"Filtered to {len(games)} installed games.", text_widget)

        icon_dir = target_dir / "Steam Game Icons"
        created = 0
        for i, game in enumerate(games, 1):
            appid = game.get("appid")
            name = game.get("name", f"steam-{appid}")
            if appid is None:
                continue
            log(f"Processing [{i}/{len(games)}] {name}...", text_widget)
            # Pass game path for local icon search
            game_path = installed_games.get(appid)
            icon_path = download_icon(appid, icon_dir, game_path, text_widget)
            create_shortcut(appid, name, target_dir, icon_path, text_widget)
            created += 1

        log(f"\n✓ Done. Created {created} shortcuts in {target_dir}", text_widget)
        messagebox.showinfo("Finished", f"Created {created} desktop shortcuts.")
    except Exception as error:
        messagebox.showerror("Error", str(error))
        log(f"Error: {error}", text_widget)
    finally:
        button.config(state="normal")


def choose_folder(entry_var: tk.StringVar):
    initial = Path(entry_var.get() or Path.home() / "Desktop")
    folder = filedialog.askdirectory(initialdir=initial, title="Select destination folder")
    if folder:
        entry_var.set(folder)


def main():
    root = tk.Tk()
    root.title("Steam Icon Panel")
    root.geometry("700x740")
    root.resizable(False, False)
    
    # Modern dark theme
    BG_COLOR = "#0d0d0d"
    FG_COLOR = "#e0e0e0"
    ACCENT_COLOR = "#00a4ff"
    SECONDARY_BG = "#1a1a1a"
    BUTTON_BG = "#1f6ba6"
    BUTTON_HOVER_BG = "#0081cc"
    
    root.config(bg=BG_COLOR)
    
    # Main frame
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill="both", expand=True, padx=0, pady=0)
    
    # Header with glowing title
    header_frame = tk.Frame(main_frame, bg=SECONDARY_BG, height=100)
    header_frame.pack(fill="x", padx=0, pady=(0, 20))
    header_frame.pack_propagate(False)
    
    # Glowing title effect
    title_label = tk.Label(
        header_frame, 
        text="STEAM ICON PANEL",
        font=("Arial", 28, "bold"),
        fg=ACCENT_COLOR,
        bg=SECONDARY_BG,
        padx=20,
        pady=15
    )
    title_label.pack(pady=10)
    
    author_label = tk.Label(
        header_frame,
        text="Made by Fri",
        font=("Arial", 10, "italic"),
        fg="#a0cfff",
        bg=SECONDARY_BG,
        padx=20,
        pady=0
    )
    author_label.pack()
    
    # Add shadow effect label for glow
    shadow_label = tk.Label(
        header_frame,
        text="STEAM ICON PANEL",
        font=("Arial", 28, "bold"),
        fg="#004070",
        bg=SECONDARY_BG,
        padx=20,
        pady=15
    )
    shadow_label.place(in_=title_label, x=2, y=2, relwidth=1, relheight=1)
    shadow_label.lower()
    
    # Content frame
    content_frame = tk.Frame(main_frame, bg=BG_COLOR)
    content_frame.pack(fill="both", expand=True, padx=20, pady=0)
    
    # API Key section
    api_label = tk.Label(content_frame, text="Steam API Key:", fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 10, "bold"))
    api_label.pack(anchor="w", pady=(10, 2))
    api_key_var = tk.StringVar()
    api_entry = tk.Entry(
        content_frame, 
        textvariable=api_key_var, 
        width=70,
        bg=SECONDARY_BG,
        fg=FG_COLOR,
        insertbackground=ACCENT_COLOR,
        border=1,
        relief="flat"
    )
    api_entry.pack(fill="x", pady=(0, 12))
    
    # SteamID section
    steamid_label = tk.Label(content_frame, text="SteamID64 or Vanity Name:", fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 10, "bold"))
    steamid_label.pack(anchor="w", pady=(0, 2))
    steamid_var = tk.StringVar()
    steamid_entry = tk.Entry(
        content_frame, 
        textvariable=steamid_var, 
        width=70,
        bg=SECONDARY_BG,
        fg=FG_COLOR,
        insertbackground=ACCENT_COLOR,
        border=1,
        relief="flat"
    )
    steamid_entry.pack(fill="x", pady=(0, 12))
    
    # Steam Library Folder section
    steam_label = tk.Label(content_frame, text="Steam Library Folder:", fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 10, "bold"))
    steam_label.pack(anchor="w", pady=(0, 2))
    
    steam_frame = tk.Frame(content_frame, bg=BG_COLOR)
    steam_frame.pack(fill="x", pady=(0, 12))
    
    # Auto-detect steam path
    auto_steam_path = get_steam_library_path()
    steam_var = tk.StringVar(value=str(auto_steam_path) if auto_steam_path else "Not found - Select manually")
    
    steam_entry = tk.Entry(
        steam_frame, 
        textvariable=steam_var, 
        width=57,
        bg=SECONDARY_BG,
        fg=FG_COLOR,
        insertbackground=ACCENT_COLOR,
        border=1,
        relief="flat"
    )
    steam_entry.pack(side="left", fill="x", expand=True)
    
    def choose_steam_folder():
        initial = Path(steam_var.get()) if steam_var.get() != "Not found - Select manually" else Path.home()
        try:
            if Path(steam_var.get()).exists():
                initial = Path(steam_var.get())
        except:
            pass
        folder = filedialog.askdirectory(initialdir=initial, title="Select Steam Library folder")
        if folder:
            steam_var.set(folder)
    
    steam_browse_button = tk.Button(
        steam_frame, 
        text="Browse",
        command=choose_steam_folder,
        bg=BUTTON_BG,
        fg="white",
        border=0,
        padx=15,
        pady=5,
        font=("Arial", 9, "bold"),
        cursor="hand2"
    )
    steam_browse_button.pack(side="left", padx=(8, 0))
    
    # Destination Folder section
    dest_label = tk.Label(content_frame, text="Destination Folder:", fg=FG_COLOR, bg=BG_COLOR, font=("Arial", 10, "bold"))
    dest_label.pack(anchor="w", pady=(0, 2))
    
    dest_frame = tk.Frame(content_frame, bg=BG_COLOR)
    dest_frame.pack(fill="x", pady=(0, 12))
    
    desktop_path = str(Path.home() / "Desktop")
    dest_var = tk.StringVar(value=desktop_path)
    dest_entry = tk.Entry(
        dest_frame, 
        textvariable=dest_var, 
        width=57,
        bg=SECONDARY_BG,
        fg=FG_COLOR,
        insertbackground=ACCENT_COLOR,
        border=1,
        relief="flat"
    )
    dest_entry.pack(side="left", fill="x", expand=True)
    
    def choose_folder_wrapper():
        initial = Path(dest_var.get() or Path.home() / "Desktop")
        folder = filedialog.askdirectory(initialdir=initial, title="Select destination folder")
        if folder:
            dest_var.set(folder)
    
    browse_button = tk.Button(
        dest_frame, 
        text="Browse",
        command=choose_folder_wrapper,
        bg=BUTTON_BG,
        fg="white",
        border=0,
        padx=15,
        pady=5,
        font=("Arial", 9, "bold"),
        cursor="hand2"
    )
    browse_button.pack(side="left", padx=(8, 0))
    
    # Instructions
    instructions = (
        "Enter your Steam Web API key and SteamID64 or vanity name.\n"
        "Your profile must be public. The app will create shortcuts for\n"
        "all downloaded games from your Steam library."
    )
    info_label = tk.Label(
        content_frame, 
        text=instructions, 
        wraplength=640, 
        justify="left",
        fg="#a0a0a0",
        bg=BG_COLOR,
        font=("Arial", 9)
    )
    info_label.pack(anchor="w", pady=(12, 12))
    
    # Status section
    status_label = tk.Label(content_frame, text="Status:", fg=ACCENT_COLOR, bg=BG_COLOR, font=("Arial", 10, "bold"))
    status_label.pack(anchor="w", pady=(12, 4))
    
    status_text = scrolledtext.ScrolledText(
        content_frame, 
        width=82, 
        height=12, 
        state="disabled",
        bg=SECONDARY_BG,
        fg=FG_COLOR,
        insertbackground=ACCENT_COLOR,
        border=1,
        relief="flat"
    )
    status_text.pack(fill="both", expand=True, pady=(0, 15))
    
    # Button frame
    button_frame = tk.Frame(content_frame, bg=BG_COLOR)
    button_frame.pack(fill="x", pady=(0, 10))
    
    action_button = tk.Button(
        button_frame, 
        text="Generate Shortcuts",
        width=28,
        bg=BUTTON_BG,
        fg="white",
        border=0,
        padx=20,
        pady=10,
        font=("Arial", 11, "bold"),
        cursor="hand2"
    )
    action_button.pack()
    
    def on_generate():
        api_key = api_key_var.get().strip()
        steamid_input = steamid_var.get().strip()
        target_dir = Path(dest_var.get().strip() or desktop_path)
        
        # Get Steam library path from user input
        steam_path_str = steam_var.get().strip()
        if steam_path_str == "Not found - Select manually":
            messagebox.showwarning("Missing Data", "Please select a Steam library folder.")
            return
        
        steam_path = Path(steam_path_str) if steam_path_str else None
        
        if not api_key or not steamid_input:
            messagebox.showwarning("Missing Data", "Please enter both Steam API key and SteamID/vanity name.")
            return
        if not target_dir.exists():
            messagebox.showwarning("Invalid Folder", "Please select a valid destination folder.")
            return
        if steam_path and not steam_path.exists():
            messagebox.showwarning("Invalid Folder", "Please select a valid Steam library folder.")
            return

        status_text.configure(state="normal")
        status_text.delete("1.0", "end")
        status_text.configure(state="disabled")
        action_button.config(state="disabled")

        worker = threading.Thread(
            target=generate_shortcuts,
            args=(api_key, steamid_input, target_dir, status_text, action_button, steam_path),
            daemon=True,
        )
        worker.start()

    action_button.config(command=on_generate)
    
    # Display Steam library status on startup
    status_text.configure(state="normal")
    if auto_steam_path and auto_steam_path.exists():
        status_text.insert("end", f"✓ Steam library auto-detected: {auto_steam_path}\n")
    else:
        status_text.insert("end", "⚠ Steam library not auto-detected. Please select manually or the app will search for installed games.\n")
    status_text.configure(state="disabled")

    root.mainloop()


if __name__ == "__main__":
    main()
