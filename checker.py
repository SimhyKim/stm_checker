import os
import time
import re
import winreg
from datetime import datetime


def get_steam_path():
    #Find steam installation path from Windows registry
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
            return os.path.normpath(steam_path)
    except Exception:
        return None


def format_speed(bytes_per_sec):
    #Convert bytes/sec to comfortable
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f} B/s"
    elif bytes_per_sec < 1024**2:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    elif bytes_per_sec < 1024**3:
        return f"{bytes_per_sec / 1024**2:.1f} MB/s"
    else:
        return f"{bytes_per_sec / 1024**3:.2f} GB/s"


def get_latest_download_speed(log_path):
    #Parse last 10 lines of content_log.txt and find the most recent 'Current download rate:' line.
    #Returns (speed_in_bytes_per_sec, line) or (0, None) if not found.
   
    if not os.path.exists(log_path):
        return 0.0, None

    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        tail = lines[-10:]
        for line in reversed(tail):
            line = line.strip()
            if not line:
                continue

            match = re.search(r'Current download rate:\s*([\d.]+)\s*Mbps', line)
            if match:
                mbps = float(match.group(1))
                bytes_per_sec = mbps * 125_000  #1 mbps= 125000 bytes/sec
                return bytes_per_sec, line
        return 0.0, None

    except Exception as e:
        print(f"Error reading log: {e}")
        return 0.0, None


def monitor_steam_downloads():
    steam_path = get_steam_path()
    if not steam_path:
        print("Steam installation not found")
        return

    log_path = os.path.join(steam_path, "logs", "content_log.txt")
    print(f"Steam path:     {steam_path}")
    print(f"Log file:       {log_path}")
    print("Start)\n")

    for minute in range(5):
        now = datetime.now().strftime("%H:%M:%S")
        speed_bps, rate_line = get_latest_download_speed(log_path)
        #Just some beautiful printing ><
        prefix = f"[{minute + 1}/5] {now} |"

        if speed_bps > 0:
            speed_str = format_speed(speed_bps)
            print(f"{prefix} Downloading — {speed_str}")
            if rate_line:
                print(f"          └─ {rate_line}")
        else:
            print(f"{prefix} No downloading found")
        print("-" * 60)
        time.sleep(60)
    print("\nFinished.")

if __name__ == "__main__":
    monitor_steam_downloads()
