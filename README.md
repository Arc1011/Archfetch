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
GPU model
indicates how much disk space is used
shows battery percentage

<img width="819" height="611" alt="V2" src="https://github.com/user-attachments/assets/98baae11-e63c-40d0-b47b-c418b56b19b9" />



INSTALLATION:

from source:

git clone https://github.com/Arc1011/Archfetch.git

cd Archfetch

python archfetch.py

Binary (recommended)

git clone https://github.com/Arc1011/Archfetch.git

cd Archfetch

python -m venv build_env

source build_env/bin/activate 

pip install psutil pyinstaller

pyinstaller --onefile --name archfetch archfetch.py 

sudo cp dist/archfetch /usr/local/bin/

sudo chmod +x /usr/local/bin/archfetch

OR:

git clone https://github.com/Arc1011/Archfetch.git && cd Archfetch

chmod +x install.sh && ./install.sh


then you can run it anyware using:

archfetch

dependencies: base-devel



I apologize for any mistakes in English
