"""
LayerX Quick Demo - Shows the complete flow without peer discovery
For testing the pipeline on a single machine
"""

import sys
import os

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract

print("\n" + "="*70)
print("LAYERX QUICK DEMO - Complete Pipeline Test")
print("="*70)

# Check for cover image
if not os.path.exists('test_lena.png'):
    print("\n❌ Error: test_lena.png not found!")
    print("   Please ensure the cover image exists in the current directory.")
    sys.exit(1)

# Step 1: Get user input
print("\n📝 Step 1: Enter your secret message")
message = input("Message: ") or "This is a test message from LayerX!"

# Step 2: Encrypt
print("\n🔐 Step 2: Encrypting with AES-256...")
password = "demo_password_123"
ciphertext, salt, iv = encrypt_message(message, password)
print(f"   ✓ Encrypted: {len(message)} chars → {len(ciphertext)} bytes")
print(f"   Salt: {salt.hex()[:32]}...")
print(f"   IV:   {iv.hex()[:32]}...")

# Step 3: Compress
print("\n🗜️  Step 3: Compressing with Huffman...")
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
print(f"   ✓ Compressed: {len(ciphertext)} → {len(payload)} bytes ({(len(payload)/len(ciphertext)*100):.1f}%)")

# Step 4: Embed
print("\n🖼️  Step 4: Embedding into image...")
stego_path = "demo_stego_output.png"
success = embed(payload, 'test_lena.png', stego_path)

if not success:
    print("   ❌ Embedding failed!")
    sys.exit(1)

print(f"   ✓ Embedded successfully into: {stego_path}")

# Step 5: Extract
print("\n📤 Step 5: Extracting from stego image...")
extracted_payload = extract(stego_path)
print(f"   ✓ Extracted: {len(extracted_payload)} bytes")

# Step 6: Decompress
print("\n🗜️  Step 6: Decompressing...")
msg_len, tree_ext, compressed_ext = parse_payload(extracted_payload)
extracted_ciphertext = decompress_huffman(compressed_ext, tree_ext)
print(f"   ✓ Decompressed: {len(extracted_payload)} → {len(extracted_ciphertext)} bytes")

# Step 7: Decrypt
print("\n🔓 Step 7: Decrypting...")
decrypted_message = decrypt_message(extracted_ciphertext, password, salt, iv)
print(f"   ✓ Decrypted: {len(extracted_ciphertext)} bytes → {len(decrypted_message)} chars")

# Step 8: Verify
print("\n✅ Step 8: Verification")
print("="*70)
print("ORIGINAL MESSAGE:")
print(f"  {message}")
print("\nEXTRACTED MESSAGE:")
print(f"  {decrypted_message}")
print("="*70)

if message == decrypted_message:
    print("\n🎉 SUCCESS! Messages match perfectly!")
    print("\n📊 Summary:")
    print(f"   - Original: {len(message)} chars")
    print(f"   - Encrypted: {len(ciphertext)} bytes")
    print(f"   - Compressed: {len(payload)} bytes")
    print(f"   - Stego image: {stego_path}")
    print(f"   - Extraction: 100% accurate")
else:
    print("\n❌ FAILED! Messages do not match!")
    print(f"   Expected: {message}")
    print(f"   Got:      {decrypted_message}")

print("\n" + "="*70)
print("Demo complete!")
print("="*70)

# Optional: Calculate PSNR
try:
    from a3_image_processing import read_image, psnr
    import numpy as np
    
    original_img = read_image('test_lena.png')
    stego_img = read_image(stego_path)
    psnr_value = psnr(original_img, stego_img)
    
    print(f"\n📊 Image Quality (PSNR): {psnr_value:.2f} dB")
    if psnr_value > 50:
        print("   Quality: Excellent (virtually imperceptible)")
    elif psnr_value > 40:
        print("   Quality: Very Good (minor differences)")
    else:
        print("   Quality: Good (some visible differences)")
except:
    pass

print("\n💡 Next steps:")
print("   - Run 'python sender.py' in one terminal")
print("   - Run 'python receiver.py' in another terminal")
print("   - Try the automatic peer discovery!")
print("\n")
