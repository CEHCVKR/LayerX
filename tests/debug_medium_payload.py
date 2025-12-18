"""
Debug medium payload to see bit error rate
"""
import sys
sys.path.append('01. Encryption Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import encrypt_message
from a4_compression import compress_huffman, create_payload, parse_payload, RS_CODEC
from a5_embedding_extraction import embed, extract

# Test with medium message
message = "A" * 100
password = "test123"

ciphertext, salt, iv = encrypt_message(message, password)
compressed, tree = compress_huffman(ciphertext)

print(f"Ciphertext: {len(ciphertext)} bytes")
print(f"Compressed: {len(compressed)} bytes")
print(f"Tree (original): {len(tree)} bytes")

# Check tree ECC
tree_with_ecc = RS_CODEC.encode(tree)
print(f"Tree (with ECC): {len(tree_with_ecc)} bytes (+{len(tree_with_ecc)-len(tree)} ECC bytes)")

payload = create_payload(ciphertext, tree, compressed)
print(f"Total payload: {len(payload)} bytes ({len(payload)*8} bits)")

# Embed
embed(payload, 'test_lena.png', 'test_medium_debug.png')
print("✅ Embedded")

# Extract
extracted = extract('test_medium_debug.png')
print(f"Extracted: {len(extracted)} bytes")

# Check byte-level errors before ECC decoding
msg_len_ext = int.from_bytes(extracted[0:4], 'little')
tree_ecc_len_ext = int.from_bytes(extracted[4:8], 'little')

print(f"\nExtracted lengths:")
print(f"  msg_len: {msg_len_ext}")
print(f"  tree_ecc_len: {tree_ecc_len_ext}")

tree_with_ecc_ext = extracted[8:8+tree_ecc_len_ext]
print(f"  tree_with_ecc: {len(tree_with_ecc_ext)} bytes")

# Compare byte errors
errors = 0
for i in range(min(len(tree_with_ecc), len(tree_with_ecc_ext))):
    if tree_with_ecc[i] != tree_with_ecc_ext[i]:
        errors += 1

print(f"\n❌ Byte errors in tree: {errors}/{len(tree_with_ecc)} ({errors/len(tree_with_ecc)*100:.2f}%)")
print(f"RS_CODEC can fix: up to 25 byte errors")

if errors > 25:
    print(f"⚠️  ERROR: {errors} errors exceeds RS capacity (25)")
else:
    print(f"✅ Should be fixable by RS")

# Try decoding
try:
    tree_decoded = RS_CODEC.decode(tree_with_ecc_ext)[0]
    print(f"\n✅ ECC decoding successful!")
    print(f"Tree match: {tree_decoded == tree}")
except Exception as e:
    print(f"\n❌ ECC decoding failed: {e}")
