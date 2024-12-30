import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from tkinter.filedialog import askopenfilename

import subprocess as subp
import json
from utils import RecentFiles

def browse():
    fpath = askopenfilename(initialdir="/",
      title="Select File", filetypes=(("Video Files",("*.mp4", "*.mkv")),("All Files","*.*")))
    f_path.set(fpath)


def print_extension():
    print(f"Selected conversion changed to : {file_extension.get()}")


def convert(event=None):
    command = ['ffmpeg']

    if '-i' in flags and flags['-i']:
        command.extend(["-i", flags['-i']])
    if "-ss" in flags and flags["-ss"]:  # start time
        command.extend(["-ss", flags["-ss"]])
    if "-t" in flags and flags["-t"]:  # duration
        command.extend(["-t", flags["-t"]])
    if "-r" in flags and flags["-r"]:  # duration
        command.extend(["-r", flags["-r"]])

    command.append(f'{output_location.get()}/output.{file_extension.get()}' )

    print(command)
    
    
    try:
        subp.run(command, check=True)
    except subp.CalledProcessError as e:
        print(f"Error while executing command: {e}")
        

def save_file(f_path):
    if not f_path: # check for empty file (since constantly updated)
        return
    recent_files.add_file(f_path)  # Add new file
    files = recent_files.get_files()  # Get the updated list
    with open("saves/save.json", "w") as f:  # Save back to the file
        json.dump({"recent_files": files}, f, indent=4)


def init_recent_files_menu():
    print("UHFIOEHF")
    with open("saves/save.json", "r") as f:
        data = json.load(f)
    
    for file in data["recent_files"]:
        recent_file_menu.add_command(label = file, command = lambda: f_path.set(file))

# Update flags whenever the StringVar changes
def update_flag(var_name, var_value):
    flags[var_name] = var_value
    print(f"Flag '{var_name}' updated to: {var_value}")



flags = {}
recent_files = RecentFiles(max_files=5)
recent_files.load_files()  # Load existing files on startup


window = ttk.Window()
window.geometry('815x500')
window.minsize(500, 500)

f_path = tk.StringVar()
start_time = tk.StringVar(value = '0')
duration_time = tk.StringVar()
fps = tk.StringVar()
video_width = tk.StringVar()
video_height = tk.StringVar()
output_location = tk.StringVar(value = 'C:/Users/AV000/Downloads')

# TODO: FIX THIS CONSTANT UPDATING OR ADD CHECKS EVERYWHERE, THIS SUCKS
# Bind callbacks to StringVar changes
f_path.trace_add("write", lambda *args: (
    update_flag("-i", f_path.get()), 
    save_file(f_path.get())
    ))
start_time.trace_add("write", lambda *args: update_flag("-ss", start_time.get()))
duration_time.trace_add("write", lambda *args: update_flag("-t", duration_time.get()))
fps.trace_add("write", lambda *args: update_flag("-r", fps.get()))

# MENU
menu = tk.Menu(window)

# File Menu
file_menu = tk.Menu(menu, tearoff=False)
file_menu.add_command(label = 'Open', command = lambda : print('Open File'))
file_menu.add_command(label = 'Open', command = lambda : print('Open Recent'))
recent_file_menu = tk.Menu(file_menu, tearoff=False)
init_recent_files_menu() # initializes recent files submenu with data read from save


# Presets Menu
presets_menu = tk.Menu(menu, tearoff=False)
file_extension = tk.StringVar(value = 'mp4')
presets_menu.add_radiobutton(label = 'Convert to GIF', variable = file_extension, value = 'gif', command = print_extension)
presets_menu.add_radiobutton(label = 'Convert to MP4', variable = file_extension, value = 'mp4', command = print_extension)
presets_menu.add_radiobutton(label = 'Convert to MP3', variable = file_extension, value = 'mp3', command = print_extension)

# Help Menu
help_menu = tk.Menu(window, tearoff=False)
help_menu.add_command(label = 'New', command = lambda : print('New File'))

help_checkvalue = tk.StringVar()
help_menu.add_checkbutton(label = 'check', onvalue = 'on', offvalue= 'off', variable = help_checkvalue)


# NOTEBOOK
notebook = ttk.Notebook(window)
basic_tab = ttk.Frame(notebook)
advanced_tab = ttk.Frame(notebook)


# TITLE
title_frame = ttk.Frame(window)
title = ttk.Label(window, text = 'FFMPEG GUI', font = 'Calibri 24 bold')


# -- INPUT FRAME ROW 1 --
# FILE PATH
inputs_frame1 = ttk.Frame(basic_tab)
fpath_label = ttk.Label(inputs_frame1, text = 'File Path: ', font = 'Calibri 12')
fpath_button = ttk.Button(inputs_frame1, text = 'Browse', command = browse)
fpath_input = ttk.Entry(inputs_frame1, textvariable = f_path)

# START TIME
start_label = ttk.Label(inputs_frame1, text = 'Start Time: ', font = 'Calibri 13')

start_input = ttk.Entry(inputs_frame1, textvariable = start_time)
startlock_button = ttk.Button(inputs_frame1, text = 'Lock', command = print(f"PLACEHOLDER: Start Time locked at {start_time.get()}"))


# -- INPUT FRAME ROW 2 --
inputs_frame2 = ttk.Frame(basic_tab)
duration_label = ttk.Label(inputs_frame2, text = 'Duration: ', font = 'Calibri 12')
duration_input = ttk.Entry(inputs_frame2, textvariable = duration_time)
durationlock_button = ttk.Button(inputs_frame2, text = 'Lock', command = print(f"PLACEHOLDER: Duration Time locked at {duration_time.get()}"))


fps_label = ttk.Label(inputs_frame2, text = 'FPS: ', font = 'Calibri 12')
fps_input = ttk.Entry(inputs_frame2, textvariable = fps)
fps_button = ttk.Button(inputs_frame2, text = 'Lock', command = print(f"PLACEHOLDER: FPS locked at {fps.get()}"))


# -- SCALE INPUT ROW 3 --
inputs_frame3 = ttk.Frame(basic_tab)
scale_label = ttk.Label(inputs_frame3, text = 'Scale: ', font = 'Calibri 12')
scale_width_input = ttk.Entry(inputs_frame3, textvariable = video_width)
X_label = ttk.Label(inputs_frame3, text = 'X', font = 'Calibri 12')
scale_height_input = ttk.Entry(inputs_frame3, textvariable = video_height)
scaleh_button = ttk.Button(inputs_frame3, text = 'Lock', command = print(f"PLACEHOLDER: Height locked at {video_height.get()}"))
scalew_button = ttk.Button(inputs_frame3, text = 'Lock', command = print(f"PLACEHOLDER: Width locked at {video_width.get()}"))


# Test / Advanced
test_label = ttk.Label(advanced_tab, text = "Hello")





# LAYOUT

# menu
window.configure(menu = menu)
menu.add_cascade(label = 'File', menu = file_menu)
menu.add_cascade(label = 'Help', menu = help_menu)
menu.add_cascade(label = 'Presets', menu = presets_menu)
file_menu.add_cascade(label = 'Recent Files', menu = recent_file_menu)

# title
title_frame.pack()
title.pack(padx = 10)

# notebook
notebook.pack(fill = 'both', pady = 10)
basic_tab.pack()
advanced_tab.pack()
notebook.add(basic_tab, text = 'Basic')
notebook.add(advanced_tab, text = 'Advanced')

# input frame ROW 1
inputs_frame1.pack(fill = 'x', pady = 10)
# file path
fpath_label.pack(side = 'left', padx = 10)
fpath_input.pack(side = 'left', ipadx = 40)
fpath_button.pack(side = 'left')
# start time
start_label.pack(side='left', padx = (60,10))
start_input.pack(side = 'left', ipadx = 40)
startlock_button.pack(side = 'left', ipadx = 7)


# input frame ROW 2
inputs_frame2.pack(fill = 'x', pady = 20)
duration_label.pack(side = 'left', padx = 10)
duration_input.pack(side = 'left', ipadx = 40)
durationlock_button.pack(side = 'left', ipadx = 7)

fps_label.pack(side = 'left', padx = 60)
fps_input.pack(side = 'left', ipadx = 40)
fps_button.pack(side = 'left', ipadx = 7)


# input frame ROW 3
inputs_frame3.pack(fill = 'x', pady = 20)
scale_label.pack(side = 'left', padx = 12)
scale_width_input.pack(side = 'left', ipadx = 40, padx = (17, 0))
scalew_button.pack(side = 'left', ipadx = 8)
X_label.pack(side = 'left', padx = 24)
scale_height_input.pack(side = 'left', ipadx = 40)
scaleh_button.pack(side = 'left', ipadx = 8)


# ADVCANCED
test_label.pack()



# KEYBINDS
# Utility
window.bind('<Control-KeyPress-Return>', convert)
# Security
window.bind('<Control-Shift-BackSpace>', lambda event: window.quit())


window.mainloop()