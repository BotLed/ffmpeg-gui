import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk

import subprocess as subp
import json
from pathlib import Path

from utils import RecentFiles
from basic_sections import FileInputSection, DurationSection, ScaleSection, SpeedSection
from advanced_sections import OutputSection


#TODO: add actual checks for non-num values in the inputs
#TODO: add option to include -c flag in command to increase conversion speed -> copy the streams without re-encoding
#TODO: add option to disable speed up/slow down sync between audio and video
#TODO: add mute video option
#TODO: add feedback for actions, relying on terminal sucks
#TODO: changes empty values to become default values
#TODO: After getting basics implemented look at optimization

#NOTE: in current implementation, issues arise when trying to use simple and complex video filters, either always use complex
# or add some way to change between the video (IMPORTANT FOR AUDIO/VIDEO SPEED UP MATCHING)


class App(ttk.Window):
    DEFAULT_FILE_EXTENSION = 'mp4'

    def __init__(self, title, size):
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0], size[1])

        # Variables
        self.file_extension = tk.StringVar(value = self.DEFAULT_FILE_EXTENSION) 
        self.file_path = tk.StringVar()
        self.flags = {}
        self.recent_files = RecentFiles(max_files=5)
        self.recent_output_dirs = RecentFiles(max_files=5)
        self.output_location = tk.StringVar(value = '/')
        self.save_file_location = Path('saves/save.json').resolve()
        # I have no clue why I made this into a tuple, this is probably stupid and is gonna force me to do
        # screen_width =, screen_height =, a million times #TODO CHANGE
        self.screen_dimensions = (self.winfo_screenwidth(), self.winfo_screenheight()) 
        

        # Load Save Data
        self.recent_files.load_files()
        self.recent_output_dirs.load_files()

        # Setup
        self.create_widgets()
        self.init_keybinds()
        self.init_window_properties()

        self.mainloop()
        


    def create_widgets(self):
        self.menu = Menu(self, self.file_extension, self.file_path, self.save_file_location) # Menu
        self.config(menu=self.menu)

        # Removed title class and frame and put it here, frame seemed to be unecessary
        self.title = ttk.Label(self, text = 'FFMPEG GUI', font = 'Calibri 24 bold').pack(padx = 10)

        # look into just passing the entirety of App because this is probably going to get way longer
        self.main = Main(self, 
                         self.file_path, 
                         self.recent_files, 
                         self.flags, 
                         self.output_location,
                         self.save_file_location,
                         self.screen_dimensions) # Notebook with tabs
        

    def init_keybinds(self):
        self.bind('<Control-KeyPress-Return>', self.convert)
        self.bind('<Control-Shift-BackSpace>', lambda event: self.quit())
        self.bind('<Cont')


    def init_window_properties(self):
         #self.attributes('-topmost', True) #TODO: add toggle for this
        pass
       

    
    def convert(self, event=None):
        command = ['ffmpeg']

        if '-i' in self.flags and self.flags['-i']:
            command.extend(["-i", self.flags['-i']])
        if "-ss" in self.flags and self.flags["-ss"]:  # start time
            command.extend(["-ss", self.flags["-ss"]])
        if "-t" in self.flags and self.flags["-t"]:  # duration
            command.extend(["-t", self.flags["-t"]])
        if "-r" in self.flags and self.flags["-r"]:  # duration
            command.extend(["-r", self.flags["-r"]])
        if "-vf" in self.flags and self.flags["-vf"]: # Don't have to worry about no value at [vf][num] because default values are set
            # Yes its hardcoded and I hate it, as the number of -vf flags I need grows I'll probably change this
            #command.extend(["-vf", f'scale={self.flags["-vf"][0]}:{self.flags["-vf"][1]}'])
            
            # Matches audio speed up with video speed up without changing pitch: https://trac.ffmpeg.org/wiki/How%20to%20speed%20up%20/%20slow%20down%20a%20video
            # Uses: #-filter_complex "[0:v]setpts=<1/x>*PTS[v];[0:a]atempo=<x>[a]" -map "[v]" -map "[a]
            # This is horrible and I hate it, need checks for inputs and a ton of other stuff filter-wise IMMEDIATELY
            
            # for speeds higher than 2x, need multiple setpts flags
            command.extend(['-filter_complex', f'[0:v]scale={self.flags["-vf"][0]}:{self.flags["-vf"][1]}, setpts={1/float(self.flags["-vf"][2])}*PTS[v];[0:a]atempo={self.flags["-vf"][2]}[a]'])
            command.extend(['-map', '[v]'])
            command.extend(['-map', '[a]']) # GIFS don't support audio mapping, remove this for GIFS as well as [0:a]

        command.append(f'{self.output_location.get()}/output.{self.file_extension.get()}' )

        
        
        try:
            subp.run(command, check=True)
        except subp.CalledProcessError as e:
            print(f"Error while executing command: {e}")


class Menu(tk.Menu):
    def __init__(self, parent, file_extension, file_path, save_file):
        super().__init__(parent)
        self.file_extension = file_extension
        self.file_path = file_path
        self.save_file_location = save_file

        self.create_widgets()
        self.create_layout()
        


    def create_widgets(self):
        self.file_menu = tk.Menu(self, tearoff = False)
        self.file_menu.add_command(label = 'Open', 
                              command = lambda : print('Open File'))
        self.file_menu.add_command(label = 'New', 
                              command = lambda : print('New File'))   

        self.help_menu = tk.Menu(self, tearoff=False)
        self.help_menu.add_command(label="Help", command=lambda: print("Help function called"))

        self.presets_menu = tk.Menu(self, tearoff = False)
        self.presets_menu.add_radiobutton(label = 'Convert to GIF', variable = self.file_extension, value = 'gif')
        self.presets_menu.add_radiobutton(label = 'Convert to MP4', variable = self.file_extension, value = 'mp4')
        self.presets_menu.add_radiobutton(label = 'Convert to MP3', variable = self.file_extension, value = 'mp3')

        self.recent_file_menu = tk.Menu(self.file_menu, tearoff = False)
        self.init_recent_files_menu()
        
    

    def create_layout(self):
        self.add_cascade(label='File', menu = self.file_menu)  # Add file menu to the menu bar 
        self.add_cascade(label = 'Presets', menu = self.presets_menu)
        self.add_cascade(label = 'Help', menu = self.help_menu)
        self.file_menu.add_cascade(label = 'Recent Files', menu = self.recent_file_menu) 


    def init_recent_files_menu(self):
        with open(self.save_file_location, "r") as f:
                data = json.load(f)
            
        for file in data["recent_files"]:
            # f = file used to create a default argument and take value of file, without it each command will link to last read file
            self.recent_file_menu.add_command(label = file, 
                                              command = lambda f = file: self.file_path.set(f))



class Main(ttk.Notebook): 
    def __init__(self, parent, filepath, recent_files, flags, output_location, save_file, screen_dimensions):
        super().__init__(parent)
        self.file_path = filepath
        self.recent_files = recent_files
        self.flags = flags
        self.output_location = output_location
        self.save_file_location = save_file
        self.screen_dimensions = screen_dimensions

        self.create_widgets()
        self.create_layout()


    def update_flag(self, flag_name, flag_value):
        if not flag_value:
            return
        
        # YIKES, make this cleaner PLEASE
        #TODO add check for empty flag
        vf_flags = ['-vf width', '-vf height', '-vf speed']
        if flag_name in vf_flags:
            if '-vf' not in self.flags:
                # -2 because it maintains aspect ratio while keeping values divisible by 2 (requirement)
                self.flags['-vf'] = ['-2'] * len(vf_flags) # len() because max allowable amount of flags

            # Directs what position to put flag value at based on flag
            if flag_name == '-vf width':
                self.flags['-vf'][0] = flag_value
            if flag_name == '-vf height':
                self.flags['-vf'][1] = flag_value
            else:
                self.flags['-vf'][2] = flag_value

            print(f'Final -vf flag: {self.flags['-vf']}')
            return


        self.flags[flag_name] = flag_value
        print(f"Flag '{flag_name}' updated to: {flag_value}")


    def create_widgets(self):
        self.basic_tab = ttk.Frame(self)
        self.advanced_tab = ttk.Frame(self)

        # Basic Tab Widgets
        self.file_section = FileInputSection(self.basic_tab, self)
        self.duration_section = DurationSection(self.basic_tab, self)
        self.scale_section = ScaleSection(self.basic_tab, self)
        self.speed_section = SpeedSection(self.basic_tab, self)

        # Advcanced Tab Widgets
        self.output_section = OutputSection(self.advanced_tab, self)


    def create_layout(self):
        self.pack(fill = 'both', pady = 10)
    
        self.add(self.basic_tab, text = 'Basic')
        self.add(self.advanced_tab, text = 'Advanced')

        self.file_section.pack(fill = 'x', pady = 10)
        self.duration_section.pack(fill= 'x', pady = 20)
        self.scale_section.pack(fill = 'x', pady = 20)
        self.speed_section.pack(fill = 'x', pady = 20)

        self.output_section.pack(fill = 'x', pady = 10)

         
App('FFmpeg-GUI', (865,500))


