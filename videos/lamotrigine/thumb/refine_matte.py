"""Clean the remove-background cutouts for the thumbnail: fill holes inside the body (the V-neck trim came out
transparent), keep only the largest component (drops a cabinet fragment above the head), and pull the edge in
slightly with a soft feather (removes the grey wall halo around the hair)."""
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

for name in sys.argv[1:]:
    src = Image.open(f"cut_{name}.png").convert("RGBA")
    rgb = np.asarray(Image.open(f"face_{name}.png").convert("RGB"))
    a = np.asarray(src)[..., 3].astype(np.float32) / 255
    solid = a > 0.5
    lab, n = ndimage.label(solid)
    sizes = ndimage.sum(solid, lab, range(1, n + 1))
    body = lab == (1 + int(np.argmax(sizes)))
    body = ndimage.binary_fill_holes(body)
    body = ndimage.binary_erosion(body, iterations=3)
    # grey wall stuck to the hair edge: in a 16 px band at the silhouette, above ear level (the edge there is hair,
    # never skin), drop light pixels; hair is dark (luma < ~80), the wall is light grey (~160-190)
    luma = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
    band = body & (ndimage.distance_transform_edt(body) < 16)
    rows = np.arange(body.shape[0])[:, None] < 560
    body &= ~(band & rows & (luma > 105))
    lab, n2 = ndimage.label(body)
    body = lab == (1 + int(np.argmax(ndimage.sum(body, lab, range(1, n2 + 1)))))
    body = ndimage.binary_opening(body, iterations=2)
    soft = np.asarray(Image.fromarray((body * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2)), dtype=np.float32) / 255
    alpha = np.where(body, np.maximum(soft, a * 0 + soft), soft)
    out = np.dstack([rgb, (alpha * 255).astype(np.uint8)])
    Image.fromarray(out, "RGBA").save(f"subject_{name}.png")
    print(name, "components:", n, "-> kept largest; holes filled; edge pulled 3 px")
