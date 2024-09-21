import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import sys
from config import save_config, OVERLAY_TEXT


class SettingsWindow:
    def __init__(self, parent, config, timer, is_initial_setup=False):
        self.parent = parent
        self.config = config
        self.timer = timer
        self.is_initial_setup = is_initial_setup
        self.window = tk.Toplevel(parent)
        self.window.title("Eye Break Settings")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        self.create_widgets()
        self.apply_styles()

    def create_widgets(self):
        # Create a main frame
        main_frame = ttk.Frame(self.window, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Welcome to Eye Break App!",
            font=("Segoe UI", 18, "bold"),
            foreground="#2c3e50",
        )
        title_label.pack(pady=(0, 10))

        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Set your break and work durations. You can change these later via the tray icon."
            if self.is_initial_setup
            else "Set your break and work durations.",
            wraplength=600,
            justify=tk.CENTER,
        )
        desc_label.pack(pady=(0, 20))

        # Break duration frame
        break_frame = ttk.Frame(main_frame)
        break_frame.pack(fill=tk.X, pady=10)
        ttk.Label(break_frame, text="Break Duration (seconds)").pack(
            padx=(0, 10), pady=5
        )
        self.break_entry = ttk.Entry(break_frame, width=10)
        self.break_entry.insert(0, str(self.config["BREAK_DURATION"]))
        self.break_entry.pack(padx=(0, 10), pady=5)

        # Work duration frame
        work_frame = ttk.Frame(main_frame)
        work_frame.pack(fill=tk.X, pady=10)
        ttk.Label(work_frame, text="Work Duration (minutes)").pack(padx=(0, 10), pady=5)
        self.work_entry = ttk.Entry(work_frame, width=10)
        self.work_entry.insert(0, str(self.config["WORK_DURATION"]))
        self.work_entry.pack(padx=(0, 10), pady=5)

        # Save button
        save_button = ttk.Button(
            main_frame, text="Save", command=self.save_settings, style="Accent.TButton"
        )
        save_button.pack(pady=10)

        # Message label
        self.message_label = ttk.Label(main_frame, text="", foreground="green")
        self.message_label.pack(pady=10)

        if self.is_initial_setup:
            note_label = ttk.Label(
                main_frame,
                text="Note: Research suggests taking 20-second breaks every 20 minutes reduce eye strain.",
                wraplength=500,
                justify=tk.CENTER,
                font=("Segoe UI", 10, "italic"),
            )
            note_label.pack(pady=(20, 0))

        if self.is_initial_setup:
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def apply_styles(self):
        self.window.tk.call("source", "azure.tcl")
        self.window.tk.call("set_theme", "light")

        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 12))
        style.configure("TEntry", font=("Segoe UI", 12))

        # Custom style for the save button
        style.configure("Accent.TButton", background="#3498db", foreground="white")
        style.map("Accent.TButton", background=[("active", "#2980b9")])

    def save_settings(self):
        try:
            break_duration = int(self.break_entry.get())
            work_duration = int(self.work_entry.get())

            if break_duration < 20:
                self.show_error("Break duration should be at least 20 seconds.")
                return

            if work_duration < 1:
                self.show_error("Work duration should be at least 1 minute.")
                return

            if work_duration < break_duration / 60:
                self.show_error("Work duration should be greater than break duration.")
                return

            self.config["BREAK_DURATION"] = break_duration
            self.config["WORK_DURATION"] = work_duration
            save_config(self.config)
            self.show_success("Settings have been saved.")

            if not self.is_initial_setup and self.timer:
                self.timer.restart_timer()
            else:
                self.window.after(2000, self.window.destroy)
                if self.is_initial_setup:
                    self.parent.quit()
        except ValueError:
            self.show_error("Please enter valid numbers for durations.")

    def show_error(self, message):
        self.message_label.config(text=message, foreground="red")

    def show_success(self, message):
        self.message_label.config(text=message, foreground="green")

    def on_closing(self):
        if messagebox.askokcancel(
            "Quit", "Do you want to quit without saving settings?"
        ):
            self.parent.quit()
            self.window.destroy()
            sys.exit(0)


class Overlay:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.overlay = None
        self.progressbar = None
        self.countdown_label = None
        self.remaining_time = 0

    def create(self):
        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.geometry(
            f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0"
        )
        self.overlay.configure(bg="#2c3e50")

        main_frame = tk.Frame(self.overlay, bg="#2c3e50")
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        label = tk.Label(
            main_frame,
            text=OVERLAY_TEXT,
            fg="#ecf0f1",
            bg="#2c3e50",
            font=("Segoe UI", 32, "bold"),
            wraplength=800,
            justify=tk.CENTER,
        )
        label.pack(pady=(0, 30))

        self.countdown_label = tk.Label(
            main_frame, text="", fg="#ecf0f1", bg="#2c3e50", font=("Segoe UI", 24)
        )
        self.countdown_label.pack(pady=(0, 20))

        self.progressbar = ttk.Progressbar(
            main_frame,
            orient="horizontal",
            length=400,
            mode="determinate",
            style="Horizontal.TProgressbar",
        )
        self.progressbar.pack()

        style = ttk.Style(self.overlay)
        style.theme_use("default")
        style.configure(
            "Horizontal.TProgressbar",
            thickness=10,
            troughcolor="#34495e",
            background="#3498db",
        )

    def show(self):
        self.remaining_time = self.config["BREAK_DURATION"]
        self.root.after(0, self.create)
        self.root.after(0, self.update_progressbar)

    def update_progressbar(self):
        if self.overlay is None or not self.overlay.winfo_exists():
            return
        if self.remaining_time > 0:
            self.progressbar["value"] = (
                1 - self.remaining_time / self.config["BREAK_DURATION"]
            ) * 100
            self.countdown_label.config(text=f"Time remaining: {self.remaining_time}s")
            self.remaining_time -= 1
            self.root.after(1000, self.update_progressbar)
        else:
            self.hide()

    def hide(self):
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()
        self.overlay = None
        self.root.after(0, self.on_overlay_closed)


class Timer:
    def __init__(self, break_callback, update_menu_callback, config):
        self.break_callback = break_callback
        self.update_menu_callback = update_menu_callback
        self.config = config
        self.is_break_time = False
        self.remaining_time = self.config["WORK_DURATION"] * 60
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            self.remaining_time = (
                self.config["WORK_DURATION"] * 60
                if not self.is_break_time
                else self.config["BREAK_DURATION"]
            )
            while self.remaining_time > 0 and not self.stop_event.is_set():
                time.sleep(1)
                self.remaining_time -= 1
                self.update_menu_callback()

            if not self.stop_event.is_set():
                self.break_callback()
                time.sleep(self.config["BREAK_DURATION"])
                self.is_break_time = False

    def stop(self):
        self.stop_event.set()

    def restart_timer(self):
        self.stop()
        self.stop_event.clear()
        self.is_break_time = False
        self.remaining_time = self.config["WORK_DURATION"] * 60
        threading.Thread(target=self.run, daemon=True).start()
