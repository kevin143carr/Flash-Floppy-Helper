import os
import platform
import logging
import sys
from tkinter import messagebox

logger = logging.getLogger(__name__)

def get_resource_path(relative_path):
    """
    Get absolute path to an external resource file, compatible with:
    - Running from source (.py)
    - Nuitka onefile/standalone (.exe on Windows)
    - macOS .app bundles (Nuitka/PyInstaller)
    """
    
    base_path = None
    
    # --- Nuitka Specific Checks ---
    # NUITKA_ONEFILE_PARENT is a reliable environment variable set by the onefile bootloader
    if "NUITKA_ONEFILE_PARENT" in os.environ:
        logger.debug("Environment detected via NUITKA_ONEFILE_PARENT (Nuitka Onefile).")
        # In this mode, we specifically want the directory where the *original* EXE was launched from.
        # sys.argv[0] often holds the path to the original executable when using the onefile bootloader.
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))

    # --- Generic Frozen Checks (Fallback for older Nuitka/PyInstaller/Standalone) ---
    elif getattr(sys, "frozen", False) or hasattr(sys.modules["__main__"], "__compiled__"):
        logger.debug("Environment detected as 'frozen/compiled' via sys.frozen or __compiled__.")
        exe_path = os.path.abspath(sys.executable)

        if sys.platform == "darwin":
            # Handle macOS specific .app bundle structure
            if exe_path.endswith("/MacOS/" + os.path.basename(exe_path)):
                base_path = os.path.abspath(os.path.join(os.path.dirname(exe_path)))
            else:
                # macOS onefile outside a bundle
                base_path = os.path.dirname(exe_path)
        
        elif sys.platform.startswith("win"):
            # Windows Nuitka/PyInstaller EXE
            base_path = os.path.dirname(exe_path)
            
    # --- Running from Source ---
    else:
        # Running from source (.py script) with a Python interpreter
        base_path = os.path.dirname(os.path.abspath(__file__))
        logger.debug("Environment detected as 'source' (.py script).")

    # Combine the base path with the desired relative path
    if base_path:
        final_path = os.path.join(base_path, relative_path)
    else:
        final_path = os.path.abspath(relative_path) # Should be a rare fallback


    # Debug logging
    logger.debug(f"Requested Relative Path: '{relative_path}'\n"
                 f"Calculated Base Path:    '{base_path}'\n"
                 f"Final Absolute Path:     '{final_path}'")
    
    return final_path


def list_files(folder_path):
    """
    Returns a list of files in the host folder with their sizes.
    Output: [(filename, size), ...]
    """
    file_list = []
    try:
        for f in os.listdir(folder_path):
            full_path = os.path.join(folder_path, f)
            if os.path.isfile(full_path):
                size = os.path.getsize(full_path)
                file_list.append((f, size))
    except Exception as e:
        print(f"Error listing host files: {e}")
    return file_list

def is_executable_file(path):
    """Check if path exists and is executable."""
    return os.path.isfile(path) and os.access(path, os.X_OK)

def is_directory(path):
    """Check if path exists and is a directory."""
    return os.path.isdir(path)

def check_paths(samdisk_path, conversion_tools_path):
    """Check cpmtools paths. Returns (ok: bool, messages: list)."""
    messages = []

    if not conversion_tools_path or not is_directory(conversion_tools_path):
        messages.append("cpmtools path is missing or not a directory.")
    else:
        # On Windows, executables end with .exe
        is_windows = platform.system().lower().startswith("win")
        suffix = ".exe" if is_windows else ""

        for exe in ["cpmls", "cpmcp"]:
            exe_path = os.path.join(conversion_tools_path, exe + suffix)
            if not is_executable_file(exe_path):
                messages.append(f"{exe + suffix} not found or not executable in cpmtools directory.")

    return len(messages) == 0, messages

def show_path_check_result(iparent, ok, messages):
    """Display results in a messagebox."""
    if ok:
        messagebox.showinfo("Success", "All paths are valid!", parent=iparent)
    else:
        messagebox.showerror("Path Check Failed", "\n".join(messages), parent=iparent)
        
def parse_size(value):
    try:
        return int(str(value).replace(',', '').strip())
    except (ValueError, TypeError):
        return 0
