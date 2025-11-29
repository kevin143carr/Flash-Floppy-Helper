import json
import os
import tkinter as tk
from tkinter import filedialog
import ffhelper_prefs as prefs  # safe self-import for get/set_pref
import ffhelper_utils as utils
from ffhelper_utils import get_resource_path
import logging

PREF_FILE = get_resource_path("ffhelper_prefs.json")

logger = logging.getLogger(__name__)

def load_prefs():
    """Load preferences from JSON file."""
    logger.info(f"Loading preferences from {PREF_FILE}")

    if os.path.exists(PREF_FILE):
        logger.debug(f"Preferences file found: {PREF_FILE}")
        try:
            with open(PREF_FILE, "r") as f:
                prefs = json.load(f)
            logger.info("Preferences loaded successfully.")
            return prefs
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {PREF_FILE}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading {PREF_FILE}: {e}")
        return {}
    else:
        logger.warning(f"Preferences file not found: {PREF_FILE}")
        return {}


def save_prefs(prefs):
    """Save preferences to JSON file."""
    with open(PREF_FILE, "w") as f:
        json.dump(prefs, f, indent=2)

def get_pref(key, default=None):
    prefs = load_prefs()
    return prefs.get(key, default)

def set_pref(key, value):
    prefs = load_prefs()
    prefs[key] = value
    save_prefs(prefs)
    
    
def check_paths_button(parent):
    ok, messages = utils.check_paths(parent.teledisk_command, parent.conversion_tools_path)
    utils.show_path_check_result(parent, ok, messages)
      
    # ----------------------------
    # Preferences
    # ----------------------------
def open_prefs_dialog(parent):
    """Show the Preferences dialog window."""
    dialog = tk.Toplevel(parent)
    dialog.title("Preferences")
    dialog.transient(parent)
    dialog.grab_set()  # make modal

    # Load current prefs
    teledisk_cmd = prefs.get_pref("tele.convparams", "")
    imagedisk_cmd = prefs.get_pref("imagedisk_command", "")
    dsk_cmd = prefs.get_pref("dsk.convparams", "")
    conversion_tools_path = prefs.get_pref("conversion_tools_path", "")
    configurations_path = prefs.get_pref("configurations_path", "")

    # Teledisk
    tk.Label(dialog, text="Teledisk (.td0) command:").pack(padx=10, pady=(10,0), anchor="w")
    entry_teledisk = tk.Entry(dialog, width=60)
    entry_teledisk.pack(padx=10, pady=2)
    entry_teledisk.insert(0, teledisk_cmd)

    # ImageDisk
    tk.Label(dialog, text="ImageDisk (.imd) command:").pack(padx=10, pady=(10,0), anchor="w")
    entry_imagedisk = tk.Entry(dialog, width=60)
    entry_imagedisk.pack(padx=10, pady=2)
    entry_imagedisk.insert(0, imagedisk_cmd)

    # DSK
    tk.Label(dialog, text="DSK (.dsk) command:").pack(padx=10, pady=(10,0), anchor="w")
    entry_dskdisk = tk.Entry(dialog, width=60)
    entry_dskdisk.pack(padx=10, pady=2)
    entry_dskdisk.insert(0, dsk_cmd)

    # Conversion Tools
    tk.Label(dialog, text="Conversion Tools Path:").pack(padx=10, pady=(10,0), anchor="w")
    entry_cpmtools = tk.Entry(dialog, width=60)
    entry_cpmtools.pack(padx=10, pady=2)
    entry_cpmtools.insert(0, conversion_tools_path)

    def browse_conversion_tools():
        path = filedialog.askdirectory(title="Select conversion tools directory")
        if path:
            entry_cpmtools.delete(0, tk.END)
            entry_cpmtools.insert(0, path)

    tk.Button(dialog, text="Browse...", command=browse_conversion_tools).pack(padx=10, pady=2, anchor="w")

    # Diskdefs
    tk.Label(dialog, text="Configuratinos Folder:").pack(padx=10, pady=(10,0), anchor="w")
    entry_diskdefs = tk.Entry(dialog, width=60)
    entry_diskdefs.pack(padx=10, pady=2)
    entry_diskdefs.insert(0, configurations_path)

    def browse_configurations():
        path = filedialog.askdirectory(title="Select configurations folder")
        if path:
            entry_diskdefs.delete(0, tk.END)
            entry_diskdefs.insert(0, path)

    tk.Button(dialog, text="Browse...", command=browse_configurations).pack(padx=10, pady=2, anchor="w")

    # --- Save & Close / Check Paths ---
    def save_all_prefs():
        prefs.set_pref("tele.convparams", entry_teledisk.get())
        prefs.set_pref("imagedisk_command", entry_imagedisk.get())
        prefs.set_pref("dsk.convparams", entry_dskdisk.get())
        prefs.set_pref("conversion_tools_path", entry_cpmtools.get())
        prefs.set_pref("configurations_path", entry_diskdefs.get())
        parent.teledisk_command = prefs.get_pref("tele.convparams", "")
        parent.imagedisk_command = prefs.get_pref("imd.convparams", "")
        parent.dsk_command = prefs.get_pref("dsk.convparams", "")
        parent.conversion_tools_path = prefs.get_pref("conversion_tools_path", "")
        parent.configurations_path = prefs.get_pref("configurations_path", "")        
        dialog.destroy()

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=10, pady=10, fill="x")

    tk.Label(button_frame).pack(side="left", expand=True)

    # parent is the main app, so we can call its check_paths_button
    tk.Button(button_frame, text="Check Paths",
              command=lambda: check_paths_button(parent)).pack(side=tk.RIGHT, padx=5)

    tk.Button(button_frame, text="Save & Close", command=save_all_prefs).pack(side=tk.RIGHT, padx=5)

    # Center the dialog on parent
    dialog.update_idletasks()
    w = dialog.winfo_width()
    h = dialog.winfo_height()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
    dialog.geometry(f"{w}x{h}+{x}+{y}")
    dialog.deiconify()

    dialog.wait_window()

