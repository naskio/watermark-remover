from tkinter import Tk, Button, Entry, StringVar, END, RIGHT, X, LEFT, Text, DISABLED
from tkinter import filedialog
from pathlib import Path
from main import main, generate_output_path
from scripts.version import __version__
# import time
from typing import Optional

BASE_DIR = Path(__file__).parent


def log_clear():
    log_txt_area.delete(1.0, END)


def log_write(text):
    log_txt_area.insert(END, text)
    log_txt_area.insert(END, '\n')


def open_file():
    input_file = filedialog.askopenfilename(
        initialdir=str(BASE_DIR),
        title="Open Word or PDF file",
        filetypes=[("Word Documents", ".docx"), ("PDF Files", ".pdf"), ],
    )
    log_clear()
    if input_file:  # file selected
        input_path = Path(input_file)
        if not input_path.exists():
            log_write(f"File {input_path} does not exist")
        elif str(input_path.suffix).lower() not in ('.docx', '.pdf'):
            log_write(f"File {input_path} is not a Word or PDF file")
        else:  # processing
            filePathText.set(input_file)
            log_write(f'Selected Input: {input_file}')
            try:
                output_file = get_output_file(input_path)
                if output_file:
                    log_write(f'Selected Output: {output_file}')
                    log_write("Processing...")
                    output_file = main(input_file, output_file)
                    log_write(f'File has been saved successfully to: {output_file}')
                else:
                    log_write(f'Operation cancelled: no output file selected')
                    # time.sleep(0.5)
                    # log_clear()
            except Exception as e:
                log_write(str(e))


def get_output_file(input_path: Path) -> Optional[str]:
    initial_path = generate_output_path(input_path)
    # print(initial_path.stem)  # Doc1_generated
    # print(initial_path.suffix)  # .docx or .pdf
    default_extension = str(input_path.suffix).lower()
    filetypes = []
    if default_extension == '.pdf':
        filetypes = [("PDF Files", ".pdf")]
    elif default_extension == '.docx':
        filetypes = [("Word Documents", ".docx")]
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


ws = Tk()
ws.title(f"Watermark Remover - by nask.io (v{__version__})")
ws.geometry("600x600")
ws['bg'] = 'gray'

log_txt_area = Text(ws, width=60, height=30, bg='white', fg='black')
log_txt_area.pack(pady=30)

filePathText = StringVar()
file_path_in = Entry(ws, bg='gray', fg='black', textvariable=filePathText)
file_path_in.config(state=DISABLED)
file_path_in.pack(side=LEFT, expand=True, fill=X, padx=30)

Button(
    ws,
    text="Choose File",
    command=open_file,
    bg='gray',
    fg='black'
).pack(side=RIGHT, expand=True, fill=X, padx=30)

ws.mainloop()
