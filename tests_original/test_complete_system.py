"""
Final end-to-end test of the fixed system
Tests multiple message sizes
"""
from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands, bytes_to_bits, bits_to_bytes
import cv2

def test_message(message, cover_path="cover.png"):
    """Test a single message through the complete pipeline"""
    print(f"\n{'='*70}")
    print(f"Testing: '{message}'")
    print('='*70)
    
    # Encrypt
    ciphertext, salt, iv = encrypt_message(message, "temp_password")
    print(f"[OK] Encrypted: {len(ciphertext)} bytes")
    
    # Compress
    compressed, tree = compress_huffman(ciphertext)
    payload = create_payload(ciphertext, tree, compressed)
    print(f"[OK] Compressed: {len(payload)} bytes")
    
    # Embed
    img = read_image(cover_path)
    bands = dwt_decompose(img, levels=2)
    payload_bits = bytes_to_bits(payload)
    modified_bands = embed_in_dwt_bands(payload_bits, bands, optimization='fixed')
    stego_img = dwt_reconstruct(modified_bands)
    psnr_value = psnr(img, stego_img)
    print(f"[OK] Embedded: {len(payload_bits)} bits, PSNR: {psnr_value:.2f} dB")
    
    # Save and reload (simulate network transfer)
    cv2.imwrite("temp_stego.png", stego_img.astype('uint8'))
    stego_loaded = read_image("temp_stego.png")
    
    # Extract
    bands_loaded = dwt_decompose(stego_loaded, levels=2)
    extracted_bits = extract_from_dwt_bands(bands_loaded, len(payload_bits), optimization='fixed')
    extracted_payload = bits_to_bytes(extracted_bits)
    print(f"[OK] Extracted: {len(extracted_payload)} bytes")
    
    # Decompress
    msg_len, tree, compressed = parse_payload(extracted_payload)
    decrypted_ciphertext = decompress_huffman(compressed, tree)
    print(f"[OK] Decompressed")
    
    # Decrypt
    decrypted_message = decrypt_message(decrypted_ciphertext, "temp_password", salt, iv)
    print(f"[OK] Decrypted: '{decrypted_message}'")
    
    # Verify
    if decrypted_message == message:
        print(f"[SUCCESS] Message recovered perfectly!")
        return True
    else:
        print(f"[FAILED] Got '{decrypted_message}' instead of '{message}'")
        return False

# Run tests
print("\n" + "="*70)
print("LAYERX STEGANOGRAPHIC SYSTEM - END-TO-END TESTS")
print("="*70)

test_messages = [
    "Hi",
    "Hello",
    "HOLAAAA",
    "This is a test message!",
    "Testing with numbers: 123456",
    "Special chars: !@#$%^&*()",
    "A longer message to test the system with more content and see how it handles various lengths.",
]

results = []
for msg in test_messages:
    try:
        success = test_message(msg)
        results.append((msg, success))
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append((msg, False))

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
passed = sum(1 for _, success in results if success)
total = len(results)
print(f"Passed: {passed}/{total}")

for msg, success in results:
    status = "[OK]" if success else "[FAIL]"
    print(f"  {status} {msg[:50]}")

if passed == total:
    print("\n[SUCCESS] ALL TESTS PASSED! System is working correctly.")
else:
    print(f"\n[WARNING] {total - passed} test(s) failed.")
