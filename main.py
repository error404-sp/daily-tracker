import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, GdkPixbuf, Notify
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
        self.set_default_size(400, 170)

        # Create main vertical layout
        layoutbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        layoutbox.set_size_request(400, -1)
        self.add(layoutbox)

        switcher_wrapper = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        switcher_wrapper.set_size_request(400, -1)  # 👈 Set width here
        layoutbox.pack_start(switcher_wrapper, False, False, 0)

        # Create StackSwitcher (tab-like control)
        switcher = Gtk.StackSwitcher()
        # layoutbox.pack_start(switcher, False, False, 0)

        # Create Stack (holds page content)
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(300)
        switcher.set_stack(stack)
        layoutbox.pack_start(stack, True, True, 0)
        switcher.set_halign(Gtk.Align.FILL)
        stack.set_halign(Gtk.Align.FILL)
        switcher.set_hexpand(True)
        stack.set_hexpand(True)
        switcher_wrapper.pack_start(switcher, True, True, 0)  # 👈 Allow filling wrapper

        
        # Tracker
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10, margin=10)
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
        
        stack.add_titled(vbox, "tracker", "Tracker")

        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        stack.add_titled(settings_box, "settings", "Settings")
        self.get_settings_tab(settings_box)


        # notification = Notify.Notification.new(
        #     "Hey there!", "This is your GTK3 notification", "dialog-information"
        # )
        # notification.set_timeout(3000)
        # notification.show()

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
            # check if notif enabled
            if self.notif_checkbox.get_active():
                GLib.timeout_add(self.settings.reminder_time * 60000, self.notify)
        else:
            date = datetime.now().strftime("%d %b %Y")
            self.state.end_session(date)
            self.session_label.set_text(f"Total sessions: {self.state.session_count}")
            self.prev_date_label.set_markup(f"<span size='8000'><b>Last session on:</b> {self.state.last_session}</span>")
            self.log_session(self.start_time, datetime.now(), self.state.session_seconds)
            
    def notify(self):
        notification = Notify.Notification.new(f"You've been focused for {self.settings.reminder_time} mins.\n Time for a break?")
        notification.set_timeout(3000)
        notification.show()
    
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

    def get_settings_tab(self, settings_box):
        settings_box.set_border_width(10)
        section_label = Gtk.Label()
        section_label.set_markup('<b>Notifications</b>')
        section_label.set_xalign(0.1)
        settings_box.pack_start(section_label, False, False, 0)
        
        self.notif_checkbox = Gtk.CheckButton(label="Enable notifications")
        self.notif_checkbox.set_margin_start(15)
        self.notif_checkbox.set_active(self.settings.enable_notif)  # Default state
        self.notif_checkbox.connect("toggled", self.on_notif)
        settings_box.pack_start(self.notif_checkbox, False, False, 0)

        low_timebox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        low_timebox.set_margin_start(15)
        low_time_label  = Gtk.Label(label="Remind me after (in mins):  ")
        low_time_label.set_xalign(0.1)
        low_timebox.pack_start(low_time_label, False, False, 0)
        self.low_time_input = Gtk.Entry()
        self.low_time_input.set_text(f"{self.settings.reminder_time}")
        self.low_time_input.set_width_chars(4)
        self.low_time_input.connect("changed", self.on_remind_change)
        low_timebox.pack_start(self.low_time_input, False, False, 0)
        settings_box.pack_start(low_timebox, False, False, 0)

        high_timebox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin=5)
        high_timebox.set_margin_start(15)
        high_time_label  = Gtk.Label(label="Session timeout after (in mins): ")
        high_time_label.set_xalign(0.1)
        high_timebox.pack_start(high_time_label, False, False, 0)
        self.high_time_input = Gtk.Entry()
        self.high_time_input.set_text(f"{self.settings.session_timeout}")
        self.high_time_input.connect("changed", self.on_timeout_change)
        self.high_time_input.set_width_chars(4)
        high_timebox.pack_start(self.high_time_input, False, False, 0)
        settings_box.pack_start(high_timebox, False, False, 0)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        settings_box.pack_start(separator, False, True, 0)

        activity_section_label = Gtk.Label()
        activity_section_label.set_markup('<b>Activity</b>')
        activity_section_label.set_xalign(0.1)
        settings_box.pack_start(activity_section_label, False, False, 0)
        activity_checkbox = Gtk.CheckButton(label="Show my last activity")
        activity_checkbox.set_margin_start(15)
        activity_checkbox.set_active(self.settings.show_activity)  # Default state
        activity_checkbox.connect("toggled", self.on_last_activity)
        settings_box.pack_start(activity_checkbox, False, False, 0)



    def on_notif(self, checkbox):
        state = checkbox.get_active()
        self.settings.update_notif(state)
        if(state):
            Notify.init("DailyTracker")

    def on_last_activity(self, checkbox):
        state = checkbox.get_active()
        self.settings.update_activity(state)

    def on_remind_change(self, text):
        val = text.get_text().strip()
        updated_input = int(val) if val.isdigit() else 0
        self.settings.update_remindtime(updated_input)

    def on_timeout_change(self, text):
        val = text.get_text().strip()
        updated_input = int(val) if val.isdigit() else 0
        self.settings.update_timeout(updated_input);     

win = DailyTracker()
icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
if os.path.exists(icon_path):
    win.set_icon_from_file(icon_path)
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
