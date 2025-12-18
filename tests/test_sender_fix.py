"""
Quick test to verify sender pipeline doesn't crash
"""

import sys
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')
sys.path.append('05. Embedding and Extraction Module')
sys.path.append('06. Optimization Module')

from a1_encryption import encrypt_message
from a2_key_management import generate_ecc_keypair
from a5_embedding_extraction import bytes_to_bits
from a6_optimization import optimize_coefficients_aco
import numpy as np

print("[*] Testing sender pipeline...")

# Test 1: Encryption
message = "Hello World"
password = "test_password_123"
salt, iv, encrypted = encrypt_message(message, password)
print(f"[+] Encryption works: {len(encrypted)} bytes")

# Test 2: Bits conversion
payload_bits = bytes_to_bits(encrypted)
print(f"[+] Bit conversion works: {len(payload_bits)} bits")

# Test 3: ACO optimization
dct_bands = {}
for band_name in ['LH1', 'HL1', 'HH1']:
    dct_bands[band_name] = np.random.randn(100, 100) * 30  # Realistic DCT magnitudes

bit_count = len(payload_bits)
print(f"[*] Calling ACO with bit_count={bit_count} (type: {type(bit_count)})")

try:
    optimized = optimize_coefficients_aco(dct_bands, bit_count)
    print(f"[+] ACO optimization works: {len(optimized)} coefficients selected")
    
    if len(optimized) == 0:
        print(f"[!] WARNING: No coefficients selected (bands may not have suitable magnitudes)")
        print(f"    This is OK - embed_in_dwt_bands will use fixed selection instead")
except TypeError as e:
    print(f"[!] ERROR: {e}")
    print(f"    bit_count type: {type(bit_count)}")
    sys.exit(1)

print(f"\n[SUCCESS] Sender pipeline test passed!")
