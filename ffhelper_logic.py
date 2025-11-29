# viewcpm_logic.py
import os
import shutil
import platform
import subprocess
import ffhelper_prefs as prefs
import shlex
from ffhelper_utils import get_resource_path
import logging

logger = logging.getLogger(__name__)

# ----------------------------
# Utilities
# ----------------------------
def run_command(cmd, use_diskdefs=False, directorystr=None):
    """
    Run shell command and return (success, output).

    Parameters:
        cmd (str): Command to run.
        cwd (str|None): Optional working directory.
        use_diskdefs (bool): If True, set CPMTOOLS to directorystr.
    """
    try:
        env = os.environ.copy()
        if use_diskdefs and directorystr:
            env['CPMTOOLS'] = directorystr
            
        if use_diskdefs:
            cwd = os.path.dirname(directorystr)  # get directory
            cwd = get_resource_path(cwd)
        else:
            cwd = None
       
        logger.debug(f"run_command {cmd} in {cwd}")
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
            env=env
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def get_tmp_folder():
    """Return path to tmp folder, create if missing."""
    tmp_dir = get_resource_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    cleanup_tmp(tmp_dir)
    return tmp_dir

def cleanup_tmp(tmp_dir):
    """Delete oldest files if more than prefs['max_tmp_files'] exist."""
    max_files = prefs.get_pref("max_tmp_files", 20)
    files = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir) if os.path.isfile(os.path.join(tmp_dir, f))]
    if len(files) <= max_files:
        return
    # sort by modification time
    files.sort(key=os.path.getmtime)
    for f in files[:len(files)-max_files]:
        os.remove(f)              
        
# ----------------------------
# Conversion
# ----------------------------

# ----------------------------
# Export IMD to DSK
# ----------------------------

def convert_imd_to_dsk(cmd_template, tools_path, imd_path, out_path):
    """
    Convert an .IMD file to .DSK using the dskconv-style command defined in prefs.json.
    cmd_template: template like `"dskconv -otype dsk {infile} {outfile}"`
    tools_path: folder where dskconv resides
    imd_path: input IMD file
    out_path: final DSK output path chosen by user
    """

    if not cmd_template or not tools_path:
        raise ValueError("Missing 'dskconv_command' or 'conversion_tools_path' in prefs")
    
    is_windows = platform.system().lower().startswith("win")
    suffix = ".exe" if is_windows else ""    

    # Extract converter name and build its full path
    cmd_words = shlex.split(cmd_template, posix=not is_windows)
    exe_name = cmd_words[0]
    converter_path = os.path.join(tools_path, exe_name + suffix)   

    if not os.path.isfile(converter_path):
        raise FileNotFoundError(f"Converter executable not found: {converter_path}")

    # Fill template placeholders
    cmd_filled = cmd_template.format(infile=imd_path, outfile=out_path)

    # Replace exe name with full path
    cmd_parts = shlex.split(cmd_filled, posix=not is_windows)
    cmd_parts[0] = converter_path
    
    # Quote parts safely for execution
    cmd = " ".join(f'"{part}"' for part in cmd_parts)

    # Run the command
    success, output = run_command(cmd)

    if not success:
        raise RuntimeError(f"DSK export failed:\n{output}")

    return out_path

def convert_dsk_to_imd(cmd_template, tools_path, image_path):
    """
    Convert a .DSK/.TD0 file to IMD using the converter defined in prefs.json.
    Returns the path to the converted IMD/RAW file in the tmp folder.
    """

    logger.debug("Entering convert_dsk_to_imd")
    if not cmd_template or not tools_path:
        raise ValueError("Missing 'teledisk_command' or 'conversion_tools_path' in prefs")

    is_windows = platform.system().lower().startswith("win")
    suffix = ".exe" if is_windows else ""

    # Extract converter name and build its full path
    cmd_words = shlex.split(cmd_template, posix=not is_windows)
    exe_name = cmd_words[0]
    converter_path = os.path.join(tools_path, exe_name + suffix)

    logger.debug(f"convert_dsk_to_imd :: checking converter path {converter_path}")
    if not os.path.isfile(converter_path):
        raise FileNotFoundError(f"Converter executable not found: {converter_path}")

    # Prepare output path in tmp folder
    tmp_dir = get_tmp_folder()
    imd_filename = os.path.splitext(os.path.basename(image_path))[0] + ".IMD"
    imd_path = os.path.join(tmp_dir, imd_filename)

    # Fill in infile/outfile placeholders
    cmd_filled = cmd_template.format(infile=image_path, outfile=imd_path)

    # Split into args correctly for the current OS
    cmd_parts = shlex.split(cmd_filled, posix=not is_windows)
    cmd_parts[0] = converter_path  # Replace exe name with full path
    
    # Quote parts safely for execution
    cmd = " ".join(f'"{part}"' for part in cmd_parts)    

    logger.debug(f"convert_dsk_to_imd :: running command {cmd}")
    success,output = run_command(cmd, True, prefs.get_pref("configurations_path"))

    if not success:
        raise RuntimeError(f"Conversion failed:\n{output}")

    return imd_path

def copy_file_to_dir(src_file, dest_dir):
    """Copy a file to a destination directory."""
    if not os.path.isfile(src_file):
        raise FileNotFoundError(f"Source file does not exist: {src_file}")

    os.makedirs(dest_dir, exist_ok=True)

    filename = os.path.basename(src_file)
    dest_path = os.path.join(dest_dir, filename)

    shutil.copy2(src_file, dest_path)  # copy2 preserves timestamps/metadata
    return dest_path

def delete_file(full_path):
    """
    Delete a file using a fully qualified file path.
    """
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"File does not exist: {full_path}")

    os.remove(full_path)



