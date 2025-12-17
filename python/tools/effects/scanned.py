import random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance


def apply(image: Image.Image) -> Image.Image:
    """
    Apply scanned document effect.
    
    Effects applied:
    - Convert to grayscale (optional, 50% chance)
    - Add slight rotation (±1-2 degrees)
    - Add noise/grain
    - Adjust contrast and brightness
    - Add slight blur
    - Add border artifacts
    """
    img = image.copy()
    
    if random.random() > 0.5:
        img = img.convert("L").convert("RGB")
    
    rotation_angle = random.uniform(-2, 2)
    img = img.rotate(rotation_angle, fillcolor=(255, 255, 255), expand=True)
    
    img_array = np.array(img)
    noise_intensity = random.uniform(5, 15)
    noise = np.random.normal(0, noise_intensity, img_array.shape).astype(np.int16)
    img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_array)
    
    contrast_factor = random.uniform(0.9, 1.1)
    brightness_factor = random.uniform(0.95, 1.05)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast_factor)
    
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness_factor)
    
    if random.random() > 0.5:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    img = _add_scan_border(img)
    
    return img


def _add_scan_border(image: Image.Image) -> Image.Image:
    """Add slight dark border to simulate scanner edge."""
    img_array = np.array(image)
    height, width = img_array.shape[:2]
    
    border_width = max(5, int(min(width, height) * 0.01))
    
    for i in range(border_width):
        darkness = int(20 * (1 - i / border_width))
        
        if len(img_array.shape) == 3:
            img_array[:, i] = np.clip(img_array[:, i].astype(np.int16) - darkness, 0, 255)
            img_array[:, -(i+1)] = np.clip(img_array[:, -(i+1)].astype(np.int16) - darkness, 0, 255)
            img_array[i, :] = np.clip(img_array[i, :].astype(np.int16) - darkness, 0, 255)
            img_array[-(i+1), :] = np.clip(img_array[-(i+1), :].astype(np.int16) - darkness, 0, 255)
    
    return Image.fromarray(img_array.astype(np.uint8))
