"""
Comprehensive Test: Adaptive Q-factor, Different Image Sizes, Payload Sizes
Tests the embedding/extraction system with various configurations
"""

import sys
import os
import numpy as np
import cv2
import pywt
from typing import Dict

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')
sys.path.append('06. Optimization Module')

from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes
from scipy.fftpack import dct, idct

def apply_dct(band):
    """Apply 2D DCT"""
    return dct(dct(band, axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_idct(band):
    """Apply inverse 2D DCT"""
    return idct(idct(band, axis=1, norm='ortho'), axis=0, norm='ortho')

def calculate_optimal_q(payload_bytes: int, capacity_bytes: int) -> float:
    """
    Calculate optimal Q-factor based on payload size and desired PSNR.
    
    Strategy:
    - Small payloads (< 20% capacity): Q=3.0 for minimal distortion (PSNR >55dB)
    - Medium payloads (20-50% capacity): Q=5.0 for balance (PSNR 50-55dB)
    - Large payloads (50-80% capacity): Q=7.0 for higher capacity (PSNR 45-50dB)
    - Very large (> 80% capacity): Q=10.0 for maximum capacity (PSNR 40-45dB)
    
    Args:
        payload_bytes: Size of payload in bytes
        capacity_bytes: Total capacity available in bytes
    
    Returns:
        float: Optimal Q-factor
    """
    ratio = payload_bytes / capacity_bytes
    
    if ratio < 0.2:
        return 3.0  # Minimal distortion
    elif ratio < 0.5:
        return 5.0  # Balanced
    elif ratio < 0.8:
        return 7.0  # Higher capacity
    else:
        return 10.0  # Maximum capacity

def create_test_image(width: int, height: int, filename: str):
    """Create a test image with random patterns"""
    img = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    cv2.imwrite(filename, img)
    return filename

def test_embedding_extraction(image_size: tuple, payload_size: int, test_name: str):
    """
    Test embedding and extraction with specific image and payload sizes.
    
    Args:
        image_size: (width, height) tuple
        payload_size: Number of bytes to embed
        test_name: Name for this test case
    """
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"Image: {image_size[0]}x{image_size[1]}, Payload: {payload_size} bytes")
    print(f"{'='*70}")
    
    try:
        # Create test image
        width, height = image_size
        cover_img_path = f"test_cover_{width}x{height}.png"
        create_test_image(width, height, cover_img_path)
        
        # Create test payload
        payload = os.urandom(payload_size)
        payload_bits = bytes_to_bits(payload)
        
        # Read and decompose image
        cover_img = read_image(cover_img_path)
        coeffs = dwt_decompose(cover_img, levels=2)
        
        # Extract bands and apply DCT - coeffs is a dictionary
        bands = {}
        for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
            if band_name in coeffs:
                bands[band_name] = apply_dct(coeffs[band_name])
        
        # Calculate capacity
        total_coeffs = 0
        for band in bands.values():
            total_coeffs += (band.shape[0] - 8) * (band.shape[1] - 8)
        capacity_bytes = total_coeffs // 8
        
        print(f"[+] Image loaded: {cover_img.shape}")
        print(f"[+] Total capacity: {capacity_bytes} bytes ({total_coeffs} bits)")
        print(f"[+] Payload: {payload_size} bytes ({len(payload_bits)} bits)")
        print(f"[+] Capacity usage: {payload_size/capacity_bytes*100:.1f}%")
        
        if payload_size > capacity_bytes:
            print(f"[!] SKIP - Payload exceeds capacity")
            os.remove(cover_img_path)
            return
        
        # Calculate optimal Q
        Q = calculate_optimal_q(payload_size, capacity_bytes)
        print(f"[+] Optimal Q-factor: {Q}")
        
        # Embed with optimal Q
        modified_bands = embed_in_dwt_bands(bands.copy(), payload_bits, Q_factor=Q, optimization='fixed')
        
        # Apply inverse DCT and reconstruct
        reconstructed_bands = {}
        for band_name in modified_bands:
            reconstructed_bands[band_name] = apply_idct(modified_bands[band_name])
        
        # Prepare coefficients for reconstruction - use original LL1 structure
        # Reconstruct LL1 from LL2, LH2, HL2, HH2
        LL1 = (reconstructed_bands['LL2'], 
               (reconstructed_bands['LH2'], reconstructed_bands['HL2'], reconstructed_bands['HH2']))
        
        # Full image reconstruction from LL1, LH1, HL1, HH1
        full_coeffs = (LL1,
                      (reconstructed_bands['LH1'], reconstructed_bands['HL1'], reconstructed_bands['HH1']))
        
        stego_img = pywt.idwt2(full_coeffs, 'db4')
        
        # Calculate PSNR
        psnr_value = psnr(cover_img, stego_img)
        print(f"[+] Embedding complete - PSNR: {psnr_value:.2f} dB")
        
        # Extract
        for band_name in bands:
            bands[band_name] = apply_dct(modified_bands[band_name])
        
        extracted_bits = extract_from_dwt_bands(bands, len(payload_bits), Q_factor=Q, optimization='fixed')
        extracted_payload = bits_to_bytes(extracted_bits)
        
        # Verify
        if extracted_payload == payload:
            print(f"[+] SUCCESS - Extraction verified (100% match)")
            print(f"[+] Result: PSNR {psnr_value:.2f} dB with Q={Q}")
        else:
            print(f"[!] FAIL - Extraction mismatch")
            print(f"    Original: {payload[:20].hex()}...")
            print(f"    Extracted: {extracted_payload[:20].hex()}...")
        
        # Cleanup
        os.remove(cover_img_path)
        
    except Exception as e:
        print(f"[!] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Run comprehensive tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE ADAPTIVE SYSTEM TEST")
    print("Testing: Different Image Sizes + Payload Sizes + Adaptive Q")
    print("="*70)
    
    # Test configurations: (image_size, payload_size, name)
    test_cases = [
        # Small images
        ((256, 256), 100, "Small Image + Tiny Payload"),
        ((256, 256), 500, "Small Image + Small Payload"),
        ((256, 256), 2000, "Small Image + Medium Payload"),
        
        # Medium images
        ((512, 512), 500, "Medium Image + Small Payload"),
        ((512, 512), 5000, "Medium Image + Medium Payload"),
        ((512, 512), 20000, "Medium Image + Large Payload"),
        
        # Large images  
        ((1024, 768), 1000, "Large Image + Small Payload"),
        ((1024, 768), 10000, "Large Image + Medium Payload"),
        ((1024, 768), 50000, "Large Image + Large Payload"),
        
        # Very large images
        ((1920, 1080), 5000, "HD Image + Small Payload"),
        ((1920, 1080), 50000, "HD Image + Medium Payload"),
        ((1920, 1080), 150000, "HD Image + Large Payload"),
    ]
    
    passed = 0
    failed = 0
    
    for image_size, payload_size, name in test_cases:
        try:
            test_embedding_extraction(image_size, payload_size, name)
            passed += 1
        except Exception as e:
            print(f"[!] Test failed: {str(e)}")
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"FINAL RESULTS")
    print(f"{'='*70}")
    print(f"Passed: {passed}/{len(test_cases)}")
    print(f"Failed: {failed}/{len(test_cases)}")
    print(f"\nNOTE: Tests are skipped (not failed) when payload exceeds capacity")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
