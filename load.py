import Tkinter as tk
import sys
import sqlite3
import os
import json
from datetime import timedelta, datetime, tzinfo

from config import config
import myNotebook as nb
import pickle
import ttk
import entry_lookup
from event_parser import EventParser
from db_connection import DbConnection
from file_finder import FileFinder
db_connection = None
event_parser = None
this = sys.modules[__name__]
conn = None

def get_plugin_dir():
    appdata = os.getenv('LOCALAPPDATA') + '\\EDMarketConnector\\plugins'
    plugin_base = os.path.basename(os.path.dirname(__file__))
    return appdata + '\\' + plugin_base
    
def close_connection():
    global conn
    conn.close()

    
def init_database():
    global conn
    global db_connection
    global event_parser
    appdata = get_plugin_dir() + '\\axi.db'
    conn = sqlite3.connect(appdata)
    #Todo: move this to the db_connection class
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS systems (address INTEGER PRIMARY KEY, name VARCHAR(50) UNIQUE);')
    c.execute('CREATE TABLE IF NOT EXISTS factions (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(50) UNIQUE);')
    c.execute('CREATE TABLE IF NOT EXISTS faction_effects (id INTEGER PRIMARY KEY AUTOINCREMENT, influence_effect INTEGER, faction_id INTEGER, system_address INTEGER, timestamp TEXT, tick_date TEXT, FOREIGN KEY(faction_id) REFERENCES factions(id),FOREIGN KEY(system_address) REFERENCES system(address));')
    c.execute('CREATE TABLE IF NOT EXISTS voucher_transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, type VARCHAR(15), faction_id INTEGER, system_address INTEGER, amount INTEGER, timestamp TEXT, tick_date TEXT, FOREIGN KEY(faction_id) REFERENCES factions(id),FOREIGN KEY(system_address) REFERENCES system(address));')
    c.execute('INSERT OR IGNORE INTO systems (address, name) VALUES (?,?)',[2007863562898,'Pleiades Sector IH-V c2-7'])
    c.execute('INSERT OR IGNORE INTO factions (name) VALUES (?)',['Anti Xeno Initiative'])
    conn.commit()
    db_connection = DbConnection(conn)
    event_parser = EventParser(db_connection)
    
def copy_text():

    sel = this.listbox.curselection()
    lines = []
    if(len(sel) == 0):
        lines = [str(s) for s in this.listbox.get(0, tk.END)]
    else:
        lines = [str(this.listbox.get(s)) for s in sel]
    text = '\n'.join(lines)
    text = str.format('```{0: <25}{1: >25}\n{2}```', this.faction_name.get(),this.system_name.get(), text)
    
    this.listbox.clipboard_clear()
    this.listbox.clipboard_append(text)
    
def plugin_app(parent):

    frame = nb.Frame(parent)
    top_frame = nb.Frame(frame)
    middle_frame = nb.Frame(frame)
    bottom_frame = nb.Frame(frame)
    faction_label = nb.Label(top_frame, textvariable=this.faction_name)
    system_label = nb.Label(top_frame, textvariable=this.system_name)
    copy_button = nb.Button(top_frame, text='Copy', command=copy_text)
    faction_label.grid(row=0,column=0)
    system_label.grid(row=0,column=1)
    copy_button.grid(row=0,column=3)
    top_frame.grid(row=0)
    bottom_frame.grid(row=2)
    
    scroll_bar = tk.Scrollbar(bottom_frame)
    listbox = tk.Listbox(bottom_frame, height=5, width=50)
    scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.pack(side=tk.LEFT, fill=tk.Y)
    
    scroll_bar.config(command=listbox.yview)
    listbox.config(yscrollcommand=scroll_bar.set)
    this.listbox = listbox
    
    return (frame)

def update_faction_effects():
    missions = this.db_connection.get_faction_effects()
    bounties = this.db_connection.get_bounty_effects()
    effects = {}
    for m in missions:
        date = m[0][:10]
        e = effects.get(date, {})
        e['Missions'] = str(m[1])
        effects[date] = e
    for b in bounties:
        date = b[0][:10]
        e = effects.get(date, {})
        e['Bounties'] = str(b[1])
        effects[date] = e
    this.listbox.config(state=tk.NORMAL)
    
    this.listbox.delete(0,tk.END)
    for date in sorted(effects.iterkeys(), reverse=True):
        e = effects[date]
        m = e.get('Missions','0')
        b = e.get('Bounties','0')
        this.listbox.insert(tk.END, str.format('{}:{: >5} miss. inf.  {: >5} bounties', date, m, b))

    
def journal_entry(cmdr, is_beta, system, station, entry, state):
    event_parser.read_entry(entry, system)
    update_faction_effects()
                

def plugin_start(plugin_dir):
    '''
    Load this plugin into EDMC
    '''
    print 'I am loaded! My plugin folder is {}'.format(plugin_dir.encode('utf-8'))
    init_database()
    if(config.get("AXI_BGS_FactionName")==None): config.set('AXI_BGS_FactionName', 'Anti Xeno Initiative')
    if(config.get("AXI_BGS_SystemName")==None): config.set('AXI_BGS_SystemName', 'Pleiades Sector IH-V c2-7')
    this.faction_name = tk.StringVar(value=config.get("AXI_BGS_FactionName"))	# Retrieve saved value from config
    this.system_name = tk.StringVar(value=config.get("AXI_BGS_SystemName"))	# Retrieve saved value from config
    
    return 'AXI BGS'
   
def plugin_stop():
    '''
    EDMC is closing
    '''
    close_connection()
    print 'Farewell cruel world!'
    
def scrape_history():
    db_connection.clear_faction_effects()
    db_connection.clear_voucher_transactions()
    finder = FileFinder()
    logdir = config.get('journaldir') or config.default_journal_dir
    current_system = None
    for f in finder.find_files(datetime(2019,01,01), logdir):
        with open(f, 'r') as fp:
            for cnt, line in enumerate(fp):
                try:
                    entry = json.loads(line)
                    if(entry['event']=='Docked'):
                        current_system = entry['StarSystem']
                    event_parser.read_entry(entry, current_system)
                except:
                    print 'AXI BGS: Could not read line' , line
    this.system_el.set_data(db_connection.get_system_names())        
    this.faction_el.set_data(db_connection.get_faction_names())        
        
    
def plugin_prefs(parent, cmdr, is_beta):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    global listbox
    frame = nb.Frame(parent)
    nb.Label(frame, text="Faction Name:").grid(row=0,column=0)
    nb.Label(frame, text="System Name").grid(row=0,column=1)
    
    faction_entry = nb.Entry(frame,width=35)
    faction_entry.grid(row=2,column=0)
    
    faction_listbox = tk.Listbox(frame,width=35)
    faction_listbox.grid(row=3,column=0)
    this.faction_el = entry_lookup.EntryLookup(faction_entry,faction_listbox, db_connection.get_faction_names(),this.faction_name.get())
    
    system_entry = nb.Entry(frame,width=35)
    system_entry.grid(row=2,column=1)
    

    system_listbox = tk.Listbox(frame,width=35)
    system_listbox.grid(row=3,column=1)
    
    this.system_el = entry_lookup.EntryLookup(system_entry,system_listbox, db_connection.get_system_names(),this.system_name.get())
    b = nb.Button(frame, text="Scrape history", command=scrape_history)
    b.grid(row=4, column=1)
    nb.Label(frame,text="Warning, this will take a while. Shut down ED before running").grid(row=4,column=0)
    return frame
   
def prefs_changed(cmdr, is_beta):
   """
   Save settings.
   """
   this.faction_name.set(this.faction_el.get_selected())
   this.system_name.set(this.system_el.get_selected())
   config.set('AXI_BGS_FactionName', this.faction_name.get())
   config.set('AXI_BGS_SystemName', this.system_name.get())	
   update_faction_effects()