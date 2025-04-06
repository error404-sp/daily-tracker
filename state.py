import json;
import os;

STATE_FILE = os.path.expanduser('~/.dailytracker_state.json')

class StateManager:
    def __init__(self):
        self.focus_seconds = 0
        self.session_count = 0
        self.timer_running = False
        self.is_focus_time = False
        self.session_seconds = 0
        self.load()

    def load(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                self.focus_seconds = data.get("focus_seconds", self.focus_seconds)
                self.session_count = data.get("session_count", self.session_count)
                self.is_focus_time = data.get("is_focus_time", self.is_focus_time)

    def save(self):
        with open(STATE_FILE, "w") as f:
            json.dump({
                "focus_seconds": self.focus_seconds,
                "session_count": self.session_count,
                "is_focus_time": self.is_focus_time,
            }, f)
    
    def stop_tracking(self):
        self.timer_running = False
        self.is_focus_time = False
        self.save()

    def end_session(self):
        self.timer_running = False
        self.session_count += 1
        self.save()

    def start_session(self):
        self.timer_running = True
        self.session_seconds = 0

    def update_focus_time(self):
        self.focus_seconds += 1
        self.session_seconds += 1

    def reset(self):
        self.focus_seconds = 0
        self.session_count = 0
        self.timer_running = False
        self.is_focus_time = True
        self.save()

