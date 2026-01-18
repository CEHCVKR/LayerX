"""
Debug tree corruption during embedding/extraction
"""
import sys
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload

# Test payload creation and parsing WITHOUT embedding
test_data = b"Hello"
print(f"Original data: {test_data}")
print(f"Length: {len(test_data)}")

# Compress
compressed, tree = compress_huffman(test_data)
print(f"\nCompressed: {len(compressed)} bytes")
print(f"Tree: {len(tree)} bytes")

# Create payload
payload = create_payload(test_data, tree, compressed)
print(f"\nPayload created: {len(payload)} bytes")

# Parse immediately (without embedding)
msg_len, tree_parsed, compressed_parsed = parse_payload(payload)
print(f"\nParsed msg_len: {msg_len}")
print(f"Parsed tree: {len(tree_parsed)} bytes")
print(f"Parsed compressed: {len(compressed_parsed)} bytes")

# Check if tree is identical
print(f"\nTree identical: {tree == tree_parsed}")
print(f"Compressed identical: {compressed == compressed_parsed}")

# Try decompression
try:
    decompressed = decompress_huffman(compressed_parsed, tree_parsed)
    print(f"\n✅ Decompression successful: {decompressed}")
    print(f"Match: {decompressed == test_data}")
except Exception as e:
    print(f"\n❌ Decompression failed: {e}")

# Now check individual bytes
print(f"\n--- Tree byte comparison (first 20 bytes) ---")
for i in range(min(20, len(tree))):
    if tree[i] != tree_parsed[i]:
        print(f"Byte {i}: Original={tree[i]:02x}, Parsed={tree_parsed[i]:02x} ❌")
    else:
        print(f"Byte {i}: {tree[i]:02x} ✅")
