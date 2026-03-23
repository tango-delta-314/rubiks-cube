"""
CIE LAB color space conversions.

Pure numpy math — no image library dependencies.
"""

import numpy as np


def srgb_to_linear(c):
    """Convert sRGB [0, 1] values to linear RGB."""
    c = np.asarray(c, dtype=np.float64)
    return np.where(
        c <= 0.04045,
        c / 12.92,
        ((c + 0.055) / 1.055) ** 2.4,
    )


# sRGB → XYZ matrix (D65 illuminant)
_SRGB_TO_XYZ = np.array([
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041],
])

# D65 white point normalization
_D65_X = 0.95047
_D65_Z = 1.08883


def rgb_to_lab(rgb_array):
    """
    Convert (..., 3) uint8 or float RGB to CIE LAB.

    Handles any shape with 3 channels in the
    last dimension.
    """
    rgb = rgb_array.astype(np.float64)
    if rgb.max() > 1.0:
        rgb = rgb / 255.0
    linear = srgb_to_linear(rgb)

    shape = linear.shape
    xyz = linear.reshape(-1, 3) @ _SRGB_TO_XYZ.T
    xyz = xyz.reshape(shape)

    xyz[..., 0] /= _D65_X
    xyz[..., 2] /= _D65_Z

    epsilon, kappa = 0.008856, 903.3
    f = np.where(
        xyz > epsilon,
        xyz ** (1.0 / 3.0),
        (kappa * xyz + 16.0) / 116.0,
    )

    L = 116.0 * f[..., 1] - 16.0
    a = 500.0 * (f[..., 0] - f[..., 1])
    b = 200.0 * (f[..., 1] - f[..., 2])

    return np.stack([L, a, b], axis=-1)
