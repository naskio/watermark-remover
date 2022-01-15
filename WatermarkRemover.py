from tkinter import Tk, Button, Entry, StringVar, END, RIGHT, X, LEFT, Text, DISABLED, CENTER, BooleanVar, Checkbutton
from tkinter import filedialog
from pathlib import Path
from main import main, generate_output_path
from scripts.version import __version__
from typing import Optional

BASE_DIR = Path(__file__).parent


def log_clear():
    log_txt_area.delete(1.0, END)


def log_write(text):
    log_txt_area.insert(END, text)
    log_txt_area.insert(END, '\n')


def open_files():
    input_files = filedialog.askopenfilenames(
        initialdir=str(BASE_DIR),
        title="Open Word or PDF file",
        filetypes=[("Word Documents", ".docx"), ("PDF Files", ".pdf"), ("Image Files", ".png"),
                   ("Image Files", ".jpg"), ("Image Files", ".jpeg"), ],
    )
    log_clear()
    if input_files:  # file selected
        output_dir = get_output_dir(BASE_DIR)
        if output_dir:
            output_dir_path = Path(output_dir)
            if not output_dir_path.exists():
                output_dir_path.mkdir(parents=True)
            for input_file in input_files:
                input_path = Path(input_file)
                if not input_path.exists():
                    log_write(f"File {input_path} does not exist")
                elif str(input_path.suffix).lower() not in ('.docx', '.pdf', '.png', '.jpg', '.jpeg'):
                    log_write(f"File {input_path} is not a Word, PDF or Image file")
                else:  # processing
                    log_write(f'Input: {input_file}')
                    try:
                        output_file = output_dir_path / (input_path.stem + f"_generated{input_path.suffix}")
                        log_write(f'Output: {output_file}')
                        log_write("Processing...")
                        if use_color_replace.get():
                            log_write(f"use color replace = {use_color_replace.get()}")
                        output_file = main(input_file, str(output_file), use_color_replace.get())
                        log_write(f'File has been saved successfully to: {output_file}')
                    except Exception as e:
                        log_write(str(e))
        else:
            log_write(f'Operation cancelled: you should select a folder')


def get_output_file(input_path: Path) -> Optional[str]:
    initial_path = generate_output_path(input_path)
    default_extension = str(input_path.suffix).lower()
    filetypes = []
    if default_extension == '.pdf':
        filetypes = [("PDF Files", ".pdf")]
    elif default_extension == '.docx':
        filetypes = [("Word Documents", ".docx")]
    elif default_extension == '.png':
        filetypes = [("Image Files", ".png")]
    elif default_extension == '.jpg':
        filetypes = [("Image Files", ".jpg")]
    elif default_extension == '.jpeg':
        filetypes = [("Image Files", ".jpeg")]
    tf = filedialog.asksaveasfile(
        mode='w',
        title="Save file to",
        initialdir=str(input_path.parent),
        initialfile=f"{initial_path.stem}{input_path.suffix}",
        defaultextension=default_extension,
        filetypes=filetypes,
    )
    if tf is None:
        return None
    else:
        name = tf.name
        tf.close()
        # print(name) # full path
        return name


def get_output_dir(base_dir: Path) -> Optional[str]:
    _dir = filedialog.askdirectory(
        title="Select output folder",
        initialdir=str(base_dir),
        mustexist=False,
    )
    if _dir is None:
        return None
    else:
        print(_dir)
        return str(_dir)


ws = Tk()
ws.title(f"Watermark Remover - by nask.io (v{__version__})")
ws.geometry("600x600")
ws['bg'] = 'gray'

log_txt_area = Text(ws, width=60, height=30, bg='white', fg='black')
log_txt_area.pack(pady=30)

Button(
    ws,
    text="Choose Files",
    command=open_files,
    bg='gray',
    fg='black'
).pack(side=RIGHT, expand=True, fill=X, padx=30)

use_color_replace = BooleanVar(value=True)
Checkbutton(
    ws,
    text="Replace using colors",
    variable=use_color_replace,
    bg='white',
    fg='black',
    offvalue=False,
    onvalue=True,
).pack(side=LEFT, expand=True, fill=X, padx=30)

ws.mainloop()
