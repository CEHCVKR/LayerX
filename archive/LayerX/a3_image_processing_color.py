"""
Color Image Steganography Support
- Process each RGB channel independently
- Maintains visual quality with color preservation
"""

import numpy as np
import pywt
import cv2
from typing import Dict, Tuple
from skimage.metrics import peak_signal_noise_ratio

def read_image_color(path: str) -> np.ndarray:
    """
    Read image in color (BGR format).
    
    Args:
        path (str): Path to image file
        
    Returns:
        numpy.ndarray: Color image as uint8 array (H x W x 3)
    """
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    
    return image.astype(np.uint8)


def dwt_decompose_color(image: np.ndarray, levels: int = 2) -> Dict[str, np.ndarray]:
    """
    Apply DWT to each RGB channel separately.
    
    Args:
        image: Color image (H x W x 3)
        levels: DWT decomposition levels
        
    Returns:
        Dict with band names -> 3-channel arrays
    """
    if len(image.shape) != 3:
        raise ValueError("Expected color image with 3 channels")
    
    channels = cv2.split(image)  # Split into B, G, R
    
    # Decompose each channel
    channel_bands = []
    for channel in channels:
        bands = {}
        coeffs = pywt.wavedec2(channel.astype('float'), 'haar', level=levels)
        
        # Extract bands
        bands['LL2'] = coeffs[0]
        bands['LH2'], bands['HL2'], bands['HH2'] = coeffs[1]
        bands['LH1'], bands['HL1'], bands['HH1'] = coeffs[2]
        
        channel_bands.append(bands)
    
    # Merge channels - create 3D arrays for each band
    merged_bands = {}
    for band_name in ['LL2', 'LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2']:
        # Stack channels: shape becomes (H, W, 3)
        merged_bands[band_name] = np.stack([
            channel_bands[0][band_name],
            channel_bands[1][band_name],
            channel_bands[2][band_name]
        ], axis=2)
    
    return merged_bands


def dwt_reconstruct_color(bands: Dict[str, np.ndarray]) -> np.ndarray:
    """
    Reconstruct color image from DWT bands.
    
    Args:
        bands: Dict with band names -> 3-channel arrays
        
    Returns:
        Color image (H x W x 3)
    """
    # Split bands back into channels
    channel_bands = [
        {
            'LL2': bands['LL2'][:, :, i],
            'LH2': bands['LH2'][:, :, i],
            'HL2': bands['HL2'][:, :, i],
            'HH2': bands['HH2'][:, :, i],
            'LH1': bands['LH1'][:, :, i],
            'HL1': bands['HL1'][:, :, i],
            'HH1': bands['HH1'][:, :, i]
        }
        for i in range(3)  # B, G, R channels
    ]
    
    # Reconstruct each channel
    reconstructed_channels = []
    for ch_bands in channel_bands:
        coeffs = [
            ch_bands['LL2'],
            (ch_bands['LH2'], ch_bands['HL2'], ch_bands['HH2']),
            (ch_bands['LH1'], ch_bands['HL1'], ch_bands['HH1'])
        ]
        
        reconstructed = pywt.waverec2(coeffs, 'haar')
        reconstructed_channels.append(reconstructed)
    
    # Merge channels back to BGR
    image = np.stack(reconstructed_channels, axis=2)
    image = np.clip(image, 0, 255)
    
    return image.astype(np.uint8)


def psnr_color(original: np.ndarray, modified: np.ndarray) -> float:
    """
    Calculate PSNR for color images.
    
    Args:
        original: Original color image
        modified: Modified color image
        
    Returns:
        PSNR value in dB
    """
    return peak_signal_noise_ratio(original, modified, data_range=255)


def save_image_color(path: str, image: np.ndarray):
    """Save color image."""
    cv2.imwrite(path, image.astype('uint8'))
    print(f"Saved: {path}")
