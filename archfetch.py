#!/usr/bin/env python
import psutil
import platform
import os
import socket
import datetime
import getpass
import re

# --- KONFIGURACJA KOLORÓW ---
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_distro_name():
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=")[1].strip().strip('"')
    except:
        pass
    return "Arch Linux"

def get_gpu():
    """Wykrywa model karty graficznej i skraca nazwę."""
    try:
        # Przeszukujemy urządzenia DRM (Direct Rendering Manager)
        gpu_list = []
        cards = [d for d in os.listdir('/sys/class/drm/') if re.match(r'card[0-9]+$', d)]
        
        for card in cards:
            uevent_path = f'/sys/class/drm/{card}/device/uevent'
            if os.path.exists(uevent_path):
                with open(uevent_path, 'r') as f:
                    content = f.read()
                    # Szukamy nazwy sterownika lub ID urządzenia
                    if "pci_id" in content.lower() or "driver" in content.lower():
                        # Używamy lspci (jeśli dostępne) dla najdokładniejszej nazwy
                        # lub wyciągamy z sysfs. Tu najbezpieczniej uzyc lspci:
                        import subprocess
                        gpu_info = subprocess.check_output("lspci | grep -E 'VGA|3D'", shell=True).decode()
                        
                        for line in gpu_info.split('\n'):
                            if not line: continue
                            # Czyszczenie nazwy: usuwamy ID pci i zbędne nawiasy
                            clean = line.split(': ')[-1]
                            clean = re.sub(r'\[.*?\]', '', clean) # Usuwa [Ryzen...]
                            clean = re.sub(r'\(.*?\)', '', clean) # Usuwa (rev ..)
                            clean = clean.replace("Corporation", "").replace("Graphics Controller", "").strip()
                            
                            # Skracanie do Twojego stylu
                            if "NVIDIA" in clean: clean = "NVIDIA " + clean.split("NVIDIA")[-1].strip()
                            if "AMD" in clean: clean = "AMD " + clean.split("AMD")[-1].strip()
                            if "Intel" in clean: clean = "Intel " + clean.split("Intel")[-1].strip()
                            
                            # Jeśli zbyt długie, bierzemy pierwsze 3 słowa
                            gpu_list.append(" ".join(clean.split()[:3]))
        
        if gpu_list:
            return ", ".join(list(set(gpu_list))) # Usuwa duplikaty
    except:
        pass
    return "GPU/eGPU"

def get_battery():
    try:
        bat = psutil.sensors_battery()
        return f"{int(bat.percent)}%" if bat else "100% (AC)"
    except:
        return "100% (AC)"

def get_disk_usage():
    try:
        return f"{psutil.disk_usage('/').percent}% used"
    except:
        return "N/A"

def clean_cpu_name():
    raw_cpu = platform.processor()
    cores = psutil.cpu_count(logical=False)
    threads = psutil.cpu_count(logical=True)
    brand = "Intel" if "Intel" in raw_cpu else "AMD" if "AMD" in raw_cpu else "CPU"
    match = re.search(r'(i[3579]|Pentium|Celeron|Xeon|Ryzen [3579]|Athlon|Threadripper|EPYC)', raw_cpu)
    series = match.group(1) if match else ""
    return f"{brand} {series} ({cores}C/{threads}T)"

def get_de_wm():
    de = os.environ.get('XDG_CURRENT_DESKTOP') or os.environ.get('DESKTOP_SESSION')
    return de.split(':')[-1].capitalize() if de else "Window Manager"

def get_stats():
    uname = platform.uname()
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    up_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
    mem = psutil.virtual_memory()
    
    try:
        pkgs = len(os.listdir('/var/lib/pacman/local')) - 1
    except:
        pkgs = "N/A"

    return [
        f"{BLUE}{BOLD}{getpass.getuser()}@{socket.gethostname()}{RESET}",
        f"{'─'*30}",
        f"{BLUE}{BOLD}OS:{RESET}      {get_distro_name()}",
        f"{BLUE}{BOLD}Kernel:{RESET}  {uname.release}",
        f"{BLUE}{BOLD}Uptime:{RESET}  {up_str}",
        f"{BLUE}{BOLD}Pakiety:{RESET} {pkgs} (pacman)",
        f"{BLUE}{BOLD}DE/WM:{RESET}   {get_de_wm()}",
        f"{BLUE}{BOLD}CPU:{RESET}     {clean_cpu_name()}",
        f"{BLUE}{BOLD}GPU:{RESET}     {get_gpu()}", # NOWOŚĆ
        f"{BLUE}{BOLD}RAM:{RESET}     {mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB",
        f"{BLUE}{BOLD}SSD:{RESET}     {get_disk_usage()}",
        f"{BLUE}{BOLD}Bateria:{RESET} {get_battery()}",
    ]

def display():
    logo = [
        f"       {BLUE}      /\      {RESET}",
        f"       {BLUE}     /  \     {RESET}",
        f"       {BLUE}    /    \    {RESET}",
        f"       {BLUE}   /      \   {RESET}",
        f"       {BLUE}  /   ,,   \  {RESET}",
        f"       {BLUE} /   |  |   \ {RESET}",
        f"       {BLUE}/_-''    ''-_\{RESET}",
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