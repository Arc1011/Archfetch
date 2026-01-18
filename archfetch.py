#!/usr/bin/env python3
import psutil
import platform
import os
import socket
import datetime
import getpass
import re
import subprocess

# --- KONFIGURACJA KOLORÓW ---
BLUE = "\033[1;34m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_distro_name():
    try:
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=")[1].strip().strip('"')
    except: pass
    return "Arch Linux"

def get_gpu():
    gpus = []
    try:
        output = subprocess.check_output("lspci | grep -iE 'VGA|3D|Display'", shell=True, stderr=subprocess.DEVNULL).decode()
        for line in output.strip().split('\n'):
            clean = line.split(': ')[-1]
            clean = re.sub(r'\[.*?\]|\(.*?\)', '', clean)
            clean = clean.replace("Corporation", "").replace("Graphics Controller", "").strip()
            parts = clean.split()
            if parts: gpus.append(f"{parts[0]} {' '.join(parts[1:2])}")
    except: pass

    if not gpus:
        try:
            for card in os.listdir('/sys/class/drm/'):
                if card.startswith('card'):
                    path = f'/sys/class/drm/{card}/device/uevent'
                    if os.path.exists(path):
                        with open(path, 'r') as f:
                            content = f.read()
                            if "msm" in content: gpus.append("Qualcomm Adreno")
                            elif "panfrost" in content or "mali" in content: gpus.append("ARM Mali")
                            elif "apple" in content: gpus.append("Apple GPU")
        except: pass
    return ", ".join(list(dict.fromkeys(gpus))) if gpus else "GPU/eGPU"

def clean_cpu_name():
    try:
        raw_name = ""
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo") as f:
                content = f.read()
                match = re.search(r'model name\s+:\s+(.*)', content, re.I) or \
                        re.search(r'Model\s+:\s+(.*)', content, re.I) or \
                        re.search(r'Hardware\s+:\s+(.*)', content, re.I)
                if match: raw_name = match.group(1).strip()
        
        if not raw_name: raw_name = platform.processor() or platform.machine()

        brand = ""
        if "Intel" in raw_name: brand = "Intel"
        elif "AMD" in raw_name: brand = "AMD"
        elif any(x in raw_name for x in ["Snapdragon", "Qualcomm"]): brand = "Snapdragon"
        elif any(x in raw_name for x in ["MediaTek", "MT6", "MT8"]): brand = "MediaTek"
        elif any(x in raw_name for x in ["Apple", "M1", "M2", "M3"]): brand = "Apple"
        
        model_match = re.search(r'(i[3579]|Ryzen [3579]|Xeon|EPYC|[G]?\d{3,4}[a-zA-Z]?|X Elite|X Plus|Dimensity \d+|M[123]( Pro| Max| Ultra)?)', raw_name, re.I)
        model_str = model_match.group(1) if model_match else ""
        
        if brand == "Snapdragon" and not model_str:
            snap_match = re.search(r'(\d{3,4})', raw_name)
            if snap_match: model_str = snap_match.group(1)

        cores = psutil.cpu_count(logical=False) or "?"
        threads = psutil.cpu_count(logical=True) or "?"
        
        full_name = f"{brand} {model_str}".strip()
        if not full_name: full_name = "Generic CPU"
        
        return f"{full_name} ({cores}C/{threads}T)"
    except: return "CPU"

def get_battery():
    try:
        battery = psutil.sensors_battery()
        if battery is None: return "100% (AC)"
        return f"{int(battery.percent)}%{' [Charging]' if battery.power_plugged else ''}"
    except: return "100% (AC)"

def get_stats():
    uname = platform.uname()
    try:
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
        up_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
    except: up_str = "N/A"

    try: pkgs = len(os.listdir('/var/lib/pacman/local')) - 1
    except: pkgs = "N/A"

    mem = psutil.virtual_memory()
    de = os.environ.get('XDG_CURRENT_DESKTOP') or os.environ.get('DESKTOP_SESSION') or "Terminal"

    return [
        f"{BLUE}{BOLD}{getpass.getuser()}@{socket.gethostname()}{RESET}",
        f"{'─'*35}",
        f"{BLUE}{BOLD}OS:{RESET}        {get_distro_name()}",
        f"{BLUE}{BOLD}Kernel:{RESET}    {uname.release}",
        f"{BLUE}{BOLD}Uptime:{RESET}    {up_str}",
        f"{BLUE}{BOLD}Packages:{RESET}  {pkgs} (pacman)",
        f"{BLUE}{BOLD}DE/WM:{RESET}     {de.split(':')[-1].capitalize()}",
        f"{BLUE}{BOLD}CPU:{RESET}       {clean_cpu_name()}",
        f"{BLUE}{BOLD}GPU:{RESET}       {get_gpu()}",
        f"{BLUE}{BOLD}RAM:{RESET}       {mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB",
        f"{BLUE}{BOLD}Disk:{RESET}      {psutil.disk_usage('/').percent}% used",
        f"{BLUE}{BOLD}Battery:{RESET}   {get_battery()}",
    ]

def display():
    logo = [
        f"       {BLUE}      /\\      {RESET}",
        f"       {BLUE}     /  \\     {RESET}",
        f"       {BLUE}    /    \\    {RESET}",
        f"       {BLUE}   /      \\   {RESET}",
        f"       {BLUE}  /   ,,   \\  {RESET}",
        f"       {BLUE} /   |  |   \\ {RESET}",
        f"       {BLUE}/_-''    ''-_\\{RESET}",
    ]
    
    stats = get_stats()
    print("")
    max_lines = max(len(logo), len(stats))
    for i in range(max_lines):
        l = logo[i] if i < len(logo) else " " * 22
        s = stats[i] if i < len(stats) else ""
        print(f"{l:<22}  {s}")
    print("")

if __name__ == "__main__":
    display()
