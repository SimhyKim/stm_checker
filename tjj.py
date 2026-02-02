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
        logging.error(f"No Steam found in the registry: {e}")
        return None

def read_content_log(log_path):
    if not os.path.exists(log_path):
        return None
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line in reversed(lines[-20:]):
                if "Downloading" in line or "Downloaded" in line or "Paused" in line:
                    return line.strip()
    except Exception as e:
        logging.warning(f"Error reading log: {e}")
    return None

def parse_download_status(log_line):
    if not log_line:
        return "Unknown", "Wait", 0.0

    match = re.search(r'Downloading\s+"([^"]+)"\s+\(\d+\)\s*-\s*([\d.]+)\s*([KMGT]B)/s', log_line)
    if match:
        game_name = match.group(1)
        speed_val = float(match.group(2))
        speed_unit = match.group(3)
        speed = speed_val * {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}[speed_unit]
        return game_name, "Download", speed

    if "Paused" in log_line:
        match = re.search(r'Paused\s+"([^"]+)"', log_line)
        game_name = match.group(1) if match else "Unknown"
        return game_name, "Pause", 0.0

    return "Unknown", "Wait", 0.0

def format_speed(bytes_per_sec):
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f} B/s"
    elif bytes_per_sec < 1024**2:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    elif bytes_per_sec < 1024**3:
        return f"{bytes_per_sec / 1024**2:.1f} MB/s"
    else:
        return f"{bytes_per_sec / 1024**3:.1f} GB/s"

def monitor_steam_downloads():
    steam_path = get_steam_path()
    if not steam_path:
        print("No Steam found.")
        return

    log_path = os.path.join(steam_path, "logs", "content_log.txt")
    print(f"Found Steam: {steam_path}")
    print(f"Log: {log_path}")
    print("Start check")

    for minute in range(5):
        log_line = read_content_log(log_path)
        game_name, status, speed_bps = parse_download_status(log_line)

        if status == "Pause":
            print(f"[{minute + 1}/5]  {game_name} — {status}")
        elif status == "Download":
            speed_str = format_speed(speed_bps)
            print(f"[{minute + 1}/5]  {game_name} — {status} ({speed_str})")
        else:
            print(f"[{minute + 1}/5]  {game_name} — {status}")

        time.sleep(60)  

    print("Ended")

if name == "__main__":
    monitor_steam_downloads()
