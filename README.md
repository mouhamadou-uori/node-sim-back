# Optical Fiber Simulation Backend

This is a Python backend application for optical fiber simulations. It provides endpoints for various optical simulations including:

1. Simple Laser Transmission
2. Fiber Optic Dispersion
3. EDFA Amplifier Simulation

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

Start the server with:
```
python app.py
```

The server will run on `http://localhost:5000` by default.

## API Endpoints

### Health Check
- `GET /api/health`
  - Returns status of the backend service

### Laser Transmission Simulation
- `POST /api/simulate/laser-transmission`
  - Simulates laser transmission through various media
  - Returns power vs distance graph and BER calculations

### Fiber Dispersion Simulation
- `POST /api/simulate/fiber-dispersion`
  - Simulates signal dispersion in optical fibers
  - Returns eye diagram and spectrum analysis

### EDFA Amplifier Simulation
- `POST /api/simulate/edfa-amplifier`
  - Simulates EDFA amplification of weak optical signals
  - Returns gain spectrum and noise figure analysis

## Input Format

Each endpoint expects a JSON payload with nodes and connections configuration as specified in the frontend application. 
