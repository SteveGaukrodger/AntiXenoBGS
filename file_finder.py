import os
from datetime import datetime

class FileFinder:
    def find_files(self, start_date, directory):
        paths = [directory + '\\' + f for f in os.listdir(directory) if f.endswith('.log')]
        files = [p for p in paths if datetime.utcfromtimestamp(os.path.getmtime(p)) > start_date]
        return files