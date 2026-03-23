"""
Rendering a StickerGrid into a viewable image.

Phase 2: everything here takes a StickerGrid
(or its colors) and produces display output.
None of this affects the domain model that
the solver consumes.
"""

import numpy as np
from PIL import Image, ImageDraw

from .color import rgb_to_lab
from .sticker_grid import StickerGrid


# ── Texture (display-only variation) ────

def apply_texture(
    grid, palette_lab, strength=0.5, seed=None,
):
    """
    Inject controlled stochastic variation into
    a sticker grid copy for a "busy", tactile
    mosaic look. Returns a new StickerGrid —
    the original is not mutated.

    Two mechanisms scaled by strength (0–1):
      1. LAB noise injection — nudges border
         stickers to tip either way
      2. Stochastic palette mixing — flips
         competitive colors probabilistically
    """
    rng = np.random.default_rng(seed)
    palette_rgb = grid.palette_rgb
    flat_lab = rgb_to_lab(
        grid.colors,
    ).reshape(-1, 3)
    n = flat_lab.shape[0]

    # Mechanism 1: LAB noise
    noise_sigma = strength * 25.0
    noisy_lab = flat_lab + rng.normal(
        0, noise_sigma, flat_lab.shape,
    )

    diff = (
        noisy_lab[:, np.newaxis, :]
        - palette_lab[np.newaxis, :, :]
    )
    dists = np.sum(diff ** 2, axis=2)
    noise_idx = np.argmin(dists, axis=1)

    # Mechanism 2: stochastic palette mixing
    sorted_idx = np.argsort(dists, axis=1)
    best_idx = sorted_idx[:, 0]
    second_idx = sorted_idx[:, 1]
    idx = np.arange(n)
    best_dist = dists[idx, best_idx]
    second_dist = dists[idx, second_idx]

    total = best_dist + second_dist
    competition = np.where(
        total > 0, best_dist / total, 0.0,
    )

    mix_threshold = 0.5 - strength * 0.35
    eligible = competition > mix_threshold

    flip_prob = competition * strength * 0.8
    flip = eligible & (rng.random(n) < flip_prob)

    final_idx = noise_idx.copy()
    final_idx[flip] = second_idx[flip]

    sh, sw = grid.colors.shape[:2]
    textured = palette_rgb[final_idx].reshape(
        sh, sw, 3,
    )

    return StickerGrid(
        colors=textured,
        palette_rgb=grid.palette_rgb,
        palette_names=grid.palette_names,
        cubes_wide=grid.cubes_wide,
        cubes_tall=grid.cubes_tall,
    )


# ── Upscale for display ────────────────

def upscale_for_display(sticker_colors, size):
    """
    Tile each sticker to size x size pixels.
    Returns a PIL Image.
    """
    big = np.repeat(
        np.repeat(sticker_colors, size, axis=0),
        size,
        axis=1,
    )
    return Image.fromarray(big.astype(np.uint8))


# ── Grid overlays ──────────────────────

def draw_grid_overlay(
    img_pil, sticker_size, stickers_per_cube=3,
):
    """
    Draw sticker-boundary (thin) and
    cube-boundary (thick) grid lines.
    """
    w, h = img_pil.size
    overlay = Image.new(
        "RGBA", (w, h), (0, 0, 0, 0),
    )
    draw = ImageDraw.Draw(overlay)
    cube_size = sticker_size * stickers_per_cube

    sticker_color = (0, 0, 0, 50)
    for x in range(0, w, sticker_size):
        draw.line(
            [(x, 0), (x, h)],
            fill=sticker_color, width=1,
        )
    for y in range(0, h, sticker_size):
        draw.line(
            [(0, y), (w, y)],
            fill=sticker_color, width=1,
        )

    cube_color = (0, 0, 0, 140)
    for x in range(0, w, cube_size):
        draw.line(
            [(x, 0), (x, h)],
            fill=cube_color, width=2,
        )
    for y in range(0, h, cube_size):
        draw.line(
            [(0, y), (w, y)],
            fill=cube_color, width=2,
        )

    return Image.alpha_composite(
        img_pil.convert("RGBA"), overlay,
    ).convert("RGB")


# ── Color statistics ────────────────────

def format_color_stats(
    colors, palette_rgb, palette_names,
):
    """
    Build a color-breakdown summary from a
    sticker color array.
    Returns a list of formatted lines.
    """
    unique, counts = np.unique(
        colors.reshape(-1, 3),
        axis=0,
        return_counts=True,
    )
    total = colors.shape[0] * colors.shape[1]

    def format_entry(rgb, count):
        name = next(
            (
                n for n, c
                in zip(palette_names, palette_rgb)
                if list(c) == rgb
            ),
            "Black" if rgb == [0, 0, 0] else "?",
        )
        bar = "█" * int(30 * count / total)
        pct = 100 * count / total
        return f"    {name:<8} {bar} {pct:5.1f}%"

    entries = sorted(
        zip(unique.tolist(), counts.tolist()),
        key=lambda x: -x[1],
    )
    return list(
        map(lambda e: format_entry(*e), entries),
    )


# ── Full render pipeline ────────────────

def render_grid(
    grid,
    sticker_size=10,
    pixel_grid=False,
    texture=False,
    texture_strength=0.5,
    palette_lab=None,
):
    """
    Render a StickerGrid to a display-ready
    PIL Image.

    Optionally applies texture (display-only
    variation) and grid overlays. The input
    grid is never mutated.
    """
    display_grid = grid

    if texture and palette_lab is not None:
        display_grid = apply_texture(
            display_grid,
            palette_lab,
            strength=texture_strength,
        )

    result_pil = upscale_for_display(
        display_grid.colors, sticker_size,
    )

    if pixel_grid and sticker_size > 1:
        result_pil = draw_grid_overlay(
            result_pil, sticker_size,
        )

    return result_pil
