import tkinter as tk
from tkinter import messagebox
import threading
import time
import pystray
from PIL import Image
import ctypes
import os
import sys

from config import load_config, save_config, add_to_startup, CONFIG_FILE, MUTEX_NAME
from settings import SettingsWindow, Overlay, Timer


class EyeBreakApp:
    def __init__(self):
        self.config = load_config()
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.overlay = Overlay(self.root, self.config)
        self.timer = Timer(self.show_break, self.update_menu, self.config)
        self.icon = None

    def show_break(self):
        self.timer.is_break_time = True
        self.root.after(0, self.overlay.show)
        # Schedule hiding the overlay after the break duration
        self.root.after(self.config["BREAK_DURATION"] * 1000, self.hide_break)

    def hide_break(self):
        self.overlay.hide()
        self.timer.is_break_time = False

    def exit_app(self):
        self.timer.stop()
        if self.icon:
            self.icon.stop()
        self.root.quit()
        os._exit(0)

    def on_closing(self):
        self.exit_app()

    def update_menu(self):
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
        self.root.after(0, lambda: SettingsWindow(self.root, self.config, self.timer))

    def run(self):
        image = Image.new("RGB", (64, 64), color=(73, 109, 137))
        menu = pystray.Menu(
            pystray.MenuItem(
                f"Work time remaining: {time.strftime(
            "%M:%S", time.gmtime(self.config["WORK_DURATION"] * 60)
        )}",
                lambda: None,
            ),
            pystray.MenuItem("Settings", self.show_settings),
            pystray.MenuItem("Exit", self.exit_app),
        )
        self.icon = pystray.Icon("eye_break", image, "Eye Break App", menu)

        timer_thread = threading.Thread(target=self.timer.run)
        timer_thread.daemon = True
        timer_thread.start()

        threading.Thread(target=self.icon.run, daemon=True).start()

        self.root.mainloop()


def main():
    ctypes.windll.kernel32.CreateMutexW(None, 1, MUTEX_NAME)
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        messagebox.showwarning("Warning", "The application is already running.")
        sys.exit(0)

    config = load_config()
    if not os.path.exists(CONFIG_FILE):
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
