from Pack_data import unpacking_data
from DC_coding import decode_dc_coefficients
from AC_coding import decode_ac_coefficients
from ZigZag import inverse_zigzag
from Quanting import dequanting_luma, dequanting_chr
from DCT import idct2
from Converter import reverse_converter
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

def up_sampling(channel, k=2):
    height, width = channel.shape
    channel_i_ds = np.zeros((height * k, width * k))
    for i in range(height):
        for j in range(width):
            channel_i_ds[i * k:(i + 1) * k, j * k:(j + 1) * k] = [
                [channel[i][j] for _ in range(k)] for _ in range(k)
            ]
    return channel_i_ds


N = 8   #Размер блоков
#Качество изображения
qual = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

for quality in qual:
    with open(f"logs/{quality}", 'rb') as f:
        packed = f.read()

    data = unpacking_data(packed)

    height, width = data["image_size"]
    h_blocks = (height + N - 1) // N
    w_blocks = (width + N - 1) // N
    height, width = height // 2, width // 2
    h_blocks_chr = (height + N - 1) // N
    w_blocks_chr = (width + N - 1) // N

    decompressed = restored = np.zeros((h_blocks * N, w_blocks * N), dtype=np.float32)

    #Декодирование DC коэффициентов
    luma_dc = data["luma_dc"]
    cb_dc = data["cb_dc"]
    cr_dc = data["cr_dc"]

    is_luma = True
    luma_dc = decode_dc_coefficients(luma_dc, h_blocks * w_blocks, is_luma)
    is_luma = False
    cb_dc = decode_dc_coefficients(cb_dc, h_blocks_chr * w_blocks_chr, is_luma)
    cr_dc = decode_dc_coefficients(cr_dc, h_blocks_chr * w_blocks_chr, is_luma)

    #Декодирование AC коэффициентов
    luma_ac = data["luma_ac"]
    cb_ac = data["cb_ac"]
    cr_ac = data["cr_ac"]

    is_luma = True
    luma_ac_decode = []
    for block in luma_ac:
        luma_ac_decode.append(decode_ac_coefficients(block, is_luma))
    is_luma = False
    cb_ac_decode = []
    for block in cb_ac:
        cb_ac_decode.append(decode_ac_coefficients(block, is_luma))
    cr_ac_decode = []
    for block in cr_ac:
        cr_ac_decode.append(decode_ac_coefficients(block, is_luma))

    #Восстановление блоков
    is_luma = True
    luma_ch = restore_image(luma_dc, luma_ac_decode, h_blocks, w_blocks, N, is_luma, quality, height * 2, width * 2)
    is_luma = False
    cb_ch = restore_image(cb_dc, cb_ac_decode, h_blocks_chr, w_blocks_chr, N, is_luma, quality, height, width)
    cr_ch = restore_image(cr_dc, cr_ac_decode, h_blocks_chr, w_blocks_chr, N, is_luma, quality, height, width)

    cb_ch = upsample(cb_ch, data["image_size"])
    cr_ch = upsample(cr_ch, data["image_size"])

    rgb_restored = reverse_converter(
        np.clip(luma_ch, 0, 255).astype(np.uint8),
        np.clip(cb_ch, 0, 255).astype(np.uint8),
        np.clip(cr_ch, 0, 255).astype(np.uint8)
    )

    Image.fromarray(rgb_restored).save(f"logs/{quality}.png")
