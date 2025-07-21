import requests
import json
import os
import time

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def test_health_endpoint():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    print("Health Check Response:", data)
    assert response.status_code == 200
    assert data["status"] == "ok"
    return True

def test_laser_transmission():
    """Test the laser transmission simulation endpoint"""
    payload = {
        "nodes": [
            {
                "id": "laser_generator_1",
                "type": "laser_source",
                "name": "Générateur Laser",
                "position": {"x": 100, "y": 200},
                "config": {
                    "optical_power": {"value": 10, "unit": "mW", "range": [0.1, 100]},
                    "wavelength": {"value": 1550, "unit": "nm", "range": [1300, 1600]},
                    "spectral_width": {"value": 0.1, "unit": "nm", "range": [0.01, 10]},
                    "polarization": {"value": "linear", "options": ["linear", "circular"]},
                    "beam_divergence": {"value": 1.2, "unit": "mrad", "range": [0.5, 5]}
                },
                "outputs": ["optical_signal"]
            },
            {
                "id": "optical_detector_1", 
                "type": "photodetector",
                "name": "Détecteur Optique",
                "position": {"x": 400, "y": 200},
                "config": {
                    "sensitivity": {"value": 0.8, "unit": "A/W", "range": [0.1, 1.5]},
                    "dark_current": {"value": 10, "unit": "nA", "range": [1, 100]},
                    "bandwidth": {"value": 10, "unit": "GHz", "range": [0.1, 50]},
                    "noise_temperature": {"value": 300, "unit": "K", "range": [77, 400]},
                    "active_area": {"value": 100, "unit": "μm²", "range": [10, 1000]}
                },
                "inputs": ["optical_signal"],
                "outputs": ["electrical_signal"]
            }
        ],
        "connections": [
            {
                "from": {"node": "laser_generator_1", "port": "optical_signal"},
                "to": {"node": "optical_detector_1", "port": "optical_signal"},
                "config": {
                    "distance": {"value": 1000, "unit": "m", "range": [1, 100000]},
                    "medium": {"value": "air", "options": ["air", "vacuum", "fiber"]}
                }
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/simulate/laser-transmission", json=payload)
    data = response.json()
    print("Laser Transmission Test:", "Success" if data.get("success") else "Failed")
    assert response.status_code == 200
    assert data["success"] == True
    assert "power_received" in data["results"]
    assert "power_vs_distance_graph" in data["results"]
    return True

def test_fiber_dispersion():
    """Test the fiber dispersion simulation endpoint"""
    payload = {
        "nodes": [
            {
                "id": "modulated_source_1",
                "type": "modulated_light_source",
                "name": "Source Modulée",
                "position": {"x": 50, "y": 150},
                "config": {
                    "carrier_wavelength": {"value": 1550, "unit": "nm", "range": [1300, 1600]},
                    "optical_power": {"value": 5, "unit": "mW", "range": [0.1, 50]},
                    "bit_rate": {"value": 10, "unit": "Gbps", "range": [0.1, 100]},
                    "modulation_type": {"value": "NRZ", "options": ["NRZ", "RZ", "DPSK", "QPSK"]},
                    "extinction_ratio": {"value": 10, "unit": "dB", "range": [5, 30]},
                    "rise_time": {"value": 20, "unit": "ps", "range": [1, 100]}
                },
                "outputs": ["modulated_optical_signal"]
            },
            {
                "id": "optical_fiber_1",
                "type": "single_mode_fiber",
                "name": "Fibre Optique",
                "position": {"x": 250, "y": 150},
                "config": {
                    "length": {"value": 50, "unit": "km", "range": [0.1, 1000]},
                    "attenuation_coeff": {"value": 0.2, "unit": "dB/km", "range": [0.1, 2]},
                    "dispersion_coeff": {"value": 17, "unit": "ps/nm/km", "range": [-50, 50]},
                    "nonlinear_coeff": {"value": 1.3, "unit": "W⁻¹km⁻¹", "range": [0, 10]},
                    "core_diameter": {"value": 9, "unit": "μm", "range": [4, 50]},
                    "numerical_aperture": {"value": 0.14, "unit": "", "range": [0.1, 0.5]}
                },
                "inputs": ["modulated_optical_signal"],
                "outputs": ["dispersed_optical_signal"]
            },
            {
                "id": "spectrum_analyzer_1",
                "type": "optical_spectrum_analyzer",
                "name": "Analyseur de Spectre",
                "position": {"x": 450, "y": 150},
                "config": {
                    "resolution": {"value": 0.01, "unit": "nm", "range": [0.001, 1]},
                    "frequency_range": {"value": 50, "unit": "GHz", "range": [1, 500]},
                    "sensitivity": {"value": -80, "unit": "dBm", "range": [-100, -40]},
                    "measurement_type": {"value": "power_spectrum", "options": ["power_spectrum", "eye_diagram", "constellation"]}
                },
                "inputs": ["dispersed_optical_signal"],
                "outputs": ["analysis_data"]
            }
        ],
        "connections": [
            {
                "from": {"node": "modulated_source_1", "port": "modulated_optical_signal"},
                "to": {"node": "optical_fiber_1", "port": "modulated_optical_signal"}
            },
            {
                "from": {"node": "optical_fiber_1", "port": "dispersed_optical_signal"},
                "to": {"node": "spectrum_analyzer_1", "port": "dispersed_optical_signal"}
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/simulate/fiber-dispersion", json=payload)
    data = response.json()
    print("Fiber Dispersion Test:", "Success" if data.get("success") else "Failed")
    assert response.status_code == 200
    assert data["success"] == True
    assert "eye_diagram" in data["results"]
    assert "spectrum" in data["results"]
    return True

def test_edfa_amplifier():
    """Test the EDFA amplifier simulation endpoint"""
    payload = {
        "nodes": [
            {
                "id": "weak_signal_source_1",
                "type": "weak_optical_source",
                "name": "Signal Faible",
                "position": {"x": 80, "y": 180},
                "config": {
                    "input_power": {"value": -20, "unit": "dBm", "range": [-50, 10]},
                    "wavelength": {"value": 1550, "unit": "nm", "range": [1530, 1565]},
                    "signal_bandwidth": {"value": 0.1, "unit": "nm", "range": [0.01, 10]},
                    "polarization_state": {"value": "random", "options": ["random", "linear", "circular"]},
                    "noise_figure": {"value": 3, "unit": "dB", "range": [0, 10]}
                },
                "outputs": ["weak_optical_signal"]
            },
            {
                "id": "edfa_amplifier_1",
                "type": "erbium_doped_fiber_amplifier",
                "name": "Amplificateur EDFA",
                "position": {"x": 300, "y": 180},
                "config": {
                    "pump_power": {"value": 100, "unit": "mW", "range": [10, 500]},
                    "pump_wavelength": {"value": 980, "unit": "nm", "options": [980, 1480]},
                    "fiber_length": {"value": 10, "unit": "m", "range": [1, 100]},
                    "er_concentration": {"value": 1000, "unit": "ppm", "range": [100, 5000]},
                    "core_radius": {"value": 2.5, "unit": "μm", "range": [1, 10]},
                    "numerical_aperture": {"value": 0.24, "unit": "", "range": [0.1, 0.5]},
                    "background_loss": {"value": 0.1, "unit": "dB/m", "range": [0.01, 1]},
                    "saturation_power": {"value": 10, "unit": "mW", "range": [1, 100]}
                },
                "inputs": ["weak_optical_signal", "pump_signal"],
                "outputs": ["amplified_signal"]
            }
        ],
        "connections": [
            {
                "from": {"node": "weak_signal_source_1", "port": "weak_optical_signal"},
                "to": {"node": "edfa_amplifier_1", "port": "weak_optical_signal"}
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/simulate/edfa-amplifier", json=payload)
    data = response.json()
    print("EDFA Amplifier Test:", "Success" if data.get("success") else "Failed")
    assert response.status_code == 200
    assert data["success"] == True
    assert "gain_db" in data["results"]
    assert "gain_spectrum" in data["results"]
    return True

def run_all_tests():
    """Run all test functions"""
    print("Starting tests...")
    
    tests = [
        test_health_endpoint,
        test_laser_transmission,
        test_fiber_dispersion,
        test_edfa_amplifier
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print(f"{test.__name__}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results.append(False)
            print(f"{test.__name__}: FAILED - {str(e)}")
        
        # Add a small delay between tests
        time.sleep(0.5)
    
    print("\nTest Summary:")
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {results.count(True)}")
    print(f"Failed: {results.count(False)}")
    
    return all(results)

if __name__ == "__main__":
    print("This script tests the optical fiber simulation backend endpoints.")
    print("Make sure the backend server is running before executing this script.")
    
    input("Press Enter to start the tests...")
    success = run_all_tests()
    
    if success:
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed. Check the output above for details.") 