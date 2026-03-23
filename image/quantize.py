"""
Quantization strategies for mapping images
to a Rubik's cube palette.

Two modes:
  - photo:   Floyd-Steinberg dithering in LAB
  - pop-art: posterize, halftone suppression,
             structured dither, outlines

All functions are pure (data in, data out).
Progress reporting is injected via an optional
`report` callable.
"""

import numpy as np
from PIL import Image, ImageFilter
from functools import reduce

from .color import rgb_to_lab
from .palette import nearest_palette_color


# ── Pipeline helper ─────────────────────

def pipe(value, *fns):
    """pipe(x, f, g) == g(f(x))."""
    return reduce(lambda v, f: f(v), fns, value)


# ── Photo mode ──────────────────────────

def quantize_photo(
    image_rgb,
    palette_rgb,
    palette_lab,
    dither=True,
    penalties=None,
    report=None,
):
    """
    Nearest-color in LAB + optional
    Floyd-Steinberg error diffusion (in RGB).
    Best for photographs with continuous
    tonal gradients.
    """
    _report = report or (lambda *a, **kw: None)
    h, w = image_rgb.shape[:2]
    img = image_rgb.astype(np.float64)
    out = np.zeros((h, w, 3), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            old_px = np.clip(
                img[y, x], 0, 255,
            ).astype(np.uint8)
            old_lab = rgb_to_lab(
                old_px.reshape(1, 1, 3),
            ).reshape(3)
            dists = np.sum(
                (palette_lab - old_lab) ** 2,
                axis=1,
            )
            if penalties is not None:
                dists = dists * penalties
            best_idx = np.argmin(dists)
            new_px = palette_rgb[best_idx]
            out[y, x] = new_px

            if dither:
                err = img[y, x] - new_px.astype(np.float64)
                if x + 1 < w:
                    img[y,   x+1] += err * 7.0 / 16.0
                if y + 1 < h:
                    if x - 1 >= 0:
                        img[y+1, x-1] += err * 3.0 / 16.0
                    img[y+1, x  ] += err * 5.0 / 16.0
                    if x + 1 < w:
                        img[y+1, x+1] += err * 1.0 / 16.0

        if y % max(1, h // 20) == 0:
            _report(int(100 * y / h))

    _report(100)
    return out


# ── Pop-art: individual pipeline steps ──

def suppress_halftones(img_pil, blur_radius=1.5):
    """
    Gaussian blur to dissolve Ben-Day dot
    patterns, followed by mild unsharp mask
    to recover edge crispness.
    """
    blurred = img_pil.filter(
        ImageFilter.GaussianBlur(
            radius=blur_radius,
        )
    )
    return blurred.filter(
        ImageFilter.UnsharpMask(
            radius=1, percent=80, threshold=2,
        )
    )


def posterize(img_array, levels=4):
    """
    Reduce each channel to `levels` discrete
    steps via staircase function. Maps each
    bucket to its midpoint.
    """
    step = 256.0 / levels
    quantized = (
        np.floor(img_array.astype(np.float64) / step)
        * step
        + step * 0.5
    )
    return np.clip(quantized, 0, 255).astype(
        np.uint8,
    )


def detect_edges(img_pil, thickness=2):
    """
    Laplacian edge detection + dilation.
    Returns boolean mask (H, W).
    Returns None if scipy is unavailable.
    """
    try:
        from scipy.ndimage import binary_dilation
    except ImportError:
        return None

    gray = img_pil.convert("L")
    lap = gray.filter(ImageFilter.Kernel(
        size=(3, 3),
        kernel=[
            -1, -1, -1,
            -1,  8, -1,
            -1, -1, -1,
        ],
        scale=1,
        offset=0,
    ))
    edge_array = np.array(lap)

    nonzero = edge_array[edge_array > 0]
    threshold = (
        np.percentile(nonzero, 75)
        if len(nonzero) > 0
        else 30
    )
    edge_mask = edge_array > threshold

    k = thickness * 2 + 1
    struct = np.ones((k, k), dtype=bool)
    return binary_dilation(
        edge_mask, structure=struct,
    )


def composite_outlines(
    quantized_rgb,
    edge_mask,
    outline_color=(0, 0, 0),
):
    """
    Burn edge pixels to a solid color on top
    of the quantized image.
    """
    result = quantized_rgb.copy()
    result[edge_mask] = outline_color
    return result


def _bayer_matrix(n):
    """
    Generate an n*n ordered dither (Bayer)
    matrix normalized to [0, 1).
    """
    size = 1
    while size < n:
        size *= 2
    M = np.array(
        [[0, 2], [3, 1]], dtype=np.float64,
    )
    while M.shape[0] < size:
        M = np.block([
            [4*M,     4*M + 2],
            [4*M + 3, 4*M + 1],
        ])
    return (M / (size * size))[:n, :n]


def structured_dither(
    img_array,
    palette_rgb,
    palette_lab,
    grid_size=3,
    ambiguity_threshold=25.0,
):
    """
    Ben-Day dot structured dither for pop-art.

    Clear pixels get hard nearest-color snap.
    Ambiguous pixels (two palette colors compete)
    get a Bayer-matrix checkerboard, with dot
    density proportional to LAB proximity.
    """
    h, w = img_array.shape[:2]
    flat_lab = rgb_to_lab(img_array).reshape(-1, 3)

    diff = (
        flat_lab[:, np.newaxis, :]
        - palette_lab[np.newaxis, :, :]
    )
    dists = np.sum(diff ** 2, axis=2)

    sorted_idx = np.argsort(dists, axis=1)
    best_idx = sorted_idx[:, 0]
    second_idx = sorted_idx[:, 1]
    n = len(dists)
    idx = np.arange(n)
    best_dist = dists[idx, best_idx]
    second_dist = dists[idx, second_idx]

    out = palette_rgb[best_idx].reshape(
        h, w, 3,
    ).copy()

    thresh_sq = ambiguity_threshold ** 2
    is_ambiguous = best_dist > thresh_sq
    ys, xs = np.where(is_ambiguous.reshape(h, w))

    if len(ys) > 0:
        bd = best_dist[is_ambiguous]
        sd = second_dist[is_ambiguous]
        second_frac = bd / (bd + sd)

        bayer = _bayer_matrix(grid_size)
        ty = (ys // grid_size) % grid_size
        tx = (xs // grid_size) % grid_size
        bayer_val = bayer[ty, tx]

        use_second = second_frac > bayer_val
        best_here = best_idx[is_ambiguous]
        second_here = second_idx[is_ambiguous]

        out[ys, xs] = np.where(
            use_second[:, np.newaxis],
            palette_rgb[second_here],
            palette_rgb[best_here],
        )

    return out


def quantize_pop_art(
    image_rgb,
    palette_rgb,
    palette_lab,
    posterize_levels=4,
    halftone_blur=1.5,
    edge_thickness=2,
    draw_outlines=True,
    dot_dither=True,
    dot_grid_size=3,
    dot_threshold=25.0,
    penalties=None,
    report=None,
):
    """
    Pop-art quantization pipeline:
      1. Halftone suppression
      2. Posterization
      3. Edge detection
      4. Structured dot dither (or hard snap)
      5. Outline compositing
    """
    _report = report or (lambda msg: None)
    img_pil = Image.fromarray(image_rgb)

    # Step 1: Suppress halftone dots
    if halftone_blur > 0:
        _report(
            "Suppressing halftone patterns"
            f" (blur r={halftone_blur})"
        )
        img_pil = suppress_halftones(
            img_pil, halftone_blur,
        )

    # Step 2: Posterize
    _report(
        f"Posterizing"
        f" ({posterize_levels} levels/channel)"
    )
    img_array = posterize(
        np.array(img_pil),
        levels=posterize_levels,
    )

    # Step 3: Edge detection
    edge_mask = None
    if draw_outlines and edge_thickness > 0:
        _report(
            "Detecting edges"
            f" (thickness={edge_thickness}px)"
        )
        edge_mask = detect_edges(
            Image.fromarray(img_array),
            thickness=edge_thickness,
        )
        if edge_mask is None:
            _report(
                "Warning: scipy not installed"
                " — skipping outlines"
            )

    # Step 4: Quantize
    if dot_dither:
        _report(
            "Quantizing with Ben-Day dot dither"
            f" (threshold={dot_threshold})"
        )
        result = structured_dither(
            img_array,
            palette_rgb,
            palette_lab,
            grid_size=dot_grid_size,
            ambiguity_threshold=dot_threshold,
        )
    else:
        _report("Quantizing (hard LAB mapping)")
        result = nearest_palette_color(
            img_array,
            palette_rgb,
            palette_lab,
            penalties,
        )

    # Step 5: Composite outlines
    if edge_mask is not None:
        _report("Compositing black outlines")
        result = composite_outlines(
            result, edge_mask,
        )

    return result
