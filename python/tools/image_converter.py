from pathlib import Path
from typing import List
from PIL import Image

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

from tools.effects import VisualEffect, apply_effect


def pdf_to_images(
    pdf_path: Path,
    output_dir: Path,
    base_name: str,
    effects: List[VisualEffect] | None = None,
    dpi: int = 200,
) -> List[Path]:
    """
    Convert a PDF to images with optional visual effects.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save images
        base_name: Base name for output files (e.g., "contract_original")
        effects: List of visual effects to apply (generates one image per effect)
        dpi: Resolution for conversion
    
    Returns:
        List of paths to generated images
    """
    if not HAS_PDF2IMAGE:
        raise ImportError(
            "pdf2image is required for PDF conversion. "
            "Install with: pip install pdf2image\n"
            "Also requires poppler: brew install poppler (macOS) or apt-get install poppler-utils (Linux)"
        )
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    effects = effects or [VisualEffect.CLEAN]
    
    pages = convert_from_path(str(pdf_path), dpi=dpi)
    
    if len(pages) == 1:
        base_image = pages[0]
    else:
        total_height = sum(page.height for page in pages)
        max_width = max(page.width for page in pages)
        
        base_image = Image.new('RGB', (max_width, total_height), 'white')
        y_offset = 0
        for page in pages:
            base_image.paste(page, (0, y_offset))
            y_offset += page.height
    
    output_paths = []
    
    for effect in effects:
        processed = apply_effect(base_image, effect)
        
        if effect == VisualEffect.CLEAN:
            filename = f"{base_name}.png"
        else:
            filename = f"{base_name}_{effect.value}.png"
        
        output_path = output_dir / filename
        processed.save(output_path, "PNG")
        output_paths.append(output_path)
    
    return output_paths


def create_preview(image_path: Path, max_size: int = 400) -> Image.Image:
    """Create a thumbnail preview of an image."""
    img = Image.open(image_path)
    img.thumbnail((max_size, max_size))
    return img
