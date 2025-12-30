# Archfetch
Archfetch - neofetch-like app

Archfetch is a minimalist, colorful neofetch-style system information tool for Arch Linux and Arch-based distributions. It displays key system stats in the terminal in a clean and concise format.
Features:

Displays username and hostname
OS and kernel version
Uptime
Installed package count (Pacman)
Desktop Environment / Window Manager
Default shell
CPU model and core/thread 
RAM usage
<img width="819" height="611" alt="archfetchzdj" src="https://github.com/user-attachments/assets/31e830c5-fe84-4985-9e66-2bdf60af6281" />



INSTALLATION:

from source:

git clone https://github.com/Arc1011/Archfetch.git

cd archfetch

python archfetch.py

Binary (recommended)

git clone https://github.com/Arc1011/Archfetch.git

cd archfetch

python -m venv build_env

source build_env/bin/activate 

pip install psutil pyinstaller

pyinstaller --onefile --name archfetch archfetch.py 

sudo cp dist/archfetch /usr/local/bin/

sudo chmod +x /usr/local/bin/archfetch


then you can run it anyware using:

archfetch



I apologize for any mistakes in English
