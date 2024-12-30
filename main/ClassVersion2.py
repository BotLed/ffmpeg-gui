import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from tkinter.filedialog import askopenfilename

import subprocess as subp
import json
from utils import RecentFiles


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
        self.output_location = tk.StringVar(value = 'C:/Users/AV000/Downloads')
        

        # Load Save Data
        self.recent_files.load_files()

        # widgets
        self.create_widgets()

        self.init_keybinds()

        # run
        self.mainloop()

    def create_widgets(self):
        self.menu = Menu(self, self.file_extension, self.file_path) # Menu
        self.config(menu=self.menu)

        self.title = Title(self) # Title

        self.main = Main(self, self.file_path, self.recent_files, self.flags) # Notebook with tabs

    
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

        command.append(f'{self.output_location.get()}/output.{self.file_extension.get()}' )

        print(command)
        
        
        try:
            subp.run(command, check=True)
        except subp.CalledProcessError as e:
            print(f"Error while executing command: {e}")

    
    def init_keybinds(self):
        self.bind('<Control-KeyPress-Return>', self.convert)
        self.bind('<Control-Shift-BackSpace>', lambda event: self.quit())


class Menu(tk.Menu):
    def __init__(self, parent, file_extension, file_path):
        super().__init__(parent)
        self.file_extension = file_extension
        self.file_path = file_path
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
        with open("saves/save.json", "r") as f:
                data = json.load(f)
            
        for file in data["recent_files"]:
            # f = file used to create a default argument and take value of file, without it each command will link to last read file
            self.recent_file_menu.add_command(label = file, 
                                              command = lambda f = file: self.file_path.set(f))



class Title(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        self.title = ttk.Label(self, text = 'FFMPEG GUI', font = 'Calibri 24 bold')
    
    def create_layout(self):
        self.pack()
        self.title.pack(padx = 10)



class Main(ttk.Notebook): 
    def __init__(self, parent, filepath, recent_files, flags):
        super().__init__(parent)
        self.file_path = filepath
        self.recent_files = recent_files
        self.flags = flags

        self.create_widgets()
        self.create_layout()


    def update_flag(self, flag_name, flag_value):
        if not flag_value:
            return
        
        # YIKES, make this cleaner PLEASE
        #TODO add check for empty flag
        if flag_name == '-vf width' or flag_name == '-vf height':
            if '-vf' not in self.flags:
                self.flags['-vf'] = ['-1'] * 2 # -1 because it maintains aspect ratio, yes it sucks I will fix, 2 because thats max length

            if flag_name == '-vf width':
                self.flags['-vf'][0] = flag_value
            else:
                self.flags['-vf'][1] = flag_value

            print(f'Final -vf flag: {self.flags['-vf']}')
            return


        self.flags[flag_name] = flag_value
        print(f"Flag '{flag_name}' updated to: {flag_value}")


    def create_widgets(self):
        self.basic_tab = ttk.Frame(self)
        self.advanced_tab = ttk.Frame(self)

        self.file_section = FileInputSection(self.basic_tab, self)
        self.duration_section = DurationSection(self.basic_tab, self)
        self.scale_section = ScaleSection(self.basic_tab, self)


    def create_layout(self):
        self.pack(fill = 'both', pady = 10)
        #self.basic_tab.pack()
        #self.advanced_tab.pack()
    
        self.add(self.basic_tab, text = 'Basic')
        self.add(self.advanced_tab, text = 'Advanced')

        self.file_section.pack(fill = 'x', pady = 10)
        self.duration_section.pack(fill= 'x', pady = 20)
        self.scale_section.pack(fill = 'x', pady = 20)



class FileInputSection(ttk.Frame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.main = main
        self.file_path = main.file_path
        self.recent_files = main.recent_files
        self.start_time = tk.StringVar(value = '0')

        self.create_widgets()
        self.create_layout()
        self.init_traces()

    def init_traces(self):
        self.file_path.trace_add("write", lambda *args: (self.main.update_flag("-i", self.file_path.get()), self.save_file()))
        self.start_time.trace_add("write", lambda *args: self.main.update_flag("-ss", self.start_time.get()))

    
    def browse(self):
        filepath = askopenfilename(initialdir="/",
        title="Select File", filetypes=(("Video Files",("*.mp4", "*.mkv")),("All Files","*.*")))
        self.file_path.set(filepath)

    
    def save_file(self):
        if not self.file_path.get(): # check for empty file (since constantly updated)
            return
        
        self.recent_files.add_file(self.file_path.get())  # Add new file
        files = self.recent_files.get_files()  # Get the updated list
        with open("saves/save.json", "w") as savefile:  # Save back to the file
            json.dump({"recent_files": files}, savefile, indent=4)

    def create_widgets(self):
        self.file_path_label = ttk.Label(self, text = 'File Path: ', font = 'Calibri 12')
        self.file_path_button = ttk.Button(self, text = 'Browse', command = self.browse)
        self.file_path_input = ttk.Entry(self, textvariable = self.file_path)

        self.start_label = ttk.Label(self, text = 'Start Time: ', font = 'Calibri 13')
        self.start_input = ttk.Entry(self, textvariable = self.start_time)
        self.startlock_button = ttk.Button(self, text = 'Lock', command = lambda: print(f"PLACEHOLDER: Start Time locked at {self.start_time.get()}"))

    def create_layout(self):
        self.file_path_label.pack(side = 'left', padx = 10)
        self.file_path_input.pack(side = 'left', ipadx = 40)
        self.file_path_button.pack(side = 'left')

        self.start_label.pack(side='left', padx = (60,10))
        self.start_input.pack(side = 'left', ipadx = 40)
        self.startlock_button.pack(side = 'left', ipadx = 7)



class DurationSection(ttk.Frame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.main = main
        self.duration_time = tk.StringVar()
        self.fps = tk.StringVar()

        self.create_widgets()
        self.create_layout()
        self.init_traces()


    def init_traces(self):
        self.duration_time.trace_add("write", lambda *args: self.main.update_flag("-t", self.duration_time.get()))
        self.fps.trace_add("write", lambda *args: self.main.update_flag("-r", self.fps.get()))


    def create_widgets(self):
        self.duration_label = ttk.Label(self, text = 'Duration: ', font = 'Calibri 12')
        self.duration_input = ttk.Entry(self, textvariable = self.duration_time)
        self.durationlock_button = ttk.Button(self, text = 'Lock', command = lambda: print(f"PLACEHOLDER: Duration Time locked at {self.duration_time.get()}"))

        self.fps_label = ttk.Label(self, text = 'FPS: ', font = 'Calibri 12')
        self.fps_input = ttk.Entry(self, textvariable = self.fps)
        self.fps_button = ttk.Button(self, text = 'Lock', command = lambda: print(f"PLACEHOLDER: FPS locked at {self.fps.get()}"))
    
    
    def create_layout(self):
        self.duration_label.pack(side = 'left', padx = 10)
        self.duration_input.pack(side = 'left', ipadx = 40)
        self.durationlock_button.pack(side = 'left', ipadx = 7)

        self.fps_label.pack(side = 'left', padx = 60)
        self.fps_input.pack(side = 'left', ipadx = 40)
        self.fps_button.pack(side = 'left', ipadx = 7)


class ScaleSection(ttk.Frame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.main = main   
        self.video_width = tk.StringVar()
        self.video_height = tk.StringVar()

        self.create_widgets()
        self.create_layout()
        self.init_traces()


    def init_traces(self):
        self.video_width.trace_add("write", lambda *args: self.main.update_flag("-vf width", self.video_width.get()))
        self.video_height.trace_add("write", lambda *args: self.main.update_flag("-vf height", self.video_height.get()))

    def create_widgets(self):
        self.scale_label = ttk.Label(self, text = 'Scale: ', font = 'Calibri 12')
        self.scale_width_input = ttk.Entry(self, textvariable = self.video_width)
        self.X_label = ttk.Label(self, text = 'X', font = 'Calibri 12')
        self.scale_height_input = ttk.Entry(self, textvariable = self.video_height)
        self.scaleh_button = ttk.Button(self, text = 'Lock', command = print(f"PLACEHOLDER: Height locked at {self.video_height.get()}"))
        self.scalew_button = ttk.Button(self, text = 'Lock', command = print(f"PLACEHOLDER: Width locked at {self.video_width.get()}"))


    def create_layout(self):
        self.scale_label.pack(side = 'left', padx = 12)
        self.scale_width_input.pack(side = 'left', ipadx = 40, padx = (17, 0))
        self.scalew_button.pack(side = 'left', ipadx = 8)
        self.X_label.pack(side = 'left', padx = 24)
        self.scale_height_input.pack(side = 'left', ipadx = 40)
        self.scaleh_button.pack(side = 'left', ipadx = 8)

    
         



App('FFmpeg-GUI', (815,500))