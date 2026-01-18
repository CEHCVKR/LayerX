"""
Debug tree corruption through embedding/extraction
"""
import sys
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract

# Test with embedding
test_data = b"Hello"
print(f"Original data: {test_data}")

# Compress
compressed, tree = compress_huffman(test_data)
print(f"Compressed: {len(compressed)} bytes")
print(f"Tree: {len(tree)} bytes")

# Create payload
payload = create_payload(test_data, tree, compressed)
print(f"Payload: {len(payload)} bytes ({len(payload)*8} bits)")

# Show original bytes
print(f"\n--- Original Tree (first 30 bytes) ---")
print(' '.join(f"{b:02x}" for b in tree[:30]))

print(f"\n--- Original Compressed ---")
print(' '.join(f"{b:02x}" for b in compressed))

# Embed
embed(payload, 'test_lena.png', 'test_tree_debug.png')
print(f"\n✅ Embedded successfully")

# Extract
extracted = extract('test_tree_debug.png')
print(f"Extracted: {len(extracted)} bytes")

# Parse
msg_len, tree_ext, compressed_ext = parse_payload(extracted)
print(f"Parsed msg_len: {msg_len}")
print(f"Parsed tree: {len(tree_ext)} bytes")
print(f"Parsed compressed: {len(compressed_ext)} bytes")

# Show extracted bytes
print(f"\n--- Extracted Tree (first 30 bytes) ---")
print(' '.join(f"{b:02x}" for b in tree_ext[:30]))

print(f"\n--- Extracted Compressed ---")
print(' '.join(f"{b:02x}" for b in compressed_ext))

# Compare
print(f"\n--- Comparison ---")
print(f"Msg length match: {msg_len == len(test_data)}")
print(f"Tree match: {tree == tree_ext}")
print(f"Compressed match: {compressed == compressed_ext}")

# Count bit errors
tree_errors = 0
for i in range(min(len(tree), len(tree_ext))):
    if tree[i] != tree_ext[i]:
        tree_errors += 1
        if tree_errors <= 10:  # Show first 10 errors
            print(f"  Tree byte {i}: {tree[i]:02x} → {tree_ext[i]:02x} (diff: {tree[i]^tree_ext[i]:08b})")

comp_errors = 0
for i in range(min(len(compressed), len(compressed_ext))):
    if compressed[i] != compressed_ext[i]:
        comp_errors += 1
        print(f"  Compressed byte {i}: {compressed[i]:02x} → {compressed_ext[i]:02x}")

print(f"\nTotal byte errors - Tree: {tree_errors}/{len(tree)}, Compressed: {comp_errors}/{len(compressed)}")

# Try decompression
try:
    decompressed = decompress_huffman(compressed_ext, tree_ext)
    print(f"\n✅ Decompression successful: {decompressed}")
except Exception as e:
    print(f"\n❌ Decompression failed: {e}")
