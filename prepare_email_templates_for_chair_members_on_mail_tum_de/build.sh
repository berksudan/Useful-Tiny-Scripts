#!/bin/bash

# Change current directory to project directory.
cd "$(dirname "$0")" || exit

# Install necessary apt packages for development
sudo apt-get install xclip
sudo apt install python3-venv python3-pip

# Create virtual environment directory
python3 -m venv venv/

# Activate virtual environment
source venv/bin/activate

# Upgrade Python
python3 -m pip install --upgrade pip

# Check version of pip
# Version must be below 18.XX and compatible with Python 3.5+
pip3 --version

# Install dependencies
pip3 install pyautogui
pip3 install pyperclip
