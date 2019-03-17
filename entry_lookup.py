import Tkinter as tk
import config


class EntryLookup:
    
    def __init__(self, entry, listbox, data, selected_value):
        self.entry = entry
        self.listbox = listbox
        self.original_data = data
        self.selected_value = tk.StringVar()
        self.selected_value.set(selected_value)
        self.entry.configure(textvariable=self.selected_value)
        #entry.pack()
        self.entry.bind('<KeyRelease>', self.on_keyrelease)
        listbox.bind('<Double-Button-1>', self.on_select)
        listbox.bind('<<ListboxSelect>>', self.on_select)
        
        #self.entry.text=
    
    def on_keyrelease(self, event):

        # get text from entry
        value = event.widget.get()
        value = value.strip().lower()

        # get data from test_list
        if value == '':
            data = self.original_data
        else:
            data = []
            for item in self.original_data:
                if value in item.lower():
                    data.append(item)                

        # update data in listbox
        self.listbox_update(data)


    def listbox_update(self, data):
        
        # delete previous data
        self.listbox.delete(0, 'end')

        # sorting data 
        data = sorted(data, key=str.lower)

        # put new data
        for item in data:
            self.listbox.insert('end', item)

    def on_select(self, event):
        self.selected_value.set(event.widget.get(event.widget.curselection()))

    def get_selected(self):
        return self.selected_value.get()

    def set_data(self, data):
        self.original_data = data