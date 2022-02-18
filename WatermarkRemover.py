from tkinter import Tk, StringVar, END, RIGHT, X, LEFT, Text, DISABLED, NORMAL, filedialog
from tkinter.ttk import Button, Radiobutton, Label
from pathlib import Path
from main import main, generate_output_path, MethodChoice
from scripts.version import __version__
from typing import Optional
import darkdetect

BASE_DIR = Path(__file__).parent
DEFAULT_DIR = Path.home() / 'Desktop'


def log_clear():
    log_txt_area.config(state=NORMAL)
    log_txt_area.delete(1.0, END)
    log_txt_area.config(state=DISABLED)


def log_write(text):
    log_txt_area.config(state=NORMAL)
    log_txt_area.insert(END, text)
    log_txt_area.insert(END, '\n')
    log_txt_area.config(state=DISABLED)


def open_files():
    input_files = filedialog.askopenfilenames(
        initialdir=str(DEFAULT_DIR),
        title="Open Word or PDF file",
        filetypes=[("Word Documents", ".docx"), ("PDF Files", ".pdf"), ("Image Files", ".png"),
                   ("Image Files", ".jpg"), ("Image Files", ".jpeg"), ],
    )
    log_clear()
    if input_files:  # file selected
        output_dir = get_output_dir(DEFAULT_DIR)
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
                        p_method_choice = MethodChoice.from_str(method_choice.get())
                        log_write(f"method: {p_method_choice.value}")
                        output_file = main(input_file, str(output_file), p_method_choice)
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


try:
    ws = Tk()
    # ws.tk.call("source", "azure.tcl")
    # setting theme
    try:
        THEME_FOLDER = BASE_DIR / 'resources' / 'azure'
        THEME_FILE = THEME_FOLDER / 'azure.tcl'
        with open(THEME_FILE, 'r', encoding="utf-8") as f:
            lines = f"""source {THEME_FOLDER / 'theme' / 'light.tcl'}
source {THEME_FOLDER / 'theme' / 'dark.tcl'}
        """
            lines += f.read()
            ws.tk.eval(lines)
        if darkdetect and darkdetect.isDark():
            ws.tk.call("set_theme", "dark")
        else:
            ws.tk.call("set_theme", "light")
    except Exception as e:
        print(e)
        print("Theme not loaded")
        raise e
        # ws['bg'] = 'gray'

    ws.title(f"Watermark Remover v{__version__} - by [www.nask.io]")
    # ws.resizable(False, False)
    # center window
    window_height = 696
    window_width = 720
    screen_width = ws.winfo_screenwidth()
    screen_height = ws.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))
    ws.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    # ws.geometry("694x600")

    log_txt_area = Text(
        ws, width=60, height=30, state=DISABLED,
        # bg='white', fg='black'
    )
    log_txt_area.pack(pady=30)

    Button(
        ws,
        text="Choose Files",
        command=open_files,
        # bg='gray',
        # fg='black'
    ).pack(side=RIGHT, expand=True, fill=X, padx=30)

    # display title
    Label(ws, text="Method").pack(side=LEFT, expand=True, fill=X, padx=30)
    method_choice = StringVar(value=MethodChoice.geofond1dot22.name)
    for method in MethodChoice:
        Radiobutton(
            ws,
            text=method.value,
            variable=method_choice,
            value=method.name,
            # bg='gray',
            # fg='black'
        ).pack(side=LEFT, expand=True, fill=X, padx=5)

    ws.mainloop()
except Exception as e:
    print("Unhandled exception")
    print(e)
    exit(1)
