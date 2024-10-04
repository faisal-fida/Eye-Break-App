import PyInstaller.__main__
import os
import subprocess
import shutil

script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

print("Building the executable...")

data_files = [
    "config.py",
    "azure.tcl",
    os.path.join("theme", "*"),
    "settings.py",
    "app.py",
]

add_data_args = [
    "--add-data=%s%s." % (os.path.join(script_dir, file), os.pathsep)
    for file in data_files
]

try:
    PyInstaller.__main__.run(
        [
            "app.py",
            "--name=EyeBreakApp",
            "--windowed",
            "--onefile",
            *add_data_args,
            "--icon=%s" % os.path.join(script_dir, "icon.ico"),
            "--hidden-import=pystray._win32",
            "--hidden-import=pkg_resources.py2_warn",
        ]
    )
    print("PyInstaller ran successfully.")
except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)

print("Build successful. Moving files...")

shutil.move(
    os.path.join(script_dir, "dist", "EyeBreakApp.exe"),
    os.path.join(script_dir, "packaging", "EyeBreakApp.exe"),
)

shutil.move(
    os.path.join(script_dir, "EyeBreakApp.spec"),
    os.path.join(script_dir, "packaging", "EyeBreakApp.spec"),
)

shutil.rmtree(os.path.join(script_dir, "build"), ignore_errors=True)
shutil.rmtree(os.path.join(script_dir, "dist"), ignore_errors=True)

print("Files moved successfully. Making the installer...")

subprocess.run(
    [
        "iscc",
        "/Qp",
        os.path.join(script_dir, "packaging", "EyeBreakApp.iss"),
    ]
)
