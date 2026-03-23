"""
Sticker grid — the core domain model for
Rubik's cube art.

A StickerGrid represents the precise color of
every sticker in a Rubik's cube mosaic. This is
the artifact consumed by both:
  - the renderer (viewable image)
  - the solver  (turns per cube)

Each cell = one physical sticker.
A 3x3 block of cells = one cube face.
"""

from dataclasses import dataclass
import numpy as np

from .color import rgb_to_lab
from .palette import nearest_palette_color


@dataclass
class StickerGrid:
    """
    A 2D grid of palette-snapped sticker colors.

    Attributes:
        colors:       (H, W, 3) uint8, one
                      RGB entry per sticker
        palette_rgb:  (P, 3) uint8
        palette_names: list[str]
        cubes_wide:   cubes across
        cubes_tall:   cubes down
    """
    colors: np.ndarray
    palette_rgb: np.ndarray
    palette_names: list
    cubes_wide: int
    cubes_tall: int

    @property
    def stickers_wide(self):
        return self.cubes_wide * 3

    @property
    def stickers_tall(self):
        return self.cubes_tall * 3

    @property
    def total_cubes(self):
        return self.cubes_wide * self.cubes_tall

    def cube_face(self, cx, cy):
        """
        Extract the 3x3 sticker block for the
        cube at grid position (cx, cy).
        Returns a (3, 3, 3) uint8 array.
        """
        sy, sx = cy * 3, cx * 3
        return self.colors[sy:sy+3, sx:sx+3]


def downsample_to_stickers(
    processed_rgb,
    stickers_w,
    stickers_h,
    palette_rgb,
    palette_lab,
    penalties=None,
):
    """
    Reduce a fully-processed image to the
    target sticker grid by area-averaging,
    then re-snap each sticker to the nearest
    palette color in LAB space.

    Returns (stickers_h, stickers_w, 3) uint8.
    """
    h, w = processed_rgb.shape[:2]

    crop_h = (h // stickers_h) * stickers_h
    crop_w = (w // stickers_w) * stickers_w
    img = processed_rgb[
        :crop_h, :crop_w
    ].astype(np.float64)

    block_h = crop_h // stickers_h
    block_w = crop_w // stickers_w
    averaged = (
        img
        .reshape(
            stickers_h, block_h,
            stickers_w, block_w, 3,
        )
        .mean(axis=(1, 3))
    )
    averaged = np.clip(
        averaged, 0, 255,
    ).astype(np.uint8)

    return nearest_palette_color(
        averaged,
        palette_rgb,
        palette_lab,
        penalties,
    )


def build_sticker_grid(
    processed_rgb,
    cubes_w,
    cubes_h,
    palette_rgb,
    palette_lab,
    palette_names,
    penalties=None,
):
    """
    Build a StickerGrid from a fully-processed
    (quantized) image.

    This is the bridge between Phase 1 (image
    processing) and everything downstream
    (rendering, solving).
    """
    stickers_w = cubes_w * 3
    stickers_h = cubes_h * 3

    sticker_colors = downsample_to_stickers(
        processed_rgb,
        stickers_w,
        stickers_h,
        palette_rgb,
        palette_lab,
        penalties,
    )

    return StickerGrid(
        colors=sticker_colors,
        palette_rgb=palette_rgb,
        palette_names=palette_names,
        cubes_wide=cubes_w,
        cubes_tall=cubes_h,
    )
