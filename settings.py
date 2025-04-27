import json;
import os;

SETTINGS_FILE = os.path.expanduser('~/.dailytracker_config.json')

class Settings: 
    def __init__(self):
        settings = self.store_or_load()
        self.username = settings.username
        self.enable_notif = settings.enable_notif
        self.reminder_time = settings.reminder_time
        self.session_timeout = settings.session_timeout
        self.show_activity = settings.show_activity
    
    def store_or_load(self):
        if(os.path.exists(SETTINGS_FILE)):
            with open(SETTINGS_FILE, "r") as file:
                data = json.load(file)
                self.username = data.get("username", "User")
                self.enable_notif = data.get("enable_notif", False)
                self.reminder_time = data.get("reminder_time", 60)
                self.session_timeout = data.get("session_timeout", 120)
                self.show_activity = data.get("show_activity", False)
                return self
            
        else:
            self.username = input('Enter Username: ')
            self.enable_notif = False
            self.reminder_time = 60
            self.session_timeout = 120
            self.show_activity = False
            config = {
                "username": self.username,
                "enable_notif": self.enable_notif,
                "reminder_time": self.reminder_time,
                "session_timeout": self.session_timeout,
                "show_activity": self.show_activity
            }
            with open(SETTINGS_FILE, "w") as file:
                json.dump(config, file, indent=4)


            return self

    def save(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump({
                "username": self.username,
                "enable_notif": self.enable_notif,
                "reminder_time": self.reminder_time,
                "session_timeout": self.session_timeout,
                "show_activity" : self.show_activity
            }, f)

    def update_remindtime(self,value):
        self.reminder_time = value
        self.save()
    
    def update_timeout(self,value):
        self.session_timeout = value
        self.save()       

    def update_notif(self, value):
        self.enable_notif = value
        self.save()

    def update_activity(self, value):
        self.show_activity = value
        self.save()