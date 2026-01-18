"""
SIMPLE Q-FACTOR TEST - Just verify embedding and extraction work with different Q values
No PSNR calculation, just verify correctness
"""

import sys
import os

sys.path.append('05. Embedding and Extraction Module')

from a5_embedding_extraction import bytes_to_bits, bits_to_bytes
import numpy as np

def test_q_factor_simple(payload_size: int, Q: float):
    """Test Q-factor parameter acceptance"""
    print(f"\n{'='*70}")
    print(f"TEST: Payload={payload_size} bytes, Q={Q}")
    print(f"{'='*70}")
    
    try:
        # Create test payload
        payload = os.urandom(payload_size)
        payload_bits = bytes_to_bits(payload)
        
        # Create mock bands (simulating DWT-DCT coefficients)
        bands = {}
        for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
            # Create random coefficients
            bands[band_name] = np.random.randn(100, 100) * 50  # Random DCT-like coefficients
        
        # Import functions
        from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands
        
        # Test embedding with Q-factor
        print(f"[+] Embedding with Q={Q}...")
        modified_bands = embed_in_dwt_bands(payload_bits, bands.copy(), Q_factor=Q, optimization='fixed')
        print(f"[+] Embedding successful")
        
        # Test extraction with same Q-factor
        print(f"[+] Extracting with Q={Q}...")
        extracted_bits = extract_from_dwt_bands(modified_bands, len(payload_bits), Q_factor=Q, optimization='fixed')
        extracted_payload = bits_to_bytes(extracted_bits)
        print(f"[+] Extraction successful")
        
        # Verify
        if extracted_payload == payload:
            print(f"[SUCCESS] Q-factor {Q} works correctly!")
            return True
        else:
            print(f"[FAIL] Mismatch detected")
            match_bytes = sum(1 for a, b in zip(payload, extracted_payload) if a == b)
            print(f"  Matching: {match_bytes}/{len(payload)} bytes ({match_bytes/len(payload)*100:.1f}%)")
            return False
            
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*70)
    print("Q-FACTOR PARAMETER TEST")
    print("Verifies that Q-factor parameter is accepted and works correctly")
    print("="*70)
    
    # Test different Q values with different payload sizes
    test_cases = [
        (100, 3.0),
        (100, 5.0),
        (100, 7.0),
        (100, 10.0),
        (500, 3.0),
        (500, 5.0),
        (500, 7.0),
        (1000, 5.0),
        (1000, 7.0),
        (1000, 10.0),
    ]
    
    passed = 0
    failed = 0
    
    for payload_size, Q in test_cases:
        result = test_q_factor_simple(payload_size, Q)
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"FINAL RESULTS")
    print(f"{'='*70}")
    print(f"Passed: {passed}/{len(test_cases)}")
    print(f"Failed: {failed}/{len(test_cases)}")
    
    if passed == len(test_cases):
        print(f"\n[SUCCESS] All Q-factor tests passed!")
        print(f"Q-factor parameter is working correctly.")
    else:
        print(f"\n[WARNING] Some tests failed")
    
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
