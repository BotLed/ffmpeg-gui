import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from tkinter.filedialog import askopenfilename

import json
import subprocess as subp
import threading

class FileInputSection(ttk.Frame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.main = main
        self.file_path = main.file_path
        self.recent_files = main.recent_files
        self.start_time = tk.StringVar(value = '0')
        self.save_file_location = main.save_file_location
        self.screen_dimensions = main.screen_dimensions

        self.create_widgets()
        self.create_layout()
        self.init_traces()

    def init_traces(self):
        self.file_path.trace_add("write", lambda *args: (self.main.update_flag("-i", self.file_path.get()), self.save_file()))
        self.start_time.trace_add("write", lambda *args: self.main.update_flag("-ss", self.start_time.get()))


    # Added so you can just auto open the file you're working with since otherwise you have to manually find it and play it beforehand
    # TODO: add mpv to dependencies, 
    def open_file(self):
        def _open_file_in_thread():
            file_path = self.file_path.get()

            # I hate this
            screen_width = self.screen_dimensions[0]
            screen_height = self.screen_dimensions[1]

            # displays the video on the right hand side in the middle of the screen, int() because mpv will scream at me if I don't
            evil_command = f'{int(screen_width/2)}x{int(screen_height/1.5)}+{int(screen_width/2)}+{int((screen_height - screen_height/1.5) / 2)}' #TODO: add options for this
            print(f"Opening file: {file_path}")

            # --pause so that it doesn't auto play
            command = ['mpv', f'--geometry={evil_command}','--pause', file_path]

            try:
                subp.run(command, check=True)
                print("File opened in paused state")
            except subp.CalledProcessError as e:
                print(f"Error while executing command: {e}")
            

        # Run the function in a new thread to prevent blocking the UI
        thread = threading.Thread(target=_open_file_in_thread)
        thread.start()
    


    def browse(self):
        filepath = askopenfilename(initialdir="/",
        title="Select File", filetypes=(("Video Files",("*.mp4", "*.mkv", "*.mov")),("All Files","*.*")))
        self.file_path.set(filepath)

    
    def save_file(self):
        if not self.file_path.get(): # check for empty file (since constantly updated)
            return
        
        save_data = {}
        with open(self.save_file_location, "r") as savefile:
            save_data = json.load(savefile)

        # Update the recent_files key
        self.recent_files.add_file(self.file_path.get())
        save_data["recent_files"] = self.recent_files.get_files()

        # Save updated data back to the file
        with open(self.save_file_location, "w") as savefile:
            json.dump(save_data, savefile, indent=4)

    def create_widgets(self):
        self.file_path_label = ttk.Label(self, text = 'File Path: ', font = 'Calibri 12')
        self.file_path_input = ttk.Entry(self, textvariable = self.file_path)
        self.file_path_button = ttk.Button(self, text = 'Browse', command = self.browse)
        self.open_file_button = ttk.Button(self, text = 'Open', command = self.open_file)

        self.start_label = ttk.Label(self, text = 'Start Time: ', font = 'Calibri 13')
        self.start_input = ttk.Entry(self, textvariable = self.start_time)
        self.startlock_button = ttk.Button(self, text = 'Lock', command = lambda: print(f"PLACEHOLDER: Start Time locked at {self.start_time.get()}"))

    def create_layout(self):
        self.file_path_label.pack(side = 'left', padx = 10)
        self.file_path_input.pack(side = 'left', ipadx = 40)
        self.file_path_button.pack(side = 'left', ipadx = 1)
        self.open_file_button.pack(side = 'left', padx = 2)

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
        self.scalew_button.pack(side = 'left', ipadx = 7)
        self.X_label.pack(side = 'left', padx = 24)
        self.scale_height_input.pack(side = 'left', ipadx = 40)
        self.scaleh_button.pack(side = 'left', ipadx = 7)


class SpeedSection(ttk.Frame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.main = main
        self.speed = tk.StringVar(value = '1.0')

        self.create_widgets()
        self.create_layout()
        self.init_traces()

    def init_traces(self):
        self.speed.trace_add("write", lambda *args: self.main.update_flag("-vf speed", self.speed.get()))

    def create_widgets(self):
        self.speed_label = ttk.Label(self, text = 'Speed: ', font = 'Calibri 12')
        self.speed_input = ttk.Entry(self, textvariable = self.speed)
        self.speedlock_button = ttk.Button(self, text = 'Lock', command = lambda: print(f"PLACEHOLDER: Duration Time locked at {self.speed.get()}"))

    def create_layout(self):
        self.speed_label.pack(side = 'left', padx = 10)
        self.speed_input.pack(side = 'left', ipadx = 40, padx = (16, 0))
        self.speedlock_button.pack(side = 'left', ipadx = 7)