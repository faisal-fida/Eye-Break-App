import os
import json
import sys
import winreg as reg

# Constants
CONFIG_FILE = "eye_break_config.json"
FONT = ("Arial", 24)  # Font for the overlay text
OVERLAY_TEXT = "Take a break!\nLook at something 20 feet away."
MUTEX_NAME = "EyeBreakAppMutex"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "BREAK_DURATION": 20,
        "WORK_DURATION": 20,
    }


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


def add_to_startup():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, "EyeBreakApp", 0, reg.REG_SZ, sys.executable)
        reg.CloseKey(key)
    except WindowsError:
        print("Unable to add to startup")
