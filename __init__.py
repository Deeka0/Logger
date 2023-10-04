from sys import platform
from time import sleep
import os, pathlib, glob


if platform in ("darwin", "linux", "linux2", "ios"):
    desktop_location = f'{os.path.expanduser("~/Desktop")}/balance.png'
    clear_arg = "clear"

elif (platform == "win32") or (platform == "win64"):
    desktop_location = f'{os.path.expanduser("~/Desktop")}\\balance.png'
    clear_arg = "cls"

else:
    exit("OS not available yet")

runtime_path = str(pathlib.Path(__file__).parent.resolve())

def clear(command):
    return os.system(command)


def clean_up():
    files = glob.glob(f"{runtime_path}/*")
    for file in files:
        if file.endswith(".log"):
            os.remove(file)
    files = glob.glob(f"{os.getcwd()}/*")
    for file in files:
        if file.endswith(".log"):
            os.remove(file)



# from __init__ import *
