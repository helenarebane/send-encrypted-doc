#!/bin/bash
echo "Checking for Java..."
if ! command -v java &> /dev/null; then
    echo "[ERROR] Java is not installed."
    exit 1
fi

echo "Installing Python dependencies..."
python3 -m pip install -r requirements.txt

echo Setup complete. Run 'python script.py [args]' to start.
