#!/bin/bash
# Szybki instalator Archfetch
python -m venv build_env
source build_env/bin/activate
pip install psutil pyinstaller
pyinstaller --onefile --name archfetch archfetch.py
sudo cp dist/archfetch /usr/local/bin/
sudo chmod +x /usr/local/bin/archfetch
rm -r Archfetch 
echo "Instalation Complited! write "archfetch" to start"
