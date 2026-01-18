#!/usr/bin/env python3
import numpy as np
import struct
import sys

# Add module paths
sys.path.append("01. Encryption Module")
sys.path.append("03. Image Processing Module")
sys.path.append("05. Embedding and Extraction Module")

from a3_image_processing import *

def debug_specific_bits():
    """Debug embedding of specific bits (especially the '1' bits)"""
    print("=== Debug Specific Bit Embedding ===")
    
    # Read test image
    image = read_image('test_lena.png')
    bands = dwt_decompose(image, levels=2)
    
    # Test payload
    test_bits = "00001011"  # First byte of length=11 (little-endian)
    print(f"Test bits: {test_bits}")
    print(f"Bit 4, 6, 7 should be '1'")
    
    # Get coefficient locations (deterministic order)
    embed_bands = ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']
    all_coefficients = []
    for band_name in embed_bands:
        if band_name in bands:
            band = bands[band_name]
            for i in range(band.shape[0]):
                for j in range(band.shape[1]):
                    all_coefficients.append((band_name, i, j))
    
    # Create modified bands
    modified_bands = {}
    for band_name, band_data in bands.items():
        if isinstance(band_data, np.ndarray):
            modified_bands[band_name] = band_data.copy()
        else:
            modified_bands[band_name] = band_data
    
    # Embed first 8 bits
    Q = 2.0
    print(f"\n--- Embedding Process ---")
    for i in range(8):
        band_name, row, col = all_coefficients[i]
        original_coeff = bands[band_name][row, col]
        bit = test_bits[i]
        
        # Quantize coefficient
        quantized = Q * round(original_coeff / Q)
        
        if bit == '1':
            # Ensure odd quantization level
            q_level = round(quantized / Q)
            if q_level % 2 == 0:
                if quantized >= 0:
                    quantized += Q
                else:
                    quantized -= Q
        else:  # bit == '0'
            # Ensure even quantization level
            q_level = round(quantized / Q)
            if q_level % 2 == 1:
                if quantized >= 0:
                    quantized += Q
                else:
                    quantized -= Q
        
        modified_bands[band_name][row, col] = quantized
        final_q_level = round(quantized / Q)
        print(f"  Bit {i} ({bit}): {original_coeff:.3f} -> {quantized:.3f}, Q-level: {final_q_level}, LSB: {final_q_level % 2}")
    
    # Reconstruct
    print(f"\n--- Reconstruction ---")
    stego_image = dwt_reconstruct(modified_bands)
    stego_bands = dwt_decompose(stego_image, levels=2)
    
    # Extract
    print(f"\n--- Extraction ---")
    extracted_bits = ""
    for i in range(8):
        band_name, row, col = all_coefficients[i]
        reconstructed = stego_bands[band_name][row, col]
        q_level = round(reconstructed / Q)
        bit = str(q_level % 2)
        extracted_bits += bit
        
        expected = test_bits[i]
        status = "✓" if bit == expected else "✗"
        print(f"  Bit {i} ({expected}): {reconstructed:.3f}, Q-level: {q_level}, LSB: {bit} {status}")
    
    print(f"\nExpected bits: {test_bits}")
    print(f"Extracted bits: {extracted_bits}")
    print(f"Match: {extracted_bits == test_bits}")

if __name__ == "__main__":
    debug_specific_bits()