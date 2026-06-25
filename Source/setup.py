"""
Requirements checker and installer for Steam Shortcut Panel
Ensures all dependencies are installed before running the main app
"""

import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

REQUIRED_PACKAGES = {
    'requests': 'requests>=2.0',
    'PIL': 'Pillow>=9.0',
}

def check_package(package_name: str) -> bool:
    """Check if a package is installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def get_missing_packages() -> list[str]:
    """Return list of missing required packages."""
    missing = []
    for import_name, pip_name in REQUIRED_PACKAGES.items():
        if not check_package(import_name):
            missing.append(pip_name)
    return missing

def install_packages(packages: list[str]) -> bool:
    """Install missing packages using pip."""
    try:
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package
            ])
        return True
    except Exception as e:
        print(f"Failed to install packages: {e}")
        return False

def show_setup_dialog() -> bool:
    """Show setup dialog and install missing packages."""
    missing = get_missing_packages()
    
    if not missing:
        return True
    
    # Create setup window
    root = tk.Tk()
    root.title("Steam Icon Panel - Setup Wizard")
    root.geometry("550x420")
    root.resizable(False, False)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Styling
    BG_COLOR = "#0d0d0d"
    FG_COLOR = "#e0e0e0"
    ACCENT_COLOR = "#00a4ff"
    SECONDARY_BG = "#1a1a1a"
    BUTTON_BG = "#1f6ba6"
    
    root.config(bg=BG_COLOR)
    
    # Header
    header = tk.Label(
        root,
        text="Steam Icon Panel - Setup Wizard",
        font=("Arial", 14, "bold"),
        fg=ACCENT_COLOR,
        bg=BG_COLOR,
        pady=10
    )
    header.pack()
    
    # Welcome message
    welcome = tk.Label(
        root,
        text="Welcome! First-time setup required",
        font=("Arial", 11),
        fg=FG_COLOR,
        bg=BG_COLOR
    )
    welcome.pack(pady=5)
    
    # Message
    message = tk.Label(
        root,
        text=f"Steam Icon Panel needs to install required packages:\n\n{chr(10).join(missing)}\n\nThese are essential for the application to function properly.",
        font=("Arial", 9),
        fg=FG_COLOR,
        bg=BG_COLOR,
        justify="left",
        wraplength=480
    )
    message.pack(pady=10, padx=20)
    
    # Info box
    info_frame = tk.Frame(root, bg=SECONDARY_BG)
    info_frame.pack(pady=8, padx=20, fill="both", expand=True)
    
    info_text = tk.Label(
        info_frame,
        text="What will be installed:\n• requests - For Steam API communication\n• Pillow - For image processing",
        font=("Arial", 8),
        fg="#a0a0a0",
        bg=SECONDARY_BG,
        justify="left",
        wraplength=480,
        padx=10,
        pady=10
    )
    info_text.pack(anchor="w")
    
    # Progress bar
    progress = ttk.Progressbar(root, mode='indeterminate', length=400)
    progress.pack(pady=8, padx=20)
    progress.pack_forget()  # Hide initially
    
    # Status label
    status_label = tk.Label(
        root,
        text="Ready to install. Click 'Install' to begin setup.",
        font=("Arial", 9),
        fg="#a0a0a0",
        bg=BG_COLOR
    )
    status_label.pack()
    
    # Buttons frame
    button_frame = tk.Frame(root, bg=BG_COLOR)
    button_frame.pack(pady=12)
    
    success = [False]  # Use list to allow modification in nested function
    
    def on_install():
        progress.pack(pady=8, padx=20)
        progress.start()
        status_label.config(text="Installing packages... Please wait. This may take 1-2 minutes.")
        install_btn.config(state="disabled")
        cancel_btn.config(state="disabled")
        root.update()
        
        if install_packages(missing):
            success[0] = True
            progress.stop()
            status_label.config(text="✓ Installation complete! Starting application...", fg="#00ff00")
            root.after(2000, root.destroy)
        else:
            progress.stop()
            status_label.config(text="✗ Installation failed. Check your internet connection.", fg="#ff0000")
            install_btn.config(state="normal")
            cancel_btn.config(state="normal")
    
    def on_cancel():
        root.destroy()
    
    install_btn = tk.Button(
        button_frame,
        text="Install & Continue",
        command=on_install,
        bg=BUTTON_BG,
        fg="white",
        padx=40,
        pady=10,
        font=("Arial", 10, "bold"),
        border=0,
        cursor="hand2"
    )
    install_btn.pack(side="left", padx=12)
    
    cancel_btn = tk.Button(
        button_frame,
        text="Cancel",
        command=on_cancel,
        bg="#555555",
        fg="white",
        padx=40,
        pady=10,
        font=("Arial", 10, "bold"),
        border=0,
        cursor="hand2"
    )
    cancel_btn.pack(side="left", padx=12)
    
    root.mainloop()
    return success[0]

if __name__ == "__main__":
    missing = get_missing_packages()
    if missing:
        print(f"Missing packages: {missing}")
        if show_setup_dialog():
            print("Setup completed successfully!")
        else:
            print("Setup cancelled.")
    else:
        print("All required packages are installed.")
