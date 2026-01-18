#!/usr/bin/env python3
import numpy as np
import os
import sys

# Add module paths
sys.path.append("01. Encryption Module")
sys.path.append("03. Image Processing Module")
sys.path.append("05. Embedding and Extraction Module")

from a3_image_processing import *
from a5_embedding_extraction import *


def debug_stable_embedding():
    """Test stable coefficient embedding strategy"""
    print("=== Debug Stable Coefficient Embedding ===")
    
    # Read test image
    if not os.path.exists('test_lena.png'):
        test_image = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
        import cv2
        cv2.imwrite('test_lena.png', test_image)
    
    image = read_image('test_lena.png')
    bands = dwt_decompose(image, levels=2)
    
    # Simple test: embed alternating pattern
    test_pattern = "10101010"  # Alternating bits
    print(f"Test pattern: {test_pattern}")
    
    # Select STABLE coefficients for embedding
    # Avoid the largest coefficients (they cause too much distortion)
    # Avoid the smallest coefficients (they're too unstable)
    stable_coefficients = []
    
    embed_bands = ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']
    for band_name in embed_bands:
        if band_name in bands:
            band = bands[band_name]
            for i in range(band.shape[0]):
                for j in range(band.shape[1]):
                    coeff_value = abs(band[i, j])
                    # Select coefficients in the "sweet spot" - not too large, not too small
                    if 1.0 <= coeff_value <= 15.0:
                        stable_coefficients.append((band_name, i, j, coeff_value))
    
    # Sort by magnitude for consistent ordering
    stable_coefficients.sort(key=lambda x: x[3], reverse=True)
    coeff_locations = stable_coefficients[:len(test_pattern)]
    
    print(f"Selected {len(coeff_locations)} stable coefficients from {len(stable_coefficients)} candidates")
    
    if len(coeff_locations) < len(test_pattern):
        print(f"Warning: Only {len(coeff_locations)} suitable coefficients found, need {len(test_pattern)}")
        return
    
    # Create modified bands
    modified_bands = {}
    for band_name, band_data in bands.items():
        if isinstance(band_data, np.ndarray):
            modified_bands[band_name] = band_data.copy()
        else:
            modified_bands[band_name] = band_data
    
    print("\n--- Embedding Process ---")
    print("Using stable coefficient selection strategy")
    
    # Embed with conservative quantization
    for i in range(len(test_pattern)):
        band_name, row, col, magnitude = coeff_locations[i]
        original = bands[band_name][row, col]
        bit = test_pattern[i]
        
        # Conservative quantization - larger steps for stability through reconstruction
        Q = 2.0  # Larger step to survive IDWT→DWT numerical errors
        
        # Quantize coefficient
        quantized = Q * round(original / Q)
        
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
        q_level = round(quantized / Q)
        print(f"  Bit {i} ({bit}): mag={magnitude:.1f}, {original:.3f} -> {quantized:.3f}, Q-level: {q_level}, LSB: {q_level % 2}")
    
    # Reconstruct and re-decompose to simulate the full process
    print("\n--- Reconstruction Process ---")
    stego_image = dwt_reconstruct(modified_bands)
    
    # Calculate PSNR manually
    original_image = dwt_reconstruct(bands)
    mse = np.mean((original_image.astype(np.float64) - stego_image.astype(np.float64)) ** 2)
    if mse == 0:
        psnr_value = float('inf')
    else:
        max_pixel = 255.0
        psnr_value = 20 * np.log10(max_pixel / np.sqrt(mse))
    print(f"PSNR: {psnr_value:.2f} dB")
    
    stego_bands = dwt_decompose(stego_image, levels=2)
    
    # Check coefficients after reconstruction
    print("\nCoefficients after reconstruction:")
    for i in range(len(test_pattern)):
        band_name, row, col, magnitude = coeff_locations[i]
        reconstructed = stego_bands[band_name][row, col]
        bit = test_pattern[i]
        
        Q = 2.0  # Same as embedding
        q_level = round(reconstructed / Q)
        print(f"  Bit {i} ({bit}): {reconstructed:.3f}, Q-level: {q_level}, LSB: {q_level % 2}")
    
    # Extract the test bits
    print("\n--- Extraction Process ---")
    extracted_bits = ""
    for i in range(len(test_pattern)):
        band_name, row, col, magnitude = coeff_locations[i]
        reconstructed = stego_bands[band_name][row, col]
        
        Q = 2.0
        q_level = round(reconstructed / Q)
        extracted_bits += str(q_level % 2)
    
    print(f"Original bits:  {test_pattern}")
    print(f"Extracted bits: {extracted_bits}")
    print(f"Match: {extracted_bits == test_pattern}")
    
    if extracted_bits == test_pattern:
        print("✅ Stable coefficient strategy SUCCESSFUL!")
    else:
        # Show bit-by-bit analysis
        print("\nBit-by-bit analysis:")
        for i in range(len(test_pattern)):
            expected = test_pattern[i]
            actual = extracted_bits[i] if i < len(extracted_bits) else 'X'
            status = "✓" if expected == actual else "✗"
            print(f"  Bit {i}: expected {expected}, got {actual} {status}")


if __name__ == "__main__":
    debug_stable_embedding()