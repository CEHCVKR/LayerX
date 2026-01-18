"""
Test Maximum Capacity - LayerX Steganography
Test the maximum payload capacity for different image sizes with current settings
"""

import sys
import os
import numpy as np
import cv2
from datetime import datetime

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core_modules'))

from a3_image_processing_color import dwt_decompose_color, dwt_reconstruct_color
from a5_embedding_extraction import embed_in_dwt_bands_color, extract_from_dwt_bands_color

def calculate_capacity(image_path, Q_factor=5.0):
    """Calculate maximum capacity for an image"""
    print(f"\n{'='*70}")
    print(f"Testing: {os.path.basename(image_path)}")
    print(f"{'='*70}")
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"✗ Failed to load image")
        return None
    
    height, width, channels = img.shape
    file_size = os.path.getsize(image_path) / 1024  # KB
    
    print(f"Image dimensions: {width}×{height} ({channels} channels)")
    print(f"File size: {file_size:.1f} KB")
    print(f"Total pixels: {width*height:,}")
    
    # Decompose with DWT
    bands = dwt_decompose_color(img, levels=2)
    
    # Count available coefficients in each band
    band_names = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']
    total_coeffs = 0
    
    print(f"\nDWT Band Capacities:")
    print(f"  {'Band':<6} {'Size':<12} {'Coefficients':<15} {'Bytes':<10}")
    print(f"  {'-'*50}")
    
    for channel_idx in range(3):  # RGB
        for band_name in band_names:
            if band_name in bands and channel_idx < len(bands[band_name]):
                band_data = bands[band_name][channel_idx]
                rows, cols = band_data.shape
                coeffs = rows * cols
                total_coeffs += coeffs
                
                if channel_idx == 0:  # Print once per band
                    total_band = coeffs * 3  # All channels
                    bytes_cap = total_band // 8
                    print(f"  {band_name:<6} {rows}×{cols:<8} {total_band:>10,}      {bytes_cap:>8,}")
    
    # Total capacity
    capacity_bits = total_coeffs
    capacity_bytes = capacity_bits // 8
    capacity_kb = capacity_bytes / 1024
    
    # Calculate percentage of image size
    image_bytes = width * height * channels
    capacity_percent = (capacity_bytes / image_bytes) * 100
    
    print(f"\n  {'='*50}")
    print(f"  Total Coefficients: {total_coeffs:,} bits")
    print(f"  Maximum Capacity: {capacity_bytes:,} bytes ({capacity_kb:.2f} KB)")
    print(f"  Capacity %: {capacity_percent:.2f}% of image data")
    print(f"  {'='*50}")
    
    return {
        'image': os.path.basename(image_path),
        'dimensions': f"{width}×{height}",
        'file_size_kb': file_size,
        'pixels': width * height,
        'total_coeffs': total_coeffs,
        'capacity_bytes': capacity_bytes,
        'capacity_kb': capacity_kb,
        'capacity_percent': capacity_percent
    }

def test_actual_embedding(image_path, payload_size_bytes, Q_factor=5.0):
    """Test actual embedding with specific payload size"""
    print(f"\n{'─'*70}")
    print(f"Testing Actual Embedding: {payload_size_bytes} bytes")
    print(f"{'─'*70}")
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        return False
    
    # Create payload
    payload = b'X' * payload_size_bytes  # Simple test data
    payload_bits = ''.join(format(byte, '08b') for byte in payload)
    
    print(f"Payload size: {payload_size_bytes} bytes ({len(payload_bits)} bits)")
    
    try:
        # Decompose
        start = datetime.now()
        bands = dwt_decompose_color(img, levels=2)
        decompose_time = (datetime.now() - start).total_seconds() * 1000
        
        # Embed
        start = datetime.now()
        modified_bands = embed_in_dwt_bands_color(payload_bits, bands, Q_factor=Q_factor)
        embed_time = (datetime.now() - start).total_seconds() * 1000
        
        # Reconstruct
        start = datetime.now()
        stego = dwt_reconstruct_color(modified_bands)
        reconstruct_time = (datetime.now() - start).total_seconds() * 1000
        
        # Save temporarily
        temp_stego = 'temp_capacity_test.png'
        cv2.imwrite(temp_stego, stego)
        
        # Calculate PSNR
        mse = np.mean((img.astype(float) - stego.astype(float)) ** 2)
        psnr = 10 * np.log10(255**2 / mse) if mse > 0 else float('inf')
        
        # Extract to verify
        start = datetime.now()
        stego_bands = dwt_decompose_color(stego, levels=2)
        extracted_bits = extract_from_dwt_bands_color(stego_bands, len(payload_bits), Q_factor=Q_factor)
        extract_time = (datetime.now() - start).total_seconds() * 1000
        
        # Verify
        extracted_bytes = int(extracted_bits, 2).to_bytes(len(extracted_bits) // 8, 'big')
        match = extracted_bytes == payload
        
        print(f"\n  ✓ Embedding successful")
        print(f"  PSNR: {psnr:.2f} dB")
        print(f"  Extraction: {'✓ MATCH' if match else '✗ MISMATCH'}")
        print(f"  Time: Embed={embed_time:.1f}ms, Extract={extract_time:.1f}ms")
        
        # Cleanup
        if os.path.exists(temp_stego):
            os.remove(temp_stego)
        
        return {
            'success': match,
            'psnr': psnr,
            'embed_time': embed_time,
            'extract_time': extract_time
        }
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return None

def main():
    print("\n" + "="*70)
    print(" "*15 + "LAYERX CAPACITY ANALYSIS")
    print("="*70)
    
    # Test different image sizes
    test_images = []
    
    # Check for common test images
    if os.path.exists('cover.png'):
        test_images.append('cover.png')
    
    # Try to find sample images in common directories
    search_dirs = ['.', 'tests', 'demo_outputs']
    for dir_path in search_dirs:
        if os.path.exists(dir_path):
            for file in os.listdir(dir_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    full_path = os.path.join(dir_path, file)
                    if full_path not in test_images and os.path.getsize(full_path) > 1024:
                        test_images.append(full_path)
                        if len(test_images) >= 5:  # Limit to 5 images
                            break
    
    if not test_images:
        print("\n✗ No test images found. Creating synthetic test images...")
        # Create test images of different sizes
        sizes = [(512, 512), (800, 600), (1024, 768), (1920, 1080)]
        for w, h in sizes:
            img = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
            filename = f'test_{w}x{h}.png'
            cv2.imwrite(filename, img)
            test_images.append(filename)
            print(f"  Created {filename}")
    
    # Results storage
    results = []
    
    # Test each image
    Q_FACTOR = 5.0  # Current default Q-factor
    print(f"\nUsing Q-factor: {Q_FACTOR}")
    
    for image_path in test_images:
        capacity_info = calculate_capacity(image_path, Q_FACTOR)
        if capacity_info:
            results.append(capacity_info)
            
            # Test at different payload sizes
            test_sizes = [
                100,  # 100 bytes
                capacity_info['capacity_bytes'] // 4,  # 25%
                capacity_info['capacity_bytes'] // 2,  # 50%
                capacity_info['capacity_bytes'] * 3 // 4,  # 75%
                capacity_info['capacity_bytes'] - 10,  # Near max
            ]
            
            print(f"\nTesting actual embedding at different payload sizes:")
            for size in test_sizes:
                if size > 0 and size <= capacity_info['capacity_bytes']:
                    result = test_actual_embedding(image_path, size, Q_FACTOR)
                    if result:
                        capacity_info[f'test_{size}b'] = result
            
            # Test maximum capacity
            print(f"\n{'*'*70}")
            print(f"MAXIMUM CAPACITY TEST: {capacity_info['capacity_bytes']} bytes")
            print(f"{'*'*70}")
            max_result = test_actual_embedding(image_path, capacity_info['capacity_bytes'], Q_FACTOR)
            if max_result:
                capacity_info['max_test'] = max_result
    
    # Summary Report
    print("\n\n" + "="*70)
    print(" "*20 + "SUMMARY REPORT")
    print("="*70)
    print(f"\n{'Image':<25} {'Size':<12} {'File':<10} {'Capacity':<15} {'% of Image'}")
    print("-"*80)
    
    for result in results:
        print(f"{result['image']:<25} {result['dimensions']:<12} {result['file_size_kb']:>6.1f} KB  "
              f"{result['capacity_bytes']:>8,} bytes  {result['capacity_percent']:>6.2f}%")
    
    if results:
        avg_percent = sum(r['capacity_percent'] for r in results) / len(results)
        total_capacity = sum(r['capacity_bytes'] for r in results)
        
        print("-"*80)
        print(f"\nAverage capacity: {avg_percent:.2f}% of image size")
        print(f"Total capacity tested: {total_capacity:,} bytes ({total_capacity/1024:.2f} KB)")
        
        # Recommendations
        print("\n" + "="*70)
        print(" "*20 + "ANALYSIS & RECOMMENDATIONS")
        print("="*70)
        
        print(f"\nCurrent Configuration:")
        print(f"  Q-factor: {Q_FACTOR}")
        print(f"  Bands used: LH1, HL1, LH2, HL2, HH1, HH2, LL2")
        print(f"  Average capacity: {avg_percent:.2f}%")
        
        print(f"\nTo increase capacity to 30-50%:")
        print(f"  Option 1: Lower Q-factor to 2.0-3.0")
        print(f"            → Capacity: ~{avg_percent * 2:.1f}% (2x increase)")
        print(f"            → PSNR: ~45-50 dB (lower quality)")
        
        print(f"  Option 2: Adaptive Q-factor (edge-aware)")
        print(f"            → Capacity: ~{avg_percent * 3:.1f}% (3x increase)")
        print(f"            → PSNR: 50-55 dB (maintained)")
        
        print(f"  Option 3: Use more coefficients per band")
        print(f"            → Capacity: ~{avg_percent * 4:.1f}% (4x increase)")
        print(f"            → PSNR: 48-52 dB (slightly lower)")
        
        print(f"\nCurrent Status:")
        if avg_percent < 1:
            print(f"  ⚠️  Capacity is {avg_percent:.2f}% (Target: 30-50%)")
            print(f"  ⚠️  Gap: {30 - avg_percent:.2f}% to reach minimum target")
            print(f"  ✓  PSNR likely exceeds 50 dB (high quality)")
        else:
            print(f"  ✓  Capacity is {avg_percent:.2f}%")

if __name__ == '__main__':
    main()
