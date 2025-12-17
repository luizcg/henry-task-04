import random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def apply(image: Image.Image) -> Image.Image:
    """
    Apply photographed document effect (simulating phone camera).
    
    Effects applied:
    - Perspective transformation (if cv2 available)
    - Uneven lighting/gradient
    - Color temperature shift
    - Slight blur (focus imperfection)
    - Camera noise
    - Shadow on edges
    """
    img = image.copy()
    
    if HAS_CV2:
        img = _apply_perspective(img)
    
    img = _apply_lighting_gradient(img)
    
    img = _apply_color_shift(img)
    
    img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.8)))
    
    img_array = np.array(img)
    noise_intensity = random.uniform(3, 8)
    noise = np.random.normal(0, noise_intensity, img_array.shape).astype(np.int16)
    img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_array)
    
    img = _add_shadow(img)
    
    return img


def _apply_perspective(image: Image.Image) -> Image.Image:
    """Apply slight perspective transformation."""
    if not HAS_CV2:
        return image
    
    img_array = np.array(image)
    height, width = img_array.shape[:2]
    
    skew = random.uniform(0.02, 0.05)
    
    src_points = np.float32([
        [0, 0],
        [width, 0],
        [width, height],
        [0, height]
    ])
    
    dst_points = np.float32([
        [width * skew * random.uniform(0, 1), height * skew * random.uniform(0, 1)],
        [width * (1 - skew * random.uniform(0, 1)), height * skew * random.uniform(0, 1)],
        [width * (1 - skew * random.uniform(0, 1)), height * (1 - skew * random.uniform(0, 1))],
        [width * skew * random.uniform(0, 1), height * (1 - skew * random.uniform(0, 1))]
    ])
    
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    transformed = cv2.warpPerspective(
        img_array, matrix, (width, height),
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255)
    )
    
    return Image.fromarray(transformed)


def _apply_lighting_gradient(image: Image.Image) -> Image.Image:
    """Apply uneven lighting to simulate ambient light."""
    img_array = np.array(image).astype(np.float32)
    height, width = img_array.shape[:2]
    
    gradient_type = random.choice(["corner", "side"])
    
    y, x = np.mgrid[0:height, 0:width]
    
    if gradient_type == "corner":
        corner = random.choice([(0, 0), (0, width), (height, 0), (height, width)])
        dist = np.sqrt((y - corner[0])**2 + (x - corner[1])**2)
        max_dist = np.sqrt(height**2 + width**2)
        gradient = 1 - (dist / max_dist) * random.uniform(0.1, 0.2)
    else:
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            gradient = 1 - (1 - x / width) * random.uniform(0.1, 0.2)
        elif side == "right":
            gradient = 1 - (x / width) * random.uniform(0.1, 0.2)
        elif side == "top":
            gradient = 1 - (1 - y / height) * random.uniform(0.1, 0.2)
        else:
            gradient = 1 - (y / height) * random.uniform(0.1, 0.2)
    
    gradient = gradient[:, :, np.newaxis]
    img_array = img_array * gradient
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    
    return Image.fromarray(img_array)


def _apply_color_shift(image: Image.Image) -> Image.Image:
    """Apply slight color temperature shift."""
    img_array = np.array(image).astype(np.float32)
    
    warm = random.random() > 0.5
    shift_amount = random.uniform(5, 15)
    
    if warm:
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] + shift_amount, 0, 255)
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] - shift_amount * 0.5, 0, 255)
    else:
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] - shift_amount * 0.5, 0, 255)
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] + shift_amount, 0, 255)
    
    return Image.fromarray(img_array.astype(np.uint8))


def _add_shadow(image: Image.Image) -> Image.Image:
    """Add shadow on one or two edges."""
    img_array = np.array(image).astype(np.float32)
    height, width = img_array.shape[:2]
    
    shadow_width = int(min(width, height) * random.uniform(0.05, 0.1))
    edges = random.sample(["left", "right", "top", "bottom"], k=random.randint(1, 2))
    
    for edge in edges:
        for i in range(shadow_width):
            darkness = 0.3 * (1 - i / shadow_width)
            
            if edge == "left":
                img_array[:, i] *= (1 - darkness)
            elif edge == "right":
                img_array[:, -(i+1)] *= (1 - darkness)
            elif edge == "top":
                img_array[i, :] *= (1 - darkness)
            elif edge == "bottom":
                img_array[-(i+1), :] *= (1 - darkness)
    
    return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))
