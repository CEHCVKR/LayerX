#!/usr/bin/env python3
import numpy as np
import struct
import sys

# Add module paths
sys.path.append("01. Encryption Module")
sys.path.append("03. Image Processing Module")
sys.path.append("05. Embedding and Extraction Module")

from a3_image_processing import *

def debug_coefficient_selection():
    """Debug coefficient selection before/after embedding"""
    print("=== Debug Coefficient Selection ===")
    
    # Read original image
    image = read_image('test_lena.png')
    original_bands = dwt_decompose(image, levels=2)
    
    # Get stable coefficients from ORIGINAL image
    embed_bands = ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']
    original_stable = []
    
    for band_name in embed_bands:
        if band_name in original_bands:
            band = original_bands[band_name]
            for i in range(band.shape[0]):
                for j in range(band.shape[1]):
                    coeff_value = abs(band[i, j])
                    if 1.0 <= coeff_value <= 15.0:
                        original_stable.append((band_name, i, j, coeff_value))
    
    original_stable.sort(key=lambda x: x[3], reverse=True)
    print(f"Original stable coefficients: {len(original_stable)}")
    
    # Show first 8 original coefficients
    print("\nFirst 8 original stable coefficients:")
    for i in range(8):
        band_name, row, col, magnitude = original_stable[i]
        coeff_val = original_bands[band_name][row, col]
        print(f"  {i}: {band_name}[{row},{col}] = {coeff_val:.3f} (mag: {magnitude:.3f})")
    
    # Create a modified version (simulate embedding)
    modified_bands = {}
    for band_name, band_data in original_bands.items():
        if isinstance(band_data, np.ndarray):
            modified_bands[band_name] = band_data.copy()
        else:
            modified_bands[band_name] = band_data
    
    # Apply minimal modifications to first 8 coefficients
    Q = 2.0
    for i in range(8):
        band_name, row, col, magnitude = original_stable[i]
        original_coeff = modified_bands[band_name][row, col]
        
        # Force to odd quantization level (bit = 1)
        quantized = Q * round(original_coeff / Q)
        q_level = round(quantized / Q)
        if q_level % 2 == 0:
            if quantized >= 0:
                quantized += Q
            else:
                quantized -= Q
        
        modified_bands[band_name][row, col] = quantized
    
    # Reconstruct and decompose
    stego_image = dwt_reconstruct(modified_bands)
    stego_bands = dwt_decompose(stego_image, levels=2)
    
    # Check same positions in stego image
    print("\nSame coefficients after IDWT->DWT:")
    for i in range(8):
        band_name, row, col, magnitude = original_stable[i]
        stego_coeff = stego_bands[band_name][row, col]
        stego_magnitude = abs(stego_coeff)
        q_level = round(stego_coeff / Q)
        meets_criteria = 1.0 <= stego_magnitude <= 15.0
        print(f"  {i}: {band_name}[{row},{col}] = {stego_coeff:.3f} (mag: {stego_magnitude:.3f}, meets criteria: {meets_criteria}, Q-level: {q_level}, LSB: {q_level % 2})")
    
    # Now test coefficient selection on stego image
    stego_stable = []
    for band_name in embed_bands:
        if band_name in stego_bands:
            band = stego_bands[band_name]
            for i in range(band.shape[0]):
                for j in range(band.shape[1]):
                    coeff_value = abs(band[i, j])
                    if 1.0 <= coeff_value <= 15.0:
                        stego_stable.append((band_name, i, j, coeff_value))
    
    stego_stable.sort(key=lambda x: x[3], reverse=True)
    print(f"\nStego stable coefficients: {len(stego_stable)}")
    print(f"Same count: {len(stego_stable) == len(original_stable)}")
    
    # Compare first 8 selections
    print("\nSelection comparison:")
    for i in range(8):
        orig = original_stable[i]
        stego = stego_stable[i] if i < len(stego_stable) else None
        
        if stego and orig[:3] == stego[:3]:  # Same band, row, col
            print(f"  {i}: SAME position {orig[0]}[{orig[1]},{orig[2]}]")
        else:
            print(f"  {i}: DIFFERENT - orig: {orig[0] if orig else 'None'}[{orig[1] if orig else 'None'},{orig[2] if orig else 'None'}], stego: {stego[0] if stego else 'None'}[{stego[1] if stego else 'None'},{stego[2] if stego else 'None'}]")

if __name__ == "__main__":
    debug_coefficient_selection()