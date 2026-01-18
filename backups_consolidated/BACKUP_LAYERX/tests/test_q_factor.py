"""
Simple Test: Verify Q-factor fix and test different Q values
Uses existing cover.png image
"""

import sys
import os

sys.path.append('03. Image Processing Module')
sys.path.append('05. Embedding and Extraction Module')

from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes
from scipy.fftpack import dct, idct
import numpy as np

def apply_dct(band):
    return dct(dct(band, axis=0, norm='ortho'), axis=1, norm='ortho')

def apply_idct(band):
    return idct(idct(band, axis=1, norm='ortho'), axis=0, norm='ortho')

def test_with_q_factor(payload_size: int, Q: float):
    """Test embedding/extraction with specific Q-factor"""
    print(f"\n{'='*70}")
    print(f"TEST: Payload={payload_size} bytes, Q={Q}")
    print(f"{'='*70}")
    
    try:
        # Check if cover.png exists
        if not os.path.exists('cover.png'):
            print("[!] cover.png not found - skipping test")
            return False
        
        # Read and decompose
        cover_img = read_image('cover.png')
        coeffs_dict = dwt_decompose(cover_img, levels=2)
        
        # Apply DCT to all bands
        bands = {}
        for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
            if band_name in coeffs_dict:
                bands[band_name] = apply_dct(coeffs_dict[band_name])
        
        # Calculate capacity
        total_coeffs = 0
        for band in bands.values():
            total_coeffs += (band.shape[0] - 8) * (band.shape[1] - 8)
        capacity_bytes = total_coeffs // 8
        
        print(f"[+] Image: {cover_img.shape}")
        print(f"[+] Capacity: {capacity_bytes} bytes")
        print(f"[+] Usage: {payload_size/capacity_bytes*100:.1f}%")
        
        if payload_size > capacity_bytes:
            print(f"[!] SKIP - Payload exceeds capacity")
            return False
        
        # Create payload
        payload = os.urandom(payload_size)
        payload_bits = bytes_to_bits(payload)
        
        # Embed with specified Q
        print(f"[+] Embedding with Q={Q}...")
        modified_bands = embed_in_dwt_bands(payload_bits, bands.copy(), Q_factor=Q, optimization='fixed')
        
        # Reconstruct for PSNR using built-in function
        reconstructed_bands = {}
        for band_name in modified_bands:
            reconstructed_bands[band_name] = apply_idct(modified_bands[band_name])
        
        # Use dwt_reconstruct from a3_image_processing
        stego_img = dwt_reconstruct(reconstructed_bands)
        
        # Calculate PSNR
        psnr_value = psnr(cover_img, stego_img)
        print(f"[+] PSNR: {psnr_value:.2f} dB")
        
        # Extract with same Q
        print(f"[+] Extracting with Q={Q}...")
        for band_name in bands:
            bands[band_name] = apply_dct(reconstructed_bands[band_name])
        
        extracted_bits = extract_from_dwt_bands(bands, len(payload_bits), Q_factor=Q, optimization='fixed')
        extracted_payload = bits_to_bytes(extracted_bits)
        
        # Verify
        if extracted_payload == payload:
            print(f"[SUCCESS] Extraction verified! PSNR={psnr_value:.2f} dB")
            return True
        else:
            print(f"[FAIL] Extraction mismatch!")
            match_bytes = sum(1 for a, b in zip(payload, extracted_payload) if a == b)
            print(f"  Matching bytes: {match_bytes}/{len(payload)} ({match_bytes/len(payload)*100:.1f}%)")
            return False
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*70)
    print("Q-FACTOR VERIFICATION TEST")
    print("Tests: Different payload sizes + Different Q-factors")
    print("="*70)
    
    # Test configurations: (payload_bytes, Q_factor)
    test_cases = [
        # Small payloads with different Q
        (100, 3.0),
        (100, 5.0),
        (100, 7.0),
        (100, 10.0),
        
        # Medium payloads with different Q
        (1000, 3.0),
        (1000, 5.0),
        (1000, 7.0),
        
        # Large payloads with different Q
        (5000, 5.0),
        (5000, 7.0),
        (5000, 10.0),
        
        # Very large payloads
        (10000, 7.0),
        (10000, 10.0),
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for payload_size, Q in test_cases:
        result = test_with_q_factor(payload_size, Q)
        if result is True:
            passed += 1
        elif result is False:
            failed += 1
        else:
            skipped += 1
    
    print(f"\n{'='*70}")
    print(f"FINAL RESULTS")
    print(f"{'='*70}")
    print(f"Passed: {passed}/{len(test_cases)}")
    print(f"Failed: {failed}/{len(test_cases)}")
    print(f"Skipped: {skipped}/{len(test_cases)}")
    
    if passed == len(test_cases):
        print(f"\n[SUCCESS] All tests passed! Q-factor parameter working correctly.")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
