
from PIL import Image

from Converter import converter
from Downsampling import downsampling
from To_blocks import to_blocks
from DCT import dct2
from Quanting import quanting_luma, quanting_chr
from ZigZag import zigzag
from DC_coding import dc_coding
from AC_coding import ac_coding
from Pack_data import pack_data

N = 8   #Размер блоков
# quality = 0   #Качество изображения
qual = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
for quality in qual:
    image = Image.open("Original/Lenna.png").convert("RGB")

    ycbcr = converter(image)
    height, width = ycbcr.shape[:2]

    DS_image = downsampling(ycbcr)

    y_ch = DS_image['y']
    cb_ch = DS_image['cb']
    cr_ch = DS_image['cr']

    y_block = to_blocks(y_ch, N)
    cb_block = to_blocks(cb_ch, N)
    cr_block = to_blocks(cr_ch, N)

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

    cb_array = []
    for block in cb_block:
        cb_dct = dct2(block)
        cb_quant = quanting_chr(cb_dct, quality)
        cb_list = zigzag(cb_quant)
        cb_array.append(cb_list)

    is_luma = False
    cb_dc_coded = dc_coding(cb_array, is_luma)
    cb_ac_coded = []
    for block in cb_array:
        cb_ac_coded.append(ac_coding(block, is_luma))

    cr_array = []
    for block in cr_block:
        cr_dct = dct2(block)
        cr_quant = quanting_chr(cr_dct, quality)
        cr_list = zigzag(cr_quant)
        cr_array.append(cr_list)

    is_luma = False
    cr_dc_coded = dc_coding(cr_array, is_luma)
    cr_ac_coded = []
    for block in cr_array:
        cr_ac_coded.append(ac_coding(block, is_luma))

    packed = pack_data(
        image_size=(height, width),
        quality=quality,
        luma_dc_coded=luma_dc_coded,
        luma_ac_coded=luma_ac_coded,
        cb_dc_coded=cb_dc_coded,
        cb_ac_coded=cb_ac_coded,
        cr_dc_coded=cr_dc_coded,
        cr_ac_coded=cr_ac_coded
    )

    with open(f"logs/{quality}", 'wb') as f:
        f.write(packed)

