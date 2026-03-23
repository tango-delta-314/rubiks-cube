#!/usr/bin/env python3
"""
Rubik's Cube Art Converter
==========================
Converts any image to a 6-color Rubik's
cube palette.

Two modes:
  photo   — Floyd-Steinberg dithering in LAB.
  pop-art — Posterize, halftone suppression,
            dot dither, black outlines.

Usage:
  python -m image.convert in.jpg out.png [opts]

See --help for full option list.
"""

import argparse
import sys
import numpy as np
from PIL import Image, ImageEnhance

from .palette import (
    build_palette,
    build_color_penalties,
)
from .quantize import (
    quantize_photo,
    quantize_pop_art,
    pipe,
)
from .sticker_grid import build_sticker_grid
from .render import render_grid, format_color_stats


# ── Pre-processing (Phase 1) ───────────

def preprocess(
    img_pil,
    pre_scale=None,
    saturation=1.3,
    contrast=1.1,
):
    """
    Optional memory-cap resize, then
    saturation/contrast boost.
    """
    steps = []
    if pre_scale:
        steps.append(lambda img: img.resize(pre_scale, Image.LANCZOS))
    if saturation != 1.0:
        steps.append(lambda img: ImageEnhance.Color(img).enhance(saturation))
    if contrast != 1.0:
        steps.append(lambda img: ImageEnhance.Contrast(img).enhance(contrast))
    return pipe(img_pil, *steps) if steps else img_pil


# ── Progress reporting ──────────────────

def make_photo_reporter():
    """Reporter callback for photo progress."""
    def report(pct):
        done = pct // 5
        bar = "█" * done + "░" * (20 - done)
        end = "\n" if pct >= 100 else ""
        print(
            f"\r  Quantizing [{bar}] {pct}%",
            end=end, flush=True,
        )
    return report


def make_pop_art_reporter():
    """Reporter callback for pop-art steps."""
    return lambda msg: print(
        f"  [pop-art] {msg}...",
    )


# ── Config summary ──────────────────────

def format_config_summary(
    args, saturation, contrast,
    cubes_w, cubes_h,
    stickers_w, stickers_h,
    sticker_size,
):
    """Build the startup banner lines."""
    mode = args.mode.upper()
    lines = [
        f"\nRubik's Cube Art Converter"
        f"  [{mode} MODE]",
        f"   Input:       {args.input}",
        f"   Output:      {args.output}",
    ]

    pal = args.palette
    if args.palette_black:
        pal += " (+black)"
    lines.append(f"   Palette:     {pal}")

    if args.cubes:
        lines.append(
            f"   Cubes:       {cubes_w}W"
            f" x {cubes_h}H"
            f"  ({stickers_w}"
            f"x{stickers_h} stickers)"
        )
        out_w = stickers_w * sticker_size
        out_h = stickers_h * sticker_size
        lines.append(
            f"   Output size: {out_w}"
            f"x{out_h}px"
            f"  ({sticker_size}px/sticker)"
        )

    lines.append(
        f"   Saturation:  {saturation}x"
        f"  |  Contrast: {contrast}x"
    )

    if args.mode == "photo":
        dither = (
            "off" if args.no_dither
            else "Floyd-Steinberg"
        )
        lines.append(
            f"   Dithering:   {dither}",
        )
        if args.texture:
            s = args.texture_strength
            lines.append(
                f"   Texture:     on"
                f" (strength={s})"
            )
    else:
        lvl = args.posterize_levels
        lines.append(
            f"   Posterize:   {lvl}"
            f" levels/channel"
        )
        outlines = (
            "off" if args.no_outlines
            else f"{args.edge_thickness}px black"
        )
        lines.append(
            f"   Outlines:    {outlines}",
        )
        halftone = (
            "off" if args.halftone_blur == 0
            else f"blur r={args.halftone_blur}"
        )
        lines.append(
            f"   Halftone:    {halftone}",
        )
        dots = (
            "off" if args.no_dot_dither
            else f"on (threshold="
                 f"{args.dot_threshold})"
        )
        lines.append(
            f"   Dot dither:  {dots}",
        )

    if args.warm > 0:
        lines.append(
            f"   Warm bias:   {args.warm}"
            f" (penalizing Green/Blue)"
        )

    return lines


# ── CLI argument parsing ────────────────

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description=(
            "Convert an image to Rubik's"
            " cube art (6 colors)."
        ),
        formatter_class=(
            argparse.RawDescriptionHelpFormatter
        ),
    )
    p.add_argument(
        "input", nargs="?",
        help="Input image path",
    )
    p.add_argument(
        "output", nargs="?",
        help="Output image path",
    )

    p.add_argument(
        "--mode",
        default="photo",
        choices=["photo", "pop-art"],
        help="'photo' (default) or 'pop-art'",
    )

    p.add_argument(
        "--cubes",
        type=int, nargs=2,
        metavar=("W", "H"),
        help="Cubes wide x tall",
    )
    p.add_argument(
        "--sticker-size",
        type=int, default=10,
        metavar="N",
        help="Pixels per sticker (default: 10)",
    )

    p.add_argument(
        "--pre-scale",
        type=int, nargs=2,
        metavar=("W", "H"),
        help="Resize source before processing",
    )

    p.add_argument(
        "--saturation",
        type=float, default=None,
        help="Saturation multiplier"
             " (default: 1.3/1.6)",
    )
    p.add_argument(
        "--contrast",
        type=float, default=None,
        help="Contrast multiplier"
             " (default: 1.1/1.4)",
    )
    p.add_argument(
        "--palette",
        default="standard",
        choices=["standard", "modern"],
        help="Palette preset (default: standard)",
    )
    p.add_argument(
        "--palette-black",
        action="store_true",
        help="Replace White with Black",
    )
    p.add_argument(
        "--show-palette",
        action="store_true",
        help="Print palette and exit",
    )
    p.add_argument(
        "--pixel-grid",
        action="store_true",
        help="Overlay grid lines on output",
    )

    # Photo mode
    p.add_argument(
        "--no-dither",
        action="store_true",
        help="[photo] Disable F-S dithering",
    )
    p.add_argument(
        "--texture",
        action="store_true",
        help="[photo] Stochastic variation",
    )
    p.add_argument(
        "--texture-strength",
        type=float, default=0.5,
        metavar="S",
        help="[photo] Intensity 0–1 (def: 0.5)",
    )
    p.add_argument(
        "--warm",
        type=float, default=0.0,
        metavar="W",
        help="[photo] Warm bias 0–1 (def: 0.0)",
    )

    # Pop-art mode
    p.add_argument(
        "--posterize-levels",
        type=int, default=4,
        help="[pop-art] Levels/channel (def: 4)",
    )
    p.add_argument(
        "--edge-thickness",
        type=int, default=2,
        help="[pop-art] Outline px (def: 2)",
    )
    p.add_argument(
        "--no-outlines",
        action="store_true",
        help="[pop-art] Skip outlines",
    )
    p.add_argument(
        "--halftone-blur",
        type=float, default=1.5,
        help="[pop-art] Blur radius (def: 1.5)",
    )
    p.add_argument(
        "--no-dot-dither",
        action="store_true",
        help="[pop-art] Disable dot dither",
    )
    p.add_argument(
        "--dot-threshold",
        type=float, default=25.0,
        help="[pop-art] Dot threshold (def: 25)",
    )

    return p.parse_args(argv)


# ── Main pipeline ──────────────────────

def main(argv=None):
    args = parse_args(argv)

    # Mode-sensitive defaults
    is_pop = args.mode == "pop-art"
    saturation = (
        args.saturation
        if args.saturation is not None
        else (1.6 if is_pop else 1.3)
    )
    contrast = (
        args.contrast
        if args.contrast is not None
        else (1.4 if is_pop else 1.1)
    )

    palette_rgb, palette_lab, palette_names = (
        build_palette(
            args.palette,
            use_black=args.palette_black,
        )
    )

    if args.show_palette:
        pal = args.palette
        if args.palette_black:
            pal += " (+black)"
        print(f"\nPalette: {pal}")
        print("-" * 35)
        for name, rgb in zip(
            palette_names, palette_rgb,
        ):
            print(
                f"  {name:<8}"
                f"  RGB({rgb[0]:3d},"
                f" {rgb[1]:3d},"
                f" {rgb[2]:3d})"
            )
        print()
        sys.exit(0)

    if not args.input or not args.output:
        parse_args(["--help"])

    # Derive sticker grid from cube count
    if args.cubes:
        cubes_w, cubes_h = args.cubes
    else:
        cubes_w, cubes_h = None, None
    stickers_w = (
        cubes_w * 3 if cubes_w else None
    )
    stickers_h = (
        cubes_h * 3 if cubes_h else None
    )
    sticker_size = args.sticker_size

    # Banner
    summary = format_config_summary(
        args, saturation, contrast,
        cubes_w, cubes_h,
        stickers_w, stickers_h,
        sticker_size,
    )
    print("\n".join(summary))
    print()

    # ── Phase 1: Image → Sticker Grid ──

    print("  Loading image...")
    img = Image.open(args.input).convert("RGB")
    src_w, src_h = img.size
    print(f"  Source: {src_w}x{src_h}px")

    pre_scale = (
        tuple(args.pre_scale)
        if args.pre_scale else None
    )
    img = preprocess(
        img,
        pre_scale=pre_scale,
        saturation=saturation,
        contrast=contrast,
    )
    proc_w, proc_h = img.size
    if pre_scale:
        print(
            f"  Pre-scaled to:"
            f" {proc_w}x{proc_h}px"
        )
    else:
        print(
            f"  Processing at full res:"
            f" {proc_w}x{proc_h}px"
        )

    img_array = np.array(img)

    # Color penalties
    penalties = None
    if args.warm > 0:
        penalties = build_color_penalties(
            palette_names,
            palette_rgb,
            warm=args.warm,
        )
        penalty_desc = ", ".join(
            f"{n}x{p:.2f}"
            for n, p
            in zip(palette_names, penalties)
            if p > 1.01
        )
        print(f"  Warm penalties: {penalty_desc}")

    # Quantize at full resolution
    dot_grid_px = (
        max(1, proc_w // stickers_w)
        if stickers_w else 3
    )

    if args.mode == "pop-art":
        processed = quantize_pop_art(
            img_array,
            palette_rgb,
            palette_lab,
            posterize_levels=args.posterize_levels,
            halftone_blur=args.halftone_blur,
            edge_thickness=args.edge_thickness,
            draw_outlines=not args.no_outlines,
            dot_dither=not args.no_dot_dither,
            dot_grid_size=dot_grid_px,
            dot_threshold=args.dot_threshold,
            penalties=penalties,
            report=make_pop_art_reporter(),
        )
    else:
        processed = quantize_photo(
            img_array,
            palette_rgb,
            palette_lab,
            dither=not args.no_dither,
            penalties=penalties,
            report=make_photo_reporter(),
        )

    # Downsample to sticker grid
    if cubes_w:
        print(
            f"  Downsampling to sticker grid"
            f" ({stickers_w}x{stickers_h})..."
        )
        grid = build_sticker_grid(
            processed,
            cubes_w, cubes_h,
            palette_rgb,
            palette_lab,
            palette_names,
            penalties=penalties,
        )
    else:
        grid = None

    # ── Phase 2: Sticker Grid → Output ──

    if grid:
        print(
            f"  Rendering"
            f" ({sticker_size}px/sticker)..."
        )
        result_pil = render_grid(
            grid,
            sticker_size=sticker_size,
            pixel_grid=args.pixel_grid,
            texture=(
                args.mode == "photo"
                and args.texture
            ),
            texture_strength=(
                args.texture_strength
            ),
            palette_lab=palette_lab,
        )
        stat_colors = grid.colors
    else:
        result_pil = Image.fromarray(processed)
        stat_colors = processed

    # ── Save & report ───────────────────

    result_pil.save(args.output)
    out_w, out_h = result_pil.size
    print(
        f"\nSaved to: {args.output}"
        f"  ({out_w}x{out_h}px)"
    )

    print("\n  Color breakdown:")
    for line in format_color_stats(
        stat_colors,
        palette_rgb,
        palette_names,
    ):
        print(line)
    print()

    if args.cubes:
        total = cubes_w * cubes_h
        print(
            f"  Physical build:"
            f" {cubes_w} x {cubes_h}"
            f" = {total} cubes total\n"
        )


if __name__ == "__main__":
    main()
