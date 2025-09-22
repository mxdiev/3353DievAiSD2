from PIL import Image
import numpy as np
from To_blocks import to_blocks
from DCT import dct2
from Quanting import quanting_luma
from ZigZag import zigzag
from DC_coding import dc_coding
from AC_coding import ac_coding
from Pack_data import pack_data_Y

N = 8  # Размер блоков
# quality = 0  # Качество изображения
qual = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

for quality in qual:
    image = Image.open("2048_no_diz.png").convert("L")

    y_ch = np.array(image, dtype=np.float32)
    height, width = y_ch.shape[:2]

    y_block = to_blocks(y_ch, N)

    luma_array = []
    for block in y_block:
        y_dct = dct2(block)
        y_quant = quanting_luma(y_dct, quality)
        y_list = zigzag(y_quant)
        luma_array.append(y_list)

    is_luma = True
    luma_dc_coded = dc_coding(luma_array, is_luma)
    luma_ac_coded = []
    for block in luma_array:
        luma_ac_coded.append(ac_coding(block, is_luma))

    packed = pack_data_Y(
        image_size=(height, width),
        quality=50,
        luma_dc_coded=luma_dc_coded,
        luma_ac_coded=luma_ac_coded,
    )

    with open(f"{quality}", 'wb') as f:
        f.write(packed)

