import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from tkinter.filedialog import askdirectory
from utils import RecentFiles
import json
import os


class OutputSection(ttk.Frame):
    def __init__(self, parent, main):
            super().__init__(parent)
            self.main = main
            self.default_dir = RecentFiles(1)
            self.output_location = main.output_location

            self.init_output_location()
            self.create_widgets()
            self.create_layout()
            

    
    def browse(self):
        dir_path = askdirectory(initialdir="/",
        title="Select Directory")
        self.output_location.set(dir_path)
        self.save_output_location()


    def init_output_location(self):
        if not self.output_location.get(): # probably useless check
            self.output_location.set('/')

        with open("saves/save.json", "r") as f:
            data = json.load(f)
            self.output_location.set(data["default_output_location"][0])
        

    def save_output_location(self):
        if not self.output_location.get():
            return
         
        save_data = {}
        if os.path.exists("saves/save.json"):
            with open("saves/save.json", "r") as savefile:
                save_data = json.load(savefile)

        # Update the default_output_location key
        self.default_dir.add_file(self.output_location.get())
        save_data["default_output_location"] = self.default_dir.get_files()

        # Save updated data back to the file
        with open("saves/save.json", "w") as savefile:
            json.dump(save_data, savefile, indent=4)

        print(f'Default output directory set to {self.default_dir.get_files()}')
          

    def create_widgets(self):
        self.output_label = ttk.Label(self, text = 'Output Directory: ', font = 'Calibri 12')
        self.output_input = ttk.Entry(self, textvariable = self.output_location)
        self.output_button = ttk.Button(self, text = 'Browse', command = self.browse)
          
          

    def create_layout(self):
        self.output_label.pack(side = 'left', padx = 10)
        self.output_input.pack(side = 'left', ipadx = 40)
        self.output_button.pack(side = 'left')
          