"""
Debug LSB embedding with the new robust method
"""

import numpy as np
import sys
import os
import struct

# Add paths
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "03. Image Processing Module"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "05. Embedding and Extraction Module"))

from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands

def debug_embedding():
    """Debug the embedding and extraction process step by step"""
    print("=== Debug LSB Embedding Process ===")
    
    # Read test image
    if not os.path.exists('test_lena.png'):
        test_image = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
        import cv2
        cv2.imwrite('test_lena.png', test_image)
    
    image = read_image('test_lena.png')
    bands = dwt_decompose(image, levels=2)
    
    # Simple test: embed length header + small message
    test_message = "Hi"
    test_message_bytes = test_message.encode('utf-8')
    
    # Simple test: embed alternating pattern
    test_pattern = "10101010"  # Alternating bits for easier testing
    test_bits = test_pattern + "0" * 24  # Pad to 32 bits
    
    print(f"Test pattern: {test_pattern}")
    print(f"Full test bits: {test_bits}")
    print(f"Test bits length: {len(test_bits)}")
    
    try:
        # Test embedding
        print("\n--- Embedding Process ---")
        modified_bands = embed_in_dwt_bands(test_bits, bands)
        
        # Check some embedded coefficients
        print("\nFirst 5 embedded coefficients:")
        coeff_locations = []
        embed_bands = ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']
        for band_name in embed_bands:
            if band_name in bands:
                band = bands[band_name]
                for i in range(band.shape[0]):
                    for j in range(band.shape[1]):
                        coeff_locations.append((band_name, i, j))
        
        # Test with adaptive quantization
        for i in range(min(8, len(coeff_locations))):
            band_name, row, col = coeff_locations[i]
            original = bands[band_name][row, col]
            bit = test_bits[i]
            
            # Adaptive quantization based on coefficient magnitude
            coeff_magnitude = abs(original)
            if coeff_magnitude > 5.0:
                Q = 2.0  # Large coefficients
            elif coeff_magnitude > 1.0:
                Q = 1.0  # Medium coefficients
            else:
                Q = 0.5  # Small coefficients
            
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
            print(f"  Bit {i} ({bit}): {original:.3f} -> {quantized:.3f}, Q={Q:.1f}, Q-level: {q_level}, LSB: {q_level % 2}")
        
        # Reconstruct and re-decompose to simulate the full process
        print("\n--- Reconstruction Process ---")
        stego_image = dwt_reconstruct(modified_bands)
        stego_bands = dwt_decompose(stego_image, levels=2)
        
        # Check coefficients after reconstruction
        print("\nFirst 8 coefficients after reconstruction:")
        for i in range(min(8, len(coeff_locations))):
            band_name, row, col = coeff_locations[i]
            reconstructed = stego_bands[band_name][row, col]
            bit = test_bits[i]
            
            # Use same adaptive quantization
            orig_coeff = bands[band_name][row, col]
            coeff_magnitude = abs(orig_coeff)
            if coeff_magnitude > 5.0:
                Q = 2.0
            elif coeff_magnitude > 1.0:
                Q = 1.0
            else:
                Q = 0.5
            
            q_level = round(reconstructed / Q)
            print(f"  Bit {i} ({bit}): {reconstructed:.3f}, Q={Q:.1f}, Q-level: {q_level}, LSB: {q_level % 2}")
        
        # Extract the test bits with adaptive quantization
        print("\n--- Extraction Process ---")
        extracted_bits = ""
        for i in range(min(8, len(coeff_locations))):
            band_name, row, col = coeff_locations[i]
            reconstructed = stego_bands[band_name][row, col]
            
            # Use same adaptive quantization
            orig_coeff = bands[band_name][row, col]
            coeff_magnitude = abs(orig_coeff)
            if coeff_magnitude > 5.0:
                Q = 2.0
            elif coeff_magnitude > 1.0:
                Q = 1.0
            else:
                Q = 0.5
            
            q_level = round(reconstructed / Q)
            extracted_bits += str(q_level % 2)
        
        test_pattern = test_bits[:8]
        print(f"Original bits:  {test_pattern}")
        print(f"Extracted bits: {extracted_bits}")
        print(f"Match: {extracted_bits == test_pattern}")
        
        if extracted_bits == test_pattern:
            print("✅ Adaptive quantization SUCCESSFUL!")
            
    except Exception as e:
        print(f"❌ Process FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_embedding()