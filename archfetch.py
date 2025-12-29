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

def clean_cpu_name():
    raw_cpu = platform.processor()
    cores = psutil.cpu_count(logical=False)
    threads = psutil.cpu_count(logical=True)
    
    # Rozpoznawanie producenta i serii
    brand = "Intel" if "Intel" in raw_cpu else "AMD" if "AMD" in raw_cpu else "CPU"
    match = re.search(r'(i[3579]|Pentium|Celeron|Xeon|Ryzen [3579]|Athlon|Threadripper|EPYC)', raw_cpu)
    series = match.group(1) if match else ""
    
    return f"{brand} {series} ({cores}C/{threads}T)"

def get_de_wm():
    de = os.environ.get('XDG_CURRENT_DESKTOP') or os.environ.get('DESKTOP_SESSION')
    if de:
        return de.split(':')[-1].capitalize()
    return "Window Manager"

def get_stats():
    uname = platform.uname()
    
    # Uptime
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    up_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"

    # RAM (Uproszczony widok MB)
    mem = psutil.virtual_memory()
    ram_str = f"{mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB"

    # Pakiety
    try:
        pkgs = len(os.listdir('/var/lib/pacman/local')) - 1
    except:
        pkgs = "N/A"

    # Przygotowanie listy statystyk
    # Każda linia ma stały prefix z kolorem
    info = [
        f"{BLUE}{BOLD}{getpass.getuser()}@{socket.gethostname()}{RESET}",
        f"{'─'*30}",
        f"{BLUE}{BOLD}OS:{RESET}      Arch Linux",
        f"{BLUE}{BOLD}Kernel:{RESET}  {uname.release}",
        f"{BLUE}{BOLD}Uptime:{RESET}  {up_str}",
        f"{BLUE}{BOLD}Pakiety:{RESET} {pkgs} (pacman)",
        f"{BLUE}{BOLD}DE/WM:{RESET}   {get_de_wm()}",
        f"{BLUE}{BOLD}Shell:{RESET}   {os.environ.get('SHELL', '').split('/')[-1]}",
        f"{BLUE}{BOLD}CPU:{RESET}     {clean_cpu_name()}",
        f"{BLUE}{BOLD}RAM:{RESET}     {ram_str}",
    ]
    return info

def display():
    # Perfekcyjne logo bez żadnych dodatków pod spodem
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
    print("") # Odstęp od góry terminala
    
    # Łączenie logo i statystyk
    # Ustawiamy stałą szerokość kolumny loga na 22 znaki
    max_lines = max(len(logo), len(stats))
    for i in range(max_lines):
        l = logo[i] if i < len(logo) else " " * 22
        s = stats[i] if i < len(stats) else ""
        
        # l:<22 zapewnia, że tekst statystyk zawsze zaczyna się w tym samym miejscu
        print(f"{l:<22}  {s}")
    
    print("") # Odstęp na dole

if __name__ == "__main__":
    display()