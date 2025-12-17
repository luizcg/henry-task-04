import random
from io import BytesIO
from PIL import Image


def apply(image: Image.Image) -> Image.Image:
    """
    Apply low resolution effect.
    
    Effects applied:
    - Reduce resolution (downscale then upscale)
    - JPEG compression artifacts
    - Slight color reduction
    """
    img = image.copy()
    original_size = img.size
    
    scale_factor = random.uniform(0.3, 0.5)
    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
    
    img = img.resize(new_size, Image.Resampling.BILINEAR)
    img = img.resize(original_size, Image.Resampling.BILINEAR)
    
    quality = random.randint(30, 60)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    img = Image.open(buffer).convert("RGB")
    
    if random.random() > 0.5:
        img = img.quantize(colors=128).convert("RGB")
    
    return img
