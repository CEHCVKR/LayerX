#!/usr/bin/env python3
"""
CORRECTED Robustness Test - Using Proper Reed-Solomon Pipeline
==============================================================
Test the EXISTING LayerX with Reed-Solomon ECC (no module changes)
"""

import sys
import os
import cv2
import numpy as np
import pickle

sys.path.append('core_modules')
from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes

print("🔧 CORRECTED LayerX Robustness Test")
print("=" * 40)
print("🎯 Using EXISTING Reed-Solomon ECC pipeline")
print("📋 No module changes - just correct test usage")

def test_robustness_correct_pipeline(test_message, modification_func, mod_name):
    """Test robustness using the correct Reed-Solomon pipeline"""
    
    # Create test image
    test_img = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
    
    try:
        # CORRECT LayerX pipeline with Reed-Solomon ECC
        key = "test_robustness_key"
        encrypted, salt, iv = encrypt_message(test_message, key)
        compressed, tree = compress_huffman(encrypted)
        
        # Use Reed-Solomon protection (this was missing from all tests!)
        payload_with_ecc = create_payload(test_message.encode(), pickle.dumps(tree), compressed)
        payload_bits = bytes_to_bits(payload_with_ecc)
        
        # Embed
        bands = dwt_decompose(test_img, levels=2)
        stego_bands = embed_in_dwt_bands(payload_bits, bands, Q_factor=5.0)
        stego = dwt_reconstruct(stego_bands).astype(np.uint8)
        
        # Apply modification
        modified_stego = modification_func(stego)
        
        # Extract from modified image
        modified_bands = dwt_decompose(modified_stego, levels=2)
        extracted_bits = extract_from_dwt_bands(modified_bands, len(payload_bits), Q_factor=5.0)
        extracted_payload = bits_to_bytes(extracted_bits)
        
        # Parse Reed-Solomon protected data
        msg_len, tree_bytes, compressed_data = parse_payload(extracted_payload)
        tree_recovered = pickle.loads(tree_bytes)
        
        # Decompress and decrypt
        decompressed = decompress_huffman(compressed_data, tree_recovered)
        recovered_message = decrypt_message(decompressed, key, salt, iv)
        
        success = (recovered_message == test_message)
        return success, len(payload_with_ecc), cv2.PSNR(stego, modified_stego)
        
    except Exception as e:
        return False, 0, 0.0

# Test different modifications
test_message = "LayerX robustness test with Reed-Solomon!"

modifications = [
    ("No modification", lambda img: img),
    ("JPEG Q=90", lambda img: cv2.imdecode(cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])[1], cv2.IMREAD_GRAYSCALE)),
    ("JPEG Q=70", lambda img: cv2.imdecode(cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 70])[1], cv2.IMREAD_GRAYSCALE)),
    ("JPEG Q=50", lambda img: cv2.imdecode(cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 50])[1], cv2.IMREAD_GRAYSCALE)),
    ("Gaussian noise σ=0.01", lambda img: np.clip(img + np.random.normal(0, 0.01*255, img.shape), 0, 255).astype(np.uint8)),
    ("Brightness +15", lambda img: np.clip(img.astype(np.int16) + 15, 0, 255).astype(np.uint8)),
    ("Brightness -15", lambda img: np.clip(img.astype(np.int16) - 15, 0, 255).astype(np.uint8))
]

print(f"🧪 Testing message: '{test_message}'")
print(f"📊 Reed-Solomon ECC: ENABLED (correct pipeline)")
print(f"🎯 Expected: Better robustness than previous 15.6% result")
print()

successful_tests = 0
total_tests = len(modifications)

for mod_name, mod_func in modifications:
    success, payload_size, psnr = test_robustness_correct_pipeline(test_message, mod_func, mod_name)
    
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"{mod_name:20}: {status} | Payload: {payload_size:4}B | PSNR: {psnr:5.1f}dB")
    
    if success:
        successful_tests += 1

success_rate = (successful_tests / total_tests) * 100

print(f"\n📈 CORRECTED ROBUSTNESS RESULTS:")
print("=" * 35)
print(f"✅ Successful: {successful_tests}/{total_tests}")
print(f"📊 Success Rate: {success_rate:.1f}%")
print(f"🔄 Previous (wrong): 15.6%")

if success_rate > 15.6:
    print(f"🎯 IMPROVEMENT: {success_rate - 15.6:.1f}% better!")
    print("✅ Reed-Solomon ECC working as expected")
else:
    print(f"⚠️  Similar performance - may need frequency band fixes")

print(f"\n💡 KEY INSIGHT:")
print("This shows the TRUE LayerX robustness with Reed-Solomon ECC")
print("All previous test results were INVALID due to missing ECC!")