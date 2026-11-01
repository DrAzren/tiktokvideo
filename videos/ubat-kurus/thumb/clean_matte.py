"""Trim matte leaks from the cover cutout: the car headrest left of the head (x<228, y 900-1115)
and the faint window/pillar ghost right of the head (x>925, y<1170). Feathered 6 px."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
D = Path(__file__).parent
im = Image.open(D / "speaker.png").convert("RGBA")
a = np.asarray(im)[..., 3].astype(np.float32)
kill = np.zeros_like(a)
kill[900:1115, :228] = 1
kill[:1170, 925:] = 1
kill = np.asarray(Image.fromarray((kill * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
out = np.asarray(im).copy()
out[..., 3] = (a * (1 - kill)).astype(np.uint8)
Image.fromarray(out).save(D / "speaker_clean.png")
print("ok")
