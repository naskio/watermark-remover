"""
Build script for the project.
"""

import fire
import PyInstaller.__main__
from sys import platform as platform_name
from pathlib import Path
import os
import shutil
import pprint
from logging import getLogger

logger = getLogger(__name__)

BASE_DIR = Path(__file__).parent
RESOURCES_DIR = BASE_DIR / 'resources'


def get_info(version: str = None, debug: bool = False, genenv: bool = False,
             sentry_dsn: str = None) -> dict:
    """Get the info for the build."""

    app_name = 'WatermarkRemover'
    icon_path = None
    os_name = None
    add_data_separator = None
    # platform specific code
    if platform_name == "linux" or platform_name == "linux2":  # linux
        icon_path = None
        os_name = 'linux'
        add_data_separator = ":"
    elif platform_name == "darwin":  # MAC OS X
        icon_path = RESOURCES_DIR / 'icon.icns'
        os_name = 'macos'
        add_data_separator = ":"
    elif platform_name == "win32":  # Windows
        icon_path = RESOURCES_DIR / 'icon.ico'
        os_name = 'win32'
        add_data_separator = ";"
    elif platform_name == "win64":  # Windows 64-bit
        icon_path = RESOURCES_DIR / 'icon.ico'
        os_name = 'win64'
        add_data_separator = ";"

    # full name
    full_name = app_name
    # if version:
    #     full_name += f'-{os_name}-{version}'

    return {
        'app_name': app_name,
        'full_name': full_name,
        'icon_path': icon_path,
        'os_name': os_name,
        'add_data_separator': add_data_separator,
        'version': version,
        'debug': debug,
        'genenv': genenv,
        'sentry_dsn': sentry_dsn,
    }


def generate_env(info: dict):
    """Generate the environment file."""
    logger.info(f'Generating environment file...')
    env_file = BASE_DIR / 'vars.txt'
    if not env_file.exists():
        logger.info(f'Creating a new environment file...')
        env_file.touch()
        with open(env_file, 'w') as f:
            if info.get('debug'):
                f.write(f'DEBUG={info.get("debug")}\n')
            if info.get('version'):
                f.write(f'VERSION={info.get("version")}\n')
            if info.get('sentry_dsn'):
                f.write(f'SENTRY_DSN={info.get("sentry_dsn")}\n')
    else:
        logger.info(f'Environment file already exists.')


def clean_files(info: dict):
    """Clean the build folder."""

    build_dir = BASE_DIR / 'build'
    dist_dir = BASE_DIR / 'dist'
    spec_file = BASE_DIR / f'{info.get("full_name")}.spec'
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if spec_file.exists():
        spec_file.unlink()


def build_app(info: dict, dirmode):
    """Build the app."""
    logger.info(f'Building version {info.get("version")}...')
    pprint.pprint(info)
    # add file assets
    theme_dir = BASE_DIR / "resources" / "theme"
    env_file = BASE_DIR / 'vars.txt'
    if not theme_dir.exists():
        logger.warning(f'{theme_dir} not found.')
    if not env_file.exists():
        logger.warning(f'{env_file} not found.')
    pi_args = [
        str(BASE_DIR / f'{info.get("app_name")}.py'),
        '--onefile' if not dirmode else '--onedir',
        '--noupx' if info.get('os_name', '').startswith('win') else None,
        '--windowed',
        f'--icon={info.get("icon_path")}',
        '--clean',
        '--log-level=WARN',
        f'--name={info.get("full_name")}',
        # f'--splash={BASE_DIR / "resources" / "splash.png"}', # not supported in macOS
        '-y'
    ]
    if theme_dir.exists():
        # without this the theme will not be found and the app crashes here: ws.tk.call("source", "main.tcl")
        pi_args.append(f'--add-data={theme_dir}{info.get("add_data_separator")}{os.path.join("resources", "theme")}')
    if env_file.exists():
        pi_args.append(f'--add-data={env_file}{info.get("add_data_separator")}.')
    # build
    return PyInstaller.__main__.run([x for x in pi_args if x])


def main(version: str = None, debug: bool = False, clean: bool = False, dirmode: bool = False, genenv: bool = False,
         sentry_dsn: str = None):
    info = get_info(version, debug, genenv, sentry_dsn)
    if clean:
        return clean_files(info)
    if genenv:
        generate_env(info)
    return build_app(info, dirmode)


if __name__ == '__main__':
    fire.Fire(main)
