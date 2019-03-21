from datetime import timedelta, datetime, tzinfo
import utctz
        
class EventParser:
    def __init__(self, db_connection, google_sheets_writer):
        self.db_connection = db_connection
        self.google_sheets_writer = google_sheets_writer

    def read_entry(self, entry, system, cmdr=None):
        if entry['event'] == 'FSDJump':
            self.read_system(entry)
        elif entry['event'] == 'Docked':
            self.read_system(entry)
        elif entry['event'] == 'MissionCompleted':
            self.read_mission_completed(entry,cmdr)
        elif entry['event'] == 'RedeemVoucher':
            self.read_voucher(entry, system)

    def read_voucher(self, entry, system):
        if(entry['event'] == 'RedeemVoucher' and entry['Type']=='bounty'):
            bounty_transactions = []
            for f in entry['Factions']:
                if f['Faction'] != '':
                    bt = {}
                    self.db_connection.add_faction(f['Faction'])
                    bt['faction_id'] = self.db_connection.get_faction_id(f['Faction'])
                    bt['system_address'] = self.db_connection.get_system_address(system)
                    bt['amount']=f['Amount']
                    ts = datetime.strptime(entry['timestamp'],'%Y-%m-%dT%H:%M:%SZ')
                    bt['ts'] = ts.replace(tzinfo=utctz.utc)
                    tick_date = ts - timedelta(hours=13, minutes=30)
                    bt['tick_date'] = tick_date.replace(hour=0, minute=0,second=0)
                    bounty_transactions.append(bt)
            self.db_connection.write_bounty_transactions(bounty_transactions)
            
    def read_system(self, entry):
        self.db_connection.add_system(entry['SystemAddress'], entry['StarSystem'])        
        
    def read_mission_completed(self, entry, cmdr=None):
        if entry['event'] == 'MissionCompleted':
            faction_effects = []
            for fe in entry['FactionEffects']:
                
                faction = fe['Faction']
                self.db_connection.add_faction(faction)
                faction_id = self.db_connection.get_faction_id(faction)
                infs = fe['Influence']
                for inf in infs:
                    effect = {}
                    effect['faction_id'] = faction_id
                    effect['system_address'] = inf['SystemAddress']
                    trend = inf['Trend']
                    inf_change = inf['Influence']
                    multiplier = -1
                    if trend=='UpGood': 
                        multiplier = 1
                    effect['inf_change'] = multiplier*len(inf_change)
                    ts = datetime.strptime(entry['timestamp'],'%Y-%m-%dT%H:%M:%SZ')
                    effect['ts'] = ts.replace(tzinfo=utctz.utc)
                    tick_date = ts - timedelta(hours=13, minutes=30)
                    effect['tick_date'] = tick_date.replace(hour=0, minute=0,second=0)
                    faction_effects.append(effect)
                    #if cmdr<>None:
                    #    google_sheets_writer.write_faction_effects(ts, cmdr, db_connection.get_system(inf['SystemAddress']), faction, effect['inf_change'], "NotImplementedError")
                        
            self.db_connection.write_faction_effects(faction_effects)
        