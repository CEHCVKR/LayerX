"""
Various Test Cases - Different message types and sizes
Tests the system with multiple scenarios
"""

import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract

print("="*70)
print("LAYERX VARIOUS TEST CASES")
print("="*70)

test_cases = [
    ("Short message", "Hi"),
    ("Single character", "X"),
    ("Numbers only", "1234567890"),
    ("Special chars", "!@#$%^&*()_+-={}[]|:;<>?,./"),
    ("Unicode", "Hello 世界 🌍"),
    ("Medium text", "The quick brown fox jumps over the lazy dog. " * 5),
    ("Long text", "This is a longer message to test the system's capacity. " * 20),
    ("Sentence", "This is a test of the LayerX steganographic system."),
    ("With newlines", "Line 1\nLine 2\nLine 3\nLine 4"),
    ("Repeated pattern", "AAAA" * 50),
]

if not os.path.exists('test_lena.png'):
    print("\n[!] Error: test_lena.png not found!")
    sys.exit(1)

passed = 0
failed = 0

for i, (test_name, message) in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"TEST CASE {i}: {test_name}")
    print(f"{'='*70}")
    print(f"Message: '{message[:50]}{'...' if len(message) > 50 else ''}'")
    print(f"Length: {len(message)} characters")
    
    try:
        # Step 1: Encrypt
        password = "test_password_123"
        ciphertext, salt, iv = encrypt_message(message, password)
        print(f"[1/5] Encrypted: {len(message)} chars -> {len(ciphertext)} bytes")
        
        # Step 2: Compress
        compressed, tree = compress_huffman(ciphertext)
        payload = create_payload(ciphertext, tree, compressed)
        compression_ratio = (len(payload) / len(ciphertext)) * 100
        print(f"[2/5] Compressed: {len(ciphertext)} -> {len(payload)} bytes ({compression_ratio:.1f}%)")
        
        # Step 3: Embed
        stego_path = f"test_case_{i}_stego.png"
        success = embed(payload, 'test_lena.png', stego_path)
        
        if not success:
            print(f"[!] FAIL - Embedding failed")
            failed += 1
            continue
        
        print(f"[3/5] Embedded into: {stego_path}")
        
        # Step 4: Extract
        extracted_payload = extract(stego_path)
        print(f"[4/5] Extracted: {len(extracted_payload)} bytes")
        
        # Step 5: Decompress
        msg_len, tree_ext, compressed_ext = parse_payload(extracted_payload)
        extracted_ciphertext = decompress_huffman(compressed_ext, tree_ext)
        print(f"[5/5] Decompressed: {len(extracted_payload)} -> {len(extracted_ciphertext)} bytes")
        
        # Step 6: Decrypt
        decrypted_message = decrypt_message(extracted_ciphertext, password, salt, iv)
        
        # Verify
        if message == decrypted_message:
            print(f"[SUCCESS] Messages match perfectly!")
            passed += 1
            
            # Calculate PSNR
            try:
                from a3_image_processing import read_image, psnr
                original = read_image('test_lena.png')
                stego = read_image(stego_path)
                psnr_val = psnr(original, stego)
                print(f"[*] PSNR Quality: {psnr_val:.2f} dB")
            except:
                pass
            
            # Cleanup
            if os.path.exists(stego_path):
                os.remove(stego_path)
        else:
            print(f"[!] FAIL - Message mismatch!")
            print(f"    Expected: '{message[:50]}...'")
            print(f"    Got:      '{decrypted_message[:50]}...'")
            failed += 1
            
    except Exception as e:
        print(f"[!] FAIL - Exception: {e}")
        failed += 1

# Final Results
print("\n" + "="*70)
print("FINAL TEST RESULTS")
print("="*70)
print(f"[*] Total Tests: {len(test_cases)}")
print(f"[*] Passed: {passed}")
print(f"[*] Failed: {failed}")
print(f"[*] Success Rate: {(passed/len(test_cases)*100):.1f}%")

if failed == 0:
    print("\n[SUCCESS] All test cases passed! System is robust.")
else:
    print(f"\n[WARNING] {failed} test case(s) failed.")

print("="*70)
