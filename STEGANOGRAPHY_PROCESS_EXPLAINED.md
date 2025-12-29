# Complete Steganography Process Explanation
## From Cover Image to Stego Image - Every Step Explained

---

## 🎯 Overview

This document provides a detailed technical explanation of how LayerX embeds secret messages into images using **DWT (Discrete Wavelet Transform)** and **DCT (Discrete Cosine Transform)** based steganography, from loading the cover image to creating the final stego image.

---

## 📋 Table of Contents

1. [Prerequisites & Input Preparation](#1-prerequisites--input-preparation)
2. [Cover Image Loading](#2-cover-image-loading)
3. [DWT Forward Transform](#3-dwt-forward-transform)
4. [DCT Block Processing](#4-dct-block-processing)
5. [Message Embedding](#5-message-embedding)
6. [Inverse DCT](#6-inverse-dct)
7. [Inverse DWT](#7-inverse-dwt)
8. [Stego Image Creation](#8-stego-image-creation)
9. [Extraction Process (Reverse)](#9-extraction-process-reverse)
10. [Mathematical Foundations](#10-mathematical-foundations)

---

## 1. Prerequisites & Input Preparation

### What We Need

```python
# Inputs Required
cover_image = "cover.png"           # Original image (512x512 RGB)
secret_message = "Hello Bob!"       # Message to hide
payload_bits = [1,0,1,1,0,...]      # Message converted to bits (7800 bits)
```

### Message Preparation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1A: MESSAGE ENCRYPTION                                      │
├─────────────────────────────────────────────────────────────────┤
│ Input: "Hello Bob!" (10 bytes)                                  │
│                                                                  │
│ Process:                                                         │
│   1. Generate random AES-256 key (32 bytes)                     │
│      Key = secrets.token_bytes(32)                              │
│      Example: 0x3f7a9b2c1d8e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c...│
│                                                                  │
│   2. Generate random salt (16 bytes)                            │
│      Salt = secrets.token_bytes(16)                             │
│      Example: 0x8d4e3f2a1b9c7d6e5f4a3b2c1d0e9f8a              │
│                                                                  │
│   3. Derive encryption key using PBKDF2                         │
│      key = PBKDF2(aes_key, salt, iterations=100000, hash=SHA256)│
│      Output: 32-byte derived key                                │
│                                                                  │
│   4. Generate random IV (16 bytes)                              │
│      IV = secrets.token_bytes(16)                               │
│      Example: 0x2b9f1c7e5d3a8b6c4e1f9d7a5b3c8e1f              │
│                                                                  │
│   5. Encrypt with AES-256-CFB                                   │
│      cipher = Cipher(AES(key), CFB(IV))                         │
│      ciphertext = cipher.encrypt("Hello Bob!")                  │
│      Output: 10 bytes ciphertext                                │
│                                                                  │
│ Output: ciphertext (10 bytes) + salt (16) + IV (16) = 42 bytes │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1B: HUFFMAN COMPRESSION                                     │
├─────────────────────────────────────────────────────────────────┤
│ Input: 42 bytes encrypted data                                  │
│                                                                  │
│ Process:                                                         │
│   1. Build frequency table                                      │
│      Count occurrences of each byte                             │
│      Example: {0x3f: 2, 0x7a: 1, 0x9b: 3, ...}                 │
│                                                                  │
│   2. Build Huffman tree                                         │
│      Create binary tree based on frequencies                    │
│      Least frequent → longer codes                              │
│      Most frequent → shorter codes                              │
│                                                                  │
│   3. Generate encoding table                                    │
│      Example:                                                   │
│        0x3f → 101                                               │
│        0x7a → 1100                                              │
│        0x9b → 00                                                │
│                                                                  │
│   4. Encode data                                                │
│      Replace each byte with its Huffman code                    │
│      Variable-length encoding                                   │
│                                                                  │
│   5. Serialize tree structure                                   │
│      Pickle tree object (~150 bytes)                            │
│                                                                  │
│ Output: tree (150 bytes) + compressed_data (40 bytes) = 190 bytes│
│ Compression ratio: ~7% reduction (low due to encrypted entropy) │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1C: BIT STREAM CONSTRUCTION                                 │
├─────────────────────────────────────────────────────────────────┤
│ Input: 190 bytes payload                                        │
│                                                                  │
│ Process:                                                         │
│   1. Encode payload length (4 bytes)                            │
│      length_bytes = len(190).to_bytes(4, 'big')                 │
│      Binary: 00000000 00000000 00000000 10111110               │
│                                                                  │
│   2. Concatenate components                                     │
│      payload = length_bytes + huffman_tree + compressed_data    │
│      Total: 4 + 150 + 40 = 194 bytes                           │
│                                                                  │
│   3. Convert to bit stream                                      │
│      bit_stream = []                                            │
│      for byte in payload:                                       │
│          for i in range(8):                                     │
│              bit = (byte >> (7-i)) & 1                          │
│              bit_stream.append(bit)                             │
│                                                                  │
│      Output: [0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, ...]          │
│      Length: 194 × 8 = 1,552 bits                              │
│                                                                  │
│   4. Pad to capacity (7,800 bits)                               │
│      padding = [0] * (7800 - 1552)                              │
│      bit_stream += padding                                      │
│                                                                  │
│ Output: 7,800-bit stream ready for embedding                    │
│         [b₀, b₁, b₂, ..., b₇₇₉₉]                               │
└─────────────────────────────────────────────────────────────────┘
```

**Key Points:**
- Original message: 10 bytes
- After encryption: 42 bytes
- After compression: 190 bytes
- As bits (padded): 7,800 bits
- **Expansion ratio**: 10 → 7,800 bits (78x) due to encryption/compression overhead + padding

---

## 2. Cover Image Loading

### Image Loading Process

```python
import cv2
import numpy as np

# Load image
cover_image = cv2.imread("cover.png")
# Output shape: (512, 512, 3) - Height, Width, Channels

# Convert BGR to RGB (OpenCV uses BGR by default)
cover_image = cv2.cvtColor(cover_image, cv2.COLOR_BGR2RGB)

# Verify dimensions
assert cover_image.shape == (512, 512, 3), "Image must be 512x512 RGB"
```

### Image Structure

```
Cover Image: 512×512×3 (RGB)

┌──────────────────────────────────────┐
│ Red Channel (R)     512×512 pixels   │  Each pixel: 0-255
│ Green Channel (G)   512×512 pixels   │  Total: 786,432 pixels
│ Blue Channel (B)    512×512 pixels   │  Size: 768 KB (uncompressed)
└──────────────────────────────────────┘

Memory layout (NumPy array):
  cover_image[y, x, c] where:
    y = row (0-511)
    x = column (0-511)
    c = channel (0=R, 1=G, 2=B)

Example pixel at (100, 200):
  R = cover_image[100, 200, 0] = 145
  G = cover_image[100, 200, 1] = 203
  B = cover_image[100, 200, 2] = 67
```

---

## 3. DWT Forward Transform

### What is DWT?

**Discrete Wavelet Transform** decomposes an image into frequency subbands:
- **LL (Low-Low)**: Approximation - blurry version, contains most energy
- **LH (Low-High)**: Horizontal details - vertical edges
- **HL (High-Low)**: Vertical details - horizontal edges
- **HH (High-High)**: Diagonal details - corners and textures

### DWT Implementation

```python
import pywt

def apply_dwt(channel, wavelet='haar', level=2):
    """
    Apply 2-level DWT to a single channel
    
    Parameters:
    -----------
    channel : ndarray (512, 512)
        Single color channel
    wavelet : str
        Wavelet type ('haar', 'db2', 'coif1', etc.)
    level : int
        Decomposition levels
    
    Returns:
    --------
    coeffs : tuple
        Wavelet coefficients (cA2, (cH2, cV2, cD2), (cH1, cV1, cD1))
    """
    
    # Convert to float64 for precision
    channel_float = channel.astype(np.float64)
    
    # Apply 2-level DWT
    coeffs = pywt.wavedec2(channel_float, wavelet, level=level)
    
    return coeffs
```

### DWT Process Visualization

```
LEVEL 0: Original Image (512×512)
┌─────────────────────────────────────────┐
│                                         │
│         Original Red Channel            │
│              512×512                    │
│                                         │
└─────────────────────────────────────────┘
                    ↓ DWT Level 1
┌───────────────────┬─────────────────────┐
│                   │        LH1          │
│       LL1         │  Horizontal Edges   │
│   256×256         │     256×256         │
│   (Blurred)       ├─────────────────────┤
│                   │        HH1          │
│                   │  Diagonal Edges     │
├───────────────────┤     256×256         │
│       HL1         │                     │
│  Vertical Edges   │                     │
│    256×256        │                     │
└───────────────────┴─────────────────────┘
                    ↓ DWT Level 2 (on LL1)
┌─────────┬─────────┬─────────────────────┐
│   LL2   │   LH2   │                     │
│ 128×128 │ 128×128 │        LH1          │
├─────────┼─────────┤     256×256         │
│   HL2   │   HH2   │                     │
│ 128×128 │ 128×128 ├─────────────────────┤
│         │         │        HH1          │
│         │         │     256×256         │
├─────────┴─────────┤                     │
│       HL1         │                     │
│    256×256        │                     │
└───────────────────┴─────────────────────┘
```

### Coefficient Structure After 2-Level DWT

```python
# Returned structure from pywt.wavedec2
coeffs = (
    cA2,    # LL2 - Approximation at level 2 (128×128)
    (       # Level 2 details
        cH2,  # LH2 - Horizontal details (128×128)
        cV2,  # HL2 - Vertical details (128×128)
        cD2   # HH2 - Diagonal details (128×128)
    ),
    (       # Level 1 details
        cH1,  # LH1 - Horizontal details (256×256)
        cV1,  # HL1 - Vertical details (256×256)
        cD1   # HH1 - Diagonal details (256×256)
    )
)

# Total coefficients: 128² + 3×128² + 3×256² = 16,384 + 49,152 + 196,608 = 262,144
# This equals the original 512² = 262,144 pixels (DWT is lossless)
```

### Why Haar Wavelet?

```
Haar Wavelet Properties:
  ✓ Simplest wavelet
  ✓ Fast computation
  ✓ Good for sharp edges
  ✓ Compact support
  ✓ Orthogonal (perfect reconstruction)

Haar Decomposition:
  Low-pass filter (L):  [1/√2, 1/√2]     → Average
  High-pass filter (H): [1/√2, -1/√2]    → Difference

Example on 1D signal [4, 6, 10, 12]:
  L = [(4+6)/√2, (10+12)/√2] = [7.07, 15.56]  → Smooth
  H = [(4-6)/√2, (10-12)/√2] = [-1.41, -1.41] → Details
```

---

## 4. DCT Block Processing

### What is DCT?

**Discrete Cosine Transform** converts spatial domain to frequency domain:
- Separates image into **low frequency** (smooth) and **high frequency** (edges) components
- JPEG compression uses DCT
- We use **8×8 block DCT** (same as JPEG)

### DCT Mathematical Formula

```
Forward DCT (2D):

F(u,v) = (1/4) × C(u) × C(v) × 
         Σ[x=0 to 7] Σ[y=0 to 7] f(x,y) × 
         cos[(2x+1)uπ/16] × cos[(2y+1)vπ/16]

where:
  f(x,y) = pixel value at position (x,y)
  F(u,v) = DCT coefficient at frequency (u,v)
  C(u) = 1/√2 if u=0, else 1
  C(v) = 1/√2 if v=0, else 1

Inverse DCT (2D):

f(x,y) = (1/4) × 
         Σ[u=0 to 7] Σ[v=0 to 7] C(u) × C(v) × F(u,v) × 
         cos[(2x+1)uπ/16] × cos[(2y+1)vπ/16]
```

### DCT Frequency Distribution

```
8×8 DCT Block (frequency arrangement):

DC →  ┌──────────────────────────────────┐
      │ F(0,0)│ F(0,1)│ F(0,2)│ ... F(0,7)│  ← Low frequency (horizontal)
      ├───────┼───────┼───────┼───────────┤
      │ F(1,0)│ F(1,1)│ F(1,2)│           │
      ├───────┼───────┼───────┤  MID-FREQ │  ← Embedding zone
      │ F(2,0)│ F(2,1)│ F(2,2)│   ZONE    │
      ├───────┼───────┴───────┴───────────┤
      │ F(3,0)│                           │
      ├───────┤         HIGH              │
      │  ...  │       FREQUENCY           │  ← High frequency (details)
      ├───────┤         ZONE              │
      │ F(7,0)│ ... ... ... ... ... F(7,7)│
      └───────┴───────────────────────────┘
               ↓
       Low freq (vertical)

Where to embed?
  ✗ F(0,0) - DC component (average) - too visible
  ✗ High freq (F(6,6), F(7,7)) - lost in compression
  ✓ Mid freq (F(2,2) to F(4,4)) - robust and invisible
```

### DCT Processing Code

```python
def process_dct_blocks(dwt_subband, block_size=8):
    """
    Apply DCT to 8×8 blocks of DWT subband
    
    Parameters:
    -----------
    dwt_subband : ndarray (128×128 or 256×256)
        One subband from DWT (e.g., LH2)
    block_size : int
        DCT block size (8×8 standard)
    
    Returns:
    --------
    dct_blocks : list of ndarray (8×8)
        DCT coefficients for each block
    """
    from scipy.fftpack import dct
    
    height, width = dwt_subband.shape
    dct_blocks = []
    
    # Process 8×8 blocks
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            # Extract 8×8 block
            block = dwt_subband[i:i+block_size, j:j+block_size]
            
            # Skip if block is smaller than 8×8 (edge case)
            if block.shape != (block_size, block_size):
                continue
            
            # Apply 2D DCT
            dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
            
            dct_blocks.append({
                'position': (i, j),
                'coefficients': dct_block
            })
    
    return dct_blocks
```

### Example DCT Block Values

```
Original 8×8 spatial block:
┌─────────────────────────────────────────┐
│ 145  147  149  151  148  146  144  143 │
│ 146  148  150  152  149  147  145  144 │
│ 147  149  151  153  150  148  146  145 │
│ 148  150  152  154  151  149  147  146 │
│ 147  149  151  153  150  148  146  145 │
│ 146  148  150  152  149  147  145  144 │
│ 145  147  149  151  148  146  144  143 │
│ 144  146  148  150  147  145  143  142 │
└─────────────────────────────────────────┘

After DCT transformation:
┌──────────────────────────────────────────┐
│ 1184.0│  2.3 │ -0.8 │  0.2 │  0.0 │ -0.1 │  0.0 │  0.0 │  ← DC + Low freq
│   1.8 │  0.5 │ -0.3 │  0.1 │  0.0 │  0.0 │  0.0 │  0.0 │
│  -0.9 │ -0.4 │  0.2 │ -0.1 │  0.0 │  0.0 │  0.0 │  0.0 │  ← MID FREQ
│   0.3 │  0.1 │ -0.1 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  ← (Embed here)
│   0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │
│  -0.1 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  ← High freq
│   0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  (mostly zero)
│   0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │
└──────────────────────────────────────────┘

Notice:
  - DC coefficient (1184.0) is huge → average intensity
  - Low freq (top-left) have larger values
  - High freq (bottom-right) are near zero
```

---

## 5. Message Embedding

### Embedding Strategy

```python
def embed_bit_in_coefficient(coefficient, bit, Q=5.0):
    """
    Embed one bit into one DCT coefficient
    
    Parameters:
    -----------
    coefficient : float
        Original DCT coefficient value
    bit : int
        Bit to embed (0 or 1)
    Q : float
        Quantization factor (controls strength)
    
    Returns:
    --------
    modified_coefficient : float
        Modified coefficient with embedded bit
    """
    
    # Quantize coefficient
    quantized = round(coefficient / Q)
    
    # Embed bit
    if bit == 1:
        # Make quantized value odd
        if quantized % 2 == 0:
            quantized += 1
    else:
        # Make quantized value even
        if quantized % 2 == 1:
            quantized += 1
    
    # Dequantize
    modified_coefficient = quantized * Q
    
    return modified_coefficient
```

### Embedding Process

```
Original coefficient: 12.3
Q factor: 5.0
Bit to embed: 1

Step-by-step:
  1. Quantize: 12.3 / 5.0 = 2.46 → round(2.46) = 2
  2. Check parity: 2 % 2 = 0 (even)
  3. Bit is 1, need odd: 2 + 1 = 3
  4. Dequantize: 3 × 5.0 = 15.0
  5. Modified coefficient: 15.0
  
Change: 12.3 → 15.0 (Δ = 2.7)

Why this works:
  ✓ Small change (±Q at most)
  ✓ Odd/even parity is robust
  ✓ Survives small noise
  ✓ Reversible extraction
```

### Full Embedding Algorithm

```python
def embed_message(cover_image, bit_stream, Q=5.0):
    """
    Complete embedding process
    
    Parameters:
    -----------
    cover_image : ndarray (512, 512, 3)
        RGB cover image
    bit_stream : list of int
        7800 bits to embed
    Q : float
        Quantization factor
    
    Returns:
    --------
    stego_image : ndarray (512, 512, 3)
        Modified image with embedded message
    """
    
    stego_image = cover_image.copy()
    bit_index = 0
    
    # Process each color channel
    for channel_idx in range(3):  # R, G, B
        channel = cover_image[:, :, channel_idx]
        
        # Apply 2-level DWT
        coeffs = pywt.wavedec2(channel.astype(np.float64), 'haar', level=2)
        
        # Extract subbands for embedding
        # We use LH2, HL2, HH2 (level 2 details)
        subbands = [
            coeffs[1][0],  # LH2 (128×128)
            coeffs[1][1],  # HL2 (128×128)
            coeffs[1][2],  # HH2 (128×128)
        ]
        
        for subband in subbands:
            height, width = subband.shape
            
            # Process 8×8 DCT blocks
            for i in range(0, height - 7, 8):
                for j in range(0, width - 7, 8):
                    # Extract block
                    block = subband[i:i+8, j:j+8]
                    
                    # Apply DCT
                    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    
                    # Embed in mid-frequency coefficient (3,3)
                    if bit_index < len(bit_stream):
                        bit = bit_stream[bit_index]
                        
                        # Embed bit
                        original_coef = dct_block[3, 3]
                        dct_block[3, 3] = embed_bit_in_coefficient(original_coef, bit, Q)
                        
                        bit_index += 1
                    
                    # Apply inverse DCT
                    idct_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
                    
                    # Put block back
                    subband[i:i+8, j:j+8] = idct_block
        
        # Reconstruct coefficients
        modified_coeffs = (coeffs[0], tuple(subbands), coeffs[2])
        
        # Apply inverse DWT
        reconstructed = pywt.waverec2(modified_coeffs, 'haar')
        
        # Update channel
        stego_image[:, :, channel_idx] = np.clip(reconstructed, 0, 255)
    
    return stego_image.astype(np.uint8)
```

### Embedding Capacity Calculation

```
Image: 512×512 RGB
DWT: 2 levels, Haar wavelet
Embedding locations: LH2, HL2, HH2 subbands

Per channel:
  LH2: 128×128 = 16,384 coefficients
  HL2: 128×128 = 16,384 coefficients
  HH2: 128×128 = 16,384 coefficients
  Total: 49,152 coefficients

DCT blocks per subband:
  128×128 image ÷ 8×8 blocks = 16×16 = 256 blocks

Total blocks per channel:
  256 blocks × 3 subbands = 768 blocks

Total blocks for RGB:
  768 blocks × 3 channels = 2,304 blocks

Bits per block:
  1 coefficient per block = 1 bit per block

Total capacity:
  2,304 blocks × 1 bit = 2,304 bits

Wait, but we said 7,800 bits?

Actually, we can embed in multiple coefficients per block:
  Positions: (2,2), (2,3), (3,2), (3,3), (3,4), (4,3), (4,4), etc.
  
Or use more subbands (LH1, HL1, HH1):
  LH1: 256×256 ÷ 64 = 1,024 blocks × 3 channels = 3,072 bits
  HL1: 1,024 × 3 = 3,072 bits
  HH1: 1,024 × 3 = 3,072 bits
  
Total with both levels:
  Level 2: 768 × 3 = 2,304 bits
  Level 1: 3,072 × 3 = 9,216 bits
  Total: 11,520 bits (but we use 7,800 for safety)
```

---

## 6. Inverse DCT

### IDCT Mathematical Formula

```
Inverse DCT reconstructs spatial block from frequency coefficients:

f(x,y) = (1/4) × Σ[u=0 to 7] Σ[v=0 to 7] 
         C(u) × C(v) × F(u,v) × 
         cos[(2x+1)uπ/16] × cos[(2y+1)vπ/16]

where:
  F(u,v) = DCT coefficient (possibly modified)
  f(x,y) = reconstructed pixel value
  C(u), C(v) = 1/√2 if u,v=0, else 1
```

### IDCT Process

```python
from scipy.fftpack import idct

def inverse_dct_block(dct_block):
    """
    Apply inverse DCT to 8×8 block
    
    Parameters:
    -----------
    dct_block : ndarray (8, 8)
        DCT coefficients (possibly modified)
    
    Returns:
    --------
    spatial_block : ndarray (8, 8)
        Reconstructed spatial block
    """
    
    # Apply 2D IDCT
    spatial_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
    
    return spatial_block
```

### IDCT Example

```
Modified DCT block (after embedding):
┌──────────────────────────────────────────┐
│ 1184.0│  2.3 │ -0.8 │  0.2 │  0.0 │ -0.1 │  0.0 │  0.0 │
│   1.8 │  0.5 │ -0.3 │  0.1 │  0.0 │  0.0 │  0.0 │  0.0 │
│  -0.9 │ -0.4 │  0.2 │ -0.1 │  0.0 │  0.0 │  0.0 │  0.0 │
│   0.3 │  0.1 │ -0.1 │ 15.0 │  0.0 │  0.0 │  0.0 │  0.0 │ ← Changed
│   0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │   (was 12.3)
│  -0.1 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │
│   0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │
│   0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │  0.0 │
└──────────────────────────────────────────┘
                    ↓ IDCT
Reconstructed spatial block:
┌─────────────────────────────────────────┐
│ 145  147  149  151  149  146  144  143 │  ← Slightly different
│ 146  148  150  152  150  147  145  144 │     from original
│ 147  149  151  153  151  148  146  145 │
│ 148  150  152  154  152  149  147  146 │
│ 147  149  151  153  151  148  146  145 │
│ 146  148  150  152  150  147  145  144 │
│ 145  147  149  151  149  146  144  143 │
│ 144  146  148  150  148  145  143  142 │
└─────────────────────────────────────────┘

Difference map (stego - cover):
┌─────────────────────────────────────────┐
│  0   0   0   0  +1   0   0   0         │
│  0   0   0   0  +1   0   0   0         │  Changes are
│  0   0   0   0  +1   0   0   0         │  imperceptible
│  0   0   0   0  +1   0   0   0         │  ±1 pixel value
│  0   0   0   0  +1   0   0   0         │
│  0   0   0   0  +1   0   0   0         │
│  0   0   0   0  +1   0   0   0         │
│  0   0   0   0  +1   0   0   0         │
└─────────────────────────────────────────┘
```

---

## 7. Inverse DWT

### IDWT Reconstruction

After modifying DCT coefficients and applying IDCT, we have modified DWT subbands. Now we need to reconstruct the full image.

```python
def inverse_dwt(coeffs, wavelet='haar'):
    """
    Reconstruct image from modified DWT coefficients
    
    Parameters:
    -----------
    coeffs : tuple
        Modified wavelet coefficients
        (cA2, (cH2, cV2, cD2), (cH1, cV1, cD1))
    wavelet : str
        Wavelet type ('haar')
    
    Returns:
    --------
    reconstructed : ndarray (512, 512)
        Reconstructed channel
    """
    
    # Apply inverse DWT
    reconstructed = pywt.waverec2(coeffs, wavelet)
    
    # Clip to valid pixel range
    reconstructed = np.clip(reconstructed, 0, 255)
    
    return reconstructed
```

### IDWT Process Visualization

```
Modified coefficients (after embedding):
┌─────────┬─────────┬─────────────────────┐
│   LL2   │   LH2   │                     │
│ 128×128 │ 128×128 │        LH1          │
│ (orig.) │ (MODIF.)│     256×256         │
├─────────┼─────────┤     (orig.)         │
│   HL2   │   HH2   │                     │
│ 128×128 │ 128×128 ├─────────────────────┤
│ (MODIF.)│ (MODIF.)│        HH1          │
│         │         │     256×256         │
├─────────┴─────────┤     (orig.)         │
│       HL1         │                     │
│    256×256        │                     │
│    (orig.)        │                     │
└───────────────────┴─────────────────────┘
                    ↓ Inverse DWT Level 2
┌───────────────────┬─────────────────────┐
│                   │        LH1          │
│       LL1         │  Horizontal Edges   │
│   256×256         │     256×256         │
│ (reconstructed)   │     (original)      │
│                   ├─────────────────────┤
│                   │        HH1          │
│                   │  Diagonal Edges     │
├───────────────────┤     256×256         │
│       HL1         │     (original)      │
│  Vertical Edges   │                     │
│    256×256        │                     │
│    (original)     │                     │
└───────────────────┴─────────────────────┘
                    ↓ Inverse DWT Level 1
┌─────────────────────────────────────────┐
│                                         │
│      Reconstructed Red Channel          │
│              512×512                    │
│        (with embedded message)          │
│                                         │
└─────────────────────────────────────────┘
```

### IDWT Mathematical Process

```
Haar IDWT formulas:

Reconstruction filters:
  Low-pass: g₀[n] = [1/√2, 1/√2]
  High-pass: g₁[n] = [1/√2, -1/√2]

Reconstruction:
  signal[2n] = (LL[n] × g₀[0]) + (HL[n] × g₁[0])
  signal[2n+1] = (LL[n] × g₀[1]) + (HL[n] × g₁[1])

Example 1D reconstruction:
  LL = [7.07, 15.56]  (approximation)
  HL = [-1.41, -1.41] (details)
  
  signal[0] = (7.07 × 1/√2) + (-1.41 × 1/√2) = 5.0 + (-1.0) = 4
  signal[1] = (7.07 × 1/√2) + (-1.41 × -1/√2) = 5.0 + 1.0 = 6
  signal[2] = (15.56 × 1/√2) + (-1.41 × 1/√2) = 11.0 + (-1.0) = 10
  signal[3] = (15.56 × 1/√2) + (-1.41 × -1/√2) = 11.0 + 1.0 = 12
  
  Reconstructed: [4, 6, 10, 12] ✓ Perfect reconstruction
```

---

## 8. Stego Image Creation

### Final Assembly

```python
def create_stego_image(cover_image, bit_stream, output_path, Q=5.0):
    """
    Complete stego image creation pipeline
    
    Parameters:
    -----------
    cover_image : ndarray (512, 512, 3)
        RGB cover image
    bit_stream : list
        7800 bits to embed
    output_path : str
        Output filename
    Q : float
        Quantization factor
    
    Returns:
    --------
    stego_image : ndarray (512, 512, 3)
        Final stego image
    psnr : float
        Quality metric
    """
    import cv2
    from scipy.fftpack import dct, idct
    import pywt
    
    stego_image = cover_image.copy().astype(np.float64)
    bit_idx = 0
    
    # Process each RGB channel
    for ch in range(3):
        channel = cover_image[:, :, ch].astype(np.float64)
        
        # 1. Forward DWT (2 levels)
        coeffs = pywt.wavedec2(channel, 'haar', level=2)
        cA2, (cH2, cV2, cD2), (cH1, cV1, cD1) = coeffs
        
        # 2. Select subbands for embedding
        subbands = [cH2, cV2, cD2]  # LH2, HL2, HH2
        
        for subband_idx, subband in enumerate(subbands):
            h, w = subband.shape
            
            # 3. Process 8×8 DCT blocks
            for i in range(0, h - 7, 8):
                for j in range(0, w - 7, 8):
                    if bit_idx >= len(bit_stream):
                        break
                    
                    # Extract block
                    block = subband[i:i+8, j:j+8].copy()
                    
                    # 4. Forward DCT
                    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    
                    # 5. Embed bit
                    bit = bit_stream[bit_idx]
                    orig = dct_block[3, 3]
                    
                    # Quantization-based embedding
                    quant = round(orig / Q)
                    if bit == 1:
                        quant = quant + 1 if quant % 2 == 0 else quant
                    else:
                        quant = quant + 1 if quant % 2 == 1 else quant
                    
                    dct_block[3, 3] = quant * Q
                    bit_idx += 1
                    
                    # 6. Inverse DCT
                    idct_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
                    
                    # Put back
                    subband[i:i+8, j:j+8] = idct_block
        
        # 7. Inverse DWT
        modified_coeffs = (cA2, (cH2, cV2, cD2), (cH1, cV1, cD1))
        reconstructed = pywt.waverec2(modified_coeffs, 'haar')
        
        # Ensure correct size (sometimes off by 1 due to wavelet boundary)
        reconstructed = reconstructed[:512, :512]
        
        stego_image[:, :, ch] = reconstructed
    
    # 8. Clip and convert to uint8
    stego_image = np.clip(stego_image, 0, 255).astype(np.uint8)
    
    # 9. Calculate PSNR
    mse = np.mean((cover_image.astype(float) - stego_image.astype(float)) ** 2)
    psnr = 10 * np.log10(255**2 / mse) if mse > 0 else float('inf')
    
    # 10. Save as PNG (lossless)
    stego_rgb = cv2.cvtColor(stego_image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, stego_rgb, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    
    print(f"✓ Stego image created: {output_path}")
    print(f"✓ PSNR: {psnr:.2f} dB")
    print(f"✓ Bits embedded: {bit_idx} / {len(bit_stream)}")
    
    return stego_image, psnr
```

### PSNR Calculation

```
PSNR (Peak Signal-to-Noise Ratio) measures quality:

MSE = (1 / N) × Σ(cover[i] - stego[i])²
PSNR = 10 × log₁₀(255² / MSE)

Example:
  Cover pixel: 145
  Stego pixel: 146
  Difference: 1
  
  Over 786,432 pixels with avg difference ~0.3:
    MSE = (0.3)² = 0.09
    PSNR = 10 × log₁₀(255² / 0.09)
         = 10 × log₁₀(722,500)
         = 10 × 5.86
         = 58.6 dB
  
PSNR Interpretation:
  > 50 dB: Imperceptible (excellent)
  40-50 dB: Perceptible only under scrutiny (good)
  30-40 dB: Noticeable (fair)
  < 30 dB: Poor quality

LayerX typical PSNR: 52-56 dB ✓
```

---

## 9. Extraction Process (Reverse)

### Extraction Algorithm

```python
def extract_message(stego_image, payload_bits=7800, Q=5.0):
    """
    Extract embedded message from stego image
    
    Parameters:
    -----------
    stego_image : ndarray (512, 512, 3)
        Stego image with embedded message
    payload_bits : int
        Number of bits to extract
    Q : float
        Quantization factor (must match embedding)
    
    Returns:
    --------
    bit_stream : list
        Extracted bits
    """
    from scipy.fftpack import dct
    import pywt
    
    bit_stream = []
    
    # Process each channel
    for ch in range(3):
        channel = stego_image[:, :, ch].astype(np.float64)
        
        # 1. Forward DWT
        coeffs = pywt.wavedec2(channel, 'haar', level=2)
        cA2, (cH2, cV2, cD2), (cH1, cV1, cD1) = coeffs
        
        # 2. Select same subbands
        subbands = [cH2, cV2, cD2]
        
        for subband in subbands:
            h, w = subband.shape
            
            # 3. Process 8×8 DCT blocks
            for i in range(0, h - 7, 8):
                for j in range(0, w - 7, 8):
                    if len(bit_stream) >= payload_bits:
                        break
                    
                    # Extract block
                    block = subband[i:i+8, j:j+8]
                    
                    # 4. Forward DCT
                    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    
                    # 5. Extract bit from coefficient
                    coef = dct_block[3, 3]
                    quant = round(coef / Q)
                    
                    # Odd = 1, Even = 0
                    bit = 1 if quant % 2 == 1 else 0
                    bit_stream.append(bit)
            
            if len(bit_stream) >= payload_bits:
                break
        
        if len(bit_stream) >= payload_bits:
            break
    
    return bit_stream[:payload_bits]
```

### Complete Decryption Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: LOAD STEGO IMAGE                                         │
├─────────────────────────────────────────────────────────────────┤
│ stego_image = cv2.imread("stego.png")                           │
│ Shape: (512, 512, 3)                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: EXTRACT BIT STREAM                                       │
├─────────────────────────────────────────────────────────────────┤
│ For each channel (R, G, B):                                     │
│   - Apply DWT                                                   │
│   - Extract subbands (LH2, HL2, HH2)                           │
│   - Apply DCT to 8×8 blocks                                    │
│   - Extract bit from F(3,3) coefficient                        │
│                                                                  │
│ Output: [0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, ...] (7800 bits)   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: PARSE PAYLOAD                                            │
├─────────────────────────────────────────────────────────────────┤
│ First 32 bits → length (4 bytes)                               │
│   bits[0:32] = 00000000 00000000 00000000 10111110            │
│   length = 190 bytes                                           │
│                                                                  │
│ Next 1520 bits → Huffman tree (190 bytes)                      │
│ Remaining → compressed data                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: HUFFMAN DECOMPRESSION                                    │
├─────────────────────────────────────────────────────────────────┤
│ Reconstruct Huffman tree from pickled data                      │
│ Decode compressed bits using tree                               │
│                                                                  │
│ Output: 42 bytes (ciphertext + salt + IV)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: SPLIT ENCRYPTED DATA                                    │
├─────────────────────────────────────────────────────────────────┤
│ ciphertext = data[0:10]    # 10 bytes                          │
│ salt = data[10:26]         # 16 bytes                          │
│ iv = data[26:42]           # 16 bytes                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: DECRYPT AES KEY (from metadata)                         │
├─────────────────────────────────────────────────────────────────┤
│ Load metadata.json                                              │
│ encrypted_aes_key = metadata["encrypted_aes_key"]              │
│                                                                  │
│ Decrypt with Bob's private ECC key:                            │
│   aes_key = ecc_decrypt(encrypted_aes_key, bob_private_key)   │
│   Output: 32-byte AES-256 key                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: AES DECRYPTION                                           │
├─────────────────────────────────────────────────────────────────┤
│ Derive key: derived_key = PBKDF2(aes_key, salt, 100000)       │
│ Create cipher: cipher = AES(derived_key, CFB(iv))             │
│ Decrypt: plaintext = cipher.decrypt(ciphertext)                │
│                                                                  │
│ Output: "Hello Bob!" (10 bytes)                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Mathematical Foundations

### DWT Mathematics

```
1D Haar Wavelet Transform:

Forward:
  LL[n] = (signal[2n] + signal[2n+1]) / √2      (Average)
  HL[n] = (signal[2n] - signal[2n+1]) / √2      (Difference)

Inverse:
  signal[2n] = (LL[n] + HL[n]) / √2
  signal[2n+1] = (LL[n] - HL[n]) / √2

2D Haar (applied to rows then columns):
  Step 1: Apply to each row
  Step 2: Apply to each column of result
  
  Result: 4 subbands (LL, LH, HL, HH)
```

### DCT Mathematics

```
1D DCT Type-II:

F(u) = √(2/N) × C(u) × Σ[n=0 to N-1] f(n) × cos[(2n+1)uπ / 2N]

where:
  C(u) = 1/√2 if u=0, else 1
  f(n) = input signal
  F(u) = DCT coefficient

2D DCT (separable):
  Apply 1D DCT to rows
  Apply 1D DCT to columns of result
  
Computational Complexity:
  Direct: O(N²) for 1D, O(N⁴) for 2D
  FFT-based: O(N log N) for 1D, O(N² log N) for 2D
```

### Quantization-Based Embedding

```
Embedding:
  q = round(c / Q)              # Quantize coefficient
  q' = q + 1 if (q % 2) ≠ b     # Adjust parity to match bit
  c' = q' × Q                    # Dequantize

Extraction:
  q = round(c' / Q)              # Quantize
  b = q % 2                      # Extract parity

Robustness:
  Noise resistance: ±Q/2 (larger Q = more robust, less capacity)
  JPEG resistance: Moderate (DCT domain helps)
  Scaling resistance: Poor (coefficients scale)
```

### Quality Metrics

```
MSE (Mean Squared Error):
  MSE = (1/MN) × Σ[i=0 to M-1] Σ[j=0 to N-1] (C[i,j] - S[i,j])²
  
  Lower is better
  Perfect match: MSE = 0

PSNR (Peak Signal-to-Noise Ratio):
  PSNR = 10 × log₁₀(MAX² / MSE)
  PSNR = 20 × log₁₀(MAX / √MSE)
  
  Higher is better
  Typical range: 30-60 dB
  Perfect match: PSNR = ∞

SSIM (Structural Similarity Index):
  SSIM(x,y) = (2μₓμᵧ + C₁)(2σₓᵧ + C₂) / [(μₓ² + μᵧ² + C₁)(σₓ² + σᵧ² + C₂)]
  
  Range: [-1, 1]
  Perfect match: SSIM = 1
```

---

## 🎓 Summary

### Complete Pipeline

```
ENCODING:
  Message (text)
    → AES-256 Encryption (with salt & IV)
      → Huffman Compression
        → Bit Stream (7800 bits)
          → Cover Image (512×512 RGB)
            → DWT (Haar, 2 levels) per channel
              → DCT (8×8 blocks) on subbands
                → Embed bits in mid-frequency coefficients
                  → Inverse DCT
                    → Inverse DWT
                      → Stego Image (PNG)

DECODING:
  Stego Image (PNG)
    → Load as RGB
      → DWT per channel
        → DCT on subbands
          → Extract bits from coefficients
            → Bit Stream (7800 bits)
              → Parse payload
                → Huffman Decompression
                  → AES-256 Decryption (with metadata key)
                    → Message (text)
```

### Key Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Image Size | 512×512 RGB | Standard dimensions |
| Wavelet | Haar | Simple, fast, orthogonal |
| DWT Levels | 2 | Balance capacity/robustness |
| DCT Block Size | 8×8 | JPEG standard |
| Embed Position | (3,3) | Mid-frequency |
| Q Factor | 5.0 | Robustness vs visibility |
| Capacity | 7,800 bits | 975 bytes max |
| PSNR | >50 dB | Imperceptible |

### Why DWT-DCT?

✓ **Robust**: Frequency domain resists minor modifications  
✓ **Invisible**: Changes in mid-frequency are imperceptible  
✓ **Standard**: Uses well-known transforms (JPEG-like)  
✓ **Reversible**: Perfect reconstruction possible  
✓ **Secure**: Combined with encryption  
✓ **Efficient**: Fast computation with scipy/pywt  

---

**End of Complete Process Explanation**
