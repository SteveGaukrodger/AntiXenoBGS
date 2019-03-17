from config import config

class DbConnection:
    def __init__(self, connection):
        self.connection = connection
    
    def add_faction(self, faction_name):
        cursor = self.connection.cursor()
        cursor.execute('INSERT OR IGNORE INTO factions (name) VALUES (?);', [faction_name])
        self.connection.commit()

    def add_system(self, system_address, system_name):
        cursor = self.connection.cursor()
        cursor.execute('INSERT OR IGNORE INTO systems (address, name) VALUES (?,?);', [system_address, system_name])
        self.connection.commit()
        
    def get_faction_id(self, faction_name):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id FROM factions WHERE name = ?', [faction_name])
        return cursor.fetchone()[0]
        
    def get_system_address(self, system_name):
        cursor = self.connection.cursor()
        cursor.execute('SELECT address FROM systems WHERE name = ?', [system_name])
        return cursor.fetchone()[0]
    
    def write_bounty_transactions(self, bounty_transactions):
        cursor = self.connection.cursor()
        for bt in bounty_transactions:
            cursor.execute('INSERT INTO voucher_transactions (faction_id, type, system_address, amount, timestamp, tick_date) VALUES (?,?,?,?,?,?)',
                        [bt['faction_id'], 'BOUNTY', bt['system_address'], bt['amount'], bt['ts'], bt['tick_date']])
        self.connection.commit()
    
    def write_faction_effects(self, faction_effects):
        cursor = self.connection.cursor()
        for fe in faction_effects:
            cursor.execute('INSERT INTO faction_effects (faction_id, system_address, influence_effect, timestamp, tick_date) VALUES (?,?,?,?, ?)',
                        [fe['faction_id'], fe['system_address'], fe['inf_change'], fe['ts'], fe['tick_date']])
        self.connection.commit()
    
    def get_system(self, system_address):
        cursor = self.connection.cursor()
        cursor.execute('SELECT name FROM systems WHERE address = ?', [system_address])
        return cursor.fetchone()[0]
    
    def get_bounty_effects(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT tick_date, COUNT(type) FROM voucher_transactions ' + 
            'INNER JOIN factions ON factions.id=voucher_transactions.faction_id ' +
            'INNER JOIN systems ON systems.address=voucher_transactions.system_address ' +
            'WHERE systems.name=? AND factions.name=? ' +
            'GROUP BY tick_date ORDER BY tick_date DESC LIMIT 30', [config.get('AXI_BGS_SystemName'),config.get('AXI_BGS_FactionName')]) 
            #DESC used to be ASC, but works better as DESC. Left sub in place in case I want to change it back some day
        return cursor.fetchall()
        
    def get_faction_effects(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT tick_date, sum(influence_effect) FROM faction_effects ' + 
            'INNER JOIN factions ON factions.id=faction_effects.faction_id ' +
            'INNER JOIN systems ON systems.address=faction_effects.system_address ' +
            'WHERE systems.name=? AND factions.name=? ' +
            'GROUP BY tick_date ORDER BY tick_date DESC LIMIT 30', [config.get('AXI_BGS_SystemName'),config.get('AXI_BGS_FactionName')]) 
            #DESC used to be ASC, but works better as DESC. Left sub in place in case I want to change it back some day
        return cursor.fetchall()
        
    def get_faction_names(self):
        c = self.connection.cursor()
        c.execute('SELECT name FROM factions;')
        return [str(r[0]) for r in c.fetchall()]

    def get_system_names(self):
        c = self.connection.cursor()
        c.execute('SELECT name FROM systems;')
        return [str(r[0]) for r in c.fetchall()]
        
    def clear_faction_effects(self):
        c = self.connection.cursor()
        c.execute('DELETE FROM faction_effects;')
        self.connection.commit()
        
    def clear_voucher_transactions(self):
        c = self.connection.cursor()
        c.execute('DELETE FROM voucher_transactions;')
        self.connection.commit()