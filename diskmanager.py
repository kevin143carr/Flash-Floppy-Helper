# viewcpm_diskops.py
import os
import threading
import ffhelper_logic as logic

class DiskImageManager:
    def __init__(self, conversion_tools_path,  prefs, status_callback=None):
        """
        conversion_tools_path: Path to CP/M tools directory
        status_callback: function(str) to update status bar
        """
        self.conversion_tools_path = conversion_tools_path
        self._current_staging_path = None
        self.status_callback = status_callback or (lambda msg: None)
        self.prefs = prefs

    def set_current_staging_path(self, image_path):
        self._current_staging_path = image_path

    def get_current_staging_path(self):
        return self._current_staging_path
        
    # --- Insert ---
    def insert_files(self, host_folder, files, callback=None):
        if not self._current_staging_path:
            raise RuntimeError("No disk image loaded.")
        def task():
            try:
                for f in files:
                    host_file = os.path.join(host_folder, f)
                    logic.copy_file_to_dir(host_file, self._current_staging_path)
                self.status_callback("Insert complete.")
            except Exception as e:
                self.status_callback(f"Insert failed: {e}")
            if callback:
                callback()
        threading.Thread(target=task, daemon=True).start()

    # --- Delete ---
    def delete_files(self, files, callback=None):
        if not self._current_staging_path:
            raise RuntimeError("No disk image loaded.")
        def task():
            try:
                for f in files:
                    delete_file = os.path.join(self._current_staging_path, f)
                    logic.delete_file(delete_file)
                self.status_callback("Delete complete.")
            except Exception as e:
                self.status_callback(f"Delete failed: {e}")
            if callback:
                callback()
        threading.Thread(target=task, daemon=True).start()
