import os
import json
import sys
import winreg as reg
import logging

# Constants
FONT = ("Arial", 24)  # Font for the overlay text
OVERLAY_TEXT = "Take a break!\nLook at something 20 feet away."
MUTEX_NAME = "EyeBreakAppMutex"
DOCUMENTS_FOLDER = os.path.join(os.environ["USERPROFILE"], "Documents")
CONFIG_FILE = os.path.join(DOCUMENTS_FOLDER, "eye_break_app.json")

# Configure logging
logging.basicConfig(
    filename=os.path.join(DOCUMENTS_FOLDER, "eye_break_app.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def load_config():
    logging.debug("Loading configuration")
    if os.path.exists(CONFIG_FILE):
        logging.info(f"Configuration file {CONFIG_FILE} found")
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            logging.debug(f"Configuration loaded: {config}")
            return config
    logging.warning(
        f"Configuration file {CONFIG_FILE} not found, using default settings"
    )
    return {
        "BREAK_DURATION": 20,
        "WORK_DURATION": 20,
    }


def save_config(config):
    logging.debug(f"Saving configuration: {config}")
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
    logging.info(f"Configuration saved to {CONFIG_FILE}")


def add_to_startup():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        logging.debug("Adding application to startup")
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, "EyeBreakApp", 0, reg.REG_SZ, sys.executable)
        reg.CloseKey(key)
        logging.info("Application added to startup successfully")
    except WindowsError as e:
        logging.error("Failed to add application to startup", exc_info=True)
        raise Exception("Permission denied. Run as administrator to add to startup.")
