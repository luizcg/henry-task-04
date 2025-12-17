from enum import Enum
from typing import Callable
from PIL import Image


class VisualEffect(str, Enum):
    CLEAN = "clean"
    SCANNED = "scanned"
    PHOTOGRAPHED = "photographed"
    LOWRES = "lowres"
    
    @classmethod
    def all(cls) -> list["VisualEffect"]:
        return list(cls)
    
    @classmethod
    def choices(cls) -> list[str]:
        return [e.value for e in cls]


def apply_effect(image: Image.Image, effect: VisualEffect) -> Image.Image:
    """Apply a visual effect to an image."""
    from tools.effects import scanned, photographed, lowres
    
    if effect == VisualEffect.CLEAN:
        return image
    elif effect == VisualEffect.SCANNED:
        return scanned.apply(image)
    elif effect == VisualEffect.PHOTOGRAPHED:
        return photographed.apply(image)
    elif effect == VisualEffect.LOWRES:
        return lowres.apply(image)
    else:
        return image
