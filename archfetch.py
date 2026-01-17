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
    try:
        output = subprocess.check_output("lspci | grep -iE 'VGA|3D|Display'", shell=True, stderr=subprocess.DEVNULL).decode()
        gpus = []
        for line in output.strip().split('\n'):
            clean = line.split(': ')[-1]
            clean = re.sub(r'\[.*?\]|\(.*?\)', '', clean)
            clean = clean.replace("Corporation", "").replace("Graphics Controller", "").strip()
            parts = clean.split()
            if parts:
                gpus.append(f"{parts[0]} {' '.join(parts[1:3])}")
        return ", ".join(dict.fromkeys(gpus))
    except: return "GPU/eGPU"

def clean_cpu_name():
    try:
        raw_name = ""
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        raw_name = line.split(":")[1].strip()
                        break
        if not raw_name: raw_name = platform.processor()

        brand = "Intel" if "Intel" in raw_name else "AMD" if "AMD" in raw_name else ""
        model = re.search(r'(i[3579]|Ryzen [3579]|Xeon|EPYC|Apple|M[123])', raw_name)
        model_str = model.group(1) if model else ""
        
        cores = psutil.cpu_count(logical=False) or "?"
        threads = psutil.cpu_count(logical=True) or "?"
        return f"{brand} {model_str} ({cores}C/{threads}T)".strip()
    except: return "CPU"

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
        f"{BLUE}{BOLD}OS:{RESET}      {get_distro_name()}",
        f"{BLUE}{BOLD}Kernel:{RESET}  {uname.release}",
        f"{BLUE}{BOLD}Uptime:{RESET}  {up_str}",
        f"{BLUE}{BOLD}Pakiety:{RESET} {pkgs} (pacman)",
        f"{BLUE}{BOLD}DE/WM:{RESET}   {de.split(':')[-1].capitalize()}",
        f"{BLUE}{BOLD}CPU:{RESET}     {clean_cpu_name()}",
        f"{BLUE}{BOLD}GPU:{RESET}     {get_gpu()}",
        f"{BLUE}{BOLD}RAM:{RESET}     {mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB",
        f"{BLUE}{BOLD}SSD:{RESET}     {psutil.disk_usage('/').percent}% used",
        f"{BLUE}{BOLD}Bateria:{RESET} {int(psutil.sensors_battery().percent) if psutil.sensors_battery() else 100}%",
    ]

def display():
    # Powrót do starego, sprawdzonego logo
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