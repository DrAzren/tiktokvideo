"""Two SVG maps from Natural Earth 10m admin-0 (public domain): Peninsular Malaya, and all of Malaysia.

Outputs public/img/map_pen.svg, public/img/map_my.svg and maps.json (pin pixel positions).
Run: ../../../.venv/bin/python make_maps.py /path/to/ne_10m_admin_0_countries.geojson
"""

import json
import sys
from pathlib import Path

D = Path(__file__).parent
NE = json.loads(Path(sys.argv[1]).read_text())
LAND, LAND_MY, EDGE = "#d9c9a6", "#efe3c6", "#8a6f45"

PINS_PEN = {"Pulau Pinang": (100.33, 5.41), "Taiping": (100.74, 4.85), "Tanjung Rambutan": (101.16, 4.68)}
PINS_MY = {"George Town": (100.33, 5.41), "Alor Setar": (100.37, 6.12), "Ipoh": (101.08, 4.60), "Kuala Lumpur": (101.69, 3.14),
           "Seremban": (101.94, 2.73), "Melaka": (102.25, 2.19), "Johor Bahru": (103.76, 1.49), "Kuantan": (103.33, 3.81),
           "Kuala Terengganu": (103.14, 5.33), "Kota Bharu": (102.24, 6.13), "Kuching": (110.34, 1.55),
           "Kota Kinabalu": (116.07, 5.98), "Sibu": (111.82, 2.29), "Tawau": (117.89, 4.25)}


def polys(feat):
    g = feat["geometry"]
    return g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]


def make(name, bbox, size, pins, emph="MYS"):
    lon0, lat0, lon1, lat1 = bbox
    W, H = size
    sx = W / (lon1 - lon0)
    sy = H / (lat1 - lat0)
    s = min(sx, sy)
    ox = (W - (lon1 - lon0) * s) / 2
    oy = (H - (lat1 - lat0) * s) / 2

    def P(lon, lat):
        return ox + (lon - lon0) * s, oy + (lat1 - lat) * s

    paths = []
    for f in NE["features"]:
        iso = f["properties"].get("ADM0_A3")
        if iso not in ("MYS", "THA", "SGP", "IDN", "BRN", "MMR", "PHL"):
            continue
        d = []
        for poly in polys(f):
            ring = poly[0]
            xs = [c[0] for c in ring]
            ys = [c[1] for c in ring]
            if max(xs) < lon0 or min(xs) > lon1 or max(ys) < lat0 or min(ys) > lat1:
                continue
            pts = [P(*c) for c in ring[::1]]
            d.append("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z")
        if d:
            fill = LAND_MY if iso == emph else LAND
            op = 1 if iso == emph else 0.45
            paths.append(f'<path d="{" ".join(d)}" fill="{fill}" fill-opacity="{op}" stroke="{EDGE}" stroke-width="1.6" stroke-opacity="{op}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
           + "".join(paths) + "</svg>")
    (D / "public" / "img" / f"{name}.svg").write_text(svg)
    return {k: [round(v, 1) for v in P(*ll)] for k, ll in pins.items()}


def main():
    out = {"pen": {"size": [1100, 1000], "pins": make("map_pen", (99.4, 1.1, 104.6, 6.9), (1100, 1000), PINS_PEN)},
           "my": {"size": [1800, 820], "pins": make("map_my", (99.3, 0.6, 119.5, 7.6), (1800, 820), PINS_MY)}}
    (D / "maps.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out)[:400])


if __name__ == "__main__":
    main()
