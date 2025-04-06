class Time:
    def __init__(self, secs):
        self.hrs = int(secs / 3600)
        self.mins = int(secs % 3600 / 60)
        self.seconds = int(secs % 60)