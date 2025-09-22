import numpy as np
from PIL import Image

np.set_printoptions(suppress=True)

def converter(image):
    rgb = np.array(image, dtype=np.float32)

    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]

    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = -0.1687 * r - 0.3313 * g + 0.5 * b + 128
    cr = 0.5 * r - 0.4187 * g - 0.0813 * b + 128

    ycbcr = np.stack([y, cb, cr], axis=-1)
    ycbcr = np.clip(ycbcr, 0, 255)

    return ycbcr

def reverse_converter(Y, Cb, Cr):
    Y = Y.astype(np.float32)
    Cb = Cb.astype(np.float32) - 128
    Cr = Cr.astype(np.float32) - 128

    R = Y + 1.402 * Cr
    G = Y - 0.34414 * Cb - 0.71414 * Cr
    B = Y + 1.772 * Cb

    rgb = np.stack([R, G, B], axis=-1)
    return np.clip(rgb, 0, 255).astype(np.uint8)