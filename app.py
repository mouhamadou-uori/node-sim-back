from flask import Flask, request, jsonify
import numpy as np
import math
from flask_cors import CORS
from scipy import special
# Configurer matplotlib pour utiliser un backend non-interactif avant de l'importer
import matplotlib
matplotlib.use('Agg')  # Utiliser le backend Agg qui ne nécessite pas Tkinter
import matplotlib.pyplot as plt
import io
import base64
from scipy import signal

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Helper functions for calculations
def q_function(x):
    return 0.5 * special.erfc(x / np.sqrt(2))

def calculate_ber(snr):
    return q_function(snr)

def generate_eye_diagram(signal_data, samples_per_bit=16, num_bits_to_display=20):
    # Simple eye diagram generation
    bit_length = samples_per_bit
    total_samples = len(signal_data)
    
    # Create a figure for the eye diagram
    plt.figure(figsize=(10, 6))
    
    # Plot multiple bit periods on top of each other
    for i in range(total_samples - bit_length):
        if i % bit_length == 0 and i // bit_length < num_bits_to_display:
            plt.plot(range(bit_length), signal_data[i:i+bit_length])
    
    plt.title('Eye Diagram')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.grid(True)
    
    # Convert plot to base64 image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_str

def generate_power_vs_distance(distances, powers):
    plt.figure(figsize=(10, 6))
    plt.plot(distances, powers)
    plt.title('Signal Power vs Distance')
    plt.xlabel('Distance (m)')
    plt.ylabel('Power (mW)')
    plt.grid(True)
    
    # Convert plot to base64 image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_str

def generate_spectrum(frequencies, amplitudes):
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies, amplitudes)
    plt.title('Optical Spectrum')
    plt.xlabel('Frequency (THz)')
    plt.ylabel('Power (dBm)')
    plt.grid(True)
    
    # Convert plot to base64 image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_str

def generate_gain_spectrum(wavelengths, gains, noise_figures):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Plot gain
    color = 'tab:blue'
    ax1.set_xlabel('Wavelength (nm)')
    ax1.set_ylabel('Gain (dB)', color=color)
    ax1.plot(wavelengths, gains, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Create second y-axis for noise figure
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Noise Figure (dB)', color=color)
    ax2.plot(wavelengths, noise_figures, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('EDFA Gain and Noise Figure vs Wavelength')
    fig.tight_layout()
    
    # Convert plot to base64 image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_str

# Endpoint 1: Simple Laser Transmission Simulation
@app.route('/api/simulate/laser-transmission', methods=['POST'])
def simulate_laser_transmission():
    try:
        data = request.json
        
        # Extract parameters from the request
        laser_config = data['nodes'][0]['config']
        detector_config = data['nodes'][1]['config']
        connection_config = data['connections'][0]['config']
        
        # Extract specific values
        power_input = laser_config['optical_power']['value']  # mW
        wavelength = laser_config['wavelength']['value']  # nm
        spectral_width = laser_config['spectral_width']['value']  # nm
        
        sensitivity = detector_config['sensitivity']['value']  # A/W
        dark_current = detector_config['dark_current']['value'] * 1e-9  # Convert nA to A
        bandwidth = detector_config['bandwidth']['value'] * 1e9  # Convert GHz to Hz
        noise_temp = detector_config['noise_temperature']['value']  # K
        
        distance = connection_config['distance']['value']  # m
        medium = connection_config['medium']['value']
        
        # Calculate attenuation based on medium
        if medium == "fiber":
            # Typical fiber attenuation coefficient (dB/km)
            alpha_db_per_km = 0.2
            alpha = alpha_db_per_km / 4.343 / 1000  # Convert to 1/m
        elif medium == "air":
            # Simplified atmospheric attenuation
            alpha = 0.1 / 1000  # 1/m
        else:  # vacuum
            alpha = 0.001 / 1000  # Very small attenuation
        
        # Calculate power at different distances for the graph
        distances = np.linspace(0, distance, 100)
        powers = [power_input * math.exp(-alpha * d) for d in distances]
        
        # Calculate received power
        power_received = power_input * math.exp(-alpha * distance)
        
        # Calculate noise power
        k_boltzmann = 1.38e-23  # Boltzmann constant
        noise_power = 4 * k_boltzmann * noise_temp * bandwidth + 2 * dark_current * bandwidth
        
        # Calculate SNR
        snr = (sensitivity * power_received) / noise_power
        
        # Calculate BER
        ber = calculate_ber(snr)
        
        # Generate power vs distance graph
        power_vs_distance_graph = generate_power_vs_distance(distances, powers)
        
        return jsonify({
            'success': True,
            'results': {
                'power_received': power_received,
                'snr': float(snr),
                'ber': float(ber),
                'power_vs_distance_graph': power_vs_distance_graph
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# Endpoint 2: Fiber Optic Dispersion Simulation
@app.route('/api/simulate/fiber-dispersion', methods=['POST'])
def simulate_fiber_dispersion():
    try:
        data = request.json
        
        # Extract parameters from the request
        source_config = data['nodes'][0]['config']
        fiber_config = data['nodes'][1]['config']
        analyzer_config = data['nodes'][2]['config']
        
        # Extract specific values
        bit_rate = source_config['bit_rate']['value'] * 1e9  # Convert Gbps to bps
        modulation_type = source_config['modulation_type']['value']
        optical_power = source_config['optical_power']['value']  # mW
        wavelength = source_config['carrier_wavelength']['value']  # nm
        extinction_ratio = source_config['extinction_ratio']['value']  # dB
        
        fiber_length = fiber_config['length']['value'] * 1000  # Convert km to m
        attenuation_coeff = fiber_config['attenuation_coeff']['value']  # dB/km
        dispersion_coeff = fiber_config['dispersion_coeff']['value']  # ps/nm/km
        spectral_width = 0.1  # nm (assuming a default if not provided)
        
        # Calculate temporal broadening due to dispersion
        temporal_broadening = abs(dispersion_coeff) * fiber_length / 1000 * spectral_width  # ps
        
        # Calculate attenuation
        attenuation = attenuation_coeff * fiber_length / 1000  # dB
        output_power = optical_power * 10**(-attenuation/10)  # mW
        
        # Generate bit sequence for simulation
        num_bits = 128
        bit_sequence = np.random.randint(0, 2, num_bits)
        
        # Generate signal based on modulation type
        samples_per_bit = 16
        total_samples = num_bits * samples_per_bit
        time = np.linspace(0, num_bits / bit_rate, total_samples)
        signal_data = np.zeros(total_samples)
        
        # Generate NRZ signal
        for i in range(num_bits):
            bit_value = bit_sequence[i]
            start_idx = i * samples_per_bit
            end_idx = (i + 1) * samples_per_bit
            
            if modulation_type == "NRZ":
                signal_data[start_idx:end_idx] = bit_value
            elif modulation_type == "RZ":
                if bit_value == 1:
                    signal_data[start_idx:start_idx + samples_per_bit//2] = 1
            # Other modulation types can be added here
        
        # Apply dispersion effect (simplified)
        # Create a Gaussian pulse to represent dispersion
        dispersion_sigma = temporal_broadening / 1000 / 1000 * bit_rate  # Convert ps to proportion of bit period
        dispersion_filter = np.exp(-0.5 * (np.linspace(-3, 3, samples_per_bit))**2 / dispersion_sigma**2)
        dispersion_filter = dispersion_filter / np.sum(dispersion_filter)  # Normalize
        
        # Apply the dispersion via convolution
        dispersed_signal = signal.convolve(signal_data, dispersion_filter, mode='same')
        
        # Apply attenuation
        dispersed_signal *= 10**(-attenuation/10)
        
        # Generate eye diagram
        eye_diagram = generate_eye_diagram(dispersed_signal, samples_per_bit)
        
        # Generate frequency spectrum
        freq_resolution = 0.01  # THz
        center_freq = 299792458 / (wavelength * 1e-9) / 1e12  # Convert wavelength to THz
        frequencies = np.linspace(center_freq - 0.5, center_freq + 0.5, 1000)
        
        # Simple Gaussian spectrum centered at carrier frequency
        spectrum = np.exp(-0.5 * ((frequencies - center_freq) / (spectral_width/100))**2)
        spectrum_db = 10 * np.log10(spectrum * output_power)
        
        spectrum_graph = generate_spectrum(frequencies, spectrum_db)
        
        return jsonify({
            'success': True,
            'results': {
                'temporal_broadening': float(temporal_broadening),  # ps
                'attenuation': float(attenuation),  # dB
                'output_power': float(output_power),  # mW
                'eye_diagram': eye_diagram,
                'spectrum': spectrum_graph
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# Endpoint 3: EDFA Amplifier Simulation
@app.route('/api/simulate/edfa-amplifier', methods=['POST'])
def simulate_edfa_amplifier():
    try:
        data = request.json
        
        # Extract parameters from the request
        signal_config = data['nodes'][0]['config']
        edfa_config = data['nodes'][1]['config']
        
        # Extract specific values
        input_power_dbm = signal_config['input_power']['value']  # dBm
        signal_wavelength = signal_config['wavelength']['value']  # nm
        
        pump_power = edfa_config['pump_power']['value']  # mW
        pump_wavelength = edfa_config['pump_wavelength']['value']  # nm
        fiber_length = edfa_config['fiber_length']['value']  # m
        er_concentration = edfa_config['er_concentration']['value']  # ppm
        saturation_power = edfa_config['saturation_power']['value']  # mW
        
        # Convert input power from dBm to mW
        input_power = 10**(input_power_dbm/10)  # mW
        
        # Calculate small signal gain (simplified model)
        # In a real system, this would be based on complex rate equations
        small_signal_gain_db = 30 * (pump_power / 100) * (fiber_length / 10) * (er_concentration / 1000)
        small_signal_gain = 10**(small_signal_gain_db/10)
        
        # Calculate actual gain with saturation effects
        gain = small_signal_gain / (1 + input_power / saturation_power)
        gain_db = 10 * np.log10(gain)
        
        # Calculate output power
        output_power = input_power * gain  # mW
        output_power_dbm = 10 * np.log10(output_power)  # dBm
        
        # Calculate noise figure (simplified)
        # In EDFA, theoretical minimum is 3 dB
        noise_figure_db = 3 + 3 * (1 - pump_power / 500) + 2 * (input_power_dbm + 30) / 40
        
        # Generate gain spectrum across C-band
        wavelengths = np.linspace(1530, 1565, 100)
        
        # Create a gain profile with wavelength dependence (simplified)
        # Peak gain at 1550 nm with roll-off at band edges
        relative_gains = np.exp(-0.5 * ((wavelengths - 1550) / 10)**2)
        gains_db = gain_db * relative_gains
        
        # Create noise figure profile
        noise_figures = noise_figure_db + 0.5 * np.abs(wavelengths - 1550)
        
        # Generate gain spectrum graph
        gain_spectrum_graph = generate_gain_spectrum(wavelengths, gains_db, noise_figures)
        
        return jsonify({
            'success': True,
            'results': {
                'gain_db': float(gain_db),
                'output_power_dbm': float(output_power_dbm),
                'noise_figure_db': float(noise_figure_db),
                'gain_spectrum': gain_spectrum_graph
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Optical fiber simulation backend is running'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 