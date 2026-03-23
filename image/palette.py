"""
Rubik's cube color palettes and
palette-space operations.

Palette construction, nearest-color lookup
(in LAB space), and optional color penalties
for biasing away from specific hues.
"""

import numpy as np

from .color import rgb_to_lab


# ── Palette definitions (sRGB, 0–255) ──

PALETTES = {
    "standard": {
        "White":  (255, 255, 255),
        "Yellow": (255, 213,   0),
        "Red":    (196,  30,  58),
        "Orange": (255,  88,   0),
        "Blue":   (  0,  70, 173),
        "Green":  (  0, 155,  72),
    },
    "modern": {
        "White":  (250, 250, 248),
        "Yellow": (255, 210,   0),
        "Red":    (186,  12,  47),
        "Orange": (255,  80,   0),
        "Blue":   (  0,  60, 200),
        "Green":  (  0, 160,  70),
    },
}

BLACK = (0, 0, 0)


# ── Palette construction ────────────────

def build_palette(preset="standard", use_black=False):
    """
    Build palette arrays from a preset name.

    Returns (rgb_values, lab_values, names):
      - rgb_values: (P, 3) uint8
      - lab_values: (P, 3) float64
      - names: list[str] of length P
    """
    palette_dict = dict(
        PALETTES.get(preset, PALETTES["standard"])
    )
    if use_black:
        palette_dict.pop("White", None)
        palette_dict["Black"] = BLACK

    names = list(palette_dict.keys())
    rgb_values = np.array(
        [palette_dict[n] for n in names],
        dtype=np.uint8,
    )
    lab_values = rgb_to_lab(
        rgb_values.reshape(1, -1, 3)
    ).reshape(-1, 3)

    return rgb_values, lab_values, names


# ── Nearest-color lookup ────────────────

def nearest_palette_color(
    img_array,
    palette_rgb,
    palette_lab,
    penalties=None,
):
    """
    Map each pixel in img_array (H, W, 3) to
    its nearest palette color in LAB space.
    Returns (H, W, 3) uint8.

    penalties: optional (P,) distance multipliers
    — values > 1.0 make that color harder to win.
    """
    h, w = img_array.shape[:2]
    flat_lab = rgb_to_lab(img_array).reshape(-1, 3)

    diff = (
        flat_lab[:, np.newaxis, :]
        - palette_lab[np.newaxis, :, :]
    )
    dists = np.sum(diff ** 2, axis=2)

    if penalties is not None:
        dists = dists * penalties[np.newaxis, :]

    best = np.argmin(dists, axis=1)
    return palette_rgb[best].reshape(h, w, 3)


# ── Color penalties (warm bias) ─────────

def build_color_penalties(
    palette_names, palette_rgb, warm=0.0,
):
    """
    Build a (P,) array of distance multipliers,
    one per palette color.

    warm (0.0–1.0): penalizes Green and Blue so
    they only win when clearly dominant. Useful
    for warm-toned subjects (fur, skin, fire).

    Penalties multiply squared LAB distance, so
    a penalty of 2.0 means the color must be
    sqrt(2) closer to beat an unpenalized one.
    """
    n = len(palette_names)
    penalties = np.ones(n, dtype=np.float64)

    if warm <= 0.0:
        return penalties

    for i, rgb in enumerate(palette_rgb):
        lab = rgb_to_lab(
            np.array(rgb, dtype=np.uint8)
            .reshape(1, 1, 3)
        ).reshape(3)
        a_star, b_star = lab[1], lab[2]
        coolness = (
            max(0.0, -a_star / 80.0)
            + max(0.0, -b_star / 80.0)
        )
        penalties[i] = 1.0 + coolness * warm * 2.0

    return penalties
