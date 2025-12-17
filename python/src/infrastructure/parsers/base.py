"""Base parser with common functionality."""
import os
import base64
import requests
from pathlib import Path
from typing import Optional, Any
from urllib.parse import urlparse

from src.domain.interfaces import ImageParserStrategy
from src.domain.models import DocumentStructure


def encode_image_base64(image_path: str) -> str:
    """Encode an image file or URL to base64 string."""
    # Check if it's a URL
    if image_path.startswith(('http://', 'https://')):
        response = requests.get(image_path, timeout=30)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    
    # Local file
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_media_type(image_path: str) -> str:
    """Get the media type for an image based on its extension or URL."""
    # Parse URL to get the path
    if image_path.startswith(('http://', 'https://')):
        parsed = urlparse(image_path)
        path = parsed.path
    else:
        path = image_path
    
    ext = Path(path).suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return media_types.get(ext, "image/jpeg")
