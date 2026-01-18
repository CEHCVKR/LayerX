#!/usr/bin/env python3
"""
Debug Reed-Solomon ECC Usage
============================
Check if Reed-Solomon is actually being used in the pipeline
"""

import sys
import os
import pickle

sys.path.append('core_modules')
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload

print("🔍 DEBUGGING Reed-Solomon ECC Usage")
print("=" * 40)

# Test 1: Check if create_payload actually adds Reed-Solomon
test_message = b"Test message for Reed-Solomon"
test_tree = b"fake_tree_data"
test_compressed = b"compressed_data_here"

print("📋 Test 1: Reed-Solomon ECC Addition")
print("-" * 35)

# Without Reed-Solomon (just concatenate)
simple_payload = test_message + test_tree + test_compressed
print(f"Simple concatenation: {len(simple_payload)} bytes")

# With Reed-Solomon (using create_payload)
rs_payload = create_payload(test_message, test_tree, test_compressed)
print(f"create_payload(): {len(rs_payload)} bytes")
print(f"Reed-Solomon overhead: {len(rs_payload) - len(simple_payload)} bytes")

if len(rs_payload) > len(simple_payload):
    print("✅ Reed-Solomon ECC appears to be adding overhead")
else:
    print("❌ Reed-Solomon ECC NOT adding protection!")

print(f"\n📋 Test 2: Reed-Solomon Error Correction")
print("-" * 40)

# Test if Reed-Solomon can actually correct errors
try:
    # Parse the payload
    msg_len, tree_recovered, compressed_recovered = parse_payload(rs_payload)
    
    print(f"Original message length: {len(test_message)}")
    print(f"Recovered message length: {msg_len}")
    print(f"Tree data match: {tree_recovered == test_tree}")
    print(f"Compressed data match: {compressed_recovered == test_compressed}")
    
    if tree_recovered == test_tree and compressed_recovered == test_compressed:
        print("✅ Reed-Solomon parsing works correctly")
    else:
        print("❌ Reed-Solomon parsing FAILED")
        
    # Test error correction by corrupting some bytes
    corrupted_payload = bytearray(rs_payload)
    # Corrupt 5 bytes in the middle
    for i in range(len(corrupted_payload)//4, len(corrupted_payload)//4 + 5):
        corrupted_payload[i] = 255
    
    print(f"\n🔧 Testing error correction with 5 corrupted bytes...")
    try:
        msg_len_c, tree_c, compressed_c = parse_payload(bytes(corrupted_payload))
        
        if tree_c == test_tree and compressed_c == test_compressed:
            print("✅ Reed-Solomon ERROR CORRECTION works!")
        else:
            print("❌ Reed-Solomon failed to correct errors")
            
    except Exception as e:
        print(f"❌ Reed-Solomon error correction failed: {e}")
        
except Exception as e:
    print(f"❌ Reed-Solomon parsing failed: {e}")

print(f"\n📋 Test 3: Check Reed-Solomon Codec Settings")
print("-" * 45)

# Check what Reed-Solomon parameters are being used
from a4_compression import get_rs_codec

small_codec = get_rs_codec(100)   # Small data
medium_codec = get_rs_codec(1000) # Medium data  
large_codec = get_rs_codec(5000)  # Large data

print(f"Small data (100B): {small_codec.nsym} parity symbols")
print(f"Medium data (1000B): {medium_codec.nsym} parity symbols")
print(f"Large data (5000B): {large_codec.nsym} parity symbols")
print(f"Max errors correctable: parity_symbols / 2")

print(f"\n💡 ANALYSIS:")
if len(rs_payload) > len(simple_payload) * 2:
    print("⚠️  Reed-Solomon overhead is VERY HIGH")
    print("   This might be causing capacity issues!")
else:
    print("✅ Reed-Solomon overhead seems reasonable")

print(f"\n🎯 CONCLUSION:")
print("If Reed-Solomon is working, robustness should be much better than 14.3%")
print("The fact that brightness changes fail suggests a pipeline bug!")