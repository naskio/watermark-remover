from tkinter import Tk, Button, Entry, StringVar, END, RIGHT, X, LEFT, Text, DISABLED
from tkinter import filedialog
from pathlib import Path
from main import main
from version import __version__

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
        filetypes=(("Word Documents", "*.docx"), ("PDF Files", "*.pdf"),)
    )
    if input_file:  # file selected
        log_clear()
        filePathText.set(input_file)
        log_write(f'input: {input_file}')
        try:
            output_file = main(input_file)
            log_write(f'File has been processed successfully!')
            log_write(f'Output: {output_file}')
        except Exception as e:
            print(e)
            log_write(str(e))


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
