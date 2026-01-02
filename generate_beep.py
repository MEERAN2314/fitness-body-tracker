"""
Simple script to generate a beep sound for exercise completion.
Run this once to create the beep.mp3 file.
"""
import numpy as np
from scipy.io import wavfile
import os

def generate_beep(filename='app/static/sounds/beep.wav', duration=0.5, frequency=800):
    """Generate a simple beep sound"""
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Generate sine wave
    wave = np.sin(2 * np.pi * frequency * t)
    
    # Apply envelope to avoid clicks
    envelope = np.ones_like(t)
    fade_samples = int(0.01 * sample_rate)
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    
    wave = wave * envelope
    
    # Convert to 16-bit PCM
    wave = (wave * 32767).astype(np.int16)
    
    # Save
    wavfile.write(filename, sample_rate, wave)
    print(f"Beep sound generated: {filename}")

if __name__ == "__main__":
    try:
        generate_beep()
        print("✓ Beep sound created successfully!")
    except ImportError:
        print("Note: scipy is needed to generate the beep sound.")
        print("You can either:")
        print("1. Install scipy: pip install scipy")
        print("2. Or use any beep.wav/beep.mp3 file in app/static/sounds/")
