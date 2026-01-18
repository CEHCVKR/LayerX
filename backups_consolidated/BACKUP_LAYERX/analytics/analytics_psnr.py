"""
PSNR Analytics - Test different payload sizes and measure quality
"""

from a1_encryption import encrypt_message
from a3_image_processing import read_image, psnr, dwt_decompose, dwt_reconstruct
from a4_compression import compress_huffman, create_payload
from a5_embedding_extraction import bytes_to_bits, embed_in_dwt_bands, extract_from_dwt_bands, bits_to_bytes
from scipy.fftpack import dct, idct
import numpy as np
import time

def apply_dct(band):
    return dct(dct(band.T, norm='ortho').T, norm='ortho')

def apply_idct(band):
    return idct(idct(band.T, norm='ortho').T, norm='ortho')

def test_payload_size(message, cover_path="cover.png"):
    """Test a single payload and return PSNR"""
    # Encryption
    password = "test_password"
    ciphertext, salt, iv = encrypt_message(message, password)
    
    # Compression
    compressed, tree = compress_huffman(ciphertext)
    payload = create_payload(ciphertext, tree, compressed)
    payload_bits = bytes_to_bits(payload)
    
    # Image processing
    img = read_image(cover_path)
    bands = dwt_decompose(img, levels=2)
    
    # Apply DCT
    dct_bands = bands.copy()
    for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
        if band_name in bands:
            dct_bands[band_name] = apply_dct(bands[band_name])
    
    # Embedding
    start_time = time.time()
    modified_bands = embed_in_dwt_bands(payload_bits, dct_bands, optimization='fixed')
    embed_time = time.time() - start_time
    
    # Inverse DCT
    for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
        if band_name in modified_bands:
            modified_bands[band_name] = apply_idct(modified_bands[band_name])
    
    # Inverse DWT
    stego_img = dwt_reconstruct(modified_bands)
    
    # Calculate PSNR
    psnr_value = psnr(img, stego_img)
    
    return {
        'message_length': len(message),
        'payload_bytes': len(payload),
        'payload_bits': len(payload_bits),
        'psnr': psnr_value,
        'embed_time': embed_time
    }


def run_analytics():
    """Run comprehensive PSNR analytics"""
    
    print("\n" + "="*80)
    print("LAYERX STEGANOGRAPHY - PSNR ANALYTICS")
    print("="*80)
    print("\nTesting different payload sizes with cover.png...")
    print("-"*80)
    
    # Test cases: various message sizes
    test_cases = [
        ("Hi", "Tiny (2 chars)"),
        ("Hello!", "Small (6 chars)"),
        ("Hello World!", "Small (12 chars)"),
        ("This is a test message.", "Medium (23 chars)"),
        ("This is a longer test message for steganography.", "Medium (50 chars)"),
        ("The quick brown fox jumps over the lazy dog. " * 2, "Large (92 chars)"),
        ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 3, "Large (174 chars)"),
        ("A" * 50, "50 chars"),
        ("A" * 100, "100 chars"),
        ("A" * 200, "200 chars"),
        ("A" * 500, "500 chars"),
    ]
    
    results = []
    
    for message, description in test_cases:
        try:
            result = test_payload_size(message)
            results.append({
                'description': description,
                'msg_len': result['message_length'],
                'payload': result['payload_bytes'],
                'bits': result['payload_bits'],
                'psnr': result['psnr'],
                'time': result['embed_time']
            })
            print(f"[OK] {description:20s} | Msg: {result['message_length']:4d} | "
                  f"Payload: {result['payload_bytes']:4d} bytes | "
                  f"PSNR: {result['psnr']:6.2f} dB | "
                  f"Time: {result['embed_time']:.3f}s")
        except Exception as e:
            print(f"[!!] {description:20s} | FAILED: {str(e)}")
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    if results:
        avg_psnr = sum(r['psnr'] for r in results) / len(results)
        min_psnr = min(r['psnr'] for r in results)
        max_psnr = max(r['psnr'] for r in results)
        
        print(f"\nTotal Tests:     {len(results)}")
        print(f"Average PSNR:    {avg_psnr:.2f} dB")
        print(f"Minimum PSNR:    {min_psnr:.2f} dB")
        print(f"Maximum PSNR:    {max_psnr:.2f} dB")
        print(f"PSNR Range:      {max_psnr - min_psnr:.2f} dB")
        
        # PSNR Quality Assessment
        print("\n" + "-"*80)
        print("QUALITY ASSESSMENT:")
        print("-"*80)
        
        excellent = sum(1 for r in results if r['psnr'] >= 50)
        good = sum(1 for r in results if 45 <= r['psnr'] < 50)
        acceptable = sum(1 for r in results if 40 <= r['psnr'] < 45)
        poor = sum(1 for r in results if r['psnr'] < 40)
        
        print(f"Excellent (≥50 dB):  {excellent:2d} tests ({excellent/len(results)*100:.1f}%)")
        print(f"Good (45-50 dB):     {good:2d} tests ({good/len(results)*100:.1f}%)")
        print(f"Acceptable (40-45):  {acceptable:2d} tests ({acceptable/len(results)*100:.1f}%)")
        print(f"Poor (<40 dB):       {poor:2d} tests ({poor/len(results)*100:.1f}%)")
        
        # Capacity analysis
        print("\n" + "-"*80)
        print("CAPACITY ANALYSIS:")
        print("-"*80)
        
        max_payload = max(r['payload'] for r in results)
        max_bits = max(r['bits'] for r in results)
        
        print(f"Maximum Payload:     {max_payload} bytes ({max_bits} bits)")
        print(f"Maximum Message:     {max(r['msg_len'] for r in results)} characters")
        
        # Check cover image capacity
        img = read_image("cover.png")
        bands = dwt_decompose(img, levels=2)
        total_coeffs = 0
        for band_name in ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']:
            if band_name in bands:
                band = bands[band_name]
                # Count coefficients (skip first 8 rows/cols)
                total_coeffs += max(0, (band.shape[0] - 8)) * max(0, (band.shape[1] - 8))
        
        print(f"Cover Image Capacity: {total_coeffs} coefficients ({total_coeffs // 8} bytes max)")
        print(f"Utilization:         {max_bits / total_coeffs * 100:.1f}% at maximum test")
        
    print("\n" + "="*80)


if __name__ == "__main__":
    run_analytics()
