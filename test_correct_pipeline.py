#!/usr/bin/env python3
"""
Test CORRECT LayerX Pipeline vs OLD Pipeline
============================================
Compare robustness: Old (no Reed-Solomon) vs New (with Reed-Solomon ECC)
"""

import sys
import os
import cv2
import numpy as np
import pickle

# Import corrected modules
sys.path.append('core_modules')
from a1_encryption import encrypt_message, decrypt_message
from a2_key_management import generate_stego_key
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes

print("🧪 TESTING CORRECT LayerX Pipeline vs OLD Pipeline")
print("=" * 55)
print("🎯 Goal: Validate Reed-Solomon ECC improves robustness")

# Create test image
test_img = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
cv2.imwrite("test_pipeline_image.png", test_img)

# Test payload
test_message = "LayerX pipeline test with Reed-Solomon ECC protection!"
print(f"📝 Test message: '{test_message}'")

print(f"\n🔍 TESTING OLD PIPELINE (No Reed-Solomon):")
print("-" * 45)

try:
    # OLD pipeline
    key = "test_key_12345"
    encrypted_old, salt, iv = encrypt_message(test_message, key)
    compressed_old, tree_old = compress_huffman(encrypted_old)
    payload_bits_old = bytes_to_bits(compressed_old)
    
    print(f"✅ Old pipeline size: {len(compressed_old)} bytes")
    print(f"✅ Old payload bits: {len(payload_bits_old)}")
    
    # Embed old way
    bands = dwt_decompose(test_img, levels=2)
    stego_bands_old = embed_in_dwt_bands(payload_bits_old, bands, Q_factor=5.0)
    stego_old = dwt_reconstruct(stego_bands_old)
    
    # Extract old way
    extracted_bits_old = extract_from_dwt_bands(stego_bands_old, len(payload_bits_old), Q_factor=5.0)
    extracted_compressed_old = bits_to_bytes(extracted_bits_old)
    
    if extracted_compressed_old == compressed_old:
        print("✅ Old pipeline extraction: SUCCESS")
        old_success = True
    else:
        print("❌ Old pipeline extraction: FAILED")
        old_success = False
        
except Exception as e:
    print(f"❌ Old pipeline error: {e}")
    old_success = False

print(f"\n🔍 TESTING NEW PIPELINE (With Reed-Solomon ECC):")
print("-" * 50)

try:
    # NEW pipeline with Reed-Solomon
    key = "test_key_12345"
    encrypted_new, salt, iv = encrypt_message(test_message, key)
    compressed_new, tree_new = compress_huffman(encrypted_new)
    
    # CRITICAL: Use create_payload for Reed-Solomon protection
    payload_with_ecc = create_payload(test_message.encode(), pickle.dumps(tree_new), compressed_new)
    payload_bits_new = bytes_to_bits(payload_with_ecc)
    
    print(f"✅ New pipeline size: {len(payload_with_ecc)} bytes")
    print(f"✅ New payload bits: {len(payload_bits_new)}")
    print(f"📊 Reed-Solomon overhead: {len(payload_with_ecc) - len(compressed_new)} bytes")
    
    # Embed new way
    bands = dwt_decompose(test_img, levels=2)
    stego_bands_new = embed_in_dwt_bands(payload_bits_new, bands, Q_factor=5.0)
    stego_new = dwt_reconstruct(stego_bands_new)
    
    # Extract new way
    extracted_bits_new = extract_from_dwt_bands(stego_bands_new, len(payload_bits_new), Q_factor=5.0)
    extracted_payload_new = bits_to_bytes(extracted_bits_new)
    
    # Parse Reed-Solomon protected payload
    msg_len, tree_bytes, compressed_data = parse_payload(extracted_payload_new)
    tree_recovered = pickle.loads(tree_bytes)
    
    if tree_recovered == tree_new and compressed_data == compressed_new:
        print("✅ New pipeline extraction: SUCCESS")
        new_success = True
    else:
        print("❌ New pipeline extraction: FAILED")
        new_success = False
        
except Exception as e:
    print(f"❌ New pipeline error: {e}")
    new_success = False

print(f"\n📊 COMPARISON RESULTS:")
print("=" * 25)
print(f"Old Pipeline (No ECC): {'✅ SUCCESS' if old_success else '❌ FAILED'}")
print(f"New Pipeline (Reed-Solomon): {'✅ SUCCESS' if new_success else '❌ FAILED'}")

if old_success and new_success:
    print("🎯 READY FOR ROBUSTNESS TESTING!")
    print("   Both pipelines work - can now compare under modifications")
elif new_success:
    print("✅ NEW PIPELINE WORKS - Reed-Solomon ECC functional")
    print("❌ Old pipeline failed - confirms our analysis")
else:
    print("❌ ISSUES FOUND - Need to debug pipelines")

print(f"\n🚀 Next: Run robustness tests with CORRECT pipeline")
print("Expected: Significant robustness improvement with Reed-Solomon ECC")