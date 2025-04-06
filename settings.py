import json;
import os;

SETTINGS_FILE = os.path.expanduser('~/.dailytracker_config.json')
STATE_FILE = os.path.expanduser('~/.dailytracker_state.json')

class Settings: 
    def __init__(self):
        self.username = self.store_or_load_user()
    
    def store_or_load_user(self):
        if(os.path.exists(SETTINGS_FILE)):
            with open(SETTINGS_FILE, "r") as file:
                data = json.load(file)
                self.username = data.get("username", "User")
                return  self.username
            
        else:
            self.username = input('Enter Username: ')
            config = {
                "username": self.username,
            }
            state_config= {
                'focus_time': 0,
                'session_count': 0,
            }
            with open(SETTINGS_FILE, "w") as file:
                json.dump(config, file, indent=4)

            with open(STATE_FILE, "w") as file:
                json.dump(state_config, file, indent=4)

            return self.username

