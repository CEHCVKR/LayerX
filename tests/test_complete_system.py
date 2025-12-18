"""
Complete System Test - Validates entire sender/receiver pipeline
Tests all modules in sequence without peer discovery
"""

import sys
import os
import json

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')
sys.path.append('06. Optimization Module')

from a1_encryption import encrypt_message, decrypt_message
from a2_key_management import generate_ecc_keypair, serialize_public_key, serialize_private_key
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
import numpy as np
import cv2

def write_image(path, img):
    """Write image to file"""
    cv2.imwrite(path, img.astype(np.uint8))
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract
from a6_optimization import optimize_coefficients_aco

print("="*70)
print("LAYERX COMPLETE SYSTEM TEST")
print("="*70)

passed = 0
failed = 0

# Test 1: Encryption Module
print("\n[Test 1] AES-256 Encryption & Decryption")
try:
    test_message = "Hello, this is a secret message!"
    ciphertext, salt, iv = encrypt_message(test_message, "test_password")
    decrypted = decrypt_message(ciphertext, "test_password", salt, iv)
    
    if decrypted == test_message:
        print(f"   ✅ PASS - Encrypted {len(test_message)} chars → {len(ciphertext)} bytes")
        passed += 1
    else:
        print("   ❌ FAIL - Decryption mismatch")
        failed += 1
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    failed += 1

# Test 2: Key Management Module
print("\n[Test 2] ECC Key Generation (SECP256R1)")
try:
    private_key, public_key = generate_ecc_keypair()
    public_pem = serialize_public_key(public_key)
    private_pem = serialize_private_key(private_key)
    
    if len(public_pem) > 100 and len(private_pem) > 100:
        print(f"   ✅ PASS - Generated keypair ({len(public_pem)} + {len(private_pem)} bytes)")
        passed += 1
    else:
        print("   ❌ FAIL - Keys too small")
        failed += 1
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    failed += 1

# Test 3: Image Processing Module  
print("\n[Test 3] DWT Decomposition & Reconstruction")
try:
    if not os.path.exists('test_lena.png'):
        print("   ⚠️  SKIP - test_lena.png not found")
    else:
        img = read_image('test_lena.png')
        bands = dwt_decompose(img, levels=2)
        reconstructed = dwt_reconstruct(bands)
        psnr_value = psnr(img, reconstructed)
        
        if psnr_value > 100:  # Perfect reconstruction should be very high
            print(f"   ✅ PASS - DWT working (PSNR: {psnr_value:.1f} dB)")
            passed += 1
        else:
            print(f"   ❌ FAIL - Poor reconstruction (PSNR: {psnr_value:.1f} dB)")
            failed += 1
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    failed += 1

# Test 4: Compression Module
print("\n[Test 4] Huffman Compression & Decompression")
try:
    test_data = b"AAAAAABBBBBCCCCCDDDDEEEEE" * 10
    compressed, tree = compress_huffman(test_data)
    decompressed = decompress_huffman(compressed, tree)
    
    if decompressed == test_data:
        ratio = (len(compressed) / len(test_data)) * 100
        print(f"   ✅ PASS - Compression ratio: {ratio:.1f}% ({len(test_data)} → {len(compressed)} bytes)")
        passed += 1
    else:
        print("   ❌ FAIL - Decompression mismatch")
        failed += 1
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    failed += 1

# Test 5: Embedding & Extraction  
print("\n[Test 5] Steganographic Embedding & Extraction")
try:
    if not os.path.exists('test_lena.png'):
        print("   ⚠️  SKIP - test_lena.png not found")
    else:
        # Create a small test payload
        test_payload = b"Secret" * 50  # 300 bytes
        compressed, tree = compress_huffman(test_payload)
        payload = create_payload(test_payload, tree, compressed)
        
        # Embed
        success = embed(payload, 'test_lena.png', 'test_system_stego.png')
        
        if not success:
            print("   ❌ FAIL - Embedding failed")
            failed += 1
        else:
            # Extract
            extracted_payload = extract('test_system_stego.png')
            msg_len, tree_ext, compressed_ext = parse_payload(extracted_payload)
            extracted_data = decompress_huffman(compressed_ext, tree_ext)
            
            if extracted_data == test_payload:
                # Check PSNR
                original = read_image('test_lena.png')
                stego = read_image('test_system_stego.png')
                psnr_val = psnr(original, stego)
                
                print(f"   ✅ PASS - Embedded & extracted {len(test_payload)} bytes (PSNR: {psnr_val:.2f} dB)")
                passed += 1
                
                # Cleanup
                os.remove('test_system_stego.png')
            else:
                print(f"   ❌ FAIL - Extraction mismatch (got {len(extracted_data)} bytes)")
                failed += 1
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    import traceback
    traceback.print_exc()
    failed += 1

# Test 6: Complete Pipeline (Encryption → Compression → Embedding → Extraction → Decompression → Decryption)
print("\n[Test 6] Complete End-to-End Pipeline")
try:
    if not os.path.exists('test_lena.png'):
        print("   ⚠️  SKIP - test_lena.png not found")
    else:
        # Original message
        original_msg = "This is a complete end-to-end test of the LayerX system!"
        
        # Step 1: Encrypt
        ciphertext, salt, iv = encrypt_message(original_msg, "pipeline_test")
        
        # Step 2: Compress
        compressed, tree = compress_huffman(ciphertext)
        payload = create_payload(ciphertext, tree, compressed)
        
        # Step 3: Embed
        embed_success = embed(payload, 'test_lena.png', 'test_pipeline_stego.png')
        
        if not embed_success:
            print("   ❌ FAIL - Embedding failed in pipeline")
            failed += 1
        else:
            # Step 4: Extract
            extracted_payload = extract('test_pipeline_stego.png')
            
            # Step 5: Decompress
            msg_len, tree_ext, compressed_ext = parse_payload(extracted_payload)
            extracted_ciphertext = decompress_huffman(compressed_ext, tree_ext)
            
            # Step 6: Decrypt
            decrypted_msg = decrypt_message(extracted_ciphertext, "pipeline_test", salt, iv)
            
            if decrypted_msg == original_msg:
                # Check quality
                original_img = read_image('test_lena.png')
                stego_img = read_image('test_pipeline_stego.png')
                psnr_val = psnr(original_img, stego_img)
                
                print(f"   ✅ PASS - Full pipeline works!")
                print(f"      Message: '{original_msg[:30]}...'")
                print(f"      Pipeline: {len(original_msg)} chars → {len(ciphertext)} → {len(payload)} → Image")
                print(f"      PSNR Quality: {psnr_val:.2f} dB")
                passed += 1
                
                # Cleanup
                os.remove('test_pipeline_stego.png')
            else:
                print(f"   ❌ FAIL - Message mismatch: '{decrypted_msg}'")
                failed += 1
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    import traceback
    traceback.print_exc()
    failed += 1

# Test 7: Peer Discovery (simulation)
print("\n[Test 7] Identity Management")
try:
    import hashlib
    
    # Simulate identity creation
    username = "TestUser"
    priv, pub = generate_ecc_keypair()
    priv_pem = serialize_private_key(priv)
    pub_pem = serialize_public_key(pub)
    address = hashlib.sha256(pub_pem).hexdigest()[:16].upper()
    
    identity = {
        "username": username,
        "address": address,
        "private_key": priv_pem.decode('utf-8'),
        "public_key": pub_pem.decode('utf-8')
    }
    
    if len(address) == 16 and len(identity['public_key']) > 100:
        print(f"   ✅ PASS - Identity created: {username} ({address})")
        passed += 1
    else:
        print("   ❌ FAIL - Invalid identity format")
        failed += 1
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    failed += 1

# Final Results
print("\n" + "="*70)
print("TEST RESULTS")
print("="*70)
print(f"✅ Passed: {passed}/7")
print(f"❌ Failed: {failed}/7")

if failed == 0:
    print("\n🎉 ALL TESTS PASSED! System is fully functional.")
    print("\nYou can now run:")
    print("  - python sender.py   (in Terminal 1)")
    print("  - python receiver.py (in Terminal 2)")
else:
    print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")

print("="*70)
