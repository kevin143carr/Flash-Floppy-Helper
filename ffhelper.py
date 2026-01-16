# viewcpm.py
import os
import tkinter as tk
import threading
import ffhelper_logic as logic
import ffhelper_prefs as prefs
import ffhelper_utils as utils
import logging
import platform
from tkinter import ttk, filedialog, messagebox, scrolledtext
from diskmanager import DiskImageManager
from ffhelper_configurations import ConfigurationsManager
from ffhelper_utils import get_resource_path, parse_convert_file
from ffhelper_logging import setup_logging

LOGFILE = setup_logging()
logger = logging.getLogger(__name__)
VERSION = "1.0.0"
base_title = f"Flash Floppy Helper {VERSION}"


# ----------------------------
# Tooltip Helper
# ----------------------------
# ----------------------------
# Tooltip Helper (cross-platform safe)
# ----------------------------
def create_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw()
    tooltip.overrideredirect(True)

    label = tk.Label(
        tooltip,
        text=text,
        background="#ffffe0",   # light yellow background
        foreground="#000000",   # black text
        relief="solid",
        borderwidth=1,
        justify="left",
        wraplength=200,
        padx=4,
        pady=2
    )
    label.pack(ipadx=1)

    def show_tooltip(event):
        tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        tooltip.deiconify()

    def hide_tooltip(event):
        tooltip.withdraw()

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)


class FlashFloppyHelper(tk.Tk):
    def __init__(self):
        logger.debug("Initizing Application")
        super().__init__()
        self.title(base_title)
        self.geometry("1100x600")
        self.minsize(800, 500)
           
        logger.debug("Getting Preferences")
        # Preferences
        self.teledisk_command = prefs.get_pref("tele.convparams", "")
        self.imagedisk_command = prefs.get_pref("imd.convparams", "")
        self.dsk_command = prefs.get_pref("dsk.convparams", "")
        self.conversion_tools_path = get_resource_path(prefs.get_pref("conversion_tools_path", ""))
        self.configurations_path = get_resource_path(prefs.get_pref("configurations_path", ""))
        
        # Make prefs available on self
        self.prefs = prefs  # <-- Add this line        
        
        logger.debug(f"Getting Configurations from {self.configurations_path}")
        # Diskdefs Manager
        self.configurations_manager = None
        if self.configurations_path and os.path.exists(self.configurations_path):
            self.configurations_manager = ConfigurationsManager(self.configurations_path)        
    
        logger.debug("Settting up Disk Image Manager")
        # Disk manager
        self.disk_manager = DiskImageManager(self.conversion_tools_path,  self.prefs, status_callback=self.status_callback)
        self.disk_manager.set_current_staging_path(self.prefs.get_pref("staging_folder"))
    
        logger.debug("Settting up User Interface")
        # UI
        self.create_toolbar()
        self.create_main_panes()
        self.create_statusbar()
        self.bind_events()
    
        # Schedule final window setup after idle      
        if platform.system() == "Windows":
            self.after(50, self.finish_setup)  # 50ms delay
        else:
            self.after_idle(self.finish_setup)
                           
    def open_staging_from_path(self, image_path):
        if not os.path.exists(image_path):
            return
        self._current_image_path = image_path
        self.update_title(image_path)  # show filename in title
        prefs.set_pref("staging_folder", image_path)  # ShaZam! — remember exact file                
        threading.Thread(target=self.populate_staging_folder, args=(image_path,), daemon=True).start()                            
        
    def finish_setup(self):
        # Center window
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
    
        # Deiconify and bring to front
        self.deiconify()
        self.lift()
        self.focus_force()

        # Load last host folder if available
        last_host = prefs.get_pref("last_host_folder", None)
        if last_host and os.path.exists(last_host):
            self.open_host_folder(last_host)
                        
        # ShaZam! — load last disk image if available
        last_image = prefs.get_pref("staging_folder", None)
        if last_image and os.path.exists(last_image):
            self.open_staging_from_path(last_image)      
        

    # ----------------------------
    # Toolbar
    # ----------------------------
    def create_toolbar(self):
        toolbar = ttk.Frame(self, padding=4)
        ttk.Button(toolbar, text="Open Source", command=self.open_host_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Open Staging", command=self.open_staging_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Insert", command=self.insert_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete", command=self.delete_file).pack(side=tk.LEFT, padx=2)
    
        # Get saved disk format from prefs
        saved_format = self.prefs.get_pref("disk_format", "")
        
        # --- Disk Format Dropdown ---
        disk_formats = []
        if self.configurations_manager:
            disk_formats = sorted(self.configurations_manager.get_disk_names(), key=str.lower)

    
        self.disk_format_var = tk.StringVar()
        self.disk_format_combo = ttk.Combobox(
            toolbar,
            textvariable=self.disk_format_var,
            values=disk_formats,
            state="readonly",
            width=20
        )
        
        if saved_format and saved_format in disk_formats:
            self.disk_format_combo.set(saved_format)
        else:
            self.disk_format_combo.set("Choose Disk Format")        
        
        self.disk_format_combo.pack(side=tk.LEFT, padx=6)
        create_tooltip(self.disk_format_combo, "Select the type of Computer")
    
        self.disk_format_combo.bind("<<ComboboxSelected>>", self.on_disk_format_selected)
        # ----------------------------
        
        # --- Export Button ---
        export_btn = ttk.Button(toolbar, text="Export", command=self.export_files_dialog)
        export_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(export_btn, "Export Files and Configs")
        
        
        # --- View Log Button (new) ---
        log_btn = ttk.Button(toolbar, text="View Log",
                             command=self.open_log_window)
        log_btn.pack(side=tk.RIGHT, padx=2)
        create_tooltip(log_btn, "View application log file")
    
        settings_btn = ttk.Button(toolbar, text="Preferences",
                                  command=lambda: prefs.open_prefs_dialog(self))
        
        settings_btn.pack(side=tk.RIGHT, padx=2)
        create_tooltip(settings_btn, "Preferences for paths and other things")
    
        toolbar.pack(side=tk.TOP, fill=tk.X)

    # ----------------------------
    # Main Panes
    # ----------------------------
    def create_main_panes(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.paned = ttk.Panedwindow(main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Left: Host Folder
        left_frame = ttk.Frame(self.paned, padding=2)
        ttk.Label(left_frame, text="Source Folder", font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        self.folder_tree = self.create_treeview(left_frame)
        self.folder_tree.pack(fill=tk.BOTH, expand=True)
        # Label to show current folder under the treeview
        self.host_folder_var = tk.StringVar(value="Folder: N/A")
        ttk.Label(left_frame, textvariable=self.host_folder_var).pack(anchor="w", pady=(2,0))        
        self.paned.add(left_frame, weight=1)

        # Right: Flash Floppy Folder
        right_frame = ttk.Frame(self.paned, padding=2)
        ttk.Label(right_frame, text="Flash Floppy Folder", font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        self.image_tree = self.create_treeview(right_frame)
        self.image_tree.pack(fill=tk.BOTH, expand=True)
        # Disk info labels
        self.disk_info_var = tk.StringVar(value="Disk Size: N/A   Free Space: N/A")
        ttk.Label(right_frame, textvariable=self.disk_info_var).pack(anchor="w", pady=(2,0))       
        
        self.paned.add(right_frame, weight=1)        

    def create_treeview(self, parent):
        tree = ttk.Treeview(parent, columns=("name", "size"), show="headings")
        tree.heading("name", text="Filename")
        tree.heading("size", text="Size Bytes")
        tree.column("name", width=300, anchor="w")
        tree.column("size", width=50, anchor="e")

        yscroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    # ----------------------------
    # Status Bar
    # ----------------------------
    def create_statusbar(self):
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X)

    def status_callback(self, msg):
        self.status_var.set(msg)
        

    # ----------------------------
    # Open Log File Window
    # ----------------------------
    def open_log_window(self):
        """Open a new window showing contents of LOGFILE."""
    
        if not os.path.exists(LOGFILE):
            messagebox.showerror(
                "Log File Missing",
                f"Log file does not exist:\n{LOGFILE}",
                parent=self
            )
            return
    
        win = tk.Toplevel(self)
        win.title("Log Viewer")
        win.geometry("800x500")
    
        text = scrolledtext.ScrolledText(win, wrap="none", font=("Courier", 17))
        text.pack(fill="both", expand=True)
    
        try:
            with open(LOGFILE, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading log:\n{e}"
    
        text.insert("1.0", content)
        text.config(state="disabled")    

    # ----------------------------
    # Event Bindings
    # ----------------------------
    def bind_events(self):
        # Drag-and-drop can be implemented later
        pass
    
    def export_files_dialog(self):
        """Prompt user for output folder, show conversion summary, and export all staging/config files automatically."""
        try:
            # ----------------------------
            # Get staging folder
            # ----------------------------
            staging_path = self.disk_manager.get_current_staging_path()
            if not staging_path:
                messagebox.showerror("Error", "No staging folder loaded.", parent=self)
                return
    
            # ----------------------------
            # Get selected disk format
            # ----------------------------
            selected_format = self.disk_format_combo.get()
            if not selected_format:
                messagebox.showerror("Error", "No disk format selected.", parent=self)
                return
    
            config_dir = os.path.join(self.configurations_path, selected_format)
            convert_file = os.path.join(config_dir, "convert.txt")
    
            # ----------------------------
            # Parse convert.txt
            # ----------------------------
            try:
                final_format, conversions = parse_convert_file(convert_file)
            except FileNotFoundError:
                messagebox.showerror("Error", f"convert.txt not found in {config_dir}", parent=self)
                return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read convert.txt:\n{e}", parent=self)
                return
    
            if not final_format:
                messagebox.showerror("Error", "FINALFORMAT not defined in convert.txt", parent=self)
                return
    
            target_ext = "." + final_format.lower()
    
            # ----------------------------
            # Show conversion summary popup
            # ----------------------------
            summary_lines = [f"FINALFORMAT: {final_format}", "Conversions:"]
            for src, rule in conversions.items():
                summary_lines.append(f"{src} -> {rule['target']}")
            summary_text = "\n".join(summary_lines)
    
            top = utils.create_modal_toplevel(self, width=400, height=200, title="Conversion Summary")
            tk.Label(top, text="The following conversions will be applied:", font=("TkDefaultFont", 10, "bold")).pack(pady=5)
            text_widget = tk.Text(top, width=50, height=10, wrap="none")
            text_widget.insert("1.0", summary_text)
            text_widget.config(state="disabled")
            text_widget.pack(padx=10, pady=5, fill="both", expand=True)
    
            ok_pressed = tk.BooleanVar(value=False)
    
            def on_ok():
                ok_pressed.set(True)
                top.destroy()
    
            tk.Button(top, text="OK", command=on_ok).pack(pady=10)
            self.wait_window(top)
    
            if not ok_pressed.get():
                return  # user closed the window without pressing OK
    
            # ----------------------------
            # Select output folder
            # ----------------------------
            out_folder = filedialog.askdirectory(parent=self, title="Select Output Folder")
            if not out_folder:
                return
    
            # ----------------------------
            # Call export logic
            # ----------------------------
            logic.export_files(
                staging_path=staging_path,
                configurations_path=config_dir,
                out_folder=out_folder,
                target_ext=target_ext,
                conversions=conversions,
                prefs=self.prefs
            )
    
            messagebox.showinfo("Export Complete", f"Files exported to:\n{out_folder}", parent=self)
    
        except Exception as e:
            messagebox.showerror("Export Error", str(e), parent=self)    
    
    
    # ----------------------------
    # Disk Format Selection
    # ----------------------------
    def on_disk_format_selected(self, event):
        selected = self.disk_format_var.get()
        if not selected or not self.configurations_manager:
            return
    
        # Save to prefs
        self.prefs.set_pref("disk_format", selected)
    
        # Optional info popup
        info = self.configurations_manager.get_disk_info(selected)
        if info:
            disksize = info.get("disksize", 0)
            size_kb = disksize / 1024
            messagebox.showinfo(
                "Disk Format Selected",
                f"Selected: {selected}\nCalculated Size: {size_kb:.1f} KB"
            )           

    # ----------------------------
    # Host Folder
    # ----------------------------
    def open_host_folder(self, folder=None):
        last_folder = prefs.get_pref("last_host_folder", os.path.expanduser("~"))
        if folder is None:
            folder = filedialog.askdirectory(title="Select Host Folder", initialdir=last_folder, parent=self)
        
        if folder:
            prefs.set_pref("last_host_folder", folder)
            for item in self.folder_tree.get_children():
                self.folder_tree.delete(item)
            files = utils.list_files(folder)
            for f, size in files:
                # ShaZam! — format size with commas
                self.folder_tree.insert("", "end", values=(f, f"{size:,}"))
            self.status_var.set(f"Loaded folder: {folder}")
            self.host_folder_var.set(f"Folder: {folder}")        

    # ----------------------------
    # Open Staging Folder
    # ----------------------------
    def open_staging_folder(self):
        last_folder = prefs.get_pref("staging_folder", os.path.expanduser("~"))
        staging_path = filedialog.askdirectory(title="Select Staging Folder", initialdir=last_folder, parent=self)
        if staging_path:
            prefs.set_pref("staging_folder", os.path.dirname(staging_path))
            self._current_image_path = staging_path
            self.update_title(staging_path)  # ShaZam! — update title bar with filename
            prefs.set_pref("staging_folder", staging_path)  # ShaZam! — remember exact file        
            threading.Thread(target=self.populate_staging_folder, args=(staging_path,), daemon=True).start()
            
    def populate_staging_folder(self, staging_folder):
        files = utils.list_files(staging_folder)
        self.image_tree.after(0, self.populate_staging_tree, files)
        
        # Sum file sizes safely (remove commas)               
        used_size = sum(int(str(size).replace(',', '')) for _, size in files)
        # free_size = max(disk_size - used_size, 0) if disk_size else 0
        
        self.disk_info_var.set(
            f"Disk Size: {used_size:,} bytes"
            if used_size else "Disk Size: N/A   Free Space: N/A"
        )        

    def populate_staging_tree(self, files):
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
        for f, size in files:
            self.image_tree.insert("", "end", values=(f, f"{size:,}"))
            
    def update_title(self, filename=None):
        if filename:
            # ShaZam! — show the filename in brackets in the title
            self.title(f"{base_title} - [{os.path.basename(filename)}]")
        else:
            self.title(base_title)

    # ----------------------------
    # Insert / Extract / Delete
    # ----------------------------
    def insert_file(self):
        selection = self.folder_tree.selection()
        if not selection:
            messagebox.showwarning("Insert", "No files selected in folder.")
            return
        files = [self.folder_tree.item(i)['values'][0] for i in selection]
        host_folder = prefs.get_pref("last_host_folder", "")
        self.disk_manager.insert_files(host_folder, files, callback=lambda:self.populate_staging_folder(self.disk_manager.get_current_staging_path()))


    def delete_file(self):
        selection = self.image_tree.selection()
        if not selection:
            messagebox.showwarning("Delete", "No files selected in disk image.")
            return
        files = [self.image_tree.item(i)['values'][0] for i in selection]
        if messagebox.askyesno("Delete", f"Delete {len(files)} file(s) from Staging?", parent=self):
            self.disk_manager.delete_files(files, callback=lambda:self.populate_staging_folder(self.disk_manager.get_current_staging_path()))

# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    app = FlashFloppyHelper()
    app.mainloop()
