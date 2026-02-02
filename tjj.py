import os
import time
import re
import winreg
import logging
from datetime import datetime

def get_steam_path():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
            return os.path.normpath(steam_path)
    except Exception as e:
        logging.error(f"No path found: {e}")
        return None

