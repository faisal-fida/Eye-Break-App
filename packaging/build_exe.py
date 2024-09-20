import PyInstaller.__main__
import os

# Determine the directory of the current script
script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


PyInstaller.__main__.run(
    [
        "app.py",  # Main script to convert to exe
        "--name=EyeBreakApp",  # Name of the executable
        "--windowed",  # Create a windowed application
        "--onefile",  # Create a single executable file
        "--add-data=%s:." % os.path.join(script_dir, "config.py"),  # Include config.py
        "--add-data=%s:."
        % os.path.join(script_dir, "settings.py"),  # Include settings.py
        "--icon=%s" % os.path.join(script_dir, "icon.ico"),  # Include icon file
        "--hidden-import=pystray._win32",  # Include hidden import
    ]
)
