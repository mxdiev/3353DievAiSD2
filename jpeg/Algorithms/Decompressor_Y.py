from Pack_data import unpacking_data_Y
from DC_coding import decode_dc_coefficients
from AC_coding import decode_ac_coefficients
from ZigZag import inverse_zigzag
from Quanting import dequanting_luma, dequanting_chr
from DCT import idct2
import numpy as np
from PIL import Image

def split_ac(h, w, all_ac_coeffs, block_size=63):
    num_full_blocks = len(all_ac_coeffs) // block_size
    remaining = len(all_ac_coeffs) % block_size

    blocks = np.array_split(all_ac_coeffs[:num_full_blocks * block_size], num_full_blocks)

    if remaining > 0:
        last_block = all_ac_coeffs[num_full_blocks * block_size:]
        padded_last_block = np.pad(last_block,
                                   (0, block_size - remaining),
                                   'constant',
                                   constant_values=0)
        blocks.append(padded_last_block)

    while len(blocks) != h * w:
        zeros = np.zeros(block_size)
        blocks.append(zeros)
    return blocks


def restore_image(dc_coefs, ac_coefs, h_blocks, w_blocks, N, is_luma, quality,
                  h, w):
    restored = np.zeros((h_blocks * N, w_blocks * N), dtype=np.float32)
    for i in range(h_blocks):
        for j in range(w_blocks):
            idx = i * w_blocks + j
            dc = dc_coefs[idx]
            ac = ac_coefs[idx]

            block = np.insert(ac, 0, dc)
            block = inverse_zigzag(block, N)
            if is_luma:
                block_dequant = dequanting_luma(block, quality)
            else:
                block_dequant = dequanting_chr(block, quality)

            block_idct = idct2(block_dequant)
            y_start, y_end = i * N, (i + 1) * N
            x_start, x_end = j * N, (j + 1) * N

            restored[y_start:y_end, x_start:x_end] = block_idct

    restored = restored[:h, :w]

    restored = np.clip(restored, 0, 255).astype(np.uint8)

    return restored

def upsample(channel: np.ndarray, size):
    img = Image.fromarray(channel)
    return np.array(img.resize((size[1], size[0]), Image.BILINEAR))

N = 8   #Размер блоков
quality = 0   #Качество изображения

with open(f"{quality}", 'rb') as f:
    packed = f.read()

data = unpacking_data_Y(packed)

height, width = data["image_size"]
h_blocks = (height + N - 1) // N
w_blocks = (width + N - 1) // N

decompressed = restored = np.zeros((h_blocks * N, w_blocks * N), dtype=np.float32)

#Декодирование DC коэффициентов
luma_dc = data["luma_dc"]

is_luma = True
luma_dc = decode_dc_coefficients(luma_dc, h_blocks * w_blocks, is_luma)

#Декодирование AC коэффициентов
luma_ac = data["luma_ac"]

is_luma = True
luma_ac_decode = []
for block in luma_ac:
    luma_ac_decode.append(decode_ac_coefficients(block, is_luma))

#Восстановление блоков
is_luma = True
luma_ch = restore_image(luma_dc, luma_ac_decode, h_blocks, w_blocks, N, is_luma, quality, height, width)

y_restored = np.array(np.clip(luma_ch, 0, 255).astype(np.uint8))

Image.fromarray(y_restored, mode='L').save(f"{quality}.png")
