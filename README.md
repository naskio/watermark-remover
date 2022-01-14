# watermark-remover

Python GUI to remove watermarks from Images inside DOCX and PDF files

## Installation

## Build

1. Install python 3.7 or later
2. Install requirements

  ```shell
  python -m pip install --upgrade pip wheel setuptools
  python -m pip install -r requirements.txt
  ```

3. Generate builds
    1. using `build.py`
       ```shell
       python build.py
       ```
    2. or Using [pyinstaller](https://pyinstaller.readthedocs.io/en/stable/index.html)
       ```shell
       pyinstaller --onefile --windowed --icon=<project-logo>.ico --add-data "<folder>;<folder>" <filename.py>
       pyinstaller --onefile --windowed WaterMarkRemover.py
       ```

## Usage

You will find a directory named `dist` with the executable file `WaterMarkRemover.exe` or `WaterMarkRemover`

-----------------------------------------------------------------------------------

# Contribute

Pull requests are welcome! For any bug reports, please create an issue.

# License

[License](LICENSE)