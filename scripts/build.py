import PyInstaller.__main__
# from WatermarkRemover import __version__
from sys import platform as _platform
from pathlib import Path

name = 'WatermarkRemover'
icon = None

BASE_DIR = Path(__file__).parent.parent
RESOURCES_DIR = BASE_DIR / 'resources'

# platform specific code
if _platform == "linux" or _platform == "linux2":  # linux
    icon = None
elif _platform == "darwin":  # MAC OS X
    icon = RESOURCES_DIR / 'icon.icns'
elif _platform == "win32":  # Windows
    icon = RESOURCES_DIR / 'icon.ico'
elif _platform == "win64":  # Windows 64-bit
    icon = RESOURCES_DIR / 'icon.ico'

PyInstaller.__main__.run([
    # f'{name}.py',
    str(BASE_DIR / f'{name}.py'),
    '--onefile',
    '--windowed',
    f'--icon={icon}',
    '--clean',
    '--log-level=WARN',
    # f'--name={name}-{__version__}',
    f'--name={name}',
    '-y'
])
