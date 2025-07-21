#!/usr/bin/env python3
"""
Simple startup script for the optical fiber simulation backend.
This script checks if all dependencies are installed and then starts the server.
"""

import sys
import subprocess
import os
import time

def check_dependencies():
    """Check if all required packages are installed"""
    try:
        import flask
        import numpy
        import scipy
        import matplotlib
        import flask_cors
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install all dependencies with: pip install -r requirements.txt")
        return False

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the Flask server"""
    print("Starting optical fiber simulation backend server...")
    try:
        # Configurer matplotlib pour utiliser un backend non-interactif
        import matplotlib
        matplotlib.use('Agg')  # Utiliser le backend Agg qui ne nécessite pas Tkinter
        
        from app import app
        print("Server is running on http://localhost:5000")
        print("Press Ctrl+C to stop the server.")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Failed to start server: {e}")
        return False
    return True

if __name__ == "__main__":
    print("Optical Fiber Simulation Backend")
    print("================================")
    
    # Check if dependencies are installed
    if not check_dependencies():
        print("\nWould you like to install the missing dependencies? (y/n)")
        choice = input().lower()
        if choice == 'y':
            if not install_dependencies():
                print("Failed to install dependencies. Exiting.")
                sys.exit(1)
        else:
            print("Cannot start server without dependencies. Exiting.")
            sys.exit(1)
    
    # Start the server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        sys.exit(0) 