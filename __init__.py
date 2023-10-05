from sys import platform
from time import sleep
from glob import glob
import os


if platform in ("darwin", "linux", "ios"):
    desktop_location = f'{os.path.expanduser("~/Desktop")}/balance.png'
    clear_arg = "clear"

elif platform == "win32":
    desktop_location = f'{os.path.expanduser("~/Desktop")}\\balance.png'
    clear_arg = "cls"

else:
    exit("OS not available yet")

runtime_path = os.path.realpath(os.path.dirname(__file__))

def clear(command):
    return os.system(command)


def clean_up():
    paths = [runtime_path, os.getcwd()]
    for path in paths:
        for file in glob(path + "/*"):
            if file.endswith(".log"):
                os.remove(file)



# from __init__ import *
