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

## Release

- Change version in file ```version.py```

- Push a new tag to the repository

```
# list tags
git tag
# create new tag
git tag -a 0.1.0 -m "version 0.1.0"
# push tag to remote
git push origin --tags
# push a specific tag to remote
git push origin 1.0.0
# delete local tag
git tag -d 1.0.0
# remove remote tag (with release)
git push --delete origin 1.0.0
# or push to remote
git push origin :refs/tags/1.0.0
```

-----------------------------------------------------------------------------------

# Contribute

Pull requests are welcome! For any bug reports, please create an issue.

# License

[License](LICENSE)