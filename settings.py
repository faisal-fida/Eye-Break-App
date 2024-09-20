from tkinter import messagebox
import tkinter as tk
import threading
import time
from tkinter import ttk

from config import save_config, FONT, OVERLAY_TEXT


class SettingsWindow:
    def __init__(self, parent, config, timer, is_initial_setup=False):
        self.parent = parent
        self.config = config
        self.timer = timer
        self.is_initial_setup = is_initial_setup
        self.window = tk.Toplevel(parent)
        self.window.title("Eye Break Settings")
        self.window.geometry("400x250")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="Break Duration (seconds):").pack(pady=5)
        self.break_entry = tk.Entry(self.window)
        self.break_entry.insert(0, str(self.config["BREAK_DURATION"]))
        self.break_entry.pack(pady=5)

        tk.Label(self.window, text="Work Duration (seconds):").pack(pady=5)
        self.work_entry = tk.Entry(self.window)
        self.work_entry.insert(0, str(self.config["WORK_DURATION"]))
        self.work_entry.pack(pady=5)

        save_button = tk.Button(self.window, text="Save", command=self.save_settings)
        save_button.pack(pady=10)

        self.message_label = tk.Label(self.window, text="", fg="green")
        self.message_label.pack(pady=5)

        if self.is_initial_setup:
            tk.Label(
                self.window,
                text="Welcome to Eye Break App!",
                font=("Arial", 14, "bold"),
            ).pack(pady=10)
            tk.Label(
                self.window, text="Please set your preferred break and work durations."
            ).pack()
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def save_settings(self):
        try:
            self.config["BREAK_DURATION"] = int(self.break_entry.get())
            self.config["WORK_DURATION"] = int(self.work_entry.get())
            save_config(self.config)
            self.message_label.config(text="Settings have been saved.")
            if not self.is_initial_setup and self.timer:
                self.timer.restart_timer()
            messagebox.showinfo("Settings Saved", "Settings have been saved.")
            self.window.destroy()

        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Please enter valid numbers for durations."
            )

    def on_closing(self):
        if messagebox.askokcancel(
            "Quit", "Do you want to quit without saving settings?"
        ):
            self.window.quit()


class Overlay:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.overlay = None
        self.progressbar = None

    def create(self):
        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.geometry(
            f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0"
        )
        self.overlay.configure(bg="black")

        label = tk.Label(
            self.overlay, text=OVERLAY_TEXT, fg="white", bg="black", font=FONT
        )
        label.pack(expand=True)

        style = ttk.Style(self.overlay)
        style.theme_use("default")
        style.configure(
            "black.Horizontal.TProgressbar", background="white", troughcolor="black"
        )

        self.progressbar = ttk.Progressbar(
            self.overlay,
            orient="horizontal",
            length=200,
            mode="determinate",
            style="black.Horizontal.TProgressbar",
        )
        self.progressbar.pack(expand=True)

    def show(self):
        self.root.after(0, self.create)
        self.root.after(0, self.update_progressbar)

    def update_progressbar(self):
        if self.overlay is None or not self.overlay.winfo_exists():
            return
        if self.progressbar["value"] < 100:
            self.progressbar["value"] += 100 / self.config["BREAK_DURATION"]
            self.root.after(1000, self.update_progressbar)
        else:
            self.hide()

    def hide(self):
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()
        self.overlay = None


class Timer:
    def __init__(self, break_callback, update_menu_callback, config):
        self.break_callback = break_callback
        self.update_menu_callback = update_menu_callback
        self.config = config
        self.is_break_time = False
        self.remaining_time = self.config["WORK_DURATION"]
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            self.remaining_time = (
                self.config["WORK_DURATION"]
                if not self.is_break_time
                else self.config["BREAK_DURATION"]
            )
            while self.remaining_time > 0 and not self.stop_event.is_set():
                time.sleep(1)
                self.remaining_time -= 1
                self.update_menu_callback()

            if not self.stop_event.is_set():
                self.break_callback()

    def stop(self):
        self.stop_event.set()

    def restart_timer(self):
        self.stop()
        self.stop_event.clear()
        self.is_break_time = False
        self.remaining_time = self.config["WORK_DURATION"]
        threading.Thread(target=self.run, daemon=True).start()
