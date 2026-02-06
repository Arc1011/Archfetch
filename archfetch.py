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
                            c = f.read().lower()
                            if "msm" in c or "adreno" in c: gpus.append("Qualcomm Adreno")
                            elif "mali" in c or "panfrost" in c: gpus.append("ARM Mali")
                            elif "mtk" in c or "mediatek" in c: gpus.append("MediaTek GPU")
                            elif "tegra" in c: gpus.append("NVIDIA Tegra")
        except: pass
    return ", ".join(list(dict.fromkeys(gpus))) if gpus else "GPU/eGPU"

def clean_cpu_name():
    """V3.4: Poprawione rozpoznawanie MediaTek (Dimensity/Helio) i Tensor."""
    try:
        raw_name = ""
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo") as f:
                content = f.read()
                # Szukamy Hardware, Model name lub Processor
                match = re.search(r'Hardware\s+:\s+(.*)', content, re.I) or \
                        re.search(r'model name\s+:\s+(.*)', content, re.I) or \
                        re.search(r'Processor\s+:\s+(.*)', content, re.I)
                if match: raw_name = match.group(1).strip()
        
        if not raw_name: raw_name = platform.processor() or platform.machine()

        brand = ""
        if any(x in raw_name for x in ["Snapdragon", "Qualcomm", "SM8", "SM7"]): brand = "Snapdragon"
        elif any(x in raw_name for x in ["MediaTek", "MT6", "MT8", "Dimensity", "Helio"]): brand = "MediaTek"
        elif any(x in raw_name for x in ["Tensor", "GS101", "GS201"]): brand = "Google Tensor"
        elif "Intel" in raw_name: brand = "Intel"
        elif "AMD" in raw_name: brand = "AMD"
        elif "Apple" in raw_name: brand = "Apple"

        # Rozszerzony regex dla MTK i mobilnych
        model_match = re.search(r'([876][\s]?Gen[\s]?\d+|[876]\d{2,3}|Dimensity\s?\d+|Helio\s?[A-Z]?\d+|G\d{2,3}|i[3579]|Ryzen [3579]|M[123])', raw_name, re.I)
        model_str = model_match.group(1) if model_match else ""

        # Specyficzne poprawki dla MediaTek
        if brand == "MediaTek" and not model_str:
            mtk_match = re.search(r'(MT\d{4})', raw_name)
            if mtk_match: model_str = mtk_match.group(1)

        cores = psutil.cpu_count(logical=False) or "?"
        threads = psutil.cpu_count(logical=True) or "?"
        
        full_name = f"{brand} {model_str}".strip()
        return f"{full_name if full_name else 'ARM Processor'} ({cores}C/{threads}T)"
    except: return "CPU"

def get_uptime():
    """V3.4: Naprawiony uptime (odporny na błędy 1000 dni)."""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime = datetime.timedelta(seconds=uptime_seconds)
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds // 60) % 60
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            return f"{hours}h {minutes}m"
    except:
        return "N/A"

def get_battery():
    """V3.4: Agresywne wykrywanie baterii na telefonach."""
    try:
        # Metoda 1: sysfs (najpewniejsza na telefonach)
        base = "/sys/class/power_supply/"
        if os.path.exists(base):
            for s in ["battery", "bms", "BAT0", "apple_adc"]:
                cap_path = f"{base}{s}/capacity"
                if os.path.exists(cap_path):
                    with open(cap_path, 'r') as f:
                        cap = f.read().strip()
                    status_path = f"{base}{s}/status"
                    status = ""
                    if os.path.exists(status_path):
                        with open(status_path, 'r') as f:
                            if "Charging" in f.read(): status = " [AC]"
                    return f"{cap}%{status}"
        
        # Metoda 2: psutil (PC)
        bat = psutil.sensors_battery()
        if bat:
            return f"{int(bat.percent)}%{' [AC]' if bat.power_plugged else ''}"
    except: pass
    return "100% (AC)"

def get_stats():
    uname = platform.uname()
    try: pkgs = len(os.listdir('/var/lib/pacman/local')) - 1
    except: pkgs = "N/A"

    mem = psutil.virtual_memory()
    de = os.environ.get('XDG_CURRENT_DESKTOP') or os.environ.get('DESKTOP_SESSION') or "Terminal"

    return [
        f"{BLUE}{BOLD}{getpass.getuser()}@{socket.gethostname()}{RESET}",
        f"{'─'*35}",
        f"{BLUE}{BOLD}OS:{RESET}        {get_distro_name()}",
        f"{BLUE}{BOLD}Kernel:{RESET}    {uname.release}",
        f"{BLUE}{BOLD}Uptime:{RESET}    {get_uptime()}",
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
