import numpy as np

def get_newquant_mat(matrix:  np.ndarray, quality) -> np.ndarray:
    if quality < 50 and quality != 0:
        scale = 5000 / quality
    elif quality == 0:
        scale = 5000
    elif quality == 100:
        return np.ones_like(matrix)
    else:
        scale = 200 - 2 * quality
    new_matrix = np.floor((matrix * scale + 50) / 100).astype(np.float32)
    return new_matrix

def quanting_luma(block: np.ndarray, quality):
    Q = np.array([
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68, 109, 103, 77],
        [24, 35, 55, 64, 81, 104, 113, 92],
        [49, 64, 78, 87, 103, 121, 120, 101],
        [72, 92, 95, 98, 112, 100, 103, 99]
    ], dtype = np.float32)
    if quality != 50: Q = get_newquant_mat(Q, quality)

    quantized = np.round(block / Q)
    return quantized

def quanting_chr(block: np.ndarray, quality):
    Q = np.array([
        [17, 18, 24, 47, 99, 99, 99, 99],
        [18, 21, 26, 66, 99, 99, 99, 99],
        [24, 26, 56, 99, 99, 99, 99, 99],
        [47, 66, 99, 99, 99, 99, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99]
    ], dtype=np.float32)
    if quality != 50: Q = get_newquant_mat(Q, quality)
    quantized = np.round(block / Q)
    return quantized

def dequanting_luma(block: np.ndarray, quality):
    Q = np.array([
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68, 109, 103, 77],
        [24, 35, 55, 64, 81, 104, 113, 92],
        [49, 64, 78, 87, 103, 121, 120, 101],
        [72, 92, 95, 98, 112, 100, 103, 99]
    ], dtype = np.float32)
    if quality != 50: Q = get_newquant_mat(Q, quality)

    dequantized = block * Q
    return dequantized.astype(np.float32)

def dequanting_chr(block: np.ndarray, quality):
    Q = np.array([
        [17, 18, 24, 47, 99, 99, 99, 99],
        [18, 21, 26, 66, 99, 99, 99, 99],
        [24, 26, 56, 99, 99, 99, 99, 99],
        [47, 66, 99, 99, 99, 99, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99]
    ], dtype=np.float32)
    if quality != 50: Q = get_newquant_mat(Q, quality)

    dequantized = block * Q
    return dequantized.astype(np.float32)
