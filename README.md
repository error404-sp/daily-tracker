# ![icon (1)](https://github.com/user-attachments/assets/43e4ada7-b714-4752-ae8e-0767277b8cc7)Daily Tracker

A simple GTK-based desktop app for tracking work sessions: clocking in/out, recording focus time, sending notifications, and logging everything into a CSV file.

![image](https://github.com/user-attachments/assets/c3059551-11ec-49f7-840c-bd952c5a1cb5)
![image](https://github.com/user-attachments/assets/f4c33a07-17ed-423d-9f26-7cd8dc9b4583)

## ✨ Features

- 🕑 **Clock In / Clock Out**  
  Start and end your focus sessions easily.

- 🔔 **Desktop Notifications**  
  Receive system notifications for break reminders.

- 📝 **CSV Logging**  
  Automatically records session start/end times and durations into a `.csv` file.

- ⏳ **Focus Time Tracking**  
  Accurately record total time spent working.

- ⌛ **Timers with GLib**  
  Smooth live timers using GLib without freezing the UI.

- 📈 **Lightweight and Minimal**  
  Pure desktop app — no cloud syncing, no account needed.

---
## 📦 Requirements

- Python 3.6+
- GTK 3 (`PyGObject`)
- GLib (from PyGObject)
- libnotify (for system notifications)

### Install Dependencies

Install via `pip`:

```bash
pip install PyGObject
```
Or install system libraries on Ubuntu/Debian:
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-glib-2.0 gir1.2-notify-0.7
```
---
## 🚀 Quick Start

```bash
git clone https://github.com/error404-sp/daily-tracker.git
cd daily-tracker
python3 main.py
```

### ⚡ Important Notes
⚠️ Linux Only:
This application is built for Linux desktop environments.
It uses GTK 3, GLib, and libnotify — all of which are native to Linux.
Running on Windows or macOS is not officially supported and may require heavy manual setup.

