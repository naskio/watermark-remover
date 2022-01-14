import PyInstaller.__main__
from version import __version__
from sys import platform as _platform
from pathlib import Path

name = 'WatermarkRemover'
icon = None

BASE_DIR = Path(__file__).parent.parent
RESOURCES_DIR = BASE_DIR / 'resources'
_os = None

# platform specific code
if _platform == "linux" or _platform == "linux2":  # linux
    icon = None
    _os = 'linux'
elif _platform == "darwin":  # MAC OS X
    icon = RESOURCES_DIR / 'icon.icns'
    _os = 'macos'
elif _platform == "win32":  # Windows
    icon = RESOURCES_DIR / 'icon.ico'
    _os = 'wind32'
elif _platform == "win64":  # Windows 64-bit
    icon = RESOURCES_DIR / 'icon.ico'
    _os = 'win64'

PyInstaller.__main__.run([
    str(BASE_DIR / f'{name}.py'),
    '--onefile',
    '--windowed',
    f'--icon={icon}',
    '--clean',
    '--log-level=WARN',
    f'--name={name}-{_os}-{__version__}',
    '-y'
])
