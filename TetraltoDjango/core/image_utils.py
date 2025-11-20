"""
Image conversion utilities for the customer portal.

Handles conversion of HEIC images to JPEG for universal browser compatibility.
"""

import io
import logging
from typing import Tuple, Optional
from PIL import Image
import pillow_heif

logger = logging.getLogger(__name__)

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()


def is_heic_format(mime_type: str) -> bool:
    """
    Check if the MIME type represents a HEIC/HEIF image.
    
    Args:
        mime_type: MIME type string from Google Drive
        
    Returns:
        True if HEIC/HEIF format, False otherwise
    """
    heic_mime_types = [
        'image/heic',
        'image/heif',
        'image/heic-sequence',
        'image/heif-sequence'
    ]
    return mime_type.lower() in heic_mime_types


def convert_heic_to_jpeg(heic_bytes: bytes, quality: int = 90) -> Tuple[bytes, str]:
    """
    Convert HEIC image bytes to JPEG format.
    
    Args:
        heic_bytes: Raw HEIC image data
        quality: JPEG quality (1-100, default 90 for high quality)
        
    Returns:
        Tuple of (jpeg_bytes, mime_type)
        
    Raises:
        Exception: If conversion fails
    """
    try:
        # Load HEIC image
        heic_image = Image.open(io.BytesIO(heic_bytes))
        
        # Convert to RGB if necessary (HEIC can have various color modes)
        if heic_image.mode not in ('RGB', 'L'):
            heic_image = heic_image.convert('RGB')
        
        # Strip EXIF data for privacy/security
        # Create new image without EXIF metadata
        data = list(heic_image.getdata())
        image_without_exif = Image.new(heic_image.mode, heic_image.size)
        image_without_exif.putdata(data)
        
        # Convert to JPEG
        jpeg_buffer = io.BytesIO()
        image_without_exif.save(
            jpeg_buffer,
            format='JPEG',
            quality=quality,
            optimize=True
        )
        
        jpeg_buffer.seek(0)
        jpeg_bytes = jpeg_buffer.read()
        
        logger.info(f"Successfully converted HEIC to JPEG (size: {len(heic_bytes)} -> {len(jpeg_bytes)} bytes)")
        
        return jpeg_bytes, 'image/jpeg'
        
    except Exception as e:
        logger.error(f"Failed to convert HEIC to JPEG: {e}")
        raise


def convert_image_if_needed(
    file_content: bytes,
    mime_type: str,
    quality: int = 90
) -> Tuple[bytes, str]:
    """
    Convert image to browser-compatible format if needed.
    
    Currently handles HEIC -> JPEG conversion. Other formats pass through unchanged.
    
    Args:
        file_content: Raw image file bytes
        mime_type: Original MIME type
        quality: JPEG quality for conversions (default 90)
        
    Returns:
        Tuple of (converted_bytes, final_mime_type)
    """
    if is_heic_format(mime_type):
        logger.info(f"Detected HEIC format ({mime_type}), converting to JPEG")
        return convert_heic_to_jpeg(file_content, quality=quality)
    
    # Pass through other formats unchanged
    return file_content, mime_type
