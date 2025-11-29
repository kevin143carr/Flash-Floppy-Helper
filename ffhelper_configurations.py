# ffhelper_configurations.py
import os

class ConfigurationsManager:
    def __init__(self, configurations_path):
        self.configurations_path = configurations_path
        self.diskdefs = []
        if os.path.exists(configurations_path):
            self._parse_configurations()

            
    def _parse_configurations(self):
        """Populate self.diskdefs with subdirectories inside configurations_path."""
        self.diskdefs = []   # clear previous list
    
        configs_dir = self.configurations_path
    
        if not os.path.isdir(configs_dir):
            return  # nothing to load
    
        for entry in os.listdir(configs_dir):
            full_path = os.path.join(configs_dir, entry)
            if os.path.isdir(full_path):
                self.diskdefs.append({
                    "name": entry,
                    "path": full_path
                })


    def get_disk_names(self):
        return [d["name"] for d in self.diskdefs]

    def get_disk_info(self, name):
        for d in self.diskdefs:
            if d["name"] == name:
                return d
        return None
