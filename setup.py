import sys
from cx_Freeze import setup, Executable

# Includere i file di configurazione di Ursina e altre librerie necessarie
include_files = [
    ('C:/Users/matti/AppData/Local/Programs/Python/Python312/Lib/site-packages/panda3d/etc/Config.prc', 'etc/Config.prc'),
    'solver.py',
]

# Definisci le opzioni di build
build_exe_options = {
    'packages': ['ursina', 'panda3d.core'],  # Includi altri pacchetti necessari
    'include_files': include_files,
    'excludes': ['tkinter'],  # Escludi pacchetti non necessari
}

# Definisci l'eseguibile
executables = [
    Executable('main.py', base=None)  # Usa 'Win32GUI' al posto di None se non vuoi una console
]

# Configura il setup
setup(
    name='rcube-solver',
    version='1.0',
    description='This application is a Rubik\'s Cube solver. It uses opencv to detect the colors of the cube faces and the Kociemba algorithm to solve the cube. The application is built using the Ursina game engine for the cube 3D model.',
    options={'build_exe': build_exe_options},
    executables=executables
)
