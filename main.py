import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf
from settings import Settings
from state import StateManager
from datetime import datetime
from util import Time
import csv
import time
import os

class DailyTracker(Gtk.Window):
    def __init__(self):
        self.settings = Settings()
        self.state = StateManager()
        super().__init__(title=f"{self.settings.username}'s Daily Tracker")
        self.csv_file = f"{self.settings.username.lower()}_focus_sessions.csv"
        self.set_default_size(400, 200)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10, margin=15)
        self.timer_label = Gtk.Label()
        self.session_label = Gtk.Label()
        self.start_time = 0
        self.update_time_labels(self.state.focus_seconds)
        self.session_label.set_text(f"Total sessions: {self.state.session_count}")
        vbox.pack_start(self.timer_label, False, False, 10)
        vbox.pack_start(self.session_label, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=10)
        hbox.set_halign(Gtk.Align.CENTER)  # Center the whole group
        hbox.set_valign(Gtk.Align.CENTER)

        # Start label
        end_label = Gtk.Label(label="End")
        hbox.pack_start(end_label, False, False, 0)

        # Switch
        self.switch = Gtk.Switch()
        self.switch.connect("notify::active", self.on_session_active)
        self.switch.set_active(False)
        self.switch.set_size_request(60, 30)
        self.switch.set_halign(Gtk.Align.CENTER)
        self.switch.set_valign(Gtk.Align.CENTER)
        hbox.pack_start(self.switch, False, False, 0)

        # End label
        start_label = Gtk.Label(label="Start")
        hbox.pack_start(start_label, False, False, 0)

        # popup description
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("add-note.svg", 16, 16)  # width, height in px
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        description_btn = Gtk.Button()
        description_btn.set_image(image)
        description_btn.set_always_show_image(True)
        description_btn.connect("clicked",self.on_popup)
        hbox.pack_start(description_btn, False, False, 0)

        vbox.pack_start(hbox, False, False, 0)
        if(len(self.state.last_session)):
            self.prev_date_label = Gtk.Label()
            self.prev_date_label.set_markup(f"<span size='8000'><b>Last session on:</b> {self.state.last_session}</span>")
            self.prev_date_label.set_xalign(1.0)
            vbox.pack_start(self.prev_date_label, False, False, 0)

        action_bar = Gtk.ActionBar()
        self.time_label = Gtk.Label(margin=10)
        now = datetime.now()
        self.time_label.set_markup(f"🕒 Now: <b>{now.strftime('%H:%M:%S')}</b>")
        action_bar.pack_start(self.time_label)
        
        hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # Start label
        day_label = Gtk.Label(label="Clock in / out ")
        hbox1.pack_start(day_label, False, False, 0)

        # Switch
        self.switch1 = Gtk.Switch()
        self.switch1.set_active(self.state.is_focus_time)
        self.switch1.connect("notify::active", self.on_focus_activate)
        
        self.switch1.set_size_request(60, 30)
        self.switch1.set_halign(Gtk.Align.CENTER)
        self.switch1.set_valign(Gtk.Align.CENTER)
        hbox1.pack_start(self.switch1, False, False, 0)
        action_bar.pack_end(hbox1)
        vbox.pack_end(action_bar, False, False, 0)
        
        self.add(vbox)

        GLib.timeout_add_seconds(1, self.update_time)


    def on_session_active(self, switch, gparam):
        if switch.get_active():
            self.start_time = datetime.now()
            if not self.state.is_focus_time:
                self.state.reset()
                self.update_time_labels(self.state.focus_seconds)
                self.switch1.set_active(self.state.is_focus_time)
                self.log_day_start(self.start_time) 
            self.state.start_session()
        else:
            date = datetime.now().strftime("%d %b %Y")
            self.state.end_session(date)
            self.session_label.set_text(f"Total sessions: {self.state.session_count}")
            self.prev_date_label.set_markup(f"<span size='8000'><b>Last session on:</b> {self.state.last_session}</span>")
            self.log_session(self.start_time, datetime.now(), self.state.session_seconds)
            
                
    def on_focus_activate(self, switch, gparam):
        if switch.get_active():
            self.state.reset()
            self.update_time_labels(self.state.focus_seconds)
            self.log_day_start(datetime.now()) 
        else:
            self.state.stop_tracking()
            self.switch.set_active(self.state.timer_running)
            self.log_day_end(datetime.now())
        self.session_label.set_text(f"Total sessions: {self.state.session_count}")
                           
    
    def update_time_labels(self, seconds):
        def_time = Time(seconds)
        self.timer_label.set_markup(f"<span size='20000' weight='bold'>Focus Time: {def_time.hrs:02}:{def_time.mins:02}:{def_time.seconds:02}</span>")
        
    
    def update_time(self):
        # update time
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.set_markup(f"🕒 Now: <b>{now}</b>")
        if(self.state.timer_running):
            self.state.update_focus_time()
            self.update_time_labels(self.state.focus_seconds)

        return True  # Keep the timer going

    def log_session(self,start, end, duration_seconds):
        with open(self.csv_file, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                writer.writerow(["S.No","Duration (HH:MM:SS)","Start Time" "End Time", "Description"])
            dur_str = time.strftime("%H:%M:%S", time.gmtime(duration_seconds))
            writer.writerow([
                self.state.session_count,
                dur_str,
                start.strftime("%H:%M:%S"),
                end.strftime("%H:%M:%S"),
                self.state.session_description
            ])

    def log_day_start(self, timestamp):
        with open(self.csv_file, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([])
            writer.writerow(["---- ","Clocked in at : ",f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}"," ----"])
            writer.writerow([])

    def log_day_end(self, timestamp):
        with open(self.csv_file, "a", newline="") as csvfile:
            def_time = Time(self.state.focus_seconds)
            writer = csv.writer(csvfile)
            writer.writerow([])
            writer.writerow(["----"," Clocked out at : ", f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}"," ----"])
            writer.writerow(["---- Focus Time :",f" {def_time.hrs:02}:{def_time.mins:02}:{def_time.seconds:02}" ,"Sessions: ", f"{self.state.session_count} ----"])
            writer.writerow([])
    
    def on_popup(self,widget):
        dialog = Gtk.Dialog(
            title="Session description",
            transient_for=self,
            flags=0,
        )
        dialog.set_default_size(350, 50)
        dialog.add_button(
            Gtk.STOCK_ADD, Gtk.ResponseType.ACCEPT,
        )

        entry = Gtk.Entry()
        entry.set_placeholder_text("Add session description")
        box = dialog.get_content_area()
        box.set_border_width(20)
        box.add(entry)
        dialog.show_all()

        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            self.state.update_description(entry.get_text())

        dialog.destroy()

win = DailyTracker()
icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
if os.path.exists(icon_path):
    win.set_icon_from_file(icon_path)
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
