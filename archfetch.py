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
    # 1. Metoda PC (lspci)
    try:
        output = subprocess.check_output("lspci | grep -iE 'VGA|3D|Display'", shell=True, stderr=subprocess.DEVNULL).decode()
        for line in output.strip().split('\n'):
            clean = line.split(': ')[-1]
            clean = re.sub(r'\[.*?\]|\(.*?\)', '', clean)
            clean = clean.replace("Corporation", "").replace("Graphics Controller", "").strip()
            parts = clean.split()
            if parts: gpus.append(f"{parts[0]} {' '.join(parts[1:2])}")
    except: pass

    # 2. Metoda Mobile (Android/ARM sysfs)
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
                            elif "tegra" in c: gpus.append("NVIDIA Tegra")
                            elif "apple" in c: gpus.append("Apple GPU")
        except: pass
    return ", ".join(list(dict.fromkeys(gpus))) if gpus else "GPU/eGPU"

def clean_cpu_name():
    """V3.3: Zaawansowane wykrywanie Snapdragona, MediaTeka i Tensora."""
    try:
        raw_name = ""
        # Głęboki skan /proc/cpuinfo dla ARM
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo") as f:
                content = f.read()
                # Szukamy Hardware (częste na Snapach) lub Model name
                h_match = re.search(r'Hardware\s+:\s+(.*)', content, re.I)
                m_match = re.search(r'model name\s+:\s+(.*)', content, re.I)
                raw_name = (h_match.group(1) if h_match else m_match.group(1) if m_match else "").strip()
        
        if not raw_name: raw_name = platform.processor() or platform.machine()

        brand = ""
        if any(x in raw_name for x in ["Snapdragon", "Qualcomm", "SM8", "SM7", "SDM"]): brand = "Snapdragon"
        elif any(x in raw_name for x in ["MediaTek", "MT6", "MT8", "Dimensity"]): brand = "MediaTek"
        elif any(x in raw_name for x in ["Tensor", "GS101", "GS201"]): brand = "Google Tensor"
        elif "Intel" in raw_name: brand = "Intel"
        elif "AMD" in raw_name: brand = "AMD"
        elif "Apple" in raw_name: brand = "Apple"

        
        model_match = re.search(r'([876][\s]?Gen[\s]?\d+|[876]\d{2,3}|Dimensity\s?\d+|G[123]|i[3579]|Ryzen [3579]|M[123])', raw_name, re.I)
        model_str = model_match.group(1) if model_match else ""

        cores = psutil.cpu_count(logical=False) or "?"
        threads = psutil.cpu_count(logical=True) or "?"
        
        full_name = f"{brand} {model_str}".strip()
        return f"{full_name if full_name else 'ARM Processor'} ({cores}C/{threads}T)"
    except: return "CPU"

def get_battery():
    """V3.3: Naprawione wykrywanie na telefonach (sysfs bypass)."""
    try:
        # 1. Próba standardowa
        bat = psutil.sensors_battery()
        if bat is not None:
            return f"{int(bat.percent)}%{' [AC]' if bat.power_plugged else ''}"

        # 2. Próba bezpośrednia z sysfs (dla telefonów/tabletów)
        base_path = "/sys/class/power_supply/"
        if os.path.exists(base_path):
            # Szukamy głównego źródła (battery lub bms)
            for supply in ["battery", "bms", "BAT0"]:
                cap_path = os.path.join(base_path, supply, "capacity")
                stat_path = os.path.join(base_path, supply, "status")
                if os.path.exists(cap_path):
                    with open(cap_path, 'r') as f:
                        cap = f.read().strip()
                    status = ""
                    if os.path.exists(stat_path):
                        with open(stat_path, 'r') as f:
                            if "Charging" in f.read(): status = " [AC]"
                    return f"{cap}%{status}"
    except: pass
    return "100% (AC)"

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
