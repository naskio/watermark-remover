# Contributing

Contributions are welcome!

--------------------------------------------------------------------------------

# Environment setup

1. Install python 3.7 or later
2. Install requirements
    ```shell
    python -m pip install --upgrade pip wheel setuptools
    python -m pip install -r requirements.txt
    ```

3. Install os dependencies of [pikepdf](https://pikepdf.readthedocs.io/en/latest/)
   , [Pillow](https://pillow.readthedocs.io/en/stable/), etc (check `requirements.txt`)

--------------------------------------------------------------------------------

# Build the application

Generate builds:

1. using `scripts/build.py`
   ```shell
   python scripts/build.py
   ```

2. or Using [pyinstaller](https://pyinstaller.readthedocs.io/en/stable/index.html)
   ```shell
   pyinstaller --onefile --windowed --icon=<project-logo>.ico --add-data "<folder>;<folder>" <filename.py>
   pyinstaller --onefile --windowed WaterMarkRemover.py
   ```

You will find a directory named `dist` with the executable file `WaterMarkRemover.exe` or `WaterMarkRemover`

--------------------------------------------------------------------------------

# Release

To release a new version of the project you need to:

- Change version in file ```scripts/version.py```.
- Commit the changes and push.
- Create a new tag locally.
- Push the new tag to the remote.

## Create release

You can create a release using the following command:

```shell
VERSION="0.1.1"; MESSAGE=""; git tag $VERSION -a -m $MESSAGE; git push origin $VERSION
```

## Cancel release

- Remove the tag from local and remote
  ```shell
  VERSION="0.1.1"; git tag --delete $VERSION; git push --delete origin $VERSION
  ```

- Delete release from [GitHub](https://github.com/naskio/watermark-remover/releases/).

--------------------------------------------------------------------------------

# Acknowledgments

- [pikepdf](https://pikepdf.readthedocs.io/en/latest/topics/page.html)
- [PyPDF2](https://stackoverflow.com/questions/41769120/search-and-replace-for-text-within-a-pdf-in-python)
