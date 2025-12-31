
import tkinter as tk
import time
import threading
import os

# macOS built-in sounds
PRE_ALERT_SOUND = "/System/Library/Sounds/Submarine.aiff"
MAIN_ALARM_SOUND = "/System/Library/Sounds/Glass.aiff"

def play_sound(path, repeats=1, pause_between=0.5):
    for i in range(repeats):
        os.system(f"afplay '{path}'")
        if i < repeats - 1:
            time.sleep(pause_between)

class CountdownTimer:
    def __init__(self, parent, title, is_hour_format=False):
        self.frame = tk.LabelFrame(parent, text=title, padx=10, pady=10)
        self.frame.pack(padx=10, pady=5, fill="x")

        # Update input labels
        if is_hour_format:
            tk.Label(self.frame, text="Hours").grid(row=0, column=0)
            self.hours_entry = tk.Entry(self.frame, width=5)
            self.hours_entry.grid(row=0, column=1)

            tk.Label(self.frame, text="Minutes").grid(row=1, column=0)
            self.minutes_entry = tk.Entry(self.frame, width=5)
            self.minutes_entry.grid(row=1, column=1)
        else:
            tk.Label(self.frame, text="Minutes").grid(row=0, column=0)
            self.entry = tk.Entry(self.frame, width=8)
            self.entry.grid(row=0, column=1)

        tk.Label(self.frame, text="Pre-alert at (minutes):").grid(row=2, column=0)
        self.pre_alert_entry = tk.Entry(self.frame, width=8)
        self.pre_alert_entry.grid(row=2, column=1)

        self.toggle_btn = tk.Button(self.frame, text="Start", command=self.toggle)
        self.toggle_btn.grid(row=0, column=2, padx=5)

        self.reset_btn = tk.Button(self.frame, text="Reset", command=self.reset)
        self.reset_btn.grid(row=0, column=3, padx=5)

        self.label = tk.Label(self.frame, text="00:00", font=("Helvetica", 48))  # Larger countdown digits
        self.label.grid(row=3, column=0, columnspan=4, pady=5)

        self.running = False
        self.pre_alert_triggered = False
        self.main_alert_triggered = False
        self.remaining_time = 0  # Track remaining time

    def toggle(self):
        if self.running:
            self.running = False  # Pause the countdown
            self.toggle_btn.config(text="Unpause")  # Change button text to Unpause
        else:
            self.start()  # Start or resume the countdown
            self.toggle_btn.config(text="Pause")  # Change button text to Pause

    def start(self):
        if self.running:
            return

        try:
            # If it's the session, get hours and minutes input
            if hasattr(self, 'hours_entry'):
                hours = int(self.hours_entry.get()) if self.hours_entry.get() else 0
                minutes = int(self.minutes_entry.get()) if self.minutes_entry.get() else 0
                self.remaining_time = (hours * 3600) + (minutes * 60)  # Convert to seconds
            else:
                self.remaining_time = int(self.entry.get()) * 60  # Convert minutes to seconds
            
            # Convert pre-alert time from minutes to seconds
            self.pre_alert_seconds = int(self.pre_alert_entry.get()) * 60
        except ValueError:
            return

        self.running = True
        self.pre_alert_triggered = False
        self.main_alert_triggered = False

        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while self.running and self.remaining_time > 0:
            mins = self.remaining_time // 60
            secs = self.remaining_time % 60
            hours = mins // 60
            mins = mins % 60
            self.label.config(text=f"{hours:02d}:{mins:02d}:{secs:02d}")

            # Pre-alert at specified minutes (now in seconds)
            if not self.pre_alert_triggered and self.remaining_time == self.pre_alert_seconds:
                self.pre_alert_triggered = True
                threading.Thread(
                    target=play_sound,
                    args=(PRE_ALERT_SOUND, 2, 0.5),
                    daemon=True
                ).start()

            # Main alert at 0
            if self.remaining_time <= 0 and not self.main_alert_triggered:
                self.main_alert_triggered = True
                threading.Thread(
                    target=play_sound,
                    args=(MAIN_ALARM_SOUND, 3, 0.8),
                    daemon=True
                ).start()

            time.sleep(1)
            self.remaining_time -= 1  # Decrement remaining time

        self.running = False

    def reset(self):
        self.running = False
        self.remaining_time = 0  # Reset remaining time
        self.label.config(text="00:00")
        if hasattr(self, 'hours_entry'):
            self.hours_entry.delete(0, tk.END)
            self.minutes_entry.delete(0, tk.END)
        else:
            self.entry.delete(0, tk.END)
        self.pre_alert_entry.delete(0, tk.END)
        self.toggle_btn.config(text="Start")  # Reset toggle button to Start

class CountdownApp:
    def __init__(self, root):
        self.root = root
        root.title("Dual Countdown Timer")

        # Current time
        self.clock_label = tk.Label(root, font=("Helvetica", 16))  # Larger current time font
        self.clock_label.pack(pady=10)
        self.update_clock()

        # Session timer allowing both hours and minutes
        self.timer1 = CountdownTimer(root, "Session", is_hour_format=True)
        # Current Presentation timer
        self.timer2 = CountdownTimer(root, "Current Presentation", is_hour_format=False)

    def update_clock(self):
        now = time.strftime("%H:%M:%S")
        self.clock_label.config(text=f"Time: {now}")
        self.root.after(1000, self.update_clock)

# --- Run App ---
root = tk.Tk()
app = CountdownApp(root)
root.mainloop()
