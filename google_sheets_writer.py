#import json
#import gspread
#from oauth2client.service_account import ServiceAccountCredentials



class GoogleSheetsWriter:
    def __init__(self, dir):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        #self.credentials = ServiceAccountCredentials.from_json_keyfile_name(dir + '/creds.json', self.scope)
        #self.file = gspread.authorize(self.credentials) # authenticate with Google
        #self.sheet = self.file.open("AXI-BGS").worksheet("Missions") # open sheet

    def write_faction_effect(self, timestamp, cmdr_name, system_name, faction_name, inf_change, mission_type):
        #self.sheet.append_row([timestamp, cmdr_name, system_name, faction_name, inf_change, mission_type])
        return None