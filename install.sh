#/bin/sh

# Ubuntu Linux install commands

# Update apt-get package lists
sudo apt-get update

# Install Python 3.10 and pip3
sudo apt-get install -y python3.10-full python3-pip

# Install sound dependencies
sudo apt-get install -y espeak

# Install yfinance and TA-Lib using pip3
pip3 install yfinance TA-Lib

# Install numpy using pip3
pip3 install numpy

# Install pytz using pip3
pip3 install pytz
