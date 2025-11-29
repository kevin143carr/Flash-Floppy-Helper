import logging
import sys
from pathlib import Path
from datetime import datetime
from ffhelper_utils import get_resource_path

def get_app_root():
    """Return folder containing the executable when frozen,
    otherwise folder containing the main script."""
    if getattr(sys, "frozen", False):
        # Nuitka / PyInstaller frozen executables
        return Path(sys.executable).resolve().parent
    else:
        # Normal Python execution
        return Path(__file__).resolve().parent

def get_log_path():
    """Generate a new timestamped log file for each run."""
    app_root = Path(get_resource_path("logs"))
    logs_dir = app_root
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"ffhelper_{timestamp}.log"

    return logs_dir / log_filename

def setup_logging():
    log_path = get_log_path()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),  # prints during dev
        ],
    )

    logging.getLogger(__name__).info(f"Logging initialized: {log_path}")
    return log_path
