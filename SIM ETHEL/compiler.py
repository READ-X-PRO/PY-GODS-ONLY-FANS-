import PyInstaller.__main__
import os

# Application entry point
entry_file = "pysim_network.py"

# Output directory for the build
build_dir = "build"
dist_dir = "dist"

# Create directories if they don't exist
os.makedirs(build_dir, exist_ok=True)
os.makedirs(dist_dir, exist_ok=True)

# PyInstaller configuration
PyInstaller.__main__.run([
    entry_file,
    '--onefile',             # Create a single executable
    '--windowed',            # Hide console window
    '--name=PySIM_Manager',  # Output filename
    f'--workpath={build_dir}',
    f'--distpath={dist_dir}',
    '--add-data=assets;assets',  # Add assets folder if needed
    '--icon=sim_icon.ico',   # Application icon
    '--noconfirm',           # Overwrite output directory without confirmation
    '--clean'                # Clean temporary files before building
])