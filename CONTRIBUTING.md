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
   , [Pillow](https://pillow.readthedocs.io/en/stable/), etc. (check `requirements.txt`)

--------------------------------------------------------------------------------

# Build the application

Generate builds:

1. Create and configure env variables (`.env` file)
   ```shell
   cp .env.example .env
   ```

2. Load env variables
   ```shell
   source .env
   ECHO $VERSION
   ECHO $DEBUG
   ```

3. using `build.py` script
   ```shell
   source .env; python3 build.py --debug $DEBUG --version $VERSION --genenv --sentry_dsn $SENTRY_DSN
   ```

4. or Using [pyinstaller](https://pyinstaller.readthedocs.io/en/stable/index.html)
   ```shell
   pyinstaller --onefile --windowed --icon=<project-logo>.ico --add-data "<folder>;<folder>" <filename.py>
   pyinstaller --onefile --windowed WaterMarkRemover.py
   ```

You will find a directory named `dist` with the executable file `WaterMarkRemover.exe`, `WaterMarkRemover`
or `WaterMarkRemover.app`.

to run the app on macOS:

```shell
open -n WatermarkRemover.app
```

## Build and Test the application locally

```shell
./test_build.local.sh 35
```

## Build installer (Windows only)

Using nsis:

```
makensis config.nsi
```

## GitHub Actions

Optionally, we can create an `.env` file in the workflow with the following variables:

- VERSION: the version of the application
- DEBUG: the debug mode of the application

--------------------------------------------------------------------------------

# Release

To release a new version of the project you need to:

- Change version in the env file `.env`.
- Commit the changes and push.
- Create a new tag locally.
- Push the new tag to the remote.

## Create release

You can create a release using the following command:

```shell
source .env; git push; git tag $VERSION -a -m "v$VERSION"; git push origin $VERSION
# or
git push; VERSION="0.1.0"; MESSAGE="v$VERSION"; git tag $VERSION -a -m $MESSAGE; git push origin $VERSION
```

## Cancel release

- Remove the tag from local and remote
  ```shell
  source .env; git tag --delete $VERSION; git push --delete origin $VERSION
  # or
  VERSION="0.1.0"; git tag --delete $VERSION; git push --delete origin $VERSION
  ```

- Delete release from [GitHub](https://github.com/naskio/watermark-remover/releases/).

--------------------------------------------------------------------------------

# Acknowledgments

- [pikepdf](https://pikepdf.readthedocs.io/en/latest/topics/page.html)
- [PyPDF2](https://stackoverflow.com/questions/41769120/search-and-replace-for-text-within-a-pdf-in-python)
