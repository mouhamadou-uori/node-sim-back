#!/bin/bash

echo "Starting Optical Fiber Simulation Backend..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8 or higher from https://www.python.org/downloads/"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Activate virtual environment and run the backend
echo "Activating virtual environment..."
source venv/bin/activate

# Run the backend
echo "Starting backend server..."
python3 run_backend.py

# Deactivate virtual environment when done
deactivate

read -p "Press Enter to exit..." 