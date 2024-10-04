import tkinter as tk
from tkinter import messagebox
import threading
import time
import pystray
from PIL import Image
import ctypes
import os
import sys
import logging

from config import load_config, save_config, add_to_startup, CONFIG_FILE, MUTEX_NAME
from settings import SettingsWindow, Overlay, Timer

# Configure logging
logging.basicConfig(
    filename="eye_break_app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class EyeBreakApp:
    def __init__(self):
        logging.debug("Initializing EyeBreakApp")
        self.config = load_config()
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.overlay = Overlay(self.root, self.config)
        self.timer = Timer(
            self.show_break, self.hide_break, self.update_menu, self.config
        )
        self.icon = None

    def show_break(self):
        logging.info("Showing break overlay")
        self.root.after(0, self.overlay.show)

    def hide_break(self):
        logging.info("Hiding break overlay")
        self.root.after(0, self.overlay.hide)
        self.timer.start_work()

    def exit_app(self):
        logging.info("Exiting application")
        self.timer.stop()
        if self.icon:
            self.icon.stop()
        self.root.quit()
        os._exit(0)

    def on_closing(self):
        logging.debug("Window close event triggered")
        self.exit_app()

    def update_menu(self):
        logging.debug("Updating system tray menu")
        if self.icon:
            state = "Break" if self.timer.is_break_time else "Work"
            remaining_time = time.strftime(
                "%M:%S", time.gmtime(self.timer.remaining_time)
            )
            self.icon.menu = pystray.Menu(
                pystray.MenuItem(
                    f"{state} time remaining: {remaining_time}", lambda: None
                ),
                pystray.MenuItem("Settings", self.show_settings),
                pystray.MenuItem("Exit", self.exit_app),
            )
            self.icon.update_menu()

    def show_settings(self):
        logging.info("Showing settings window")
        self.root.after(
            0, lambda: SettingsWindow(self.root, self.config, self.timer, False)
        )

    def run(self):
        logging.debug("Running EyeBreakApp")
        image = Image.new("RGB", (64, 64), color=(73, 109, 137))
        menu = pystray.Menu(
            pystray.MenuItem(
                f"Work time remaining: {time.strftime('%M:%S', time.gmtime(self.config['WORK_DURATION'] * 60))}",
                lambda: None,
            ),
            pystray.MenuItem("Settings", self.show_settings),
            pystray.MenuItem("Exit", self.exit_app),
        )
        self.icon = pystray.Icon("eye_break", image, "Eye Break App", menu)

        self.timer.start()
        threading.Thread(target=self.icon.run, daemon=True).start()

        self.root.mainloop()


def main():
    logging.debug("Starting main function")
    ctypes.windll.kernel32.CreateMutexW(None, 1, MUTEX_NAME)
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        logging.warning("The application is already running.")
        messagebox.showwarning("Warning", "The application is already running.")
        sys.exit(0)

    config = load_config()
    if not os.path.exists(CONFIG_FILE):
        logging.info("Initial setup required")
        print("Initial setup", CONFIG_FILE)
        root = tk.Tk()
        root.withdraw()
        SettingsWindow(root, config, None, is_initial_setup=True)
        root.mainloop()
        save_config(config)
        add_to_startup()

    app = EyeBreakApp()
    app.run()


if __name__ == "__main__":
    main()
