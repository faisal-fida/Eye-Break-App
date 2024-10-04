import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import sys
import logging
from config import save_config, OVERLAY_TEXT

# Configure logging
logging.basicConfig(
    filename="eye_break_app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class SettingsWindow:
    def __init__(self, parent, config, timer, is_initial_setup=False):
        logging.debug("Initializing SettingsWindow")
        self.parent = parent
        self.config = config
        self.timer = timer
        self.is_initial_setup = is_initial_setup
        self.window = tk.Toplevel(parent)
        self.window.title("Eye Break Settings")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        self.create_widgets()
        try:
            self.apply_styles()
        except tk.TclError as e:
            logging.error("Theme file not found", exc_info=True)
            raise Exception(f"Theme file not found. Error: {e}")

    def create_widgets(self):
        logging.debug("Creating widgets for SettingsWindow")
        main_frame = ttk.Frame(self.window, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            main_frame,
            text="Welcome to Eye Break App!",
            font=("Segoe UI", 18, "bold"),
            foreground="#222324",
        )
        title_label.pack(pady=(0, 10))

        desc_label = ttk.Label(
            main_frame,
            text="Set your break and work durations. You can change these later via the tray icon."
            if self.is_initial_setup
            else "Set your break and work durations.",
            wraplength=600,
            justify=tk.CENTER,
        )
        desc_label.pack(pady=(0, 20))

        break_frame = ttk.Frame(main_frame)
        break_frame.pack(fill=tk.X, pady=10)
        ttk.Label(break_frame, text="Break Duration (seconds)").pack(
            padx=(0, 10), pady=5
        )
        self.break_entry = ttk.Entry(break_frame, width=10)
        self.break_entry.insert(0, str(self.config["BREAK_DURATION"]))
        self.break_entry.pack(padx=(0, 10), pady=5)

        work_frame = ttk.Frame(main_frame)
        work_frame.pack(fill=tk.X, pady=10)
        ttk.Label(work_frame, text="Work Duration (minutes)").pack(padx=(0, 10), pady=5)
        self.work_entry = ttk.Entry(work_frame, width=10)
        self.work_entry.insert(0, str(self.config["WORK_DURATION"]))
        self.work_entry.pack(padx=(0, 10), pady=5)

        save_button = ttk.Button(
            main_frame, text="Save", command=self.save_settings, style="Accent.TButton"
        )
        save_button.pack(pady=10)

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
        logging.debug("Applying styles to SettingsWindow")
        self.window.tk.call("source", "azure.tcl")
        self.window.tk.call("set_theme", "light")

        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 12))
        style.configure("TEntry", font=("Segoe UI", 12))

        style.configure("Accent.TButton", background="#3498db", foreground="white")
        style.map("Accent.TButton", background=[("active", "#2980b9")])

    def save_settings(self):
        logging.debug("Saving settings")
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
            logging.error("Invalid input for durations", exc_info=True)
            self.show_error("Please enter valid numbers for durations.")

    def show_error(self, message):
        logging.error(f"Error: {message}")
        self.message_label.config(text=message, foreground="red")

    def show_success(self, message):
        logging.info(f"Success: {message}")
        self.message_label.config(text=message, foreground="green")

    def on_closing(self):
        logging.debug("Closing SettingsWindow")
        if messagebox.askokcancel(
            "Quit", "Do you want to quit without saving settings?"
        ):
            self.parent.quit()
            self.window.destroy()
            sys.exit(0)


class Overlay:
    def __init__(self, root, config):
        logging.debug("Initializing Overlay")
        self.root = root
        self.config = config
        self.overlay = None
        self.remaining_time = 0
        self.update_job = None

    def create(self):
        logging.debug("Creating overlay window")
        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.geometry(
            f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0"
        )
        self.overlay.configure(bg="#222324")

        main_frame = tk.Frame(self.overlay, bg="#222324")
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        label = tk.Label(
            main_frame,
            text=OVERLAY_TEXT,
            fg="#ecf0f1",
            bg="#222324",
            font=("Segoe UI", 30, "bold"),
            wraplength=800,
            justify=tk.CENTER,
        )
        label.pack(pady=(0, 30))

    def show(self):
        logging.info("Showing overlay")
        self.remaining_time = self.config["BREAK_DURATION"]
        self.root.after(0, self.create)

    def hide(self):
        logging.info("Hiding overlay")
        if self.update_job:
            self.root.after_cancel(self.update_job)
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()
        self.overlay = None


class Timer:
    def __init__(
        self, break_callback, end_break_callback, update_menu_callback, config
    ):
        logging.debug("Initializing Timer")
        self.break_callback = break_callback
        self.end_break_callback = end_break_callback
        self.update_menu_callback = update_menu_callback
        self.config = config
        self.is_break_time = False
        self.remaining_time = self.config["WORK_DURATION"] * 60
        self.stop_event = threading.Event()
        self.timer_thread = None

    def run(self):
        logging.debug("Starting timer run loop")
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
                if not self.is_break_time:
                    logging.info("Starting break time")
                    self.is_break_time = True
                    self.break_callback()
                else:
                    logging.info("Ending break time")
                    self.is_break_time = False
                    self.end_break_callback()

    def start(self):
        logging.debug("Starting timer thread")
        self.timer_thread = threading.Thread(target=self.run, daemon=True)
        self.timer_thread.start()

    def stop(self):
        logging.debug("Stopping timer")
        self.stop_event.set()
        if self.timer_thread:
            self.timer_thread.join()

    def start_work(self):
        logging.debug("Starting work period")
        self.is_break_time = False
        self.remaining_time = self.config["WORK_DURATION"] * 60

    def restart_timer(self):
        logging.debug("Restarting timer")
        self.stop()
        self.stop_event.clear()
        self.start()
