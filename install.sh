# A Shell script

# Install dependencies using apt-get
echo "Installing dependencies using apt-get..."
sudo apt-get update
sudo apt-get install -y python3-pip

# Install dependencies using pip3
echo "Installing dependencies using pip3..."
pip3 install yfinance TA-Lib
