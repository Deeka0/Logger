

from sys import exit, platform
from glob import glob
from shutil import get_terminal_size
import os




if platform not in ("darwin", "linux", "ios", "android", "win32"):
    exit("OS not available yet.")

if platform == "win32":
    clear_arg = "cls"
else:
    clear_arg = "clear"

runtime_path = os.path.dirname(__file__)
desktop_path = os.path.expanduser("~/Desktop")


def clear(command: str) -> int:
    return os.system(command)


def clean_up() -> None:
    paths = (runtime_path, os.getcwd())
    for path in paths:
        for file in glob(path + "/*"):
            if file.endswith("driver.log"):
                os.remove(file)


def cprint(text: str) -> None:
    # columns, lines = get_terminal_size()
    print(text.center(get_terminal_size().columns))


