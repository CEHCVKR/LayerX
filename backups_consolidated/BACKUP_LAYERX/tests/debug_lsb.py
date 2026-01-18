"""
Debug LSB embedding in DWT coefficients
"""

import numpy as np
import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "03. Image Processing Module"))
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct

def test_lsb_embedding():
    """Test basic LSB embedding in DWT coefficients"""
    print("=== Testing LSB Embedding in DWT Coefficients ===")
    
    # Create test image
    if not os.path.exists('test_lena.png'):
        # Create a simple test pattern
        test_image = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
        import cv2
        cv2.imwrite('test_lena.png', test_image)
    
    # Read and decompose image
    image = read_image('test_lena.png')
    bands = dwt_decompose(image, levels=2)
    
    print(f"Original image shape: {image.shape}")
    print(f"HH1 band shape: {bands['HH1'].shape}")
    print(f"HH1 band range: {bands['HH1'].min():.3f} to {bands['HH1'].max():.3f}")
    
    # Test LSB on a few coefficients
    test_coeffs = bands['HH1'].flatten()[:10].copy()
    
    print("\nOriginal coefficients (first 10):")
    for i, coeff in enumerate(test_coeffs):
        print(f"  {i}: {coeff:.6f} -> int: {int(round(coeff))} -> LSB: {int(round(coeff)) % 2}")
    
    # Test embedding pattern: 1010101010
    test_bits = "1010101010"
    modified_coeffs = test_coeffs.copy()
    
    print("\nEmbedding pattern:", test_bits)
    
    for i, bit in enumerate(test_bits):
        coeff = modified_coeffs[i]
        coeff_int = int(round(coeff))
        
        if bit == '0':
            # Make LSB 0 (even)
            if coeff_int % 2 == 1:
                coeff_int -= 1
        else:  # bit == '1'
            # Make LSB 1 (odd)
            if coeff_int % 2 == 0:
                coeff_int += 1
        
        modified_coeffs[i] = float(coeff_int)
    
    print("\nModified coefficients:")
    for i, coeff in enumerate(modified_coeffs):
        print(f"  {i}: {coeff:.6f} -> int: {int(round(coeff))} -> LSB: {int(round(coeff)) % 2}")
    
    # Extract the bits
    extracted_bits = []
    for i in range(len(test_bits)):
        coeff = modified_coeffs[i]
        coeff_int = int(round(coeff))
        lsb = '1' if coeff_int % 2 == 1 else '0'
        extracted_bits.append(lsb)
    
    extracted_pattern = ''.join(extracted_bits)
    print(f"\nExtracted pattern: {extracted_pattern}")
    print(f"Original pattern:  {test_bits}")
    print(f"Match: {extracted_pattern == test_bits}")
    
    # Test with actual DWT reconstruction
    print("\n=== Testing with full DWT reconstruction ===")
    
    # Replace HH1 band with modified coefficients
    modified_bands = bands.copy()
    modified_bands['HH1'] = bands['HH1'].copy()
    modified_bands['HH1'].flat[:len(modified_coeffs)] = modified_coeffs
    
    # Reconstruct image
    reconstructed = dwt_reconstruct(modified_bands)
    
    # Re-decompose
    new_bands = dwt_decompose(reconstructed, levels=2)
    
    # Extract bits again
    new_coeffs = new_bands['HH1'].flatten()[:10]
    new_extracted_bits = []
    
    for i in range(len(test_bits)):
        coeff = new_coeffs[i]
        coeff_int = int(round(coeff))
        lsb = '1' if coeff_int % 2 == 1 else '0'
        new_extracted_bits.append(lsb)
    
    new_pattern = ''.join(new_extracted_bits)
    print(f"After reconstruction: {new_pattern}")
    print(f"Original pattern:    {test_bits}")
    print(f"Match after reconstruction: {new_pattern == test_bits}")
    
    return new_pattern == test_bits

if __name__ == "__main__":
    success = test_lsb_embedding()
    if success:
        print("\n✅ LSB embedding works correctly!")
    else:
        print("\n❌ LSB embedding has issues!")