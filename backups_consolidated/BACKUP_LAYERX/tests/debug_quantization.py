"""
Debug quantization embedding/extraction
"""
import numpy as np

Q = 5.0

# Test a few sample coefficients
test_coeffs = [10.5, -15.3, 0.8, 100.2, -50.7, 3.2, -7.8]

print("Testing quantization with Q =", Q)
print("="*70)

for orig_coeff in test_coeffs:
    print(f"\nOriginal coefficient: {orig_coeff:.2f}")
    
    # Test embedding bit '0'
    quantized_0 = Q * round(orig_coeff / Q)
    q_level_0 = round(quantized_0 / Q)
    if q_level_0 % 2 == 1:  # Should be even for '0'
        quantized_0 = quantized_0 + Q if quantized_0 >= 0 else quantized_0 - Q
    
    # Extraction
    extracted_q_level_0 = round(quantized_0 / Q)
    extracted_bit_0 = '1' if extracted_q_level_0 % 2 == 1 else '0'
    
    print(f"  Embed '0': {orig_coeff:.2f} → {quantized_0:.2f} (q_level={round(quantized_0/Q)}) → extract '{extracted_bit_0}'")
    
    # Test embedding bit '1'
    quantized_1 = Q * round(orig_coeff / Q)
    q_level_1 = round(quantized_1 / Q)
    if q_level_1 % 2 == 0:  # Should be odd for '1'
        quantized_1 = quantized_1 + Q if quantized_1 >= 0 else quantized_1 - Q
    
    # Extraction
    extracted_q_level_1 = round(quantized_1 / Q)
    extracted_bit_1 = '1' if extracted_q_level_1 % 2 == 1 else '0'
    
    print(f"  Embed '1': {orig_coeff:.2f} → {quantized_1:.2f} (q_level={round(quantized_1/Q)}) → extract '{extracted_bit_1}'")
    
    # Check if round-trip works
    if extracted_bit_0 != '0':
        print(f"  ❌ ERROR: Bit '0' extracted as '{extracted_bit_0}'")
    if extracted_bit_1 != '1':
        print(f"  ❌ ERROR: Bit '1' extracted as '{extracted_bit_1}'")

print("\n" + "="*70)
print("Testing simple byte round-trip")
print("="*70)

# Test a simple byte
test_byte = 0x10  # Binary: 00010000
test_bits = format(test_byte, '08b')
print(f"Test byte: 0x{test_byte:02x} = {test_bits}")

# Simulate embedding
coeffs = [10.0 + i * 2.5 for i in range(8)]
print(f"\nOriginal coefficients: {[f'{c:.1f}' for c in coeffs]}")

embedded_coeffs = []
for i, bit in enumerate(test_bits):
    coeff = coeffs[i]
    quantized = Q * round(coeff / Q)
    
    if bit == '1':
        q_level = round(quantized / Q)
        if q_level % 2 == 0:
            quantized = quantized + Q if quantized >= 0 else quantized - Q
    else:  # bit == '0'
        q_level = round(quantized / Q)
        if q_level % 2 == 1:
            quantized = quantized + Q if quantized >= 0 else quantized - Q
    
    embedded_coeffs.append(quantized)

print(f"Embedded coefficients: {[f'{c:.1f}' for c in embedded_coeffs]}")

# Extract bits
extracted_bits = []
for coeff in embedded_coeffs:
    q_level = round(coeff / Q)
    extracted_bits.append('1' if q_level % 2 == 1 else '0')

extracted_bits_str = ''.join(extracted_bits)
extracted_byte = int(extracted_bits_str, 2)

print(f"Extracted bits: {extracted_bits_str}")
print(f"Extracted byte: 0x{extracted_byte:02x}")
print(f"Match: {extracted_byte == test_byte} {'✅' if extracted_byte == test_byte else '❌'}")
